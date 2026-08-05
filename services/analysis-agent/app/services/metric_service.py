import httpx

from app.config import settings


class MetricService:

    def __init__(self):
        self.base_url = settings.METRIC_SERVICE_URL

    async def get_overview(self):
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                f"{self.base_url}/metrics/overview"
            )
            response.raise_for_status()
            return response.json()

    async def get_cpu_history(self):
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                f"{self.base_url}/metrics/history/cpu"
            )
            response.raise_for_status()
            return response.json()

    async def get_memory_history(self):
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                f"{self.base_url}/metrics/history/memory"
            )
            response.raise_for_status()
            return response.json()