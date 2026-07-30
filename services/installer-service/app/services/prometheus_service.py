from kubernetes.client.rest import ApiException

from app.aws.cluster_context import ClusterContextBuilder
from app.helm.installer import HelmInstaller
from app.kubernetes.client import KubernetesClient
from app.kubernetes.kubeconfig import KubeConfigGenerator
from app.kubernetes.verifier import PrometheusVerifier


class PrometheusService:

    def _get_clients(
        self,
        context,
    ):

        kube = KubernetesClient(context)

        return (
            kube.core_v1(),
            kube.apps_v1(),
        )

    def _get_prometheus_status(
        self,
        context,
    ):

        core_v1, apps_v1 = self._get_clients(
            context,
        )

        verifier = PrometheusVerifier()

        return verifier.is_installed(
            core_v1,
            apps_v1,
        )

    def check_cluster_connection(
        self,
        role_arn: str,
        cluster_name: str,
    ):

        try:

            context = ClusterContextBuilder().build(
                role_arn,
                cluster_name,
            )

            core_v1, _ = self._get_clients(
                context,
            )

            namespaces = core_v1.list_namespace()

            return {
                "connected": True,
                "cluster": cluster_name,
                "namespaces": len(namespaces.items),
            }

        except ApiException as e:

            return {
                "connected": False,
                "error": str(e),
            }

        except Exception as e:

            return {
                "connected": False,
                "error": str(e),
            }

    def get_prometheus_status(
        self,
        role_arn: str,
        cluster_name: str,
    ):

        try:

            context = ClusterContextBuilder().build(
                role_arn,
                cluster_name,
            )

            status = self._get_prometheus_status(
                context,
            )

            return {
                "connected": True,
                "cluster": cluster_name,
                "prometheus": status,
            }

        except ApiException as e:

            return {
                "connected": False,
                "error": str(e),
            }

        except Exception as e:

            return {
                "connected": False,
                "error": str(e),
            }

    def install_prometheus(
        self,
        role_arn: str,
        cluster_name: str,
    ):

        try:

            context = ClusterContextBuilder().build(
                role_arn,
                cluster_name,
            )

            status = self._get_prometheus_status(
                context,
            )

            if status["installed"]:
                return {
                    "success": True,
                    "message": "Prometheus is already installed.",
                    "prometheus": status,
                }

            kubeconfig = KubeConfigGenerator().generate(
                context,
            )

            installer = HelmInstaller(
                kubeconfig,
            )

            installer.add_repository()
            installer.update_repositories()
            installer.install()

            verification = self._get_prometheus_status(
                context,
            )

            return {
                "success": verification["installed"],
                "message": (
                    "Prometheus installed successfully."
                    if verification["installed"]
                    else "Installation completed but verification failed."
                ),
                "prometheus": verification,
            }

        except Exception as e:

            return {
                "success": False,
                "error": str(e),
            }