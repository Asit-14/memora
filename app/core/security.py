from  passlib.context import CryptContext

pwd_context =  CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    # print("TYPE:", type(password))
    # print("VALUE:", password)
    # print("LENGTH:", len(password))

    if len(password) > 72:
        raise ValueError("Password too long (max 72 chars)")

    return pwd_context.hash(password)

def  verify_password(plain_password : str , hashed_password : str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
