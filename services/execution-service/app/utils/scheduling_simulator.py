class SchedulingSimulator:

    @staticmethod
    def simulate(
        scheduling,
        removable_node
    ):

        removable = None

        cpu_available = 0
        memory_available = 0
        pods_available = 0

        # ----------------------------------------
        # Find removable node
        # ----------------------------------------

        for node in scheduling["nodes"]:

            if node["name"] == removable_node:

                removable = node

            else:

                cpu_available += node["available"]["cpu_millicores"]

                memory_available += node["available"]["memory_mib"]

                pods_available += node["pods"]["available"]

        if removable is None:

            return {

                "safe": False,

                "reason": "Node not found."

            }

        # ----------------------------------------
        # Resources that must move
        # ----------------------------------------

        cpu_needed = removable["requested"]["cpu_millicores"]

        memory_needed = removable["requested"]["memory_mib"]

        pods_needed = removable["workload_pods"]

        # ----------------------------------------
        # Validate
        # ----------------------------------------

        cpu_ok = cpu_available >= cpu_needed

        memory_ok = memory_available >= memory_needed

        pods_ok = pods_available >= pods_needed

        safe = (

            cpu_ok

            and memory_ok

            and pods_ok

        )

        # ----------------------------------------
        # Failure Reason
        # ----------------------------------------

        if safe:

            reason = "All workloads can be scheduled."

        else:

            reasons = []

            if not cpu_ok:
                reasons.append("CPU")

            if not memory_ok:
                reasons.append("Memory")

            if not pods_ok:
                reasons.append("Pod Capacity")

            reason = (

                "Insufficient "

                + ", ".join(reasons)

                + " on remaining nodes."

            )

        # ----------------------------------------

        return {

            "safe": safe,

            "cpu_needed": cpu_needed,

            "cpu_available": cpu_available,

            "memory_needed": memory_needed,

            "memory_available": memory_available,

            "pods_needed": pods_needed,

            "pods_available": pods_available,

            "checks": {

                "cpu": cpu_ok,

                "memory": memory_ok,

                "pods": pods_ok

            },

            "reason": reason

        }