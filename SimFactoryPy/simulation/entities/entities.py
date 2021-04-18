from __future__ import annotations
from dataclasses import dataclass, asdict
import json
from fractions import Fraction
from typing import ClassVar
import os


def get_entity_from_cache(name: str, cache: str)->dict:
    entity_files = os.listdir(cache)
    entity_file = None
    for f in entity_files:
        if f == name+".json":
            entity_file = os.path.join(cache, f)
            break

    if entity_file == None:
        raise FileNotFoundError(f"Could not find entity '{name}' from cache")

    with open(entity_file, "r") as f:
        return json.load(f)


@dataclass(frozen = True)
class Item():
    name : str
    fluid : bool = False
    stack_cap : int = None
    sink_value : float = None
    cache : ClassVar[str] = os.path.join(os.path.dirname(__file__), "entity_cache/items")

    @classmethod
    def fromCache(cls, name)->Item:
        item_dict = get_entity_from_cache(name, cls.cache)
        return Item(**item_dict)
        

    def toCache(self):
        with open(os.path.join(self.cache, self.name + ".json"), "w") as f:
            json.dump(asdict(self),f)

    def __str__(self):
        return self.name


@dataclass(frozen=True)
class Recipe():
    name : str
    ingredients : list[tuple[Item, int]]
    products : list[tuple[Item, int]]
    time_to_make : Fraction
    building : str
    cache : ClassVar[str] = os.path.join(os.path.dirname(__file__),"entity_cache/recipes")

    def __str__(self):
        return self.name

    def toCache(self):
        with open(os.path.join(self.cache, self.name + ".json"), "w") as f:
            self_dict = asdict(self)
            self_dict["time_to_make"] = (
                self_dict["time_to_make"].numerator, 
                self_dict["time_to_make"].denominator
            )
            json.dump(self_dict, f)

    @classmethod
    def fromCache(cls, name) -> Recipe:
        recipe_dict = get_entity_from_cache(name, cls.cache)
        recipe_dict["time_to_make"] = Fraction(
            recipe_dict["time_to_make"][0],
            recipe_dict["time_to_make"][1]
        )
        recipe_dict["ingredients"] = [
            Item(**item) for item in recipe_dict["ingredients"]
        ]
        recipe_dict["products"] = [
            Item(**item) for item in recipe_dict["products"]
        ]
        return Recipe(**recipe_dict)

    

