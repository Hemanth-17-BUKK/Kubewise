from collections import defaultdict

from kubernetes import client

from app.utils.resource_parser import ResourceParser


class SchedulingService:

    def __init__(self):

        self.core_api = client.CoreV1Api()

    def get_scheduling_context(self):

        nodes = self.core_api.list_node().items

        pods = self.core_api.list_pod_for_all_namespaces().items

        pods_by_node = defaultdict(list)

        for pod in pods:

            if pod.spec.node_name:

                pods_by_node[pod.spec.node_name].append(pod)

        scheduling_nodes = []

        for node in nodes:

            allocatable_cpu = ResourceParser.parse_cpu(
                node.status.allocatable["cpu"]
            )

            allocatable_memory = ResourceParser.parse_memory(
                node.status.allocatable["memory"]
            )

            capacity_cpu = ResourceParser.parse_cpu(
                node.status.capacity["cpu"]
            )

            capacity_memory = ResourceParser.parse_memory(
                node.status.capacity["memory"]
            )

            requested_cpu = 0
            requested_memory = 0

            for pod in pods_by_node[node.metadata.name]:

                for container in pod.spec.containers:

                    requests = container.resources.requests or {}

                    requested_cpu += ResourceParser.parse_cpu(
                        requests.get("cpu", "0")
                    )

                    requested_memory += ResourceParser.parse_memory(
                        requests.get("memory", "0Mi")
                    )

            scheduling_nodes.append({

                "name": node.metadata.name,

                "capacity": {

                    "cpu_millicores": capacity_cpu,

                    "memory_mib": capacity_memory

                },

                "allocatable": {

                    "cpu_millicores": allocatable_cpu,

                    "memory_mib": allocatable_memory

                },

                "requested": {

                    "cpu_millicores": requested_cpu,

                    "memory_mib": requested_memory

                },

                "available": {

                    "cpu_millicores": allocatable_cpu - requested_cpu,

                    "memory_mib": allocatable_memory - requested_memory

                },

                "pod_count": len(
                    pods_by_node[node.metadata.name]
                )

            })

        return {

            "nodes": scheduling_nodes

        }