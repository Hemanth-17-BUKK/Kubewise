import shutil
import subprocess


class HelmClient:

    def __init__(self, kubeconfig: str):
        self.kubeconfig = kubeconfig

    def run(self, command):

        if shutil.which("helm") is None:
            raise RuntimeError(
                "Helm executable not found in PATH."
            )

        full_command = command + [
            "--kubeconfig",
            self.kubeconfig,
        ]

        print()
        print("Executing:")
        print(" ".join(full_command))
        print()

        result = subprocess.run(
            full_command,
            capture_output=True,
            text=True,
            timeout=600,
        )

        print("STDOUT")
        print(result.stdout)

        if result.stderr:
            print("STDERR")
            print(result.stderr)

        if result.returncode != 0:
            raise RuntimeError(result.stderr)

        return result.stdout