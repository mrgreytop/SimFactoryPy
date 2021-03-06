import simpy
from simpy.exceptions import Interrupt
import sys
import logging
import numpy as np

sys.path.append("..")
from SimFactoryPy.simulation import Logistics
from SimFactoryPy.simulation.Loggers import parse_env_time
from base import BaseSimTest
from tabulate import tabulate


log = logging.getLogger("TestLogger")

def producer(env:simpy.Environment, belt:Logistics.ConveyorBelt):
    while True:
        yield belt.put("ore")

def receiver(env:simpy.Environment,belt:Logistics.ConveyorBelt):
    while True:
        t = yield env.process(belt.get())
        log.info(f"Received item from conveyor at :{env.now:.3f}: Sent at :{t:.3f}")
    
    

class TestConveyorBelt(BaseSimTest):

    def test_put_speed(self):
        belt_speed = 10
        run_time = 0.5
        belt = Logistics.ConveyorBelt(
            self.env, 100, belt_speed
        )
        self.env.process(
            producer(self.env, belt)
        )
        self.env.process(
            receiver(self.env, belt)
        )

        with self.assertLogs("SimFactory"):
            with self.assertLogs(log) as cm:
                self.env.run(run_time)

        def get_times(message):
            parts = message.split(":")
            return float(parts[-1]), float(parts[1])

        times = [get_times(r.message) for r in cm.records]
        expectedTimes = [
            (i, i+belt.period) 
            for i in np.arange(0,run_time-belt.period,belt.period)
        ]
        
        np.testing.assert_array_almost_equal(times,expectedTimes)

    def test_get_speed(self):
        belt_speed = 60
        run_time = 1
        belt = Logistics.ConveyorBelt(
            self.env, 100, belt_speed
        )
        belt.store.items = [0 for _ in range(belt.store.capacity)]
        
        self.env.process(
            receiver(self.env, belt)
        )

        with self.assertLogs("SimFactory"):
            with self.assertLogs(log):
                self.env.run(run_time)

        expectedItems = belt.store.capacity - belt_speed * run_time
        self.assertEqual(len(belt.store.items),expectedItems)


class TestSplitter(BaseSimTest):

    def test_2_belts(self):
        out_rate = in_rate = 10
        run_time = 1

        capacities = [(in_rate, "in"),(out_rate, "out1"),(out_rate,"out2")]
        in_belt, *out_belts = [
            Logistics.ConveyorBelt(self.env,cap,in_rate, name = name)
            for cap,name in capacities
        ]
        
        s = Logistics.Splitter(self.env, in_belt, out_belts)

        self.env.process(producer(self.env, in_belt))

        with self.assertLogs("SimFactory"):
            self.env.run(run_time)

        out_belt_levels = [b.store.level for b in out_belts]

        perfect_split = run_time*in_rate/2
        

        if perfect_split % 1 != 0:
            split = [np.ceil(perfect_split), np.floor(perfect_split)]
        else:
            split = [perfect_split] * 2
            
        self.assertSequenceEqual(split, out_belt_levels)
    
    def test_3_belts(self):
        out_rate = in_rate = 10
        run_time = 1

        capacities = [(in_rate, "in"),(out_rate, "out1"),(out_rate,"out2"),(out_rate,"out3")]
        in_belt, *out_belts = [
            Logistics.ConveyorBelt(self.env,cap,in_rate, name = name)
            for cap,name in capacities
        ]
        
        s = Logistics.Splitter(self.env, in_belt, out_belts)

        self.env.process(producer(self.env, in_belt))

        with self.assertLogs("SimFactory"):
            self.env.run(run_time)

        out_belt_levels = [b.store.level for b in out_belts]

        produced_items = run_time*in_rate
        remainder = produced_items % 3
        perfect_split = produced_items // 3
        if remainder == 2:
            split = [perfect_split+1, perfect_split+1, perfect_split]
        elif remainder == 1:
            split = [perfect_split+1, perfect_split, perfect_split]
        else:
            split = [perfect_split]*3
                    
        self.assertSequenceEqual(split, out_belt_levels)