import yaml

from dogapi import dog_stats_api, dog_http_api

from helpers import settings


def setup():
    """
    Initialize connection to datadog during locust startup.

    Reads the datadog api key from (in order):
    1) the DATADOG_API_KEY setting in the settings file
    2) the DATADOG_API_KEY of a yaml file specified by the ANSIBLE_VARS
       setting in the settings file
    """

    api_key = settings.data.get('DATADOG_API_KEY')
    if api_key is None:
        server_vars_path = settings.data['ANSIBLE_VARS']
        with open(server_vars_path, 'r') as server_vars_file:
            server_vars = yaml.safe_load(server_vars_file)
        api_key = server_vars.get('DATADOG_API_KEY')

    # By default use the statsd agent
    dog_stats_api.start(
        statsd=True,
        api_key=api_key,
    )
