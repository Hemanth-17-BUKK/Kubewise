class ClusterContextBuilder:

    @staticmethod
    def build(
        metrics: dict,
        cluster: dict,
        scheduling: dict,
        validation: dict
    ):

        cpu_values = [
            point["value"]
            for point in metrics["cpu_history"]["values"]
        ]

        memory_values = [
            point["value"]
            for point in metrics["memory_history"]["values"]
        ]

        return {

            "metrics": {

                "current": {

                    "cpu": metrics["overview"]["cpu"]["cpu_usage"],

                    "memory": metrics["overview"]["memory"]["memory_usage"]

                },

                "history": {

                    "average_cpu": round(
                        sum(cpu_values) / len(cpu_values),
                        2
                    ),

                    "peak_cpu": round(
                        max(cpu_values),
                        2
                    ),

                    "minimum_cpu": round(
                        min(cpu_values),
                        2
                    ),

                    "average_memory": round(
                        sum(memory_values) / len(memory_values),
                        2
                    ),

                    "peak_memory": round(
                        max(memory_values),
                        2
                    ),

                    "minimum_memory": round(
                        min(memory_values),
                        2
                    )

                },

                "top_cpu_pods": metrics["overview"]["top_cpu_pods"],

                "top_memory_pods": metrics["overview"]["top_memory_pods"]

            },

            "cluster": cluster,

            "scheduling": {

                "summary": scheduling["summary"],

                "nodes": scheduling["nodes"]

            },

            "optimization_validation": validation

        }