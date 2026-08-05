from app.services.pricing_service import PricingService


class SavingsCalculator:

    def __init__(self):

        self.pricing = PricingService()

    def calculate(
        self,
        current_cost,
        optimization_plan
    ):

        instance = optimization_plan["target_instance_type"]

        nodes = optimization_plan["target_node_count"]

        region = "us-east-1"

        optimized_price = self.pricing.get_ec2_price(
            instance_type=instance,
            region=region
        )

        optimized_monthly_cost = round(
            optimized_price["price_per_hour"] * nodes * 730,
            2
        )

        savings = round(
            current_cost["monthly_cost"] -
            optimized_monthly_cost,
            2
        )

        savings = max(savings, 0)

        reduction = 0

        if current_cost["monthly_cost"] > 0:

            reduction = round(
                (savings / current_cost["monthly_cost"]) * 100,
                2
            )

        return {

            "optimized_monthly_cost": optimized_monthly_cost,

            "estimated_savings": {

                "monthly_usd": savings

            },

            "expected_cost_reduction_percent": reduction

        }