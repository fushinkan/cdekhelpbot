import bcrypt
from jose import jwt

from app.core.config import settings


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
    
    
    @classmethod
    async def encode_jwt(
        cls, 
        *, 
        payload: dict, 
        private_key: str = settings.jwt_settings.private_key_path.read_text(), 
        algorithm: str = settings.jwt_settings.algorithm
        ):
        
        """
        Создает access_token.

        Args:
            payload (dict): Данные для кодирования.
            key (str): Приватный ключ для подписи токена.
            algorithm (str): Алгоритм шифрования по умолчанию взят из настроек.

        Returns:
            _type_: _description_
        """
    
        return jwt.encode(payload, key=private_key, algorithm=algorithm)
    
    
    @classmethod
    async def decode_jwt(
        cls, 
        *, 
        access_token: str | bytes, 
        public_key: str = settings.jwt_settings.public_key_path.read_text(),
        algorithm: str = settings.jwt_settings.algorithm
        ):
        
        """
        Расшифровывает токен
        
        Args:
            access_token (str): Access Token созданный для пользователя.
            public_key (str): Публичный ключ для подписи токена.
            algorithm (str): Алгоритм шифрования по умолчанию взят из настроек.

        Returns:
            _type_: _description_
        """
        
        return jwt.decode(token=access_token, key=public_key, algorithms=[algorithm])