  
from datetime import datetime, timezone
from typing import Union

def getDateOnUTC(parsed_value: Union[str, datetime, None]) -> datetime:

    if parsed_value is None:
        return datetime.now(timezone.utc)

    if isinstance(parsed_value, datetime):
        value = parsed_value
    elif isinstance(parsed_value, str):
        value_text = parsed_value.strip()
        if not value_text:
            return datetime.now(timezone.utc)
        if value_text.endswith(("Z", "z")):
            value_text = f"{value_text[:-1]}+00:00"
        value = datetime.fromisoformat(value_text)
    else:
        raise TypeError("parsed_value must be None, a string, or datetime")

    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    print(f"Parsed date: {value} -> UTC: {value.astimezone(timezone.utc)}")
    return value.astimezone(timezone.utc)
