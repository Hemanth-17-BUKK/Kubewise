import threading
import uuid
from datetime import datetime

from app.repositories.execution_repository import ExecutionRepository

from app.services.aws_service import AWSService
from app.services.kubernetes_service import KubernetesService
from app.services.rollback_service import RollbackService
from app.services.termination_service import TerminationService

from app.utils.drain_validator import DrainValidator
from app.utils.execution_logger import ExecutionLogger
from app.utils.health_checker import HealthChecker
from app.utils.node_drainer import NodeDrainer
from app.utils.node_selector import NodeSelector
from app.utils.scheduling_simulator import SchedulingSimulator


class ExecutionService:

    def __init__(self):

        self.kubernetes_service = KubernetesService()

        self.aws_service = AWSService()

        self.logger = ExecutionLogger()

        self.termination_service = TerminationService()

        self.rollback_service = RollbackService()

        self.validator = DrainValidator(

            self.kubernetes_service.core_api,

            self.kubernetes_service.policy_api

        )

        self.drainer = NodeDrainer(

            self.kubernetes_service.core_api,

            self.kubernetes_service.policy_api

        )

        self.health_checker = HealthChecker(

            self.kubernetes_service.core_api

        )

    # -------------------------------------------------------
    # Response Builder
    # -------------------------------------------------------

    def _build_response(

        self,

        operation_id,

        status,

        **kwargs

    ):

        return {

            "operation_id": operation_id,

            "status": status,

            **kwargs

        }

    # -------------------------------------------------------
    # Persist Execution
    # -------------------------------------------------------

    def _save_execution(

        self,

        operation_id,

        cluster_name,

        started_at,

        response

    ):

        ExecutionRepository.save(

            {

                "operation_id": operation_id,

                "cluster_name": cluster_name,

                "status": response["status"],

                "started_at": started_at,

                "completed_at": None,

                "logs": self.logger.get_logs(),

                "response": response

            }

        )

        return response
    # -------------------------------------------------------
    # Execute
    # -------------------------------------------------------

    async def execute(

        self,

        request

    ):

        operation_id = str(uuid.uuid4())

        started_at = datetime.utcnow().isoformat()

        # ----------------------------------------
        # Approval
        # ----------------------------------------

        if not request.approval:

            response = self._build_response(

                operation_id,

                "CANCELLED",

                message="Execution requires user approval."

            )

            return self._save_execution(

                operation_id,

                request.cluster_name,

                started_at,

                response

            )

        # ----------------------------------------
        # Prepare Execution
        # ----------------------------------------

        preparation = self._prepare_execution(

            request,

            operation_id,

            started_at

        )

        if preparation["completed"]:

            return preparation["response"]

        # ----------------------------------------
        # Execute Node Removal
        # ----------------------------------------

        return self._execute_node_removal(

            request,

            operation_id,

            started_at,

            preparation

        )
    
        # -------------------------------------------------------
    # Prepare Execution
    # -------------------------------------------------------

    def _prepare_execution(

        self,

        request,

        operation_id,

        started_at

    ):

        # ----------------------------------------
        # Scheduling
        # ----------------------------------------

        self.logger.add(

            "SCHEDULING",

            "STARTED",

            "Collecting scheduling information."

        )

        print("STEP 0 - Fetching scheduling info")

        scheduling = self.kubernetes_service.get_scheduling_info()

        print("STEP 1 - Scheduling info received")

        print("\n========== CURRENT NODES ==========")

        for node in scheduling["nodes"]:

            print(node["name"])

        print("===================================\n")

        current_node_count = len(

            scheduling["nodes"]

        )

        print(

            f"STEP 2 - Node count = {current_node_count}"

        )

        if current_node_count <= request.target_node_count:

            response = {

                "status": "NO_ACTION",

                "operation_id": operation_id,

                "current_node_count": current_node_count,

                "target_node_count": request.target_node_count,

                "message":

                    f"Cluster already has "

                    f"{current_node_count} nodes. "

                    "No optimization required."

            }

            return {

                "completed": True,

                "response": response

            }

        self.logger.add(

            "SCHEDULING",

            "SUCCESS",

            "Scheduling information collected."

        )

        # ----------------------------------------
        # Candidate Nodes
        # ----------------------------------------

        candidates = []

        for node in scheduling["nodes"]:

            candidates.append(

                {

                    "name": node["name"],

                    "workload_pods":

                        node["workload_pods"],

                    "requested_cpu":

                        node["requested"]["cpu_millicores"],

                    "requested_memory":

                        node["requested"]["memory_mib"],

                    "has_statefulset":

                        node.get(

                            "has_statefulset",

                            False

                        ),

                    "has_local_storage":

                        node.get(

                            "has_local_storage",

                            False

                        ),

                    "has_pdb":

                        node.get(

                            "has_pdb",

                            False

                        )

                }

            )

        # ----------------------------------------
        # Node Selection
        # ----------------------------------------

        self.logger.add(

            "NODE_SELECTION",

            "STARTED",

            "Selecting removable node."

        )

        print("STEP 3 - Selecting removable node")

        current_node = self.kubernetes_service.get_current_node_name()

        print(f"STEP 3.1 - Execution service running on: {current_node}")

        removable_node = NodeSelector.select(

            candidates,

            current_node=current_node

        )

        print(

            "STEP 4 - Selected:",

            removable_node["name"]

        )

        self.logger.add(

            "NODE_SELECTION",

            "SUCCESS",

            f"Selected node "

            f"{removable_node['name']}."

        )

        # ----------------------------------------
        # Simulation
        # ----------------------------------------

        self.logger.add(

            "SIMULATION",

            "STARTED",

            "Running scheduling simulation."

        )

        print("STEP 5 - Starting simulation")

        simulation = SchedulingSimulator.simulate(

            scheduling,

            removable_node["name"]

        )

        print("STEP 6 - Simulation finished")

        self.logger.add(

            "SIMULATION",

            "SUCCESS",

            "Scheduling simulation completed."

        )

        if not simulation["safe"]:

            response = self._build_response(

                operation_id,

                "BLOCKED",

                selected_node=removable_node,

                simulation=simulation,

                logs=self.logger.get_logs(),

                message=(

                    "Remaining nodes cannot "

                    "accommodate all workloads."

                )

            )

            return {

                "completed": True,

                "response":

                    self._save_execution(

                        operation_id,

                        request.cluster_name,

                        started_at,

                        response

                    )

            }

        # ----------------------------------------
        # Validation
        # ----------------------------------------

        self.logger.add(

            "VALIDATION",

            "STARTED",

            "Running drain validation."

        )

        print("STEP 7 - Starting validation")

        validation = self.validator.validate(

            removable_node["name"]

        )

        print("STEP 8 - Validation complete")

        if not validation["safe"]:

            self.logger.add(

                "VALIDATION",

                "FAILED",

                "Drain validation failed."

            )

            response = self._build_response(

                operation_id,

                "BLOCKED",

                selected_node=removable_node,

                simulation=simulation,

                validation=validation,

                logs=self.logger.get_logs(),

                message=

                    "Node cannot be safely drained."

            )

            return {

                "completed": True,

                "response":

                    self._save_execution(

                        operation_id,

                        request.cluster_name,

                        started_at,

                        response

                    )

            }

        self.logger.add(

            "VALIDATION",

            "SUCCESS",

            "Drain validation completed."

        )

        # ----------------------------------------
        # Dry Run
        # ----------------------------------------

        print(

            f"STEP 9 - dry_run = "

            f"{request.dry_run}"

        )

        if request.dry_run:

            response = self._build_response(

                operation_id,

                "READY",

                selected_node=removable_node,

                simulation=simulation,

                validation=validation,

                target_node_count=request.target_node_count,

                logs=self.logger.get_logs(),

                message=

                    "Dry run enabled. "

                    "No infrastructure changes applied."

            )

            return {

                "completed": True,

                "response":

                    self._save_execution(

                        operation_id,

                        request.cluster_name,

                        started_at,

                        response

                    )

            }

        print("PASSED DRY RUN")

        return {

            "completed": False,

            "scheduling": scheduling,

            "removable_node": removable_node,

            "simulation": simulation,

            "validation": validation

        }
        # -------------------------------------------------------
    # Execute Node Removal
    # -------------------------------------------------------

    def _execute_node_removal(

        self,

        request,

        operation_id,

        started_at,

        preparation

    ):

        removable_node = preparation["removable_node"]

        simulation = preparation["simulation"]

        validation = preparation["validation"]

        # ----------------------------------------
        # Capture Baseline
        # ----------------------------------------

        print("STEP 10 - Capturing baseline")

        baseline = self.health_checker.snapshot()

        print("STEP 11 - Baseline captured")

        # ----------------------------------------
        # Cordon
        # ----------------------------------------

        self.logger.add(

            "CORDON",

            "STARTED",

            "Cordoning node."

        )

        print("CORDONING NODE")

        self.kubernetes_service.cordon_node(

            removable_node["name"]

        )

        print("NODE CORDONED")

        self.logger.add(

            "CORDON",

            "SUCCESS",

            "Node cordoned successfully."

        )

        # ----------------------------------------
        # Drain
        # ----------------------------------------

        self.logger.add(

            "DRAIN",

            "STARTED",

            "Draining node."

        )

        print("STARTING DRAIN")

        drain_result = self.drainer.drain(

            removable_node["name"]

        )

        print("DRAIN COMPLETE")

        self.logger.add(

            "DRAIN",

            "SUCCESS",

            "Node drained successfully."

        )

        # ----------------------------------------
        # Instance Lookup
        # ----------------------------------------

        print("LOOKING UP INSTANCE")

        instance_id = self.termination_service.get_instance_id(

            self.kubernetes_service,

            removable_node["name"]

        )

        print("INSTANCE:", instance_id)

        # ----------------------------------------
        # Termination
        # ----------------------------------------

        self.logger.add(

            "EC2_TERMINATION",

            "STARTED",

            f"Terminating instance {instance_id}."

        )

        print("TERMINATING INSTANCE")

        self.termination_service.terminate_instance(

            instance_id

        )

        print("TERMINATION REQUEST SENT")

        self.logger.add(

            "EC2_TERMINATION",

            "SUCCESS",

            "Termination request submitted."

        )

        # ----------------------------------------
        # Initial Response
        # ----------------------------------------

        response = self._build_response(

            operation_id,

            "WAITING_FOR_TERMINATION",

            selected_node=removable_node,

            terminated_instance=instance_id,

            simulation=simulation,

            validation=validation,

            drain=drain_result,

            logs=self.logger.get_logs(),

            message="Execution started. Waiting for EC2 instance termination."

        )

        # ----------------------------------------
        # Save BEFORE Thread Starts
        # ----------------------------------------

        self._save_execution(

            operation_id,

            request.cluster_name,

            started_at,

            response

        )

        # ----------------------------------------
        # Update Status
        # ----------------------------------------

        ExecutionRepository.update_status(

            operation_id,

            "WAITING_FOR_TERMINATION"

        )

        # ----------------------------------------
        # Background Worker
        # ----------------------------------------

        print("CREATING BACKGROUND THREAD")

        thread = threading.Thread(

            target=self._finish_execution,

            kwargs={

                "operation_id": operation_id,

                "cluster_name": request.cluster_name,

                "node_name": removable_node["name"],

                "instance_id": instance_id,

                "baseline": baseline

            },

            daemon=True

        )

        thread.start()

        print("BACKGROUND THREAD STARTED")

        return response

        # -------------------------------------------------------
    # Background Execution
    # -------------------------------------------------------

    def _finish_execution(

        self,

        operation_id,

        cluster_name,

        node_name,

        instance_id,

        baseline

    ):

        try:

            print("BACKGROUND - Waiting for EC2 termination")

            self.termination_service.wait_until_terminated(
                instance_id
            )

            ExecutionRepository.update_status(

                operation_id,

                "WAITING_FOR_NODE_REMOVAL"

            )

            print("BACKGROUND - EC2 terminated")

            self.kubernetes_service.wait_until_node_removed(
                node_name
            )

            ExecutionRepository.update_status(

                operation_id,

                "HEALTH_CHECK"

            )

            print("BACKGROUND - Node removed")

            print("BACKGROUND - Running health checks")

            healthy = self.health_checker.verify_cluster(
                baseline
            )

            if healthy:

                ExecutionRepository.update_status(

                    operation_id,

                    "COMPLETED"

                )

                execution = ExecutionRepository.get(
                    operation_id
                )

                if execution:

                    execution["response"]["status"] = "COMPLETED"

                    execution["response"]["message"] = (

                        "Cluster optimization completed successfully."

                    )

                print("BACKGROUND - COMPLETED")

            else:

                print("BACKGROUND - HEALTH CHECK FAILED")

                ExecutionRepository.update_status(

                    operation_id,

                    "ROLLBACK"

                )

                self.rollback_service.rollback()

                ExecutionRepository.update_status(

                    operation_id,

                    "ROLLED_BACK"

                )

                execution = ExecutionRepository.get(
                    operation_id
                )

                if execution:

                    execution["response"]["status"] = "ROLLED_BACK"

                    execution["response"]["message"] = (

                        "Rollback completed."

                    )

                print("BACKGROUND - ROLLBACK COMPLETE")

        except Exception as ex:

            print("BACKGROUND ERROR")

            print(ex)

            ExecutionRepository.update_status(

                operation_id,

                "FAILED"

            )

            execution = ExecutionRepository.get(
                operation_id
            )

            if execution:

                execution["response"]["status"] = "FAILED"

                execution["response"]["message"] = str(ex)

            print("BACKGROUND - FAILED")