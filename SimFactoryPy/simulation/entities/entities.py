from dataclasses import dataclass

@dataclass
class Recipe():
    name : str
    ingredients : dict
    products : dict
    base_rate : float
    building : str

@dataclass
class Item():
    name : str
    stack_cap : int

    def __repr__(self):
        return f"Item({self.name}, {self.stack_cap})"

    def __str__(self):
        return self.name

class CompoundResource():

    def __init__(self, name, recipes : list[Recipe]):
        self.name =  name
        self.recipes = recipes

    

