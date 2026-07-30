# import json
# import os
# import subprocess


# class EKSTokenGenerator:

#     def generate(
#         self,
#         cluster_name: str,
#         region: str,
#         credentials: dict,
#     ) -> str:

#         env = os.environ.copy()

#         env["AWS_ACCESS_KEY_ID"] = credentials["AccessKeyId"]
#         env["AWS_SECRET_ACCESS_KEY"] = credentials["SecretAccessKey"]
#         env["AWS_SESSION_TOKEN"] = credentials["SessionToken"]
#         env["AWS_DEFAULT_REGION"] = region

#         print("\n================ AWS ENV ================")
#         print("ACCESS KEY :", credentials["AccessKeyId"][:10] + "...")
#         print("REGION     :", region)
#         print("=========================================\n")

#         identity = subprocess.run(
#             [
#                 "aws",
#                 "sts",
#                 "get-caller-identity",
#             ],
#             capture_output=True,
#             text=True,
#             env=env,
#             check=True,
#         )

#         print("AWS CLI Identity")
#         print(identity.stdout)

#         result = subprocess.run(
#             [
#                 "aws",
#                 "eks",
#                 "get-token",
#                 "--cluster-name",
#                 cluster_name,
#                 "--region",
#                 region,
#             ],
#             capture_output=True,
#             text=True,
#             env=env,
#             check=True,
#         )

#         response = json.loads(result.stdout)

#         token = response["status"]["token"]

#         print("TOKEN PREFIX")
#         print(token[:100] + "...")

#         return token


import base64

from botocore.auth import SigV4QueryAuth
from botocore.awsrequest import AWSRequest
from botocore.credentials import Credentials


class EKSTokenGenerator:

    def generate(
        self,
        cluster_name: str,
        region: str,
        credentials: dict,
    ) -> str:

        creds = Credentials(
            access_key=credentials["AccessKeyId"],
            secret_key=credentials["SecretAccessKey"],
            token=credentials["SessionToken"],
        )

        request = AWSRequest(
            method="GET",
            url=f"https://sts.{region}.amazonaws.com/?Action=GetCallerIdentity&Version=2011-06-15",
            headers={
                "x-k8s-aws-id": cluster_name,
            },
        )

        SigV4QueryAuth(
            creds,
            "sts",
            region,
            expires=60,
        ).add_auth(request)

        signed_url = request.url

        token = (
            "k8s-aws-v1."
            + base64.urlsafe_b64encode(
                signed_url.encode("utf-8")
            )
            .decode("utf-8")
            .rstrip("=")
        )

        return token