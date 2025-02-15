import re

def validate_identity(identity_type: str, number: str) -> bool:
    if identity_type == "nid":
        return bool(re.match(r'^(\d{10}|\d{17})$', number))
    elif identity_type == "brn":
        return bool(re.match(r'^\d{17}$', number))  # Adjust regex as per BRN format
    elif identity_type == "passport":
        return bool(re.match(r'^[A-Z]{2}\d{7}$', number))  # Adjust for BD passport format
    return False 