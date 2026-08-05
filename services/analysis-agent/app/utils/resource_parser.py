from kubernetes import client


class ResourceParser:

    @staticmethod
    def parse(core_api: client.CoreV1Api):

        nodes = []

        total_alloc_cpu = 0
        total_alloc_mem = 0

        total_requested_cpu = 0
        total_requested_mem = 0

        total_available_cpu = 0
        total_available_mem = 0

        total_workload_pods = 0
        total_daemonset_pods = 0

        node_list = core_api.list_node()

        for node in node_list.items:

            alloc_cpu_raw = node.status.allocatable["cpu"]

            if alloc_cpu_raw.endswith("m"):
                alloc_cpu = int(alloc_cpu_raw[:-1])
            else:
                alloc_cpu = int(float(alloc_cpu_raw) * 1000)

            capacity_cpu_raw = node.status.capacity["cpu"]

            if capacity_cpu_raw.endswith("m"):
                capacity_cpu = int(capacity_cpu_raw[:-1])
            else:
                capacity_cpu = int(float(capacity_cpu_raw) * 1000)

            alloc_mem = (
                int(node.status.allocatable["memory"][:-2]) / 1024
            )

            capacity_mem = (
                int(node.status.capacity["memory"][:-2]) / 1024
            )

            requested_cpu = 0
            requested_mem = 0

            daemonset_pods = 0
            workload_pods = 0
            pod_count = 0

            pods = core_api.list_pod_for_all_namespaces(
                field_selector=f"spec.nodeName={node.metadata.name}"
            )

            for pod in pods.items:

                pod_count += 1

                owners = pod.metadata.owner_references or []

                if any(
                    owner.kind == "DaemonSet"
                    for owner in owners
                ):
                    daemonset_pods += 1
                else:
                    workload_pods += 1

                for container in pod.spec.containers:

                    requests = container.resources.requests or {}

                    cpu = requests.get("cpu")
                    mem = requests.get("memory")

                    if cpu:

                        if cpu.endswith("m"):
                            requested_cpu += int(cpu[:-1])
                        else:
                            requested_cpu += int(float(cpu) * 1000)

                    if mem:

                        if mem.endswith("Mi"):
                            requested_mem += int(mem[:-2])

                        elif mem.endswith("Gi"):
                            requested_mem += int(
                                float(mem[:-2]) * 1024
                            )

            available_cpu = alloc_cpu - requested_cpu

            available_mem = alloc_mem - requested_mem

            available_cpu_percent = round(
                (available_cpu / alloc_cpu) * 100,
                2
            )

            available_memory_percent = round(
                (available_mem / alloc_mem) * 100,
                2
            )

            total_alloc_cpu += alloc_cpu
            total_alloc_mem += alloc_mem

            total_requested_cpu += requested_cpu
            total_requested_mem += requested_mem

            total_available_cpu += available_cpu
            total_available_mem += available_mem

            total_workload_pods += workload_pods
            total_daemonset_pods += daemonset_pods

            nodes.append({

                "name": node.metadata.name,

                "capacity": {

                    "cpu_millicores": capacity_cpu,

                    "memory_mib": round(capacity_mem)

                },

                "allocatable": {

                    "cpu_millicores": alloc_cpu,

                    "memory_mib": round(alloc_mem)

                },

                "requested": {

                    "cpu_millicores": requested_cpu,

                    "memory_mib": requested_mem

                },

                "available": {

                    "cpu_millicores": available_cpu,

                    "memory_mib": round(available_mem)

                },

                "available_cpu_percent": available_cpu_percent,

                "available_memory_percent": available_memory_percent,

                "pod_count": pod_count,

                "workload_pods": workload_pods,

                "daemonset_pods": daemonset_pods

            })

        summary = {

            "total_allocatable_cpu": total_alloc_cpu,

            "total_allocatable_memory": round(
                total_alloc_mem
            ),

            "total_requested_cpu": total_requested_cpu,

            "total_requested_memory": total_requested_mem,

            "total_available_cpu": total_available_cpu,

            "total_available_memory": round(
                total_available_mem
            ),

            "total_workload_pods": total_workload_pods,

            "total_daemonset_pods": total_daemonset_pods,

            "average_available_cpu_percent": round(
                (total_available_cpu / total_alloc_cpu) * 100,
                2
            ),

            "average_available_memory_percent": round(
                (total_available_mem / total_alloc_mem) * 100,
                2
            )

        }

        return {

            "summary": summary,

            "nodes": nodes

        }