import json
import boto3
from botocore.exceptions import ClientError


REGION_MAPPING = {
    "us-east-1": "US East (N. Virginia)",
    "us-east-2": "US East (Ohio)",
    "us-west-1": "US West (N. California)",
    "us-west-2": "US West (Oregon)",
    "ap-south-1": "Asia Pacific (Mumbai)",
    "ap-southeast-1": "Asia Pacific (Singapore)",
    "eu-west-1": "EU (Ireland)"
}


class PricingService:

    def __init__(self):
        self.client = boto3.client(
            "pricing",
            region_name="us-east-1"
        )

    def get_ec2_price(
        self,
        instance_type: str,
        region: str
    ):

        aws_region = REGION_MAPPING.get(region)

        if aws_region is None:
            raise Exception(
                f"Unsupported AWS Region: {region}"
            )

        response = self.client.get_products(
            ServiceCode="AmazonEC2",
            Filters=[
                {
                    "Type": "TERM_MATCH",
                    "Field": "instanceType",
                    "Value": instance_type,
                },
                {
                    "Type": "TERM_MATCH",
                    "Field": "location",
                    "Value": aws_region,
                },
                {
                    "Type": "TERM_MATCH",
                    "Field": "operatingSystem",
                    "Value": "Linux",
                },
                {
                    "Type": "TERM_MATCH",
                    "Field": "tenancy",
                    "Value": "Shared",
                },
                {
                    "Type": "TERM_MATCH",
                    "Field": "preInstalledSw",
                    "Value": "NA",
                },
                {
                    "Type": "TERM_MATCH",
                    "Field": "capacitystatus",
                    "Value": "Used",
                },
            ],
            MaxResults=1,
        )

        if len(response["PriceList"]) == 0:
            raise Exception("Price not found.")

        product = json.loads(response["PriceList"][0])

        ondemand = next(
            iter(product["terms"]["OnDemand"].values())
        )

        dimension = next(
            iter(ondemand["priceDimensions"].values())
        )

        return {
            "instance_type": instance_type,
            "region": region,
            "currency": "USD",
            "price_per_hour": float(
                dimension["pricePerUnit"]["USD"]
            ),
        }