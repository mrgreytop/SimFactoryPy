from bs4 import BeautifulSoup
import bs4


def parse_ingredient_cell(cell : bs4.Tag) -> tuple:
    if str(cell.string) == u"\u00A0":
        return None
    
    ing_contents = cell.contents[0].div.contents
    
    amount = int(
        str(ing_contents[0].string)
        .split(" ")[0]
    )
    name = str(ing_contents[-1].string)

    return name, amount


def find_recipes(soup: BeautifulSoup) -> dict:
    table : bs4.PageElement = soup.find("table", class_ = "wikitable")
    recipe_rows = table.tbody.children
    # consume title row
    next(recipe_rows)
    

    recipes = {}

    recipe_name = ""
    ingredients = {}
    building = ""
    products = {}
    ing_only_row = False
    num_ingredients = None

    while True:
        # get the next row
        try:
            row = next(recipe_rows)
        except StopIteration:
            break

        tr = row.contents

        # rows with rowspan == 2 will have ingredient only rows
        if ing_only_row:
            print("ingredient only row")
            for cell in tr:
                ingredient = parse_ingredient_cell(cell)
                if ingredient:
                    name, amount = ingredient
                    ingredients[name] = amount

            recipes[recipe_name] = {
                "ingredients":ingredients,
                "products":products,
                "building":building
            }

            recipe_name = ""
            ingredients = {}
            products = {}
            building = ""
            ing_only_row = False
            continue

        # 1st column for name
        recipe_name = tr[0].contents[0]
        print("recipe name", recipe_name)

        # rest of columns depend on number of ingredients
        rowspan = int(tr[0]["rowspan"])
        colspan = int(tr[1]["colspan"])
        num_ingredients = (
            1 if colspan == 12 else 
            2 if colspan == 6 and rowspan == 1 else
            4
        )
        print("num ingredients", num_ingredients)

        
        # building name
        building = str(tr[2 if num_ingredients < 2 else 3].span.a.string)
        print("building name", building)

        # product columns use all but the last rows
        for cell in tr[3 if num_ingredients < 2 else 4:-1]:
            product = parse_ingredient_cell(cell)
            if product:
                name, amount = product
                products[name] = amount

        # if 2 or less then only 1 row for ingredients
        # so we assign the recipe and process the next row as 
        # a new recipe
        if num_ingredients < 4:
            for cell in tr[1:1+num_ingredients]:
                ingredient = parse_ingredient_cell(cell)
                if ingredient:
                    name, amount = ingredient
                    ingredients[name] = amount

            recipes[recipe_name] = {
                "ingredients":ingredients,
                "products":products,
                "building":building
            }

            recipe_name = ""
            ingredients = {}
            products = {}
            building = ""
        # else there are two ingredient rows so we process
        # the next row as ingredients for the same recipe (top of loop)
        else:
            for cell in tr[1:3]:
                ingredient = parse_ingredient_cell(cell)
                if ingredient:
                    name, amount = ingredient
                    ingredients[name] = amount
            ing_only_row = True
            
    return recipes
            




    


    
