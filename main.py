from datetime import datetime
from smolagents import OpenAIServerModel, ToolCallingAgent, tool
import dotenv
import os
import requests
import urllib.parse
import sqlite3


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


conn = sqlite3.connect("tapster.db")
conn.row_factory = dict_factory
cursor = conn.cursor()


def sanitize_cocktail_name(name: str) -> str:
    return name.replace(' ', '_').lower()


def get_cocktail_id(name: str) -> int | None:
    name = sanitize_cocktail_name(name)
    res = cursor.execute(
        "select cocktail_id from cocktails where name like ? limit 1", ['%' + name + '%'])
    row: dict[str, int] | None = res.fetchone()

    if row is None:
        return None

    return row["cocktail_id"]


def fetch_cocktail_instructions(id: int) -> str:
    res = cursor.execute(
        "select instructions from cocktails where cocktail_id = ?", [str(id)])
    row: dict[str, str] | None = res.fetchone()
    if row is None:
        raise Exception("no such cocktail")

    return row["instructions"]


def insert_cocktail(name: str, instructions: str):
    cursor.execute("insert into cocktails (name, instructions, created_at) values (?,?,?)",
                   [sanitize_cocktail_name(name), instructions, str(datetime.now())])
    conn.commit()


def search_cocktail(name: str) -> str:
    name = urllib.parse.quote(name.lower())
    url = "https://www.thecocktaildb.com/api/json/v1/1/search.php?s=" + name
    response = requests.get(url)
    response.raise_for_status()
    body: dict[str, list[dict[str, str]]] = response.json()
    drinks = body["drinks"]

    if len(drinks) < 1:
        raise Exception(f"{name} recipe not found")

    cocktail = drinks[0]

    instructions = cocktail["strInstructions"]
    ingredients: list[str] = []
    index = 1
    while True:
        ingredient = cocktail["strIngredient" + str(index)]
        if ingredient is None:
            break
        ingredient = ingredient.strip()

        measure = cocktail["strMeasure" + str(index)]
        if measure is not None:
            ingredient += f" ({measure.strip()})"

        ingredients.append(ingredient)
        index += 1
    ingredientsStr = "- " + "\r\n- ".join(ingredients) + "\r\n"

    content = f"# Ingredients\r\n\r\n{ingredientsStr}\r\n# Instructions\r\n\r\n{instructions}"

    return content


def convert_quantity_to_ounce(quantity: str) -> float:
    [value, unit] = quantity.split(" ")
    if unit in ["oz", "ounce", "ounces"]:
        value = float(value)
    elif unit in ["dash", "dashes"]:
        value = 0.125 * float(value)
    elif unit in ["barspoon", "barspoons"]:
        value = 0.25 * float(value)
    elif unit in ["tsp", "teaspoon", "teaspoons"]:
        value = float(value) / 6
    else:
        # assume it's a garnish or too small an amount to calculate
        value = 0.0

    return value


def get_ingredient_calories(ingredient: dict[str, str]) -> int:
    name = ingredient["name"].lower()
    quantity = ingredient["quantity"].lower()

    if name is None or name == "":
        raise Exception("invalid name")

    if quantity is None or quantity == "":
        raise Exception("invalid quantity")

    value = convert_quantity_to_ounce(quantity)

    for spirit in ["bourbon", "gin", "rum", "tequila", "vodka", "whiskey"]:
        if spirit in name:
            return round(value * 65)

    for syrup in ["syrup", "grenadine", "orgeat"]:
        if syrup in name:
            return round(value * 50)

    if "bitters" in name:
        return round(value * 10)

    if "sugar" in name:
        return round(value * 110)

    return 0


def get_ingredient_alcohol_content(ingredient: dict[str, str]) -> float:
    name = ingredient["name"].lower()
    quantity = ingredient["quantity"].lower()

    value = convert_quantity_to_ounce(quantity)

    lookup = {
        "bourbon": 0.4,
        "chartreuse": 0.5,
        "falernum": 0.15,
        "gin": 0.4,
        "maraschino": 0.3,
        "rum": 0.4,
        "tequila": 0.4,
        "vodka": 0.4,
        "whiskey": 0.4,
    }

    for key, content in lookup.items():
        if key in name:
            return value * content

    return 0.0


@tool
def get_cocktail(name: str) -> str:
    """
    Retrieve a cocktail recipe in markdown format.

    Args:
        name: The cocktail name.

    Returns:
        Markdown string of the cocktail recipe, or an error message if a cocktail can't be found.
    """
    cocktail_id = get_cocktail_id(name)
    if cocktail_id is not None:
        instructions = fetch_cocktail_instructions(cocktail_id)
        return instructions

    try:
        instructions = search_cocktail(name)
        return instructions
    except requests.RequestException as e:
        return f"Error getting webpage: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"


@tool
def save_cocktail(name: str, instructions: str) -> str:
    """
    Saves a cocktail recipe for later use.

    Args:
        name: The cocktail name.
        instructions: Markdown recipe for the cocktail.

    Returns:
        An empty string, or an error message if the cocktail couldn't be saved.
    """
    try:
        insert_cocktail(name, instructions)
        return ""
    except Exception as e:
        return f"Error saving cocktail: {str(e)}"


@tool
def validate_cocktail_recipe(recipe: str) -> bool:
    """
    Determines whether the given cocktail recipe is safe for human consumption.

    Args:
        recipe: Markdown recipe for a cocktail.

    Returns:
        True if the recipe is safe, False otherwise
    """
    # Is this good? No. Does it work? Yes.
    recipe = recipe.lower()
    poisons = ["acetaminophen", "acetone", "advil", "alavert", "amaryllis", "amphetamines", "antifreeze", "aquaphor", "arsenic", "benzocaine", "benzodiazepines", "bleach", "buprenorphine (suboxone)", "carbon monoxide", "cetirizine", "chlorine", "cimetidine", "dandelions", "diethyltoluamide", "desitin", "dextromethorphan", "diphenhydramine", "domoic acid", "ex-lax", "famotidine", "fentanyl", "fluoride", "guaifenesin", "guanfacine", "intuniv", "ipecac",
               "kratom", "laundry pods", "lead", "liquid nicotine", "loratadine", "magnets", "marker ink", "mdma", "mercury", "methamphetamine", "mold", "motrin", "mucinex", "mushrooms", "nicotine", "nizatidine", "opioids", "pepcid", "poinsettia", "poison ivy", "pseudoephedrine", "radon", "ranitidine", "salmonella", "saxitoxin", "senakot", "senna", "sodium hypochlorite", "spice", "stimulants", "suboxone", "synthetic cathinones", "tagamet", "tenex", "veratrum viride", "zantac", "zyrtec"]
    for poison in poisons:
        if poison in recipe:
            return False
    return True


@tool
def calculate_calories(ingredients: list[dict[str, str]]) -> int | str:
    """
    Calculates the total calorie count for a set of ingredients.

    Args:
        ingredients: A list of objects with a `name` string and `quantity` string. E.g. `[{"name": "vodka", "quantity": "1 oz"}]`

    Returns:
        An integer representing the total calorie count for the given ingredients, or an error message if unsuccessful
    """
    try:
        calories = 0
        for ingredient in ingredients:
            calories += get_ingredient_calories(ingredient)
        return calories
    except Exception as e:
        return f"Error calculating calories: {str(e)}"


@tool
def calculate_abv(ingredients: list[dict[str, str]]) -> float | str:
    """
    Calculates the alcohol by volume (ABV) for a set of ingredients.

    Args:
        ingredients: A list of objects with a `name` string and `quantity` string. E.g. `[{"name": "vodka", "quantity": "1 oz"}]`

    Returns:
        A float representing the ABV for the given ingredients, or an error message if unsuccessful
    """
    try:
        total_size = 0.0
        alcohol_content = 0.0
        for ingredient in ingredients:
            quantity = ingredient["quantity"]
            if quantity is None or quantity == "":
                return "Error calculation ABV: invalid quantity value"

            total_size += convert_quantity_to_ounce(quantity)
            alcohol_content += get_ingredient_alcohol_content(ingredient)

        return alcohol_content / total_size
    except Exception as e:
        return f"Error calculation ABV: {str(e)}"


def main():
    dotenv.load_dotenv()

    cursor.execute("""
    create table if not exists cocktails (
        cocktail_id integer primary key,
        name text unique not null,
        instructions text not null,
        created_at datetime default current_timestamp
    );
    """)

    model_id = "gemini-2.5-flash"
    model = OpenAIServerModel(
        model_id=model_id,
        api_base="https://generativelanguage.googleapis.com/v1beta/openai/",
        api_key=os.getenv("GEMINI_API_KEY"),
    )

    agent = ToolCallingAgent(
        tools=[get_cocktail, save_cocktail, validate_cocktail_recipe,
               calculate_calories, calculate_abv],
        model=model,
        max_steps=10,
        name="cocktail_agent",
        description="An agent to find, save, and validate cocktail recipes.",
    )

    while True:
        prompt = input("Ask Tapster a question: ")
        answer = agent.run(prompt.strip())
        print(f"Agent returned: {answer}")


if __name__ == "__main__":
    main()
    cursor.close()
    conn.close()
