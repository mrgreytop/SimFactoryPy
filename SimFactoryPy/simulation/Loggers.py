import logging
from logging.config import dictConfig
import simpy


dictConfig({
    "version":1.0,
    "formatters":{
        "simple":{
            "format":"(%(asctime)s) %(message)s",
            "datefmt":"%H:%M:%S"
        }
    },
    "handlers":{
        "console":{
            "class": "logging.StreamHandler",
            "formatter":"simple",
            "level":logging.DEBUG
        }
    },
    "loggers":{
        "SimFactory":{
            "handlers":["console"],
            "level":logging.DEBUG
        }
    }
})

class SimLoggerAdapter(logging.LoggerAdapter):

    def __init__(self, logger, extra):
        try:
            env = extra["env"]
        except KeyError:
            raise ValueError("Must supply a simpy.Environment to extra args")

        if not isinstance(env, simpy.Environment):
            raise TypeError("env in extra must be a simpy.Environment")

        super().__init__(logger, extra)

    def process(self, msg, kwargs):
        env:simpy.Environment = self.extra["env"]
        return f"[{env.now*60:.3f}] {msg}", kwargs

