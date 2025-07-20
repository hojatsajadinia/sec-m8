import os
import subprocess
import shlex
import json


class GitleaksScanner:
    def __init__(self):
        pass

    def scan(self):
        command = self.build_gitleaks_command()
        print("Running Gitleaks command:\n", shlex.join(command))  # for debug

        result = subprocess.run(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

        print("STDOUT:\n", result.stdout)
        print("STDERR:\n", result.stderr)

        return result.returncode

    def report(self):
        report_path = "gitleaks_report_sec-m8.json"
        if not os.path.isfile(report_path):
            raise FileNotFoundError(f"{report_path} not found in current directory.")

        with open(report_path, "r") as f:
            return json.load(f)

    def normalize_flag(self, name: str) -> str:
        """Convert env var to CLI flag, e.g., GITLEAKS_REPORT_PATH → --report-path"""
        if len(name.replace("GITLEAKS_", "")) == 1:
            return "-" + name.replace("GITLEAKS_", "").lower()
        else:
            return "--" + name.replace("GITLEAKS_", "").lower().replace("_", "-")

    def build_gitleaks_command(self):
        base_command = [
            "gitleaks",
            "git",
            "--report-format",
            "json",
            "--report-path",
            "gitleaks_report_sec-m8.json",
        ]
        cli_flags = []

        for key, value in os.environ.items():
            if not key.startswith("GITLEAKS_"):
                continue

            flag = self.normalize_flag(key)
            if flag in ["--report-format", "--report-path"]:
                # Skip flags that are already set in base_command
                continue
            # Boolean flag (true/false) with no value
            if value.lower() in ("1", "true", "yes"):
                cli_flags.append(flag)
            elif value.lower() in ("0", "false", "no"):
                continue  # skip false flags
            else:
                # Handle flags with values, e.g. --log-level=debug
                cli_flags.append(f"{flag}={value}")

        return base_command + cli_flags
