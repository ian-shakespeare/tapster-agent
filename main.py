from datetime import datetime
from smolagents import CodeAgent, OpenAIServerModel, Tool
from sqlalchemy import (Column, DateTime, Integer, MetaData, String,
                        Table, create_engine, insert)
import dotenv
import os


engine = create_engine("sqlite:///tapster.db")
metadata_obj = MetaData()


def insert_rows_into_table(rows, table, engine=engine):
    for row in rows:
        stmt = insert(table).values(**row)
        with engine.begin() as connection:
            connection.execute(stmt)


recipes = Table(
    "recipes",
    metadata_obj,
    Column("recipe_id", Integer, primary_key=True),
    Column("name", String(64), nullable=False, unique=True),
    Column("instructions", String(5000), nullable=False),
    Column("created_at", DateTime, nullable=False, default=datetime.now)
)

metadata_obj.create_all(engine)


class SQLEngine(Tool):
    pass


class Calculator(Tool):
    name = "calculator"
    description = (
        "Computes the result of a mathematical expression."
        "The expression must be valid Python 3 syntax."
    )
    inputs: dict = {
        "expressions": {
            "type": "string",
            "description": "The Python expression to evaluate.",
        }
    }
    output_type = "string"

    def forward(self, expressions: str) -> str:
        """
        Evaluates the mathematical python expression and returns the result.

        Args:
            expression: The python mathematical expression.

        Returns:
            The numerical result of evaluating the expression.
        """
        return str(eval(expressions))


def main():
    dotenv.load_dotenv()

    tool = Calculator()
    tools: list[Tool] = [tool]
    additional_authorized_imports = []

    model_id = "gemini-2.5-flash"
    model = OpenAIServerModel(
        model_id=model_id,
        api_base="https://generativelanguage.googleapis.com/v1beta/openai/",
        api_key=os.getenv("GEMINI_API_KEY"),
    )
    agent = CodeAgent(
        tools=tools,
        model=model,
        additional_authorized_imports=additional_authorized_imports,
        max_steps=3,
    )

    while True:
        prompt = input("Enter a math problem: ")
        answer = agent.run(prompt.strip())
        print(f"Agent returned: {answer}")


if __name__ == "__main__":
    main()
