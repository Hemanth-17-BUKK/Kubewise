from collections import defaultdict

from kubernetes import client, config

from app.utils.resource_parser import ResourceParser


class KubernetesService:

    def __init__(self):

        try:
            config.load_incluster_config()
            print("Loaded in-cluster Kubernetes config")

        except Exception:
            config.load_kube_config()
            print("Loaded local kubeconfig")

        self.core_api = client.CoreV1Api()

    def get_cluster_info(self):

        nodes = self.core_api.list_node()

        cluster_nodes = []

        instance_groups = defaultdict(int)

        for node in nodes.items:

            labels = node.metadata.labels

            instance_type = labels.get(
                "node.kubernetes.io/instance-type",
                "Unknown"
            )

            region = labels.get(
                "topology.kubernetes.io/region",
                "Unknown"
            )

            zone = labels.get(
                "topology.kubernetes.io/zone",
                "Unknown"
            )

            cluster_nodes.append({

                "name": node.metadata.name,

                "instance_type": instance_type,

                "region": region,

                "zone": zone,

                "os": labels.get(
                    "kubernetes.io/os",
                    "Unknown"
                ),

                "architecture": labels.get(
                    "kubernetes.io/arch",
                    "Unknown"
                )

            })

            instance_groups[(instance_type, region)] += 1

        grouped_instances = []

        for (instance_type, region), count in instance_groups.items():

            grouped_instances.append({

                "instance_type": instance_type,

                "region": region,

                "count": count

            })

        return {

            "node_count": len(cluster_nodes),

            "instance_groups": grouped_instances,

            "nodes": cluster_nodes

        }

    def get_scheduling_info(self):

        return ResourceParser.parse(
            self.core_api
        )