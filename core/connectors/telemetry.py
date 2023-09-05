import sentry_sdk  # type: ignore
from sentry_sdk.integrations.flask import FlaskIntegration  # type: ignore

from core.configurations import Telemetry


def init_telemetry():
    if Telemetry.disable:
        return

    sentry_sdk.init(
        dsn="https://af004e4eff23f9923ee02c040133a4fd@o4505051351089152.ingest.sentry.io/4505829940789248",
        integrations=[FlaskIntegration()],
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0,
    )

    return
