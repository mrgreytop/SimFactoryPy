import logging
from logging.config import dictConfig
import simpy


dictConfig({
    "version":1.0,
    "formatters":{
        "simple":{
            "format":"%(message)s"
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
        },
        "TestLogger":{
            "handlers":["console"],
            "level":logging.DEBUG
        }
    }
})

class SimLoggerAdapter(logging.LoggerAdapter):

    def __init__(self, logger, extra):
        try:
            self.env = extra["env"]
        except KeyError:
            raise ValueError("Must supply a simpy.Environment to extra args")

        if not isinstance(self.env, simpy.Environment):
            raise TypeError("env in extra must be a simpy.Environment")

        self.object = extra.get("object")
        super().__init__(logger, extra)

    def process(self, msg, kwargs)->tuple:
        if self.object == None:
            return f"{self.env.now}: {msg}", kwargs
        else:
            return f"{self.env.now}: {self.object}: {msg}", kwargs
            

def parse_env_time(message):
    return float(message.split(":")[0])
