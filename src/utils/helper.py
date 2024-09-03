import json

def getConfig() -> dict:
    with open("config.json", 'r', encoding='utf-8') as file:
        configDict = json.load(file)
    return configDict

def getLanguage(languagePath) -> dict:
    with open(languagePath, 'r', encoding='utf-8') as file:
        langDict = json.load(file)
    return langDict