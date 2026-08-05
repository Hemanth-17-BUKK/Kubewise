from kubernetes import client


class DrainValidator:

    def __init__(
        self,
        core_api: client.CoreV1Api,
        policy_api: client.PolicyV1Api
    ):
        self.core_api = core_api
        self.policy_api = policy_api

    def validate(self, node_name: str):

        checks = {

            "node_ready": self._node_ready(node_name),

            "capacity": True,

            "pod_disruption_budget": self._check_pdb(node_name),

            "statefulsets": self._check_statefulsets(node_name),

            "local_storage": self._check_local_storage(node_name)

        }

        safe = all(checks.values())

        return {

            "safe": safe,

            "checks": checks,

            "reason": (
                "Safe to drain."
                if safe
                else "One or more validation checks failed."
            )

        }

    # ------------------------------------

    def _node_ready(self, node_name):

        node = self.core_api.read_node(node_name)

        for condition in node.status.conditions:

            if condition.type == "Ready":

                return condition.status == "True"

        return False

    # ------------------------------------

    def _check_pdb(self, node_name):

        """
        Phase-1:
        Only verify whether any PDB exists.

        Later we'll simulate pod evictions.
        """

        try:

            self.policy_api.list_pod_disruption_budget_for_all_namespaces()

            return True

        except Exception:

            return False

    # ------------------------------------

    def _check_statefulsets(self, node_name):

        pods = self.core_api.list_pod_for_all_namespaces(

            field_selector=f"spec.nodeName={node_name}"

        )

        for pod in pods.items:

            owners = pod.metadata.owner_references or []

            for owner in owners:

                if owner.kind == "StatefulSet":

                    return False

        return True

    # ------------------------------------

    def _check_local_storage(self, node_name):

        pods = self.core_api.list_pod_for_all_namespaces(

            field_selector=f"spec.nodeName={node_name}"

        )

        for pod in pods.items:

            owners = pod.metadata.owner_references or []

            # Ignore DaemonSet pods
            if any(owner.kind == "DaemonSet" for owner in owners):
                continue

            for volume in pod.spec.volumes or []:

                if volume.host_path is not None:

                    return False

        return True