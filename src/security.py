from pwdlib import PasswordHash

pwd_context = PasswordHash.recommended()


def get_password_hash(raw_password: str) -> str:
    return pwd_context.hash(raw_password)


def verify_password(raw_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(raw_password, hashed_password)
