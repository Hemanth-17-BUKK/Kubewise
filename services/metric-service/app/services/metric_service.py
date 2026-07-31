from app.prometheus.client import PrometheusClient
from app.prometheus import queries
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo


class MetricService:

    def __init__(self):
        self.prometheus = PrometheusClient()

    # ----------------------------------------------------
    # Private Helpers
    # ----------------------------------------------------

    def _get_single_metric_value(self, response):

        try:
            return round(
                float(response["data"]["result"][0]["value"][1]),
                2
            )

        except (KeyError, IndexError, ValueError, TypeError):
            return None

    def _get_metric_list(self, response, key, metric_type="raw"):

        metrics = []

        try:
            for item in response["data"]["result"]:

                value = float(item["value"][1])

                if metric_type == "cpu":
                    # Convert CPU cores -> millicores
                    value = round(value * 1000, 2)
                    value_field = "cpu_millicores"

                elif metric_type == "memory":
                    # Convert Bytes -> MiB
                    value = round(value / (1024 * 1024), 2)
                    value_field = "memory_mib"

                else:
                    value = round(value, 2)
                    value_field = "value"

                metrics.append({
                    key: item["metric"].get(key, "unknown"),
                    value_field: value
                })

        except (KeyError, IndexError, ValueError, TypeError):
            return []

        return metrics

    # ----------------------------------------------------
    # History Helpers
    # ----------------------------------------------------

    def _parse_duration(self, duration: str):

        if duration.endswith("m"):
            return timedelta(minutes=int(duration[:-1]))

        if duration.endswith("h"):
            return timedelta(hours=int(duration[:-1]))

        if duration.endswith("d"):
            return timedelta(days=int(duration[:-1]))

        raise ValueError("Invalid duration format")

    def _get_default_step(self, duration: str):

        mapping = {
            "30m": "30s",
            "1h": "60s",
            "6h": "5m",
            "12h": "10m",
            "24h": "15m",
            "7d": "1h"
        }

        return mapping.get(duration, "60s")

    def _get_time_range(
        self,
        duration=None,
        start=None,
        end=None,
        step=None
    ):

        if start and end:

            start_dt = datetime.fromisoformat(
                start.replace("Z", "+00:00")
            )

            end_dt = datetime.fromisoformat(
                end.replace("Z", "+00:00")
            )

            duration_label = None

        else:

            duration = duration or "1h"

            end_dt = datetime.now(timezone.utc)

            start_dt = end_dt - self._parse_duration(duration)

            duration_label = duration

        if not step:
            step = self._get_default_step(
                duration_label or "1h"
            )

        return (
            start_dt,
            end_dt,
            step,
            duration_label
        )

    def _parse_range_response(self, response):

        values = []

        try:

            results = response["data"]["result"]

            if not results:
                return []

            for ts, value in results[0]["values"]:

                values.append({
                    "timestamp": datetime.fromtimestamp(
                        float(ts),
                        tz=timezone.utc
                    ).astimezone(
                        ZoneInfo("Asia/Kolkata")
                    ).isoformat(),

                    "value": round(float(value), 2)
                })

        except (KeyError, IndexError, ValueError, TypeError):

            return []

        return values

    def get_cpu_history(
        self,
        duration=None,
        start=None,
        end=None,
        step=None
    ):

        start_dt, end_dt, step, duration_label = self._get_time_range(
            duration,
            start,
            end,
            step
        )

        response = self.prometheus.query_range(
            queries.CPU_HISTORY,
            start_dt,
            end_dt,
            step
        )

        values = self._parse_range_response(response)

        return {
            "metric": "cpu",
            "unit": "%",
            "timezone": "Asia/Kolkata",
            "start": start_dt.astimezone(
                ZoneInfo("Asia/Kolkata")
            ).isoformat(),
            "end": end_dt.astimezone(
                ZoneInfo("Asia/Kolkata")
            ).isoformat(),
            "duration": duration_label,
            "step": step,
            "points": len(values),
            "values": values
        }

    def get_memory_history(
        self,
        duration=None,
        start=None,
        end=None,
        step=None
    ):

        start_dt, end_dt, step, duration_label = self._get_time_range(
            duration,
            start,
            end,
            step
        )

        response = self.prometheus.query_range(
            queries.MEMORY_HISTORY,
            start_dt,
            end_dt,
            step
        )

        values = self._parse_range_response(response)

        return {
            "metric": "memory",
            "unit": "%",
            "timezone": "Asia/Kolkata",
            "start": start_dt.astimezone(
                ZoneInfo("Asia/Kolkata")
            ).isoformat(),
            "end": end_dt.astimezone(
                ZoneInfo("Asia/Kolkata")
            ).isoformat(),
            "duration": duration_label,
            "step": step,
            "points": len(values),
            "values": values
        }

    # ----------------------------------------------------
    # Cluster Metrics
    # ----------------------------------------------------

    def get_cpu_usage(self):

        response = self.prometheus.query(
            queries.CPU_USAGE
        )

        return {
            "cpu_usage": self._get_single_metric_value(response),
            "unit": "%"
        }

    def get_memory_usage(self):

        response = self.prometheus.query(
            queries.MEMORY_USAGE
        )

        return {
            "memory_usage": self._get_single_metric_value(response),
            "unit": "%"
        }

    # ----------------------------------------------------
    # Pod Metrics
    # ----------------------------------------------------

    def get_top_cpu_pods(self):

        response = self.prometheus.query(
            queries.TOP_CPU_PODS
        )

        return self._get_metric_list(
            response,
            "pod",
            "cpu"
        )

    def get_top_memory_pods(self):

        response = self.prometheus.query(
            queries.TOP_MEMORY_PODS
        )

        return self._get_metric_list(
            response,
            "pod",
            "memory"
        )

    # ----------------------------------------------------
    # Node Metrics
    # ----------------------------------------------------

    def get_node_cpu_usage(self):

        response = self.prometheus.query(
            queries.NODE_CPU_USAGE
        )

        return self._get_metric_list(
            response,
            "instance",
            "cpu"
        )

    def get_node_memory_usage(self):

        response = self.prometheus.query(
            queries.NODE_MEMORY_USAGE
        )

        return self._get_metric_list(
            response,
            "instance",
            "memory"
        )

    # ----------------------------------------------------
    # Dashboard Overview
    # ----------------------------------------------------

    def get_overview(self):

        return {
            "cpu": self.get_cpu_usage(),
            "memory": self.get_memory_usage(),
            "top_cpu_pods": self.get_top_cpu_pods(),
            "top_memory_pods": self.get_top_memory_pods()
        }