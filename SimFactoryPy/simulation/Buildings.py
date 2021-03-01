import simpy
from simpy.exceptions import Interrupt
from .Resources import Item
from .Logistics import ConveyorBelt
from .Loggers import SimLoggerAdapter
import logging

log = logging.getLogger("SimFactory")

class Miner():
    """
    Simulates the Miner

    Parameters:
        env: The simpy.Environment
        item: A Resources.Item which is being mined
        belt: A Logistics.ConveyorBelt output, default None
    """

    def __init__(self, env:simpy.Environment, 
        item:Item, rate, belt:ConveyorBelt = None):

        self.env = env
        self.log = SimLoggerAdapter(log, {"env":self.env})

        self.item = item
        self.period = 1/rate
        self.belt = belt

        self.output_stack = simpy.Container(self.env, capacity=item.stack_cap)

        self.env.process(self.run())

    def run(self):
        while True:
            if self.belt != None:
                try:
                    self.log.info(f"putting {self.item} on belt")
                    put = self.belt.put(self.item)
                except Interrupt as e:
                    self.log.info(e.cause)
                    self.log.info(f"putting {self.item} on stack")
                    put = self.output_stack.put(1)
            else:
                put = self.output_stack.put(1)

            self.log.info(f"wating: {self.period:.3f}")
            yield (self.env.timeout(self.period) & put)


class Constructor():

    """
    Simulates the Constructor.

    Parameters:
        env: The simpy.Environment
        out_rate: Number of items per min produced
        recipe: e.g {in:(Item(iron ore), 3),out:(Item(iron bar), 1)}
    """

    def __init__(self, env : simpy.Environment, 
        out_rate : float, in_belt:ConveyorBelt, out_belt:ConveyorBelt,
        recipe:dict):
        
        self.env = env
        self.recipe = recipe

        self.in_belt = in_belt
        self.out_belt = out_belt

        self.out_stack = simpy.Container(
            self.env, capacity = self.recipe["out"][0].stack_cap
        )
        self.in_stack = simpy.Container(
            self.env, capacity = self.recipe["in"][0].stack_cap
        )

        self.period = 1/out_rate
        self.log = SimLoggerAdapter(log, {"env":self.env})

    def run(self):
        while True:

            self.env.process(self.produce())


    def input(self):
        while True:
            yield

    def produce(self):
        yield self.env.timeout(self.period)
        for _ in range(self.recipe["out"][1]):
            yield self.output()

    def output(self):
        if len(self.out_belt.store.items) < self.out_belt.store.capacity:
            return self.out_belt.put(self.recipe["out"][0])
        else:
            return self.out_stack.put(self.recipe["out"][0])

        

