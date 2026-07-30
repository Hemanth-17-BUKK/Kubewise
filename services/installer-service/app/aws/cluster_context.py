from app.aws.eks import EKSClient
from app.aws.sts import STSClient
from app.aws.token import EKSTokenGenerator
from app.config.settings import settings
from app.models.cluster_context import ClusterContext


class ClusterContextBuilder:
    """
    Builds a reusable ClusterContext by making the
    required AWS API calls exactly once.
    """

    def build(
        self,
        role_arn: str,
        cluster_name: str,
    ) -> ClusterContext:

        # 1. Assume IAM Role
        credentials = STSClient().assume_role(role_arn)

        # 2. Describe EKS Cluster
        cluster = EKSClient(credentials).describe_cluster(
            cluster_name
        )

        # 3. Generate Kubernetes authentication token
        token = EKSTokenGenerator().generate(
            cluster_name=cluster_name,
            region=settings.aws_region,
            credentials=credentials,
        )

        return ClusterContext(
            credentials=credentials,
            cluster=cluster,
            token=token,
            cluster_name=cluster_name,
        )