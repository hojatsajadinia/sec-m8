import requests

def get(url, params=None, headers=None):
    """Perform a GET request."""
    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()
    return response


def post(url, data=None, headers=None):
    """Perform a POST request."""
    response = requests.request("POST", url, json=data, headers=headers)
    response.raise_for_status()
    return response
