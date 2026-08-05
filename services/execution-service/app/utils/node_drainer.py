import time

from kubernetes import client
from kubernetes.client.rest import ApiException


class NodeDrainer:

    PROTECTED_NAMESPACES = {
        "kube-system",
        "kube-public",
        "kube-node-lease",
        "monitoring"
    }

    def __init__(
        self,
        core_api,
        policy_api
    ):

        self.core_api = core_api
        self.policy_api = policy_api

    # --------------------------------------------------
    # Drain Node
    # --------------------------------------------------

    def drain(
        self,
        node_name
    ):

        print(f"\n[DRAIN] Starting drain for node: {node_name}")

        pods = self.core_api.list_pod_for_all_namespaces(

            field_selector=f"spec.nodeName={node_name}"

        )

        print(f"[DRAIN] Found {len(pods.items)} pods on node")

        evicted = []

        skipped = []

        for pod in pods.items:

            namespace = pod.metadata.namespace
            name = pod.metadata.name

            print(f"[DRAIN] Inspecting {namespace}/{name}")

            #
            # Skip protected namespaces
            #
            if namespace in self.PROTECTED_NAMESPACES:

                print(f"[DRAIN] Skipping protected namespace: {namespace}/{name}")

                skipped.append(f"{namespace}/{name}")

                continue

            #
            # Skip completed pods
            #
            if pod.status.phase in ("Succeeded", "Failed"):

                print(f"[DRAIN] Skipping completed pod: {namespace}/{name}")

                continue

            #
            # Skip mirror/static pods
            #
            annotations = pod.metadata.annotations or {}

            if "kubernetes.io/config.mirror" in annotations:

                print(f"[DRAIN] Skipping mirror pod: {namespace}/{name}")

                skipped.append(f"{namespace}/{name}")

                continue

            #
            # Skip DaemonSets
            #
            owners = pod.metadata.owner_references or []

            if any(owner.kind == "DaemonSet" for owner in owners):

                print(f"[DRAIN] Skipping DaemonSet: {namespace}/{name}")

                skipped.append(f"{namespace}/{name}")

                continue

            print(f"[DRAIN] Evicting {namespace}/{name}")

            eviction = client.V1Eviction(

                metadata=client.V1ObjectMeta(

                    name=name,

                    namespace=namespace

                )

            )

            try:

                self.core_api.create_namespaced_pod_eviction(

                    name=name,

                    namespace=namespace,

                    body=eviction

                )

                print(f"[DRAIN] Evicted {namespace}/{name}")

                evicted.append(

                    f"{namespace}/{name}"

                )

            except ApiException as e:

                print(f"[DRAIN ERROR] {namespace}/{name}")
                print(f"[DRAIN ERROR] Status: {e.status}")

                if e.body:
                    print(e.body)

                #
                # Pod protected by PodDisruptionBudget
                #
                if e.status == 429:

                    skipped.append(

                        f"{namespace}/{name} (Protected by PDB)"

                    )

                    continue

                #
                # Pod already removed
                #
                if e.status == 404:

                    continue

                raise

        print("[DRAIN] Waiting for application pods to leave node")

        self.wait_until_empty(node_name)

        print("[DRAIN] Node drain completed")

        return {

            "evicted": evicted,

            "skipped": skipped

        }

    # --------------------------------------------------
    # Wait Until Node Empty
    # --------------------------------------------------

    def wait_until_empty(

        self,

        node_name,

        timeout=120

    ):

        start = time.time()

        while True:

            pods = self.core_api.list_pod_for_all_namespaces(

                field_selector=f"spec.nodeName={node_name}"

            )

            remaining = []

            for pod in pods.items:

                namespace = pod.metadata.namespace

                #
                # Ignore protected namespaces
                #
                if namespace in self.PROTECTED_NAMESPACES:

                    continue

                #
                # Ignore completed pods
                #
                if pod.status.phase in ("Succeeded", "Failed"):

                    continue

                #
                # Ignore mirror/static pods
                #
                annotations = pod.metadata.annotations or {}

                if "kubernetes.io/config.mirror" in annotations:

                    continue

                #
                # Ignore DaemonSets
                #
                owners = pod.metadata.owner_references or []

                if any(owner.kind == "DaemonSet" for owner in owners):

                    continue

                remaining.append(pod)

            print(f"[WAIT] Remaining application pods: {len(remaining)}")

            if remaining:

                for pod in remaining:

                    print(
                        f"[WAIT] {pod.metadata.namespace}/{pod.metadata.name}"
                    )

            if not remaining:

                print("[WAIT] Node is empty")

                return

            if time.time() - start > timeout:

                raise TimeoutError(

                    f"Timed out waiting for application pods to leave node {node_name}."

                )

            time.sleep(5)