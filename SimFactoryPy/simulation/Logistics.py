import sys
sys.path.append("../..")
from SimFactoryPy.simulation.Loggers import SimLoggerAdapter
import logging
import simpy

log = logging.getLogger("SimFactory")


class ConveyorBelt():
    
    def __init__(self, env, length:int, rate:int, initial:int = 0):

        self.env = env
        self.log = SimLoggerAdapter(log, {"env":self.env})
        self.rate = rate
        self.period = length/self.rate

        self.store = simpy.Store(self.env, capacity=length)

    def traverse(self, item):
        yield self.env.timeout(self.period)
        self.store.put(item)

    def put(self, item):
        yield self.env.timeout(1/self.rate)
        self.env.process(self.traverse(item))
    
    def get(self):
        p_get = self.store.get()
        p_time = self.env.timeout(1/self.rate)
        condvalue = yield (p_get & p_time)
        return condvalue[p_get]
