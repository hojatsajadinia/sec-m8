from utils.http import post
from utils.get_env_variable import get_env_variable
import subprocess


class Gitlab:
    def __init__(self, gitlab_url, gitlab_token, logger):
        self.gitlab_url = gitlab_url.strip()
        self.gitlab_token = gitlab_token.strip()
        self.logger = logger

    def comment_on_merge_request(self, report):
        try:
            ci_merge_request_iid = get_env_variable("CI_MERGE_REQUEST_IID")
            ci_project_id = get_env_variable("CI_PROJECT_ID")
        except EnvironmentError:
            self.logger.info("No Merge Request ID found.")
            return
        headers = {
            "PRIVATE-TOKEN": self.gitlab_token,
            "Content-Type": "application/json",
        }
        table = self.format_gitleaks_report(report)
        if not table:
            self.logger.info("No findings to report.")
            return
        response = post(
            f"{self.gitlab_url}/api/v4/projects/{ci_project_id}/merge_requests/{ci_merge_request_iid}/notes",
            headers=headers,
            data={"body": f"### Gitleaks Report\n\n{table}"},
        )
        if response.status_code == 201:
            self.logger.info("Comment posted successfully on the Merge Request.")
        else:
            self.logger.error(
                f"Failed to post comment on Merge Request: {response.status_code} - {response.text}"
            )

    def format_gitleaks_report(self, report):
        scan_code_change = get_env_variable("SCAN_CODE_CHANGE", False)
        hashes = []
        if str(scan_code_change).lower() in ("1", "true", "yes"):
            self.logger.info("Fetching commit hashes for code changes.")
            target_branch = get_env_variable("CI_MERGE_REQUEST_TARGET_BRANCH_NAME")
            diff_base_sha = get_env_variable("CI_MERGE_REQUEST_DIFF_BASE_SHA")
            commit_sha = get_env_variable("CI_COMMIT_SHA")
            # Fetch the target branch without printing output
            subprocess.run(
                ["git", "fetch", "origin", target_branch],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            # Get the commit hashes
            result = subprocess.run(
                ["git", "log", "--pretty=format:%H", f"{diff_base_sha}..{commit_sha}"],
                stdout=subprocess.PIPE,
                check=True,
                text=True,
            )
            hashes = result.stdout.strip().splitlines()
            self.logger.info(f"Found {len(hashes)} commit hashes for code changes.")

        # Start table
        table = "| RuleID | File | Author | Link |\n"
        table += "| ------ | ---- | ------ | ---- |\n"
        total_rows = 0
        for entry in report:
            if hashes and entry.get("Commit") not in hashes:
                continue
            rule_id = entry.get("RuleID", "")
            file = entry.get("File", "")
            author = entry.get("Author", "")
            link = entry.get("Link", "")

            # Markdown-safe link
            link_md = f"[Link]({link})" if link else ""

            # Escape pipe characters in data
            file = file.replace("|", "\\|")
            author = author.replace("|", "\\|")

            table += f"| {rule_id} | {file} | {author} | {link_md} |\n"
            total_rows += 1
        if total_rows == 0:
            return
        else:
            return table
