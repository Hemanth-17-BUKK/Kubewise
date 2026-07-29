import base64
import os
import tempfile

from kubernetes import client


class KubernetesClient:
    """
    Creates an authenticated Kubernetes API client for an EKS cluster.
    """

    def __init__(
        self,
        endpoint: str,
        ca_data: str,
        token: str,
    ):
        self.endpoint = endpoint
        self.ca_data = ca_data
        self.token = token

        self._ca_cert_path = self._create_ca_cert_file()
        self._api_client = self._create_api_client()

    def _create_ca_cert_file(self) -> str:
        """
        Decode the base64 encoded EKS CA certificate
        and store it in a temporary file.
        """

        ca_cert = base64.b64decode(self.ca_data)

        temp = tempfile.NamedTemporaryFile(delete=False)
        temp.write(ca_cert)
        temp.close()

        return temp.name

    def _create_api_client(self) -> client.ApiClient:
        """
        Configure the Kubernetes ApiClient.
        """

        configuration = client.Configuration()

        configuration.host = self.endpoint
        configuration.verify_ssl = True
        configuration.ssl_ca_cert = self._ca_cert_path

        configuration.api_key = {
            "authorization": self.token
        }

        configuration.api_key_prefix = {
            "authorization": "Bearer"
        }

        return client.ApiClient(configuration)

    def get_api_client(self) -> client.ApiClient:
        return self._api_client

    def core_v1(self) -> client.CoreV1Api:
        return client.CoreV1Api(self._api_client)

    def apps_v1(self) -> client.AppsV1Api:
        return client.AppsV1Api(self._api_client)

    def batch_v1(self) -> client.BatchV1Api:
        return client.BatchV1Api(self._api_client)

    def networking_v1(self) -> client.NetworkingV1Api:
        return client.NetworkingV1Api(self._api_client)

    def custom_objects(self) -> client.CustomObjectsApi:
        return client.CustomObjectsApi(self._api_client)

    def version(self) -> client.VersionApi:
        return client.VersionApi(self._api_client)

    def close(self):
        """
        Cleanup temporary CA certificate.
        """

        if os.path.exists(self._ca_cert_path):
            os.remove(self._ca_cert_path)

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass