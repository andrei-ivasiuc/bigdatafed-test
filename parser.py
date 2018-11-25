import json
from parser.parser import Parser

if __name__ == "__main__":
    with open('schema.json') as f:
        schema = json.load(f)
    p = Parser(schema)
    p.fetch_all()
