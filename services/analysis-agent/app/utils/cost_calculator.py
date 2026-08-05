from typing import Dict


class CostCalculator:

    HOURS_PER_DAY = 24
    HOURS_PER_MONTH = 730

    @staticmethod
    def calculate_cluster_cost(
        cluster_info: Dict,
        pricing_info: Dict,
    ) -> Dict:

        node_count = cluster_info["node_count"]

        hourly_price = pricing_info["price_per_hour"]

        hourly_cost = round(
            node_count * hourly_price,
            4
        )

        daily_cost = round(
            hourly_cost * CostCalculator.HOURS_PER_DAY,
            2
        )

        monthly_cost = round(
            hourly_cost * CostCalculator.HOURS_PER_MONTH,
            2
        )

        return {
            "currency": pricing_info["currency"],
            "instance_type": pricing_info["instance_type"],
            "node_count": node_count,
            "hourly_cost": hourly_cost,
            "daily_cost": daily_cost,
            "monthly_cost": monthly_cost
        }