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
        self.log = SimLoggerAdapter(
            log, {"env":self.env, "object":"Belt"})
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
        self.log.info(f"putting {item} on belt")
        self.traverse(item)
        return self.env.timeout(self.period)
    
    def get(self):
        self.log.info("looking for item from belt")
        p_get = self.store.get()
        p_time = self.env.timeout(self.period)
        condvalue = yield (p_get & p_time)
        self.log.info(f"{condvalue[p_get]} removed")
        return condvalue[p_get]


class Splitter():
    
    def __init__(self, env:simpy.Environment, in_belt:ConveyorBelt, out_belts:list):
        if len(out_belts) > 3:
            raise ValueError("The number of output belts must be 3 or less")
        elif len(out_belts) < 1:
            raise ValueError("Must have at least one output belt")

        self.in_belt = in_belt
        self.out_belts = out_belts

        self.store = simpy.Store(env, capacity = 1)

        self.env.process(self.run())

    def run(self):
        while True:
            for belt in self.out_belts:
                item = yield self.env.process(self.in_belt.get())
                yield belt.put(item)