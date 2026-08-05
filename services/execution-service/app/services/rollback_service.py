import time

from app.services.aws_service import AWSService
from app.services.kubernetes_service import KubernetesService

from app.utils.health_checker import HealthChecker


class RollbackService:

    def __init__(self):

        self.aws_service = AWSService()

        self.kubernetes_service = KubernetesService()

        self.health_checker = HealthChecker(
            self.kubernetes_service.core_api
        )

    async def rollback(

        self,

        request,

        baseline

    ):

        try:

            # ------------------------------------------
            # Restore NodeGroup Size
            # ------------------------------------------

            self.aws_service.scale_nodegroup(

                cluster_name=request.cluster_name,

                desired_size=request.target_node_count + 1

            )

            # ------------------------------------------
            # Wait for Node Recovery
            # ------------------------------------------

            timeout = 300

            start = time.time()

            while True:

                nodes = self.kubernetes_service.core_api.list_node().items

                ready = 0

                for node in nodes:

                    for condition in node.status.conditions:

                        if (

                            condition.type == "Ready"

                            and condition.status == "True"

                        ):

                            ready += 1

                if ready >= request.target_node_count + 1:

                    break

                if time.time() - start > timeout:

                    return {

                        "status": "FAILED_RECOVERY",

                        "message": "Rollback timed out while waiting for node recovery."

                    }

                time.sleep(5)

            # ------------------------------------------
            # Verify Health
            # ------------------------------------------

            health = self.health_checker.check(

                request.target_node_count + 1,

                baseline

            )

            if health["healthy"]:

                return {

                    "status": "RECOVERED",

                    "health": health,

                    "message": "Cluster successfully recovered."

                }

            return {

                "status": "FAILED_RECOVERY",

                "health": health,

                "message": "Automatic rollback failed."

            }

        except Exception as e:

            return {

                "status": "FAILED_RECOVERY",

                "message": str(e)

            }