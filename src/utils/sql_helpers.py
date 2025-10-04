import json

def sql_value_string(value):
    """Convert a Python value to a SQL literal string"""
    if value is None:
        return "NULL"
    elif isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    elif isinstance(value, (int, float)):
        return str(value)
    elif isinstance(value, list):
        if len(value) == 0:
            return "'{}'"
        if all(isinstance(el, dict) for el in value):
            return "'" + json.dumps(value).replace("'", "''") + "'::jsonb"
        elems = []
        for el in value:
            if isinstance(el, (int, float)):
                elems.append(str(el))
            else:
                safe = str(el).replace("'", "''").replace('"', '\\"')
                elems.append(f'"{safe}"')
        return "'{" + ",".join(elems) + "}'"
    elif isinstance(value, dict):
        return "'" + json.dumps(value).replace("'", "''") + "'::jsonb"
    else:
        return "'" + str(value).replace("'", "''") + "'"
