# External
from fuzzywuzzy import fuzz
import re
from transliterate import translit


# Чорний список слів, що мають видалятися
black_list = ['UA patent.', 'Patent UA.', 'Ua patent.', 'Copyright', 'All rights reserved.', 'Copyright.', r'©.*?\.',
              'U.a. Patent.', 'Патент UA.', r'Patent of ukraine /d+', r'Use permitted under.*?\)\.',
              'U.A. Patent.']

# Очистка тексту від слів з ЧС
def clear_garbage(string):
    for i in black_list:
        string = re.sub(i, '', string).strip()

    return string

# Метод токенізації
def tokenize(surname, name):
    try:
        # Пониження реєстру
        name = name.lower()

        # Транслітерація тексту
        if 'і' in name:
            name = translit(name, "uk", reversed=True)
        else:
            name = translit(name, "ru", reversed=True)

        # Видалення зайвих символів
        name = re.sub('[^a-zA-Z\' ]+', ' ', name)
        # Видалення зайвих пробільних символів
        name = re.sub(' +', ' ', name).strip()

        # Організація списку токенів
        tokens = [surname]
        for part in name.split():
            # Додавання до списку унікальних токенів
            if fuzz.ratio(surname.lower(), part) >= 90:
                continue
            i = part[0]
            if i.upper() not in tokens:
                tokens.append(i.upper())

        return tokens
    except Exception as err:
        print(err)

# Побудова імені в формат "Прізвище Ім'я"
def build_name(tokens):
    try:
        name = tokens[0]
        if len(tokens) > 1:
            name = name + ' ' + ''.join(tokens[1:])

        return name
    except Exception as err:
        print(err)

def build_name_in_scopus_form(tokens):
    try:
        name = tokens[0]
        if len(tokens) > 1:
            name = name + ' ' + ' '.join(tokens[1:])

        return name
    except Exception as err:
        print(err)
