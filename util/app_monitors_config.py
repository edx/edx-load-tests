"""
edX-specific monitoring apps.

Not directly useful outside of edX, but stands as a helpful example.  For a
list of supported monitoring apps, refer to util/app_monitors.py.
"""
from util.app_monitors import NewRelicMonitor

# Manually entered by looking at the the NR web UI
MONITORS = [
    NewRelicMonitor(
        account_name='edX-Root',
        account_id='88178',
        app_name='loadtest-edx-edxapp-lms',
        app_id='3545617',
    ),
    NewRelicMonitor(
        account_name='edX-Root',
        account_id='88178',
        app_name='loadtest-edx-ecommerce',
        app_id='5371731',
    ),
    # TODO: fill in more monitors.
]
