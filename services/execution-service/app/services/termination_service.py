import time

import boto3


class TerminationService:

    def __init__(self):

        self.eks = boto3.client("eks")

        self.ec2 = boto3.client("ec2")

        self.autoscaling = boto3.client("autoscaling")

    # --------------------------------------------------
    # Kubernetes Node -> EC2 Instance
    # --------------------------------------------------

    def get_instance_id(
        self,
        kubernetes_service,
        node_name
    ):

        node = kubernetes_service.core_api.read_node(
            node_name
        )

        provider_id = node.spec.provider_id

        # aws:///us-east-1a/i-0123456789

        return provider_id.split("/")[-1]

    # --------------------------------------------------
    # Terminate Instance
    # --------------------------------------------------

    def terminate_instance(
        self,
        instance_id
    ):

        self.autoscaling.terminate_instance_in_auto_scaling_group(

            InstanceId=instance_id,

            ShouldDecrementDesiredCapacity=True

        )

    # --------------------------------------------------
    # Wait Until Gone
    # --------------------------------------------------

    def wait_until_terminated(
        self,
        instance_id,
        timeout=900
    ):

        start = time.time()

        while True:

            response = self.ec2.describe_instances(

                InstanceIds=[instance_id]

            )

            state = response["Reservations"][0]["Instances"][0]["State"]["Name"]

            if state == "terminated":

                return

            if time.time() - start > timeout:

                raise TimeoutError(
                    "EC2 termination timeout."
                )

            time.sleep(10)