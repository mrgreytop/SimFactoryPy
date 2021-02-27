import sys

from simpy.exceptions import Interrupt
sys.path.append("../..")
from SimFactoryPy.simulation.Loggers import SimLoggerAdapter
import logging
import simpy

log = logging.getLogger("SimFactory")


class ConveyorBelt():
    
    def __init__(self, env, length:int, rate:int, initial:int = 0):
        if length <= 0:
            raise ValueError("Belt is too short")

        self.env = env
        self.log = SimLoggerAdapter(log, {"env":self.env})
        self.rate = rate
        self.period = length/self.rate

        self.store = simpy.Store(self.env, capacity=length)

    def traverse(self, item):
        try:
            yield self.env.timeout(self.period)
            self.store.put(item)
        except Interrupt:
            pass

    def put(self, item):
        yield self.env.timeout(1/self.rate)
        p = self.env.process(self.traverse(item))
        if len(self.store.items) >= self.store.capacity:
            p.interrupt()
            raise Interrupt("Belt is full")
    
    def get(self):
        p_get = self.store.get()
        p_time = self.env.timeout(1/self.rate)
        condvalue = yield (p_get & p_time)
        return condvalue[p_get]
