import re

class Validator:
    """
    Валидация данных в Telegram-боте.
    """

    @classmethod
    def validate_password(cls, *, plain_password: str) -> bool:
        """
        Валидация сложности пароля.

        Пароль должен содержать:
        - минимум 8 символов
        - хотя бы одну заглавную букву
        - хотя бы одну строчную букву
        - хотя бы одну цифру

        Args:
            plain_password (str): Введённый пароль.

        Returns:
            bool: True, если пароль соответствует всем требованиям.
        """

        if len(plain_password) < 8:
            return False
        if not re.search(r"[A-Z]", plain_password):
            return False
        if not re.search(r"[a-z]", plain_password):
            return False
        if not re.search(r"[0-9]", plain_password):
            return False
        
        return True
