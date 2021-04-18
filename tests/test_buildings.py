from unittest.case import expectedFailure
import numpy as np
import sys
from fractions import Fraction
sys.path.append("..")
from SimFactoryPy.simulation.Logistics import ConveyorBelt
from SimFactoryPy.simulation.Buildings import Miner, Constructor
from SimFactoryPy.simulation.entities.entities import Item, Recipe
from tests.base import BaseSimTest, DP
from tabulate import TableFormat, tabulate


class TestMiner(BaseSimTest):

    def test_stack(self):
        item_stack = 4
        m = Miner(self.env, Item(
            name = "Ore",
            fluid=False,
            stack_cap=item_stack,
            sink_value=0
        ), item_stack)

        with self.assertLogs("SimFactory"):
            self.env.run(1)

        
        # print("\n", tabulate(m.output_stack.data, headers = "keys"), sep="")

        self.assertEqual(m.output_stack.level, item_stack)
        self.assertEqual(len(m.output_stack.put_queue), 0)

    def test_out_speed(self):
    
        miner_rate = 60
        run_time = 2
        m = Miner(self.env, Item(
            name = "small item", stack_cap = 1000, sink_value = 0, fluid = False), miner_rate)

        with self.assertLogs("SimFactory") as cm:
            self.env.run(run_time)
        
        # print(tabulate(m.output_stack.data, headers="keys"))
        self.assertEqual(
            m.output_stack.level, run_time * miner_rate
        )

    def test_fast_conveyor(self):
        belt_rate = 8
        miner_rate = 4
        run_time = 2
        belt = ConveyorBelt(self.env, 100, belt_rate)
        m = Miner(self.env, Item(
            name="iron ore", fluid=False, stack_cap=100, sink_value=0
            ), miner_rate, belt=belt)

        with self.assertLogs("SimFactory"):
            self.env.run(run_time)

        self.assertEqual(m.output_stack.level, 0)
        self.assertEqual(len(belt.store.items), run_time * miner_rate)

    def test_slow_conveyor(self):
        belt_rate = 1 #item/min
        miner_rate = 2 #item/min
        run_time = 4
        belt = ConveyorBelt(self.env, 100, belt_rate)
        m = Miner(self.env, Item(
            name = "iron ore", 
            fluid=False,
            stack_cap=100,
            sink_value=0
        ), miner_rate, belt = belt)

        with self.assertLogs("SimFactory"):
            self.env.run(run_time)

        self.assertEqual(len(belt.store.items), run_time * belt_rate)

class TestConstructor(BaseSimTest):

    def test_stacks(self):
        ore = Item(name = "Ore", fluid = False, stack_cap=100, sink_value=0)
        bar = Item(name = "Bar", fluid = False, stack_cap=100, sink_value=0)
        time_to_make = Fraction(6,1)
        recipe = Recipe(name = "Bar", ingredients=[(ore,1)], products=[(bar, 1)],
            time_to_make=time_to_make, 
            building = "Constructor"
        )
        run_time = Fraction(60,60)
        in_rate = 100

        in_belt = ConveyorBelt(self.env, 1, in_rate)
        c = Constructor(
            self.env,
            in_belt=in_belt, 
            recipe=recipe,
            out_belt=None
        )
        m = Miner(self.env, ore, in_rate, belt = in_belt)

        with self.assertLogs("SimFactory") as cm:
            self.env.run(run_time)
        

        expected_output = int((run_time - in_belt.period) * 60 / time_to_make)
        self.assertEqual(c.out_stack.level, expected_output)

