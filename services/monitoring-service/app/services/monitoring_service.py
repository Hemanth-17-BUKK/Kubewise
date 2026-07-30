# import base64
# import tempfile

# import boto3
# import requests

# from app.aws.eks_client import EKSClient
# from app.aws.sts_client import STSClient
# from app.aws.token import EKSTokenGenerator


# class MonitoringService:

#     def __init__(self):
#         self.sts = STSClient()
#         self.token_generator = EKSTokenGenerator()

#     def connect(
#         self,
#         role_arn: str,
#         cluster_name: str,
#     ):
#         # Step 1: Assume the customer's IAM role
#         credentials = self.sts.assume_role(role_arn)

#         print(credentials["AccessKeyId"])
#         print(credentials["SecretAccessKey"])
#         print(credentials["SessionToken"])

#         # Verify assumed identity
#         sts = boto3.client(
#             "sts",
#             aws_access_key_id=credentials["AccessKeyId"],
#             aws_secret_access_key=credentials["SecretAccessKey"],
#             aws_session_token=credentials["SessionToken"],
#         )

#         print("\n" + "=" * 80)
#         print("ASSUMED ROLE IDENTITY")
#         print(sts.get_caller_identity())
#         print("=" * 80)

#         # Step 2: Create authenticated EKS client
#         eks = EKSClient(credentials)

#         # Step 3: Fetch cluster details
#         cluster = eks.describe_cluster(cluster_name)

#         endpoint = cluster["endpoint"]
#         ca_data = cluster["certificateAuthority"]["data"]
#         region = cluster["arn"].split(":")[3]

#         print(f"Cluster Endpoint: {endpoint}")
#         print(f"Region: {region}")

#         # Step 4: Generate Kubernetes authentication token
#         token = self.token_generator.generate(
#             cluster_name=cluster_name,
#             region=region,
#             credentials=credentials,
#         )

#         print("\nTOKEN PREFIX")
#         print(token[:120] + "...")

#         # -------------------------------------------------------
#         # Decode CA certificate into a temporary file
#         # -------------------------------------------------------
#         ca_file = tempfile.NamedTemporaryFile(delete=False, suffix=".crt")

#         ca_file.write(base64.b64decode(ca_data))
#         ca_file.close()

#         # -------------------------------------------------------
#         # Direct HTTPS request to Kubernetes API
#         # -------------------------------------------------------
#         headers = {
#             "Authorization": f"Bearer {token}",
#             "Accept": "application/json",
#         }

#         response = requests.get(
#             f"{endpoint}/api/v1/namespaces",
#             headers=headers,
#             verify=ca_file.name,
#             timeout=30,
#         )

#         print("\n" + "=" * 80)
#         print("REQUEST STATUS:", response.status_code)
#         print("RESPONSE HEADERS:")
#         print(response.headers)
#         print("RESPONSE BODY:")
#         print(response.text)
#         print("=" * 80)

#         if response.status_code != 200:
#             raise Exception(f"EKS API returned {response.status_code}")

#         data = response.json()

#         namespaces = [
#             item["metadata"]["name"]
#             for item in data["items"]
#         ]

#         return {
#             "connected": True,
#             "cluster": cluster_name,
#             "namespaces": namespaces,
#         }


import boto3

from app.aws.eks_client import EKSClient
from app.aws.sts_client import STSClient
from app.aws.token import EKSTokenGenerator
from app.kubernetes.client import KubernetesClient


class MonitoringService:

    def __init__(self):
        self.sts = STSClient()
        self.token_generator = EKSTokenGenerator()

    def _create_client(
        self,
        role_arn: str,
        cluster_name: str,
    ) -> KubernetesClient:
        """
        Authenticate with AWS and return an authenticated Kubernetes client.
        """

        # Step 1: Assume IAM Role
        credentials = self.sts.assume_role(role_arn)

        # Debug (optional)
        sts = boto3.client(
            "sts",
            aws_access_key_id=credentials["AccessKeyId"],
            aws_secret_access_key=credentials["SecretAccessKey"],
            aws_session_token=credentials["SessionToken"],
        )

        print("=" * 80)
        print("ASSUMED ROLE")
        print(sts.get_caller_identity())
        print("=" * 80)

        # Step 2: Describe EKS Cluster
        eks = EKSClient(credentials)
        cluster = eks.describe_cluster(cluster_name)

        endpoint = cluster["endpoint"]
        ca_data = cluster["certificateAuthority"]["data"]
        region = cluster["arn"].split(":")[3]

        # Step 3: Generate Kubernetes Token
        token = self.token_generator.generate(
            cluster_name=cluster_name,
            region=region,
            credentials=credentials,
        )

        return KubernetesClient(
            endpoint=endpoint,
            ca_data=ca_data,
            token=token,
        )

    def connect(
        self,
        role_arn: str,
        cluster_name: str,
    ):
        """
        Verify cluster connectivity.
        """

        k8s = self._create_client(
            role_arn=role_arn,
            cluster_name=cluster_name,
        )

        data = k8s.get("/api/v1/namespaces")

        namespaces = [
            item["metadata"]["name"]
            for item in data["items"]
        ]

        k8s.close()

        return {
            "connected": True,
            "cluster": cluster_name,
            "namespaces": namespaces,
        }

    def list_nodes(
        self,
        role_arn: str,
        cluster_name: str,
    ):
        k8s = self._create_client(role_arn, cluster_name)
        data = k8s.get("/api/v1/nodes")
        k8s.close()
        return data

    def list_pods(
        self,
        role_arn: str,
        cluster_name: str,
    ):
        k8s = self._create_client(role_arn, cluster_name)
        data = k8s.get("/api/v1/pods")
        k8s.close()
        return data

    def list_deployments(
        self,
        role_arn: str,
        cluster_name: str,
    ):
        k8s = self._create_client(role_arn, cluster_name)
        data = k8s.get("/apis/apps/v1/deployments")
        k8s.close()
        return data

    def list_services(
        self,
        role_arn: str,
        cluster_name: str,
    ):
        k8s = self._create_client(role_arn, cluster_name)
        data = k8s.get("/api/v1/services")
        k8s.close()
        return data

    def list_namespaces(
        self,
        role_arn: str,
        cluster_name: str,
    ):
        k8s = self._create_client(role_arn, cluster_name)
        data = k8s.get("/api/v1/namespaces")
        k8s.close()
        return data

    def get_node_metrics(
        self,
        role_arn: str,
        cluster_name: str,
    ):
        k8s = self._create_client(role_arn, cluster_name)
        data = k8s.get("/apis/metrics.k8s.io/v1beta1/nodes")
        k8s.close()
        return data

    def get_pod_metrics(
        self,
        role_arn: str,
        cluster_name: str,
    ):
        k8s = self._create_client(role_arn, cluster_name)
        data = k8s.get("/apis/metrics.k8s.io/v1beta1/pods")
        k8s.close()
        return data