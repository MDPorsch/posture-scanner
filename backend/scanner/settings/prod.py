import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.celery import CeleryIntegration
from .base import *  # noqa
import environ

env = environ.Env()
DEBUG = False
ENVIRONMENT = env("ENVIRONMENT", default="production")
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["*.onrender.com"])
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=["https://your-app.vercel.app"])
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

sentry_sdk.init(
    dsn=env("SENTRY_DSN", default=""),
    integrations=[DjangoIntegration(), CeleryIntegration()],
    traces_sample_rate=0.2,
    send_default_pii=False,
    environment=ENVIRONMENT,
    release=env("RENDER_GIT_COMMIT", default="unknown"),
)
