"""
"""
try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode
from datetime import datetime, timedelta


class AppMonitor(object):
    """
    Representation of a monitoring service web dashboard for a web app.
    """

    def __init__(self, monitoring_service_name, app_name):
        self._monitoring_service_name = monitoring_service_name
        self._app_name = app_name

    @property
    def app_name(self):
        """
        The name of the app being represented by this instance of the
        monitoring service.
        """
        return self._app_name

    @property
    def monitoring_service_name(self):
        """
        The name of this monitoring service.
        """
        return self._monitoring_service_name

    def url(self, begin_time=None, end_time=None):
        """
        Generate a dashboard URL for the configured app and the given
        timeframe.

        Parameters:
            begin_time (datetime.datetime): beginning of timeframe to display
            end_time (datetime.datetime): end of timeframe to display

        Returns:
            str: URL of the dashboard.
        """
        raise NotImplementedError()


class NewRelicMonitor(AppMonitor):
    """
    This class represents the New Relic APM dashboard for a specific app.
    """
    NEWRELIC_APM_TEMPLATE = 'https://rpm.newrelic.com/accounts/{account_id}/applications/{app_id}'

    def __init__(self, account_name=None, account_id=None, app_name=None, app_id=None,):
        super(NewRelicMonitor, self).__init__(
            'New Relic APM dashboard',
            app_name,
        )
        self._account_name = account_name
        self._account_id = account_id
        self._app_name = app_name
        self._app_id = app_id

    def url(self, begin_time=None, end_time=None):
        """
        Generate an APM URL for this app and the given timeframe

        This method is an implementation of the same-signature method in the
        superclass.
        """
        # pad the time range by a few minutes for better visual context
        begin_time_padded = begin_time - timedelta(minutes=4)
        end_time_padded = end_time + timedelta(minutes=4)

        url_without_times = self.NEWRELIC_APM_TEMPLATE.format(
            account_id=self._account_id,
            app_id=self._app_id,
        )
        query_data = {}
        if begin_time:
            # "%s" is the strftime syntax for the number of seconds since
            # the Epoch.
            query_data['tw[start]'] = begin_time.strftime('%s')
            if end_time:
                query_data['tw[end]'] = end_time.strftime('%s')
            else:
                # Due to a race condition in the jenkins job (locust handles
                # SIGTERM after this script gets triggered rather than before),
                # the end_time may not be known yet.  We just assume that the
                # test will be ending soon, so just set the end time to now.
                query_data['tw[end]'] = datetime.now().strftime('%s')
        url = None
        if query_data:
            url = '{}?{}'.format(url_without_times, urlencode(query_data))
        else:
            url = url_without_times
        return url
