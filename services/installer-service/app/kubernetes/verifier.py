from kubernetes.client.rest import ApiException


class PrometheusVerifier:

    NAMESPACE = "monitoring"

    SERVICE_NAME = "prometheus-server"
    DEPLOYMENT_NAME = "prometheus-server"

    def is_installed(self, core_v1, apps_v1):

        status = {
            "installed": False,
            "healthy": False,
            "namespace": False,
            "service": False,
            "deployment": False,
        }

        # Check namespace
        try:
            core_v1.read_namespace(self.NAMESPACE)
            status["namespace"] = True
        except ApiException as e:
            if e.status == 404:
                return status
            raise

        # Check Prometheus service
        try:
            core_v1.read_namespaced_service(
                name=self.SERVICE_NAME,
                namespace=self.NAMESPACE,
            )
            status["service"] = True
        except ApiException as e:
            if e.status == 404:
                return status
            raise

        # Check Prometheus deployment
        try:
            deployment = apps_v1.read_namespaced_deployment(
                name=self.DEPLOYMENT_NAME,
                namespace=self.NAMESPACE,
            )

            status["deployment"] = True

            replicas = deployment.status.replicas or 0
            ready = deployment.status.ready_replicas or 0

            if replicas > 0 and replicas == ready:
                status["installed"] = True
                status["healthy"] = True

        except ApiException as e:
            if e.status == 404:
                return status
            raise

        return status