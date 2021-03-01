import unittest
import simpy
import logging
import sys
sys.path.append("..")
from SimFactoryPy.simulation.Loggers import SimLoggerAdapter

# Number of decimal places of time accuracy
DP = 3

class BaseSimTest(unittest.TestCase):

    def setUp(self) -> None:
        self.env = simpy.Environment()
        self.log = logging.getLogger("SimFactory")
        self.sim_log = SimLoggerAdapter(self.log, {"env":self.env})
        
        return super().setUp()