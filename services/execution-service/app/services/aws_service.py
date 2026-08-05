import time

import boto3


class AWSService:

    def __init__(self):

        self.eks = boto3.client("eks")

        self.autoscaling = boto3.client("autoscaling")

    # ------------------------------------------------
    # Get Nodegroup
    # ------------------------------------------------

    def get_nodegroup(

        self,

        cluster_name

    ):

        response = self.eks.list_nodegroups(

            clusterName=cluster_name

        )

        if len(response["nodegroups"]) == 0:

            raise Exception("No managed nodegroups found.")

        return response["nodegroups"][0]

    # ------------------------------------------------
    # Get ASG
    # ------------------------------------------------

    def get_asg(

        self,

        cluster_name,

        nodegroup_name

    ):

        response = self.eks.describe_nodegroup(

            clusterName=cluster_name,

            nodegroupName=nodegroup_name

        )

        resources = response["nodegroup"]["resources"]

        return resources["autoScalingGroups"][0]["name"]

    # ------------------------------------------------
    # Scale
    # ------------------------------------------------

    def scale(

        self,

        asg_name,

        desired_capacity

    ):

        self.autoscaling.update_auto_scaling_group(

            AutoScalingGroupName=asg_name,

            DesiredCapacity=desired_capacity,

            MinSize=desired_capacity

        )

    # ------------------------------------------------
    # Wait
    # ------------------------------------------------

    def wait_until_scaled(

        self,

        asg_name,

        expected,

        timeout=900

    ):

        start = time.time()

        while True:

            response = self.autoscaling.describe_auto_scaling_groups(

                AutoScalingGroupNames=[asg_name]

            )

            group = response["AutoScalingGroups"][0]

            in_service = len(

                [

                    i

                    for i in group["Instances"]

                    if i["LifecycleState"] == "InService"

                ]

            )

            if in_service == expected:

                return True

            if time.time() - start > timeout:

                raise TimeoutError(
                    "Scaling timeout."
                )

            time.sleep(10)