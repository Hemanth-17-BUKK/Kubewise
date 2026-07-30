from uuid import uuid4

from app.aws.sts_client import STSClient
from app.aws.eks_client import EKSClient

from app.schemas.aws import (
    AWSConnectResponse,
    ClusterInfo
)


class AWSService:

    def __init__(self):
        self.sts = STSClient()

    def connect(self, role_arn: str):

        credentials = self.sts.assume_role(role_arn)

        account_id = self.sts.get_account_id(credentials)

        eks = EKSClient(credentials)

        cluster_names = eks.list_clusters()

        clusters = []

        for cluster_name in cluster_names:

            cluster = eks.describe_cluster(cluster_name)

            clusters.append(
                ClusterInfo(
                    name=cluster["name"],
                    arn=cluster["arn"],
                    region=cluster["arn"].split(":")[3],
                    status=cluster["status"],
                    version=cluster["version"],
                )
            )

        return AWSConnectResponse(
            connectionId=str(uuid4()),
            accountId=account_id,
            clusters=clusters
        )