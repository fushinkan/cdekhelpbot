class Validator:
    """
    Валидация для бота.
    """
    
    @classmethod
    def validate_password(cls, *, plain_password: str) -> bool:
        """
        Валидация пароля.
        
        Args:
            plain_password (str): Пароль длиной от 8 символов.

        Returns:
            bool: True, если валидация пройдена успешно.
        """
        
        return len(plain_password) >= 8