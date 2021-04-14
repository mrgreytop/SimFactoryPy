from dataclasses import dataclass
from fractions import Fraction

@dataclass
class Item():
    name : str
    stack_cap : int
    sink_value : int

    def __repr__(self):
        return f"Item({self.name}, stack:{self.stack_cap}, sink:{self.sink_value})"

    def __str__(self):
        return self.name


@dataclass
class Recipe():
    name : str
    ingredients : dict[Item, Fraction]
    products : dict[Item, Fraction]
    base_rate : float
    building : str

    def __str__(self):
        return self.name



    

