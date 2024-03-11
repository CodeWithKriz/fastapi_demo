from passlib.hash import sha256_crypt
from random import randrange

def hash_password(password):
    return sha256_crypt.hash(str(password))

def verify_password(password, hashed_password):
    return sha256_crypt.verify(password, hashed_password)

def get_random_number():
    return randrange(1000001, 10000000)
