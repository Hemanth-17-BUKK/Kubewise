import boto3

from app.config.settings import settings


class EKSClient:

    def __init__(self, credentials):

        self.client = boto3.client(
            "eks",
            region_name=settings.aws_region,
            aws_access_key_id=credentials["AccessKeyId"],
            aws_secret_access_key=credentials["SecretAccessKey"],
            aws_session_token=credentials["SessionToken"],
        )

    def list_clusters(self):

        return self.client.list_clusters()["clusters"]

    def describe_cluster(self, cluster_name):

        return self.client.describe_cluster(
            name=cluster_name
        )["cluster"]