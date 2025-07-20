import os
from sys import exit
from utils.logger import Logger
from scanners.gitleaks import GitleaksScanner
import json

logger = Logger().get_logger()


def get_env_variable(var_name, default=None):
    value = os.getenv(var_name, default)
    if value is None:
        raise EnvironmentError(f"Required environment variable '{var_name}' not set.")
    return value


def main():
    # Scan types: secret, secret:gitleaks, secret:trufflehog, SAST, SAST:semgrep, SCA, SCA:depdency-check, image, image:trivy
    try:
        scan_type = get_env_variable("SCAN_TYPE")
    except EnvironmentError:
        logger.error("SCAN_TYPE is not set.")
        exit(2)

    scan_mode = scan_type.split(":")[0]
    scan_tool = scan_type.split(":")[1] if ":" in scan_type else None

    if scan_tool is None:
        logger.info(f"Using default tool (gitleaks) for scan mode '{scan_mode}'.")
        scan_tool = "gitleaks"

    # Check if scan_mode and scan_tool are valid
    if scan_mode not in ["secret", "SAST", "SCA", "image"]:
        logger.error(
            f"Invalid scan mode: {scan_mode}. Supported modes are: secret, SAST, SCA, image."
        )
        exit(2)
    if scan_tool and scan_tool not in [
        "gitleaks",
        "trufflehog",
        "semgrep",
        "dependency-check",
        "trivy",
    ]:
        logger.error(
            f"Invalid scan tool: {scan_tool}. Supported tools are: gitleaks, trufflehog, semgrep, dependency-check, trivy."
        )
        exit(2)

    logger.info(f"Starting scan with mode: {scan_mode}, tool: {scan_tool}")
    if scan_mode == "secret":
        if scan_tool == "gitleaks":
            logger.info("Running Gitleaks scan...")

            gitleaksScanne = GitleaksScanner()
            if gitleaksScanne.scan():
                logger.info("Gitleaks scan completed successfully.")
                report = gitleaksScanne.report()
                logger.info("Gitleaks report generated.")
                print(json.dumps(report, indent=2))

        elif scan_tool == "trufflehog":
            logger.info("Running TruffleHog scan...")
            # Add TruffleHog scan logic here
        else:
            logger.error(f"Unsupported secret scan tool: {scan_tool}")
            exit(2)


if __name__ == "__main__":
    main()
