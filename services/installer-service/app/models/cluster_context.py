from dataclasses import dataclass


@dataclass
class ClusterContext:
    """
    Holds all authentication and cluster information
    for a single request.
    """

    credentials: dict
    cluster: dict
    token: str
    cluster_name: str