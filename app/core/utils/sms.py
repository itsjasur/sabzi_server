from fastapi import HTTPException
from fastapi import status


def send_sms(phone_number: str, verification_code: str) -> bool:
    try:
        return True

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Sms sending error",
        ) from e
