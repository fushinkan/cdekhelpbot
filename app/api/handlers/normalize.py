from bot.utils.exceptions import IncorrectPhone


async def normalize_phone(phone: str) -> str:
    """
    Приводит номер телефона к одному формату.
    """
    phone = phone.strip()
    digits = "".join(ch for ch in phone if ch.isdigit())
    
    if digits.startswith("8") and len(digits) == 11:
        digits= "7" + digits[1:]
    elif digits.startswith("+7") and len(digits) == 12:
        digits = digits[1:]
    elif len(digits) == 10 and digits.startswith("9"):
        digits = "7" + digits
    elif digits.startswith("7") and len(digits) == 11:
        pass
    else:
        raise IncorrectPhone(IncorrectPhone.__doc__)
    
    return digits