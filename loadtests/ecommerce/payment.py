"""Locust tests for the E-Commerce Service payment notification endpoints."""
import base64
import hashlib
import hmac

from locust import task

from helpers import settings
from helpers.api import LocustEdxRestApiClient
from helpers.auto_auth_tasks import AutoAuthTasks


def sign(message, secret):
    """Compute a Base64-encoded HMAC-SHA256.

    Arguments:
        message (unicode): The value to be signed.
        secret (unicode): The secret key to use when signing the message.

    Returns:
        unicode: The message signature.
    """
    message = message.encode('utf-8')
    secret = secret.encode('utf-8')

    # Calculate a message hash (i.e., digest) using the provided secret key
    digest = hmac.new(secret, msg=message, digestmod=hashlib.sha256).digest()

    # Base64-encode the message hash
    signature = base64.b64encode(digest).decode()

    return signature


class CybersourcePaymentTasks(AutoAuthTasks):
    def __init__(self, *args, **kwargs):
        super(CybersourcePaymentTasks, self).__init__(*args, **kwargs)
        self.ecommerce_service_url = settings.data['ecommerce']['url']['service']
        self.cybersource_secret_key = settings.data['ecommerce']['cybersource_secret_key']

    @task
    def payment_process(self):
        """Simulate the CyberSource payment process.

        Mirrors the way a user would behave when interacting with the payment
        flow. Contacts the ecommerce service directly to emulate the merchant
        notification sent by CyberSource.
        """
        self.auto_auth()

        self.api_client = LocustEdxRestApiClient(
            settings.data['ecommerce']['url']['api'],
            session=self.client,
            signing_key=settings.data['jwt']['secret_key'],
            issuer=settings.data['jwt']['issuer'],
            username=self._username,
            email=self._email,
        )

        # Emulate rendering of payment buttons
        self.api_client.payment.processors().get()

        # Emulate basket creation and payment
        order_id = self.cybersource_notification()

        # Emulate rendering of the receipt page
        self.api_client.orders(order_id).get(name='/api/v2/orders/:id/')

    def cybersource_notification(self):
        """Contact Otto's CyberSource notification endpoint."""
        basket_id, amount = self._get_basket_details()
        data = self._get_cybersource_notification_data(basket_id, amount)

        # This endpoint isn't part of the versioned API. It's also not protected
        # by JWT auth, so there's no need to use the API client here.
        url = '{}/payment/cybersource/notify/'.format(self.ecommerce_service_url)
        self.client.post(
            url,
            data=data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )

        order_id = data['req_reference_number']

        return order_id

    def _get_basket_details(self):
        """Creates a basket and returns its ID and amount.

        Contacts Otto directly to create the user's basket.
        """
        basket = self.api_client.baskets.post({
            'products': [{'sku': settings.data['ecommerce']['paid_sku']}],
            'checkout': True,
            'payment_processor_name': 'cybersource'
        })
        return basket['id'], basket['payment_data']['payment_form_data']['amount']

    def _get_cybersource_notification_data(self, basket_id, amount):
        """Returns a dict simulating a CyberSource payment response."""
        order_id = basket_id + settings.data['ecommerce']['order']['offset']
        order_number = u'{prefix}-{order_id}'.format(
            prefix=settings.data['ecommerce']['order']['prefix'],
            order_id=order_id
        )

        notification = {
            'decision': 'ACCEPT',
            'req_reference_number': order_number,
            'transaction_id': '123456',
            'auth_amount': amount,
            'req_amount': amount,
            'req_tax_amount': '0.00',
            'req_currency': 'USD',
            'req_card_number': 'xxxxxxxxxxxx1111',
            'req_card_type': '001',
            'req_bill_to_forename': 'Ed',
            'req_bill_to_surname': 'Xavier',
            'req_bill_to_address_line1': '141 Portland Ave.',
            'req_bill_to_address_line2': '9th Floor',
            'req_bill_to_address_city': 'Cambridge',
            'req_bill_to_address_postal_code': '02141',
            'req_bill_to_address_state': 'MA',
            'req_bill_to_address_country': 'US'
        }

        notification['signed_field_names'] = ','.join(notification.keys())
        notification['signature'] = self._generate_cybersource_signature(
            self.cybersource_secret_key,
            notification
        )
        return notification

    def _generate_cybersource_signature(self, secret_key, data):
        """Generate a signature for the given data dict."""
        keys = data[u'signed_field_names'].split(u',')

        message = u','.join([u'{key}={value}'.format(key=key, value=data[key]) for key in keys])
        return sign(message, secret_key)
