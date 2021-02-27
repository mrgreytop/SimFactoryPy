import unittest
import simpy
import sys
import numpy as np

sys.path.append("..")
from SimFactoryPy.simulation import Logistics
from SimFactoryPy.simulation.Loggers import SimLoggerAdapter, parse_env_time
import logging



def producer(env:simpy.Environment, 
    belt:Logistics.ConveyorBelt, log):
    while True:
        yield env.process(belt.put(("ore", env.now)))

def receiver(env:simpy.Environment,
    belt:Logistics.ConveyorBelt, log):
    while True:
        item, t = yield env.process(belt.get())
        log.info(f"Received '{item}' from conveyor. Sent at :{t*60:.3f}")
    
    

class TestConveyorBelt(unittest.TestCase):

    def setUp(self) -> None:
        self.env = simpy.Environment()
        self.log = logging.getLogger("SimFactory")
        self.sim_log = SimLoggerAdapter(self.log, {"env":self.env})
        
        return super().setUp()

    def test_put_speed(self):
        belt_speed = 120
        run_time = 0.5
        belt = Logistics.ConveyorBelt(
            self.env, 1, belt_speed
        )
        self.env.process(
            producer(self.env, belt, self.sim_log)
        )
        self.env.process(
            receiver(self.env, belt, self.sim_log)
        )
        with self.assertLogs("SimFactory") as cm:
            self.env.run(run_time)

        # there must be less than *belt_speed* records per minute
        self.assertLess(len(cm.records)/run_time, belt_speed)

        def parse_sent_time(message):
            return float(message.split(":")[-1])

        sent_times = np.array(
            [parse_sent_time(r.message) for r in cm.records]
        )
        step_diff = np.diff(sent_times, n = 1)
        
        # the time between messages must
        # be more than the *belt.period*
        self.assertTrue(
            all(step_diff >= (1/belt_speed))
        )

    def test_get_speed(self):
        belt_speed = 120
        run_time = 1
        belt = Logistics.ConveyorBelt(
            self.env, 100, belt_speed
        )
        belt.store.items = [("ore",0) for _ in range(belt.store.capacity)]
        
        self.env.process(
            receiver(self.env, belt ,self.sim_log)
        )

        with self.assertLogs("SimFactory") as cm:
            self.env.run(run_time)

        # there must be less than *belt_speed* records per minute
        self.assertLess(len(cm.records)/run_time, belt_speed)

        recieve_times = np.array(
            [parse_env_time(r.message) for r in cm.records]
        )
        step_diff = np.diff(recieve_times, n = 1)
        
        # the time between messages must
        # be more than the 1/belt_speed
        self.assertTrue(
            all(step_diff >= (1/belt_speed))
        )

