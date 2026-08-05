class InstanceRecommendation:

    SIZE_ORDER = [
        "nano",
        "micro",
        "small",
        "medium",
        "large",
        "xlarge",
        "2xlarge",
        "4xlarge",
        "8xlarge",
        "12xlarge",
        "16xlarge",
        "24xlarge"
    ]

    @classmethod
    def recommend(cls, current_instance: str):

        family, size = current_instance.rsplit(".", 1)

        if size not in cls.SIZE_ORDER:
            return current_instance

        index = cls.SIZE_ORDER.index(size)

        # Already the smallest instance
        if index == 0:
            return current_instance

        smaller = cls.SIZE_ORDER[index - 1]

        return f"{family}.{smaller}"