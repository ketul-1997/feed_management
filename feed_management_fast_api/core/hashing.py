from passlib.context import CryptContext

context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Hasher:
    @staticmethod
    def password_verification(plain_password, hashed_password):
        return context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash_value(password):
        return context.hash(password)
