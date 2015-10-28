"""Configuration for Programs load testing."""
import os


# URL CONFIGURATION
PROGRAMS_SERVICE_URL = os.environ.get(
    'PROGRAMS_SERVICE_URL',
    'http://localhost:8004'
).strip('/')

PROGRAMS_API_URL = os.environ.get(
    'PROGRAMS_API_URL',
    '{}/api/v1/'.format(PROGRAMS_SERVICE_URL)
)
# END URL CONFIGURATION


# JWT CONFIGURATION
JWT_AUDIENCE = os.environ.get('JWT_AUDIENCE', 'replace-me')
JWT_ISSUER = os.environ.get('JWT_ISSUER', 'http://127.0.0.1:8000/oauth2')
JWT_EXPIRATION_DELTA = int(os.environ.get('JWT_EXPIRATION_DELTA', 1))
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')

if not JWT_SECRET_KEY:
    raise RuntimeError('A JWT secret key is required to run Programs load tests.')
# END JWT CONFIGURATION
