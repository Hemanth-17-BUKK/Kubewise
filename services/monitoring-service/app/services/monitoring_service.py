import base64
import tempfile

import boto3
import requests

from app.aws.eks_client import EKSClient
from app.aws.sts_client import STSClient
from app.aws.token import EKSTokenGenerator


class MonitoringService:

    def __init__(self):
        self.sts = STSClient()
        self.token_generator = EKSTokenGenerator()

    def connect(
        self,
        role_arn: str,
        cluster_name: str,
    ):
        # Step 1: Assume the customer's IAM role
        credentials = self.sts.assume_role(role_arn)

        print(credentials["AccessKeyId"])
        print(credentials["SecretAccessKey"])
        print(credentials["SessionToken"])

        # Verify assumed identity
        sts = boto3.client(
            "sts",
            aws_access_key_id=credentials["AccessKeyId"],
            aws_secret_access_key=credentials["SecretAccessKey"],
            aws_session_token=credentials["SessionToken"],
        )

        print("\n" + "=" * 80)
        print("ASSUMED ROLE IDENTITY")
        print(sts.get_caller_identity())
        print("=" * 80)

        # Step 2: Create authenticated EKS client
        eks = EKSClient(credentials)

        # Step 3: Fetch cluster details
        cluster = eks.describe_cluster(cluster_name)

        endpoint = cluster["endpoint"]
        ca_data = cluster["certificateAuthority"]["data"]
        region = cluster["arn"].split(":")[3]

        print(f"Cluster Endpoint: {endpoint}")
        print(f"Region: {region}")

        # Step 4: Generate Kubernetes authentication token
        token = self.token_generator.generate(
            cluster_name=cluster_name,
            region=region,
            credentials=credentials,
        )

        print("\nTOKEN PREFIX")
        print(token[:120] + "...")

        # -------------------------------------------------------
        # Decode CA certificate into a temporary file
        # -------------------------------------------------------
        ca_file = tempfile.NamedTemporaryFile(delete=False, suffix=".crt")

        ca_file.write(base64.b64decode(ca_data))
        ca_file.close()

        # -------------------------------------------------------
        # Direct HTTPS request to Kubernetes API
        # -------------------------------------------------------
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        }

        response = requests.get(
            f"{endpoint}/api/v1/namespaces",
            headers=headers,
            verify=ca_file.name,
            timeout=30,
        )

        print("\n" + "=" * 80)
        print("REQUEST STATUS:", response.status_code)
        print("RESPONSE HEADERS:")
        print(response.headers)
        print("RESPONSE BODY:")
        print(response.text)
        print("=" * 80)

        if response.status_code != 200:
            raise Exception(f"EKS API returned {response.status_code}")

        data = response.json()

        namespaces = [
            item["metadata"]["name"]
            for item in data["items"]
        ]

        return {
            "connected": True,
            "cluster": cluster_name,
            "namespaces": namespaces,
        }