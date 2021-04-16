import unittest
import json
import os
import sys
sys.path.append("..")
from SimFactoryPy.simulation.entities.entities import Item, Recipe
from fractions import Fraction

class TestEntities(unittest.TestCase):

    def test_item_cache_write(self):
        plastic = Item(name = "Plastic", fluid=False, stack_cap=100, sink_value=0)
        plastic.toCache()

        with open(os.path.join(Item.cache, "Plastic.json"), "r") as f:
            plastic_dict = json.load(f)

        self.assertDictEqual(
            plastic_dict,
            {
                "name":"Plastic",
                "fluid":False,
                "stack_cap":100,
                "sink_value":0.0
            }
        )

    def test_item_cache_read(self):
        plastic = Item(name="Plastic", fluid=False,
                       stack_cap=100, sink_value=0)
        plastic.toCache()

        read_plastic = Item.fromCache("Plastic")

        self.assertEqual(plastic, read_plastic)

    def test_recipe_cache_write(self):
        plastic_item = Item(name = "Plastic", fluid=False, stack_cap=100, sink_value=0)
        plastic = Recipe(name = "Plastic", ingredients=[], products=[plastic_item],
            time_to_make=Fraction(1,1),building = "Manufacturer"
        )
        plastic.toCache()

        with open(os.path.join(Recipe.cache, "Plastic.json"), "r") as f:
            plastic_dict = json.load(f)

        self.assertDictEqual(
            plastic_dict,
            {
                'name': 'Plastic', 
                'ingredients': [], 
                'products': [
                    {'name': 'Plastic', 'fluid': False, 'stack_cap': 100, 'sink_value': 0}
                ],
                'time_to_make': [1, 1], 
                'building': 'Manufacturer'
            }
        )
        

    def test_recipe_cache_read(self):
        plastic_item = Item(name="Plastic", fluid=False,
                            stack_cap=100, sink_value=0)
        plastic = Recipe(name="Plastic", ingredients=[], products=[plastic_item],
                         time_to_make=Fraction(2, 1), building="Manufacturer"
                         )
        plastic.toCache()

        plastic_cache = Recipe.fromCache("Plastic")
        print(repr(plastic_cache))
        self.assertEqual(
            plastic, plastic_cache
        )


        
