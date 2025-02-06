def format_range(input_str: str) -> str:
    if "-" in input_str:
        parts = input_str.split("-")

        if len(parts) == 2 and parts[1] == "": 
            return f"{parts[0]}"
        return f"within {parts[0]} to {parts[1]}" 

    return input_str 

