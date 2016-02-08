"""Configuration for Course Discovery load testing."""
import os

# URL CONFIGURATION
COURSE_DISCOVERY_SERVICE_URL = os.environ.get('COURSE_DISCOVERY_SERVICE_URL', 'http://localhost:8008').strip('/')
COURSE_DISCOVERY_API_URL = '{}/api/v1/'.format(COURSE_DISCOVERY_SERVICE_URL)
# END URL CONFIGURATION


# JWT CONFIGURATION
JWT_AUDIENCE = os.environ.get('JWT_AUDIENCE', 'course-discovery')
JWT_EXPIRATION_DELTA = int(os.environ.get('JWT_EXPIRATION_DELTA', 1))
JWT_ISSUER = os.environ.get('JWT_ISSUER', 'course-discovery')
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'course-discovery-jwt-secret-key')
# END JWT CONFIGURATION
