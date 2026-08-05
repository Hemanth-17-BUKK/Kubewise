class NodeSelector:

    @staticmethod
    def select(
        nodes,
        current_node=None
    ):

        candidates = []

        for node in nodes:

            # ----------------------------------------
            # Never remove the node running the optimizer
            # ----------------------------------------

            if current_node is not None and node["name"] == current_node:

                print(
                    f"[SELECTOR] Skipping current execution node: {current_node}"
                )

                continue

            # ----------------------------------------
            # Ignore nodes that only contain DaemonSets
            # ----------------------------------------

            if node["workload_pods"] == 0:
                continue

            score = 0

            score += node["workload_pods"] * 1000
            score += node["requested_cpu"]
            score += node["requested_memory"]

            if node["has_statefulset"]:
                score += 10000

            if node["has_local_storage"]:
                score += 5000

            if node["has_pdb"]:
                score += 3000

            candidates.append({

                "name": node["name"],

                "score": score,

                "workload_pods": node["workload_pods"],

                "requested_cpu": node["requested_cpu"],

                "requested_memory": node["requested_memory"],

                "has_statefulset": node["has_statefulset"],

                "has_local_storage": node["has_local_storage"],

                "has_pdb": node["has_pdb"]

            })

        if len(candidates) == 0:

            raise Exception(
                "No removable worker node found."
            )

        candidates.sort(

            key=lambda x: x["score"]

        )

        print(
            f"[SELECTOR] Selected node: {candidates[0]['name']}"
        )

        return candidates[0]