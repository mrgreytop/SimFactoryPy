import simpy
from simpy.events import AllOf
from simpy.exceptions import Interrupt
from .Resources import MonitorContainer
from .entities.entities import Item, Recipe
from .Logistics import ConveyorBelt
from .Loggers import SimLoggerAdapter
import logging
from fractions import Fraction


log = logging.getLogger("SimFactory")

class Miner():
    """
    Simulates the Miner

    Parameters:
        env: The simpy.Environment
        item: A entities.Item which is being mined
        belt: A Logistics.ConveyorBelt output, default None
    """

    def __init__(self, env:simpy.Environment, 
        item:Item, rate, belt:ConveyorBelt = None):

        self.env = env
        self.log = SimLoggerAdapter(
            log, {"env":self.env, "object":"Miner"})

        self.item = item
        self.period = Fraction(1,rate)
        self.belt = belt

        self.output_stack = MonitorContainer(self.env, 
            capacity=item.stack_cap, parent = "Miner")

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

            self.log.info(f"mining {self.item}")
            yield (self.env.timeout(self.period) & put)


class Constructor():

    """
    Simulates the Constructor.

    Parameters:
        env: The simpy.Environment
        out_rate: Number of items per min produced
        recipe: e.g {in:(Item(iron ore), 3),out:(Item(iron bar), 1)}
    """

    def __init__(self, env: simpy.Environment, recipe: Recipe, 
    in_belt: ConveyorBelt, out_belt:ConveyorBelt = None):
        
        self.env = env
        self.recipe = recipe

        if self.recipe.building != "Constructor":
            raise Exception(f"Recipe requires {self.recipe.building}")

        self.in_belt = in_belt
        self.out_belt = out_belt

        self.out_stack = MonitorContainer(
            self.env, capacity = self.recipe.products[0][0].stack_cap,
            parent = "Constructor Out"
        )

        self.in_stack = MonitorContainer(
            self.env, capacity = self.recipe.ingredients[0][0].stack_cap,
            parent = "Constructor In"
        )

        self.period = self.recipe.time_to_make / 60
        self.log = SimLoggerAdapter(
            log, {"env":self.env, "object":"Constructor"})

        self.env.process(self.run())


    def run(self):
        self.env.process(self.input())
        while True:
            self.log.info("allocating item space")
            yield self.allocate_inputs()
            self.log.info("producing item")
            yield self.env.timeout(self.period)
            self.log.info("produced item")
            yield AllOf(self.env, self.output(self.recipe.products[0][1]))
            self.log.info("output items")


    def input(self):
        while True:
            item:Item = yield self.env.process(self.in_belt.get())
            self.log.info(f"fetched {item}")
            yield self.in_stack.put(1)
            self.log.info(f"put 1 {item} on input stack")


    def allocate_inputs(self)->AllOf:
        gets = [self.in_stack.get(self.recipe.ingredients[0][1])]
        return AllOf(self.env, gets)


    def output(self, amount)->list:
        puts = []
        if (self.out_belt != None): 
            for _ in range(amount):
                if len(self.out_belt.store.items) < self.out_belt.store.capacity:
                    puts.append(
                        self.out_belt.put(self.recipe.products[0][0])
                    )
                else:
                    break

        overflow = amount - len(puts)
        if overflow > 0:
            puts.append(
                self.out_stack.put(overflow)
            )

        return puts



