import sys
sys.path.append("../..")
from SimFactoryPy.simulation.Loggers import SimLoggerAdapter
import logging
import simpy
import typing

log = logging.getLogger("SimFactory")

class ConveyorBelt():
    
    def __init__(self, env, 
        length:int, rate:int, input:simpy.Store, output:simpy.Store):

        self.env = env
        self.log = SimLoggerAdapter(log, {"env":self.env})
        self.input = input
        self.output = output
        self.period = 1/rate

        self.on_belt = simpy.Store(self.env, capacity=length)

        self.env.process(self.run())

    def run(self):
        yield (
            self.env.process(self.get()) &
            self.env.process(self.put())
        )

    def get(self):
        while True:
            self.log.info("getting")
            yield self.input.get()
            yield self.env.timeout(self.period)


    def put(self):
        while True:
            # TODO add time onto period to allow item to traverse the belt
            yield self.env.timeout(self.period)
            self.log.info("putting")
            yield self.output.put(self.on_belt.get())
