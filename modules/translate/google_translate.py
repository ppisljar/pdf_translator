from .base import TranslateBase 
from googletrans import Translator, LANGUAGES

language_codes = []
languages = []

# Iterate over the LANGUAGES dictionary
for code, name in LANGUAGES.items():
    language_codes.append(code)  # Append the code to the language_codes list
    languages.append(name)  # Append the name to the languages list



class TranslateGoogleTranslate(TranslateBase):
    def init(self, cfg: dict):
        self.client = Translator()

    def get_languages(self):
        
        return  language_codes

    def translate(self, text: str, from_lang='en', to_lang='sl') -> str:
        print(f"translating {text} from {from_lang} to {to_lang}")
        trans = self.client.translate(text, src=from_lang, dest=to_lang)
        print(trans)
        return trans.text