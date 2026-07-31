"""
Centralized PromQL queries used by the Metric Service.
"""

# ------------------------------------------------------------------
# Cluster Overview
# ------------------------------------------------------------------

CPU_USAGE = """
100 - (
    avg(
        rate(node_cpu_seconds_total{mode="idle"}[5m])
    ) * 100
)
"""

MEMORY_USAGE = """
(
    1 -
    (
        sum(node_memory_MemAvailable_bytes)
        /
        sum(node_memory_MemTotal_bytes)
    )
) * 100
"""


# ------------------------------------------------------------------
# Pod Metrics
# ------------------------------------------------------------------

TOP_CPU_PODS = """
topk(
    10,
    sum by (pod) (
        rate(container_cpu_usage_seconds_total{
            container!="",
            pod!=""
        }[5m])
    )
)
"""

TOP_MEMORY_PODS = """
topk(
    10,
    sum by (pod) (
        container_memory_working_set_bytes{
            container!="",
            pod!=""
        }
    )
)
"""


# ------------------------------------------------------------------
# Node Metrics
# ------------------------------------------------------------------

NODE_CPU_USAGE = """
100 - (
    avg by(instance)(
        rate(node_cpu_seconds_total{mode="idle"}[5m])
    ) * 100
)
"""

NODE_MEMORY_USAGE = """
(
    1 -
    (
        node_memory_MemAvailable_bytes
        /
        node_memory_MemTotal_bytes
    )
) * 100
"""

# ----------------------------------------------------
# Historical Queries
# ----------------------------------------------------

CPU_HISTORY = """
100 - (
    avg(
        rate(node_cpu_seconds_total{mode="idle"}[5m])
    ) * 100
)
"""

MEMORY_HISTORY = """
100 * (
    1 -
    (
        sum(node_memory_MemAvailable_bytes)
        /
        sum(node_memory_MemTotal_bytes)
    )
)
"""