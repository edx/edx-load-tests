"""Configuration shared across ecommerce tasks."""
import os


# ID of a course with a free course seat.
FREE_COURSE_ID = os.environ.get('FREE_COURSE_ID', 'edX/DemoX/Demo_Course')

# SKU corresponding to a product with a non-zero price. Must be associated with
# a paid course seat.
PAID_SKU = os.environ.get('PAID_SKU')

if PAID_SKU is None:
    raise RuntimeError('A SKU corresponding to a paid course seat is required to run load tests.')

ECOMMERCE_SERVICE_URL = os.environ.get(
    'ECOMMERCE_SERVICE_URL',
    'http://localhost:8002'
).strip('/')

ECOMMERCE_API_URL = os.environ.get(
    'ECOMMERCE_API_URL',
    '{}/api/v2/'.format(ECOMMERCE_SERVICE_URL)
)

ECOMMERCE_JWT_SECRET_KEY = os.environ.get('ECOMMERCE_JWT_SECRET_KEY', 'insecure-secret-key')
ECOMMERCE_JWT_ISSUER = os.environ.get('ECOMMERCE_JWT_ISSUER', 'http://127.0.0.1:8000/oauth2')

ECOMMERCE_ORDER_OFFSET = os.environ.get('ECOMMERCE_ORDER_OFFSET', 100000)
ECOMMERCE_ORDER_PREFIX = os.environ.get('ECOMMERCE_ORDER_PREFIX', 'OSCR')

CYBERSOURCE_SECRET_KEY = os.environ.get('CYBERSOURCE_SECRET_KEY', 'fake-secret-key')

COUPON_CODE = os.environ.get('COUPON_CODE')
