import numpy as np
import sys
sys.path.append("..")
from SimFactoryPy.simulation.Logistics import ConveyorBelt
from SimFactoryPy.simulation.Buildings import Miner
from SimFactoryPy.simulation.Resources import Item
from tests.base import BaseSimTest, DP

class TestMiner(BaseSimTest):

    def test_stack(self):
        item_stack = 4
        m = Miner(self.env, Item("iron ore", item_stack), item_stack)

        with self.assertLogs("SimFactory"):
            self.env.run(1)

        self.assertEqual(m.output_stack.level, item_stack)
        self.assertEqual(len(m.output_stack.put_queue), 0)

    def test_out_speed(self):
    
        miner_rate = 60
        run_time = 2
        m = Miner(self.env, Item("small item", 1000), miner_rate)

        with self.assertLogs("SimFactory") as cm:
            self.env.run(run_time)

        self.assertAlmostEqual(
            m.output_stack.level, run_time * miner_rate,
            places = -1
        )

    def test_fast_conveyor(self):
        belt_rate = 8
        miner_rate = 4
        run_time = 2
        belt = ConveyorBelt(self.env, 100, belt_rate)
        m = Miner(self.env, Item("iron ore", 100), 
            miner_rate, belt = belt)

        with self.assertLogs("SimFactory"):
            self.env.run(run_time)

        self.assertEqual(m.output_stack.level, 0)
        self.assertEqual(len(belt.store.items), run_time * miner_rate)

    def test_slow_conveyor(self):
        belt_rate = 1 #item/min
        miner_rate = 2 #item/min
        run_time = 4
        belt = ConveyorBelt(self.env, 100, belt_rate)
        m = Miner(self.env, Item("iron ore", 100), miner_rate, belt = belt)

        with self.assertLogs("SimFactory"):
            self.env.run(run_time)

        self.assertEqual(len(belt.store.items), run_time * belt_rate)