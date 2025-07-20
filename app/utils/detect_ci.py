import os

def detect_ci():
    if os.getenv('GITLAB_CI'):
        return "gitlab"
    elif os.getenv('GITHUB_ACTIONS'):
        return "github"
    elif os.getenv('BITBUCKET_BUILD_NUMBER'):
        return "bitbucket"
    else:
        return "unknown"