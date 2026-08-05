from app.services.metric_service import MetricService
from app.services.kubernetes_service import KubernetesService
from app.services.pricing_service import PricingService
from app.services.bedrock_service import BedrockService

from app.utils.cluster_context_builder import ClusterContextBuilder
from app.utils.cost_calculator import CostCalculator
from app.utils.instance_recommendation import InstanceRecommendation
from app.utils.llm_parser import parse_llm_json
from app.utils.savings_calculator import SavingsCalculator
from app.utils.scheduling_validator import SchedulingValidator


class AnalysisService:

    def __init__(self):

        self.metric_service = MetricService()

        self.kubernetes_service = KubernetesService()

        self.pricing_service = PricingService()

        self.bedrock_service = BedrockService()

        self.savings_calculator = SavingsCalculator()

    async def analyze(self, request):

        # ---------------------------------------------
        # Metrics
        # ---------------------------------------------

        overview = await self.metric_service.get_overview()

        cpu_history = await self.metric_service.get_cpu_history()

        memory_history = await self.metric_service.get_memory_history()

        metrics = {
            "overview": overview,
            "cpu_history": cpu_history,
            "memory_history": memory_history
        }

        # ---------------------------------------------
        # Cluster Information
        # ---------------------------------------------

        cluster_info = self.kubernetes_service.get_cluster_info()

        # ---------------------------------------------
        # Scheduling Information
        # ---------------------------------------------

        scheduling = self.kubernetes_service.get_scheduling_info()

        # ---------------------------------------------
        # Python Scheduling Validation
        # ---------------------------------------------

        target_node_count = max(
            cluster_info["node_count"] - 1,
            1
        )

        validation = SchedulingValidator.validate(
            scheduling=scheduling,
            target_node_count=target_node_count
        )

        # ---------------------------------------------
        # Build Context
        # ---------------------------------------------

        analysis_context = ClusterContextBuilder.build(
            metrics,
            cluster_info,
            scheduling,
            validation
        )

        # ---------------------------------------------
        # Pricing
        # ---------------------------------------------

        pricing = self.pricing_service.get_ec2_price(
            instance_type=cluster_info["instance_groups"][0]["instance_type"],
            region=cluster_info["instance_groups"][0]["region"]
        )

        analysis_context["pricing"] = pricing

        # ---------------------------------------------
        # Current Cost
        # ---------------------------------------------

        cost = CostCalculator.calculate_cluster_cost(
            cluster_info,
            pricing
        )

        analysis_context["cost"] = cost

        # ---------------------------------------------
        # Bedrock Analysis
        # ---------------------------------------------

        ai_response = self.bedrock_service.analyze(
            analysis_context
        )

        ai_analysis = parse_llm_json(
            ai_response
        )

        # ---------------------------------------------
        # Python Validation Overrides
        # ---------------------------------------------

        ai_analysis["optimization_safe"] = validation[
            "optimization_safe"
        ]

        ai_analysis["optimization_type"] = validation[
            "optimization_type"
        ]

        ai_analysis["recommended_node_count"] = validation[
            "recommended_node_count"
        ]

        ai_analysis["validation_reason"] = validation[
            "validation_reason"
        ]

        ai_analysis["optimization_plan"][
            "target_node_count"
        ] = validation[
            "recommended_node_count"
        ]

        # ---------------------------------------------
        # Python Instance Recommendation
        # ---------------------------------------------

        current_instance = pricing["instance_type"]

        recommended_instance = InstanceRecommendation.recommend(
            current_instance
        )

        ai_analysis["recommended_instance_type"] = recommended_instance

        ai_analysis["optimization_plan"][
            "target_instance_type"
        ] = recommended_instance

        # ---------------------------------------------
        # Savings
        # ---------------------------------------------

        savings = self.savings_calculator.calculate(
            current_cost=cost,
            optimization_plan={
                "target_instance_type": recommended_instance,
                "target_node_count": ai_analysis[
                    "recommended_node_count"
                ]
            }
        )

        ai_analysis["optimized_monthly_cost"] = savings[
            "optimized_monthly_cost"
        ]

        ai_analysis["estimated_savings"] = savings[
            "estimated_savings"
        ]

        ai_analysis[
            "expected_cost_reduction_percent"
        ] = savings[
            "expected_cost_reduction_percent"
        ]

        # ---------------------------------------------
        # Final Response
        # ---------------------------------------------

        return {
            "analysis_context": analysis_context,
            "ai_analysis": ai_analysis
        }