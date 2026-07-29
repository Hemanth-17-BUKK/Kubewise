import json
import os
import subprocess


class EKSTokenGenerator:

    def generate(
        self,
        cluster_name: str,
        region: str,
        credentials: dict,
    ) -> str:

        env = os.environ.copy()

        env["AWS_ACCESS_KEY_ID"] = credentials["AccessKeyId"]
        env["AWS_SECRET_ACCESS_KEY"] = credentials["SecretAccessKey"]
        env["AWS_SESSION_TOKEN"] = credentials["SessionToken"]
        env["AWS_DEFAULT_REGION"] = region

        print("\n================ AWS ENV ================")
        print("ACCESS KEY :", credentials["AccessKeyId"][:10] + "...")
        print("REGION     :", region)
        print("=========================================\n")

        identity = subprocess.run(
            [
                "aws",
                "sts",
                "get-caller-identity",
            ],
            capture_output=True,
            text=True,
            env=env,
            check=True,
        )

        print("AWS CLI Identity")
        print(identity.stdout)

        result = subprocess.run(
            [
                "aws",
                "eks",
                "get-token",
                "--cluster-name",
                cluster_name,
                "--region",
                region,
            ],
            capture_output=True,
            text=True,
            env=env,
            check=True,
        )

        response = json.loads(result.stdout)

        token = response["status"]["token"]

        print("TOKEN PREFIX")
        print(token[:100] + "...")

        return token