import time

from kubernetes import client


class HealthChecker:

    def __init__(self, core_api):

        self.core_api = core_api

    # --------------------------------------------------
    # Capture baseline before execution
    # --------------------------------------------------

    def snapshot(self):

        report = self._cluster_status()

        return {

            "pending_pods": report["pending_pods"],

            "failed_pods": report["failed_pods"],

            "crashloop_pods": report["crashloop_pods"]

        }

    # --------------------------------------------------
    # Verify Cluster
    # --------------------------------------------------

    def verify_cluster(

        self,

        baseline,

        timeout=300

    ):

        current_nodes = len(

            self.core_api.list_node().items

        )

        report = self.check(

            expected_nodes=current_nodes,

            baseline=baseline,

            timeout=timeout

        )

        return report["healthy"]

    # --------------------------------------------------
    # Health verification
    # --------------------------------------------------

    def check(

        self,

        expected_nodes,

        baseline,

        timeout=60

    ):

        start = time.time()

        while True:

            report = self._cluster_status()

            healthy = (

                report["ready_nodes"] == expected_nodes

                and report["not_ready_nodes"] == 0

                and report["pending_pods"] <= baseline["pending_pods"]

                and report["failed_pods"] <= baseline["failed_pods"]

                and report["crashloop_pods"] <= baseline["crashloop_pods"]

            )

            if healthy:

                report["healthy"] = True

                report["message"] = "Cluster is healthy."

                return report

            if time.time() - start > timeout:

                report["healthy"] = False

                report["message"] = self._build_failure_message(

                    report,

                    baseline

                )

                return report

            time.sleep(3)

    # --------------------------------------------------
    # Current Cluster Status
    # --------------------------------------------------

    def _cluster_status(self):

        nodes = self.core_api.list_node().items

        ready_nodes = 0
        not_ready_nodes = 0

        for node in nodes:

            ready = False

            for condition in node.status.conditions:

                if (

                    condition.type == "Ready"

                    and condition.status == "True"

                ):

                    ready = True

            if ready:

                ready_nodes += 1

            else:

                not_ready_nodes += 1

        pods = self.core_api.list_pod_for_all_namespaces().items

        running = 0
        pending = 0
        failed = 0
        crashloop = 0

        pending_details = []

        for pod in pods:

            phase = pod.status.phase

            if phase == "Running":

                running += 1

            elif phase == "Pending":

                pending += 1

                pending_details.append({

                    "namespace": pod.metadata.namespace,

                    "pod": pod.metadata.name,

                    "reason": self._pending_reason(

                        pod.metadata.namespace,

                        pod.metadata.name

                    )

                })

            elif phase == "Failed":

                failed += 1

            statuses = pod.status.container_statuses or []

            for container in statuses:

                waiting = container.state.waiting

                if (

                    waiting

                    and waiting.reason == "CrashLoopBackOff"

                ):

                    crashloop += 1

        return {

            "healthy": False,

            "ready_nodes": ready_nodes,

            "not_ready_nodes": not_ready_nodes,

            "running_pods": running,

            "pending_pods": pending,

            "failed_pods": failed,

            "crashloop_pods": crashloop,

            "pending_details": pending_details

        }

    # --------------------------------------------------
    # Pending Reason
    # --------------------------------------------------

    def _pending_reason(

        self,

        namespace,

        pod_name

    ):

        try:

            events = self.core_api.list_namespaced_event(

                namespace=namespace,

                field_selector=f"involvedObject.name={pod_name}"

            )

            if not events.items:

                return "Unknown"

            latest = sorted(

                events.items,

                key=lambda e: (

                    e.last_timestamp

                    or e.event_time

                    or e.metadata.creation_timestamp

                ),

                reverse=True

            )[0]

            return latest.message

        except Exception:

            return "Unknown"

    # --------------------------------------------------
    # Failure Message
    # --------------------------------------------------

    def _build_failure_message(

        self,

        report,

        baseline

    ):

        messages = []

        if report["not_ready_nodes"] > 0:

            messages.append(

                f"{report['not_ready_nodes']} node(s) are NotReady."

            )

        if report["pending_pods"] > baseline["pending_pods"]:

            messages.append(

                f"Pending pods increased from "

                f"{baseline['pending_pods']} "

                f"to {report['pending_pods']}."

            )

        if report["failed_pods"] > baseline["failed_pods"]:

            messages.append(

                "New Failed pods detected."

            )

        if report["crashloop_pods"] > baseline["crashloop_pods"]:

            messages.append(

                "New CrashLoopBackOff pods detected."

            )

        if report["pending_details"]:

            messages.append(

                "Pending reasons: "

                + "; ".join(

                    item["reason"]

                    for item in report["pending_details"]

                )

            )

        if not messages:

            return "Cluster health verification failed."

        return " ".join(messages)