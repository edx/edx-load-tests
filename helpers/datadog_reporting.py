import os
import yaml

from dogapi import dog_stats_api, dog_http_api


def setup():
    """
    Initialize connection to datadog during locust startup.

    Reads the datadog api key from (in order):
    1) An environment variable named DATADOG_API_KEY
    2) the DATADOG_API_KEY of a yaml file at
       2a) the environment variable ANSIBLE_VARS
       2b) /edx/app/edx_ansible/server-vars.yaml
    """

    api_key = os.env.get('DATADOG_API_KEY')

    if api_key is None:
        server_vars_path = os.env.get('ANSIBLE_VARS', '/edx/app/edx_ansible/server-vars.yaml')
        server_vars = yaml.safe_load(server_vars_path)
        api_key = server_vars.get('DATADOG_API_KEY')

    # By default use the statsd agent
    dog_stats_api.start(
        statsd=True,
        api_key=api_key,
    )
