import os


def get_env_variable(var_name, default=None):
    value = os.getenv(var_name, default)
    if value is None:
        raise EnvironmentError(f"Required environment variable '{var_name}' not set.")
    return value
