import boto3

from app.config.settings import settings


class STSClient:

    def __init__(self):
        self.client = boto3.client(
            "sts",
            region_name=settings.aws_region
        )

    def assume_role(self, role_arn: str):

        response = self.client.assume_role(
            RoleArn=role_arn,
            RoleSessionName=settings.role_session_name
        )

        return response["Credentials"]

    def get_account_id(self, credentials):

        client = boto3.client(
            "sts",
            aws_access_key_id=credentials["AccessKeyId"],
            aws_secret_access_key=credentials["SecretAccessKey"],
            aws_session_token=credentials["SessionToken"],
            region_name=settings.aws_region,
        )

        return client.get_caller_identity()["Account"]