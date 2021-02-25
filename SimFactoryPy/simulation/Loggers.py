import logging
from typing import Type
import simpy

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
        return "[%s] %s" % (env.now, msg), kwargs


log = logging.getLogger()
adapter = SimLoggerAdapter(log, {"env":simpy.Environment()})
adapter.debug("hello")
