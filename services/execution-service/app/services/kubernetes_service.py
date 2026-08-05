import os
import time

from kubernetes import client, config

from app.utils.resource_parser import ResourceParser


class KubernetesService:

    def __init__(self):

        try:
            config.load_incluster_config()
            print("Loaded in-cluster config")

        except Exception:
            config.load_kube_config()
            print("Loaded local kubeconfig")

        self.core_api = client.CoreV1Api()
        self.policy_api = client.PolicyV1Api()

    # --------------------------------------------------
    # Scheduling Information
    # --------------------------------------------------

    def get_scheduling_info(self):

        return ResourceParser.parse(

            self.core_api

        )

    # --------------------------------------------------
    # Get Current Node Name
    # --------------------------------------------------

    def get_current_node_name(self):

        pod_name = os.environ.get("HOSTNAME")

        if not pod_name:

            raise Exception(
                "HOSTNAME environment variable not found."
            )

        namespace = os.environ.get(

            "POD_NAMESPACE",

            "kubeai"

        )

        pod = self.core_api.read_namespaced_pod(

            name=pod_name,

            namespace=namespace

        )

        print(

            f"[K8S] Execution service is running on node: {pod.spec.node_name}"

        )

        return pod.spec.node_name

    # --------------------------------------------------
    # Cordon Node
    # --------------------------------------------------

    def cordon_node(self, node_name):

        body = {

            "spec": {

                "unschedulable": True

            }

        }

        self.core_api.patch_node(

            node_name,

            body

        )

    # --------------------------------------------------
    # Uncordon Node
    # --------------------------------------------------

    def uncordon_node(self, node_name):

        body = {

            "spec": {

                "unschedulable": False

            }

        }

        self.core_api.patch_node(

            node_name,

            body

        )

    # --------------------------------------------------
    # Wait Until Node Removed
    # --------------------------------------------------

    def wait_until_node_removed(

        self,

        node_name,

        timeout=600

    ):

        print(

            f"[K8S] Waiting for node {node_name} to disappear..."

        )

        start = time.time()

        while True:

            nodes = self.core_api.list_node().items

            exists = any(

                node.metadata.name == node_name

                for node in nodes

            )

            if not exists:

                print(

                    f"[K8S] Node {node_name} removed."

                )

                return True

            if time.time() - start > timeout:

                print(

                    f"[K8S] Timeout waiting for node {node_name}."

                )

                return False

            time.sleep(5)

    # --------------------------------------------------
    # Wait Until Expected Node Count
    # --------------------------------------------------

    def wait_until_node_count(

        self,

        expected_count,

        timeout=600

    ):

        start = time.time()

        while True:

            ready_nodes = 0

            nodes = self.core_api.list_node().items

            for node in nodes:

                for condition in node.status.conditions:

                    if (

                        condition.type == "Ready"

                        and condition.status == "True"

                    ):

                        ready_nodes += 1

                        break

            if ready_nodes >= expected_count:

                return True

            if time.time() - start > timeout:

                return False

            time.sleep(10)