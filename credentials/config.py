"""Configuration for Credential load testing."""
import os


# URL CONFIGURATION
CREDENTIAL_SERVICE_URL = os.environ.get(
    'CREDENTIAL_SERVICE_URL',
    'http://localhost:8150'
).strip('/')

CREDENTIAL_API_URL = os.environ.get(
    'CREDENTIAL_API_URL',
    '{}/api/v1/'.format(CREDENTIAL_SERVICE_URL)
)


# JWT CONFIGURATION
JWT_AUDIENCE = os.environ.get('JWT_AUDIENCE', 'credentials-key')
JWT_ISSUER = os.environ.get('JWT_ISSUER', 'http://localhost:8000/oauth2')
JWT_EXPIRATION_DELTA = int(os.environ.get('JWT_EXPIRATION_DELTA', 1))
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'credentials-secret')
