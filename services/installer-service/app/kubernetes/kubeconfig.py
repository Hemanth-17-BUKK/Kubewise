import tempfile

import yaml

from app.models.cluster_context import ClusterContext


class KubeConfigGenerator:
    """
    Generates a temporary kubeconfig file from an
    existing ClusterContext.

    No AWS API calls are made here.
    """

    def generate(
        self,
        context: ClusterContext,
    ) -> str:

        cluster = context.cluster

        kubeconfig = {
            "apiVersion": "v1",
            "kind": "Config",
            "clusters": [
                {
                    "name": context.cluster_name,
                    "cluster": {
                        "server": cluster["endpoint"],
                        "certificate-authority-data": cluster[
                            "certificateAuthority"
                        ]["data"],
                    },
                }
            ],
            "contexts": [
                {
                    "name": context.cluster_name,
                    "context": {
                        "cluster": context.cluster_name,
                        "user": context.cluster_name,
                    },
                }
            ],
            "current-context": context.cluster_name,
            "users": [
                {
                    "name": context.cluster_name,
                    "user": {
                        "token": context.token,
                    },
                }
            ],
        }

        temp = tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".yaml",
            delete=False,
        )

        yaml.safe_dump(
            kubeconfig,
            temp,
            default_flow_style=False,
        )

        temp.close()

        return temp.name