import unittest
from bs4 import BeautifulSoup
import requests
import os
import pprint
import sys
sys.path.append("..")
from SimFactoryPy.entities.wikiScraping import find_recipes


class TestRecipeScrape(unittest.TestCase):

    def load_page_from_file(self, filename) -> BeautifulSoup:
        with open(filename, "rb") as f:
            return BeautifulSoup(f.read(), "html.parser")

    def load_page_from_url(self, url : str, cache_file = True) -> BeautifulSoup:
        html = requests.get(url).content
        if cache_file:
            filename = url.split("/")[-1]
            with open(os.path.join("files", filename), "wb") as f:
                f.write(html)

        return BeautifulSoup(html, "html.parser")

    def test_steel_ingot(self):
        soup = self.load_page_from_file("files/Steel_Ingot.html")
        recipes = find_recipes(soup)
        expected_recipes = {
            "Steel Ingot":{
                "ingredients":{
                    "Iron Ore":3,
                    "Coal":3
                },
                "products":{
                    "Steel Ingot":3
                },
                "building":"Foundry"
            }
        }

        self.assertDictEqual(
            recipes["Steel Ingot"], 
            expected_recipes["Steel Ingot"],
            msg = f"\n{pprint.pformat(recipes['Steel Ingot'])}"
        )