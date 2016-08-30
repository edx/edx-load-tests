"""Configuration for Credential load testing."""
import os


# URL CONFIGURATION
CREDENTIAL_SERVICE_URL = os.environ.get(
    'CREDENTIAL_SERVICE_URL',
    'http://127.0.0.1:8150'
).strip('/')

CREDENTIAL_API_URL = os.environ.get(
    'CREDENTIAL_API_URL',
    '{}/api/v1/'.format(CREDENTIAL_SERVICE_URL)
)

LMS_ROOT_URL = os.environ.get(
    'LMS_ROOT_URL',
    'http://127.0.0.1:8000'
).strip('/')

# Default program_id will 3, for which we have corresponding program in programs service fixtures.
PROGRAM_ID = os.environ.get('PROGRAM_ID', 3)

# Default username will 'user1', for which we have corresponding credential in credential service fixtures.
USERNAME = os.environ.get('USERNAME', 'user1')

# JWT CONFIGURATION
JWT = {
    "JWT_AUDIENCE": os.environ.get('JWT_AUDIENCE', 'credentials-key'),
    "JWT_ISSUER": os.environ.get('JWT_ISSUER', 'http://127.0.0.1:8000/oauth2'),
    "JWT_EXPIRATION_DELTA": int(os.environ.get('JWT_EXPIRATION_DELTA', 1)),
    "JWT_SECRET_KEY": os.environ.get('JWT_SECRET_KEY', 'credentials-secret')
}
