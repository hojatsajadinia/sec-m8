from utils.http import post
from utils.get_env_variable import get_env_variable
import json


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
        response = post(
            f"{self.gitlab_url}/api/v4/projects/{ci_project_id}/merge_requests/{ci_merge_request_iid}/notes",
            headers=headers,
            data={"body": f"### Gitleaks Report\n\n{self.format_gitleaks_report(report)}"}
        )
        if response.status_code == 201:
            self.logger.info("Comment posted successfully on the Merge Request.")
        else:
            self.logger.error(
                f"Failed to post comment on Merge Request: {response.status_code} - {response.text}"
            )

    def format_gitleaks_report(self, report):
        # Start table
        table = "| RuleID | File | Author | Link |\n"
        table += "| ------ | ---- | ------ | ---- |\n"

        for entry in report:
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

        return table
