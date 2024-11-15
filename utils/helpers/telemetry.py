import os
from datetime import datetime

from opentelemetry import metrics
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource

from utils.helpers.logger import logger


class StreamlitTelemetryManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            logger.info("Creating new StreamlitTelemetryManager instance")
        return cls._instance

    def __init__(self):
        if not hasattr(self, "_initialized"):
            logger.info("Initializing StreamlitTelemetryManager")
            self._meter_provider = None
            try:
                self._initialize_telemetry()
                self._define_metrics()
                self._initialized = True
                self._feedback_start_times = {}
                logger.info("StreamlitTelemetryManager initialized successfully")
            except Exception as e:
                logger.error(
                    f"Failed to initialize StreamlitTelemetryManager: {str(e)}",
                    exc_info=True,
                )
                raise

    def _initialize_telemetry(self):
        try:
            service_name = os.getenv("OTEL_SERVICE_NAME", "Streamlit Frontend")
            environment = os.getenv(
                "OTEL_RESOURCE_ATTRIBUTES", "deployment.environment=staging"
            ).split("=")[1]
            logger.info(
                f"Initializing telemetry for service: {service_name} in environment: {environment}"
            )

            resource = Resource.create(
                {"service.name": service_name, "deployment.environment": environment}
            )

            endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")
            logger.debug(f"Setting up OTLP exporter with endpoint: {endpoint}")

            otlp_metric_exporter = OTLPMetricExporter(endpoint=endpoint, insecure=True)
            metric_reader = PeriodicExportingMetricReader(
                otlp_metric_exporter, export_interval_millis=60000
            )
            self._meter_provider = MeterProvider(
                resource=resource, metric_readers=[metric_reader]
            )
            metrics.set_meter_provider(self._meter_provider)
            logger.info("Telemetry initialization completed successfully")
        except Exception as e:
            logger.error(f"Failed to initialize telemetry: {str(e)}", exc_info=True)
            raise

    def _define_metrics(self):
        try:
            logger.debug("Defining metrics")
            meter = metrics.get_meter("Streamlit Metrics")
            self.feedback_duration = meter.create_histogram(
                "feedback_duration_seconds",
                description="Time taken by user to provide feedback after API response",
                unit="seconds",
            )
            logger.debug("Metrics defined successfully")
        except Exception as e:
            logger.error(f"Failed to define metrics: {str(e)}", exc_info=True)
            raise

    def start_feedback_timer(self) -> str:
        """Start timing when API response is received"""
        try:
            session_id = str(datetime.now().timestamp())
            self._feedback_start_times[session_id] = datetime.now()
            logger.info(f"Started feedback timer for session: {session_id}")
            return session_id
        except Exception as e:
            logger.error(f"Failed to start feedback timer: {str(e)}", exc_info=True)
            raise

    def record_feedback_duration(self, session_id: str):
        """Record the duration when feedback is submitted"""
        try:
            if session_id in self._feedback_start_times:
                duration = (
                    datetime.now() - self._feedback_start_times[session_id]
                ).total_seconds()
                self.feedback_duration.record(duration, {"session_id": session_id})
                del self._feedback_start_times[session_id]
                logger.info(
                    f"Recorded feedback duration for session {session_id}: {duration} seconds"
                )
            else:
                logger.warning(f"No start time found for session: {session_id}")
        except Exception as e:
            logger.error(f"Failed to record feedback duration: {str(e)}", exc_info=True)
            raise

    def shutdown(self):
        try:
            if self._meter_provider:
                self._meter_provider.shutdown()
                self._meter_provider = None
                logger.info("Telemetry meter provider shut down successfully")
        except Exception as e:
            logger.error(f"Failed to shutdown meter provider: {str(e)}", exc_info=True)
            raise


def track_api_response() -> str:
    """
    Call this function when API results are received.
    Returns a session_id that should be used when tracking the feedback submission.

    Returns:
        str: Session ID to be used when tracking feedback submission
    """
    try:
        logger.info("Tracking API response")
        manager = StreamlitTelemetryManager()
        session_id = manager.start_feedback_timer()
        logger.info(f"API response tracked with session ID: {session_id}")
        return session_id
    except Exception as e:
        logger.error(f"Failed to track API response: {str(e)}", exc_info=True)
        raise


def track_user_feedback(session_id: str) -> None:
    """
    Call this function when user submits their feedback.

    Args:
        session_id: The session ID received from track_api_response()
    """
    try:
        logger.info(f"Tracking user feedback for session: {session_id}")
        manager = StreamlitTelemetryManager()
        manager.record_feedback_duration(session_id)
        logger.info(f"User feedback tracked successfully for session: {session_id}")
    except Exception as e:
        logger.error(f"Failed to track user feedback: {str(e)}", exc_info=True)
        raise
