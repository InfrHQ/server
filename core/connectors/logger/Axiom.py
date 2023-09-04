import logging
import requests
import json

from core.configurations import Axiom


class AxiomHandler(logging.Handler):
    def __init__(self, flush_limit=10):
        super().__init__()
        self.buffer = []
        self.flush_limit = flush_limit

    def emit(self, record):

        if 'extra' not in record.__dict__ and hasattr(record, 'extra'):
            record.__dict__['extra'] = record.extra  # type: ignore

        extra = record.__dict__.get('extra', {})
        if extra:
            extra = json.loads(extra)
        log_entry = {
            'unix_timestamp': record.created,
            'log_type': record.levelname,
            'message': record.getMessage(),
            'extra': extra
        }
        self.buffer.append(log_entry)
        if len(self.buffer) >= self.flush_limit:
            self.flush()

    def flush(self):
        # with self.lock:
        if len(self.buffer) > 0:
            try:
                requests.post(url=Axiom.url, json=self.buffer,  # type: ignore
                              headers={"Authorization": f"Bearer {Axiom.api_key}"})
                self.buffer = []
            except Exception as e:
                print(f"Failed to upload logs to Axiom: {e}")  # changed to print

    def __del__(self):
        self.flush()
