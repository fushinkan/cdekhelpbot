import bcrypt


class Security:
    """Класс с методами защиты в Telegtam-боте."""
    
    @classmethod
    def hashed_password(cls, *, password: str) -> str:
        """
        Метод хэширует пароль, введенный пользователем (admin или user).
        
        Returns:
            str: Хэш в виде строки (utf-8).
        """
        
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


    @classmethod
    def verify_password(cls, *, plain_password: str, hashed_password: str) -> bool:
        """
        Метод сравнивает введенный пароль с его хэшированной версией.
        
        Returns:
            bool: True, если пароли совпадают.
        """
        
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))