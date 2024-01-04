# External
import hashlib
import random
import re


class UserManager:
    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    regex = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')

    # Метод отримання хешу від тексту
    def get_hash(self, plain_text):
        return hashlib.md5(plain_text.encode('utf-8')).hexdigest()

    # Метод генерації паролю
    def randomize_password(self):
        return ''.join([self.chars[random.randint(0, len(self.chars) - 1)] for i in range(random.randint(5, 15))])

    # Метод валідації емейлу
    def is_email_valid(self, email):
        if re.fullmatch(self.regex, email):
            return True
        else:
            return False

    # Метод валідації паролю
    def validate(self, user, password):
        return user.password == self.get_hash(password)
