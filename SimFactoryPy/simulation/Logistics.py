from fractions import Fraction
from typing import List
from SimFactoryPy.simulation.Resources import MonitorStore
from simpy.exceptions import Interrupt
from .Loggers import SimLoggerAdapter
import logging
import simpy

log = logging.getLogger("SimFactory")


class ConveyorBelt():
    
    def __init__(self, env, length:int, rate:int, name="Belt"):
        if length <= 0:
            raise ValueError("Belt is too short")

        self.env = env
        self.log = SimLoggerAdapter(
            log, {"env":self.env, "object":name})
        self.rate = rate
        self.period = Fraction(1,self.rate)
        self.traverse_period = (length-1)*self.period

        self.store = MonitorStore(self.env, capacity=length, parent = name)

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
        self.env = env
        self.log = SimLoggerAdapter(log, {"env":self.env, "object":"Splitter"})

        self.env.process(self.run())

    def run(self):
        i = 0
        while True:
            self.log.info("getting item from input belt")
            item = yield self.env.process(self.in_belt.get())
            self.log.info("got item from input belt")
            self.log.info(f"putting item on belt {i}")
            self.out_belts[i].put(item)
            self.log.info(f"put item on belt {i}")
            i+=1
            i%=len(self.out_belts)


class Merger():

    def __init__(self, env, out_belt:ConveyorBelt, in_belts:list):
        if len(in_belts > 3):
            raise ValueError("Must have less than 3 input belts")
        elif len(in_belts < 1):
            raise ValueError("Must have at least one input belt")

        self.in_belts = in_belts
        self.out_belt = out_belt
        self.env = env
        self.log = SimLoggerAdapter(log, {"env":self.env, "object":"Merger"})

        self.env.process(self.run())

    def run(self):
        i = 0
        while True:
            item = yield self.env.process(self.in_belts[i].get())
            self.out_belt.put(item)
            i+=1
            i%=len(self.in_belts)
