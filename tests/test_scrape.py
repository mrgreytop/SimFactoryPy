import unittest
from unittest.case import expectedFailure
from bs4 import BeautifulSoup
import requests
import os
import pprint
import sys
import json
sys.path.append("..")
from SimFactoryPy.entities.wikiScraping import find_recipes

def nested_dict_sort(d :dict)->dict:
    pass

class TestRecipeScrape(unittest.TestCase):

    def load_page_from_file(self, filename) -> BeautifulSoup:
        with open(filename, "rb") as f:
            return BeautifulSoup(f.read(), "html.parser")

    def load_page_from_url(self, url : str, cache_file = True) -> BeautifulSoup:
        html = requests.get(url).content
        if cache_file:
            filename = url.split("/")[-1]+".html"
            with open(os.path.join("files", filename), "wb") as f:
                f.write(html)
        return BeautifulSoup(html, "html.parser")

    def test_constructor(self):
        soup = self.load_page_from_file("files/Iron_Plate.html")
        recipes = find_recipes(soup)

        with open(os.path.join("files","iron_plate_test.json"), "r") as f:
            expected_recipes = json.load(f)

        self.assertDictEqual(
            recipes, 
            expected_recipes
        )

    def test_assembler(self):
        soup = self.load_page_from_file("files/Steel_Ingot.html")
        recipes = find_recipes(soup)

        with open(os.path.join("files","steel_ing_test.json"), "r") as f:
            expected_recipes = json.load(f)

        self.assertDictEqual(
            recipes, 
            expected_recipes
        )

    def test_manufacturer(self):
        soup = self.load_page_from_file("files/Computer.html")

        recipes = find_recipes(soup)

        with open(os.path.join("files","computer_test.json"), "r") as f:
            expected_recipes = json.load(f)

        self.assertDictEqual(
            recipes,
            expected_recipes
        )

    def test_refinery(self):
        soup = self.load_page_from_file("files/Plastic.html")

        recipes = find_recipes(soup)

        with open(os.path.join("files", "plastic_test.json"), "r") as f:
            expected_recipes = json.load(f)

        self.assertDictEqual(
            recipes,
            expected_recipes
        )
        
    def test_blender(self):
        
        soup = self.load_page_from_url("https://satisfactory.fandom.com/wiki/Battery")

        recipes = find_recipes(soup)

        with open(os.path.join("files", "battery_test.json"), "r") as f:
            expected_recipes = json.load(f)

        self.assertDictEqual(
            recipes,
            expected_recipes
        )


