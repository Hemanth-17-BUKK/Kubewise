import base64
import tempfile

from kubernetes import client
from kubernetes.client import Configuration

from app.models.cluster_context import ClusterContext


class KubernetesClient:
    """
    Creates Kubernetes API clients using an already-built ClusterContext.

    This class never calls AWS.
    It simply consumes:
        - cluster endpoint
        - CA certificate
        - authentication token
    """

    def __init__(self, context: ClusterContext):
        self.context = context

    def _configuration(self):

        cluster = self.context.cluster

        configuration = Configuration()

        configuration.host = cluster["endpoint"]

        configuration.verify_ssl = True

        configuration.api_key = {
            "authorization": f"Bearer {self.context.token}"
        }

        # Decode cluster CA certificate
        ca_data = base64.b64decode(
            cluster["certificateAuthority"]["data"]
        )

        temp = tempfile.NamedTemporaryFile(
            delete=False
        )

        temp.write(ca_data)

        temp.close()

        configuration.ssl_ca_cert = temp.name

        return configuration

    def core_v1(self):

        api_client = client.ApiClient(
            self._configuration()
        )

        return client.CoreV1Api(api_client)

    def apps_v1(self):

        api_client = client.ApiClient(
            self._configuration()
        )

        return client.AppsV1Api(api_client)