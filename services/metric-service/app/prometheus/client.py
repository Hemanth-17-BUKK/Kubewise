from app.config.settings import settings
import requests
from requests.exceptions import RequestException


class PrometheusClient:

    def __init__(self):
        self.base_url = settings.prometheus_url.rstrip("/")

    def query(self, promql: str):

        try:
            response = requests.get(
                f"{self.base_url}/api/v1/query",
                params={
                    "query": promql
                },
                timeout=30,
            )

            response.raise_for_status()

            return response.json()

        except RequestException as e:
            raise Exception(f"Prometheus query failed: {e}")

    def query_range(self, promql: str, start, end, step):

        try:
            response = requests.get(
                f"{self.base_url}/api/v1/query_range",
                params={
                    "query": promql,
                    "start": int(start.timestamp()),
                    "end": int(end.timestamp()),
                    "step": step,
                },
                timeout=30,
            )

            response.raise_for_status()

            return response.json()

        except RequestException as e:
            raise Exception(f"Prometheus range query failed: {e}")