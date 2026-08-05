class SchedulingValidator:

    @staticmethod
    def validate(
        scheduling: dict,
        target_node_count: int
    ):

        summary = scheduling["summary"]

        current_nodes = len(scheduling["nodes"])

        alloc_cpu_per_node = (
            summary["total_allocatable_cpu"] /
            current_nodes
        )

        alloc_mem_per_node = (
            summary["total_allocatable_memory"] /
            current_nodes
        )

        future_alloc_cpu = (
            alloc_cpu_per_node *
            target_node_count
        )

        future_alloc_memory = (
            alloc_mem_per_node *
            target_node_count
        )

        cpu_headroom = (
            future_alloc_cpu -
            summary["total_requested_cpu"]
        )

        memory_headroom = (
            future_alloc_memory -
            summary["total_requested_memory"]
        )

        can_fit_cpu = cpu_headroom >= 0
        can_fit_memory = memory_headroom >= 0

        cpu_headroom_percent = round(
            cpu_headroom /
            future_alloc_cpu * 100,
            2
        )

        memory_headroom_percent = round(
            memory_headroom /
            future_alloc_memory * 100,
            2
        )

        future_pods = round(
            summary["total_workload_pods"] /
            target_node_count,
            2
        )

        optimization_safe = (
            can_fit_cpu and
            can_fit_memory
        )

        if optimization_safe:

            optimization_type = "REDUCE_NODE_COUNT"

            recommended_node_count = target_node_count

            validation_reason = (
                f"Scheduling validation succeeded. "
                f"All workloads fit on {target_node_count} nodes "
                f"with {cpu_headroom_percent}% CPU headroom "
                f"and {memory_headroom_percent}% memory headroom."
            )

        else:

            optimization_type = "NO_ACTION_REQUIRED"

            recommended_node_count = current_nodes

            reasons = []

            if not can_fit_cpu:
                reasons.append("CPU capacity is insufficient")

            if not can_fit_memory:
                reasons.append("Memory capacity is insufficient")

            validation_reason = (
                "Scheduling validation failed. " +
                " and ".join(reasons) +
                "."
            )

        return {

            "can_fit_cpu": can_fit_cpu,

            "can_fit_memory": can_fit_memory,

            "cpu_headroom_percent": cpu_headroom_percent,

            "memory_headroom_percent": memory_headroom_percent,

            "future_pods_per_node": future_pods,

            "optimization_safe": optimization_safe,

            "optimization_type": optimization_type,

            "recommended_node_count": recommended_node_count,

            "validation_reason": validation_reason

        }