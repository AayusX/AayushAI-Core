# utils/encryption.py
import os
from cryptography.fernet import Fernet

def generate_key(key_file):
    if not os.path.exists(key_file):
        key = Fernet.generate_key()
        with open(key_file, "wb") as f:
            f.write(key)
    else:
        with open(key_file, "rb") as f:
            key = f.read()
    return Fernet(key)

def set_password(pass_file, key_file):
    fernet = generate_key(key_file)
    while True:
        p1 = input("New Password: ")
        p2 = input("Confirm Password: ")
        if p1 == p2:
            enc = fernet.encrypt(p1.encode())
            with open(pass_file, "wb") as f:
                f.write(enc)
            print("Password saved successfully.")
            return True
        else:
            print("Passwords do not match. Try again.")

def verify_password(pass_file, key_file):
    fernet = generate_key(key_file)
    with open(pass_file, "rb") as f:
        encrypted = f.read()
    stored = fernet.decrypt(encrypted).decode()
    attempts = 3
    while attempts > 0:
        entered = input("Enter Password: ")
        if entered == stored:
            print("Access granted.")
            return True
        else:
            attempts -= 1
            print(f"Incorrect password. Attempts left: {attempts}")
    return False
