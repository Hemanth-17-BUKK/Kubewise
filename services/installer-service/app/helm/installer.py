from app.helm.client import HelmClient


class HelmInstaller:

    REPOSITORY_NAME = "prometheus-community"

    REPOSITORY_URL = (
        "https://prometheus-community.github.io/helm-charts"
    )

    RELEASE_NAME = "prometheus"

    CHART = "prometheus-community/prometheus"

    NAMESPACE = "monitoring"

    HELM_VALUES = [
        ("alertmanager.enabled", "false"),
        ("server.persistentVolume.enabled", "false"),
        ("prometheus-pushgateway.enabled", "false"),
    ]

    def __init__(self, kubeconfig: str):
        self.helm = HelmClient(kubeconfig)

    def add_repository(self):

        print("=" * 60)
        print("STEP 1 : Adding Helm Repository")
        print("=" * 60)

        return self.helm.run(
            [
                "helm",
                "repo",
                "add",
                self.REPOSITORY_NAME,
                self.REPOSITORY_URL,
            ]
        )

    def update_repositories(self):

        print("=" * 60)
        print("STEP 2 : Updating Helm Repository")
        print("=" * 60)

        return self.helm.run(
            [
                "helm",
                "repo",
                "update",
            ]
        )

    def install(self):

        print("=" * 60)
        print("STEP 3 : Installing Prometheus")
        print("=" * 60)

        command = [
            "helm",
            "upgrade",
            "--install",
            self.RELEASE_NAME,
            self.CHART,
            "--namespace",
            self.NAMESPACE,
            "--create-namespace",
        ]

        # Add all Helm values
        for key, value in self.HELM_VALUES:
            command.extend(["--set", f"{key}={value}"])

        command.extend(
            [
                "--wait",
                "--timeout",
                "10m",
            ]
        )

        return self.helm.run(command)