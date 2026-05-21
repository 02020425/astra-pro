from prometheus_client import Counter, Histogram, Gauge, Info
from time import time


REQUEST_COUNT = Counter(
    "astra_pro_requests_total",
    "Total number of requests",
    ["endpoint", "method", "status_code"],
)

REQUEST_LATENCY = Histogram(
    "astra_pro_request_latency_seconds",
    "Request latency in seconds",
    ["endpoint", "method"],
)

ACTIVE_REQUESTS = Gauge(
    "astra_pro_active_requests",
    "Number of active requests",
)

LLM_CALLS = Counter(
    "astra_pro_llm_calls_total",
    "Total number of LLM calls",
    ["model"],
)

LLM_CALL_LATENCY = Histogram(
    "astra_pro_llm_call_latency_seconds",
    "LLM call latency in seconds",
    ["model"],
)

AGENT_CALLS = Counter(
    "astra_pro_agent_calls_total",
    "Total number of agent calls",
    ["agent_name"],
)

APP_INFO = Info("astra_pro", "Application information")


def record_request(endpoint: str, method: str, status_code: int, latency: float):
    REQUEST_COUNT.labels(endpoint=endpoint, method=method, status_code=status_code).inc()
    REQUEST_LATENCY.labels(endpoint=endpoint, method=method).observe(latency)


def record_llm_call(model: str, latency: float):
    LLM_CALLS.labels(model=model).inc()
    LLM_CALL_LATENCY.labels(model=model).observe(latency)


def record_agent_call(agent_name: str):
    AGENT_CALLS.labels(agent_name=agent_name).inc()


class Timer:
    def __init__(self):
        self.start = None
        self.end = None
    
    def __enter__(self):
        self.start = time()
        return self
    
    def __exit__(self, *args):
        self.end = time()
    
    @property
    def elapsed(self):
        if self.end is None:
            return time() - self.start
        return self.end - self.start