from bot.utils.exceptions import IncorrectPhoneException


class Normalize:
    """Класс с различными методами нормализации ввода."""
    
    @classmethod
    async def normalize_phone(cls, *, phone: str) -> str:
        """
        Приводит номер телефона к одному формату.

        Args:
            phone (str): Номер телефона, который вводит пользователь/админ.

        Raises:
            IncorrectPhoneException: Кастомный класс с ошибкой.

        Returns:
            str: Номер телефона в формате 7ХХХХХХХХХХ.
        """
        
        phone = phone.strip()
        
        digits = "".join(ch for ch in phone if ch.isdigit())
        
        if digits.startswith("8") and len(digits) == 11:
            digits= "7" + digits[1:]
            
        elif len(digits) == 10 and digits.startswith("9"):
            digits = "7" + digits
            
        elif digits.startswith("7") and len(digits) == 11:
            pass
        
        else:
            raise IncorrectPhoneException(IncorrectPhoneException.__doc__)
        
        return digits