import pytest
from jose.exceptions import JWTError, ExpiredSignatureError

from app.api.utils.security import Security

from datetime import datetime, timedelta, timezone

class TestSecurity:
    def test_hashed_password(cls):
        password = "secretpassword123"
        hashed = Security.hashed_password(password=password)
        
        assert hashed is not None
        assert isinstance(hashed, str)
        
        assert hashed != password
        
        assert Security.verify_password(hashed_password=hashed, plain_password=password) is True
        
        assert Security.verify_password(hashed_password=hashed, plain_password="wrongpassword") is False
    
    @pytest.mark.asyncio
    async def test_jwt(cls):
        payload = {"sub": "123", "telegram_name": "testuser", "telegram_id": 123, "role": "user"}
        
        token = await Security.encode_jwt(payload=payload)
        
        assert token is not None
        assert isinstance(token, str)
        
        decoded = await Security.decode_jwt(access_token=token)
    
        assert decoded is not None
        assert decoded["sub"] == "123"
        assert decoded["telegram_id"] == 123
        
        expired_payload = payload.copy()
        expired_payload["exp"] = datetime.now(tz=timezone.utc) - timedelta(minutes=10)
        expired_token = await Security.encode_jwt(payload=expired_payload)
        
        with pytest.raises(ExpiredSignatureError):
            await Security.decode_jwt(access_token=expired_token)
            
        with pytest.raises(JWTError):
            await Security.decode_jwt(access_token="invalid_token")