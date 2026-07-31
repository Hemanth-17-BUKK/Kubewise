# from app.prometheus.client import PrometheusClient

# client = PrometheusClient()

# result = client.query("up")

# print(result)

from app.services.metric_service import MetricService

service = MetricService()

print(service.get_cpu_usage())