import sys

from simpy.exceptions import Interrupt
sys.path.append("../..")
from SimFactoryPy.simulation.Loggers import SimLoggerAdapter
import logging
import simpy

log = logging.getLogger("SimFactory")


class ConveyorBelt():
    
    def __init__(self, env, length:int, rate:int):
        if length <= 0:
            raise ValueError("Belt is too short")

        self.env = env
        self.log = SimLoggerAdapter(log, {"env":self.env})
        self.rate = rate
        self.period = 1/self.rate
        self.traverse_period = length*self.period

        self.store = simpy.Store(self.env, capacity=length)

    def traverse(self, item):
        try:
            self.env.timeout(self.traverse_period)
            self.store.put(item)
        except Interrupt:
            pass

    def put(self, item):
        self.log.info("putting item on conveyor")
        self.traverse(item)
        return self.env.timeout(self.period)
    
    def get(self):
        self.log.info("getting item from conveyor")
        p_get = self.store.get()
        p_time = self.env.timeout(self.period)
        condvalue = yield (p_get & p_time)
        return condvalue[p_get]
