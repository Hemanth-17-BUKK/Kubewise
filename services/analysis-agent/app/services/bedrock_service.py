import json

import boto3
from botocore.exceptions import ClientError

from app.config import settings


class BedrockService:

    def __init__(self):
        self.client = boto3.client(
            "bedrock-runtime",
            region_name=settings.AWS_REGION
        )

    def load_prompt(self):
        with open(
            "app/prompts/analysis_prompt.txt",
            "r",
            encoding="utf-8"
        ) as file:
            return file.read()

    def analyze(self, analysis_context: dict):

        prompt = self.load_prompt()

        try:

            response = self.client.converse(

                modelId=settings.BEDROCK_MODEL_ID,

                system=[
                    {
                        "text": prompt
                    }
                ],

                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "text": json.dumps(
                                    analysis_context,
                                    indent=2
                                )
                            }
                        ]
                    }
                ],

                inferenceConfig={
                    "temperature": 0.2,
                    "maxTokens": 2000,
                    "topP": 0.9
                }

            )

            return response["output"]["message"]["content"][0]["text"]

        except ClientError as e:

            raise Exception(
                f"Bedrock Error: {e.response['Error']['Message']}"
            )