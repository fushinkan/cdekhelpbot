import bcrypt

def hashed_password(password: str) -> str:
    """
    Функция хэширует пароль.
    
    Returns:
        str: Хэш в виде строки (utf-8).
    """
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Функция сравнивает введенный пароль с его хэшированной версией.
    
    Returns:
        bool: True, если пароли совпадают.
    """
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))