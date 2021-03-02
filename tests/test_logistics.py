import simpy
from simpy.exceptions import Interrupt
import sys
import logging
import numpy as np

sys.path.append("..")
from SimFactoryPy.simulation import Logistics
from SimFactoryPy.simulation.Loggers import parse_env_time
from base import BaseSimTest


log = logging.getLogger("TestLogger")

def producer(env:simpy.Environment, belt:Logistics.ConveyorBelt):
    while True:
        yield belt.put(env.now)

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