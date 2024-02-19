from .base import TranslateBase 
from googletrans import Translator, LANGUAGES


class TranslateOpenAIGPT(TranslateBase):
    def init(self, cfg: dict):
        self.client = Translator()

    def get_languages():
        return  LANGUAGES

    def translate(self, text: str, from_lang='en', to_lang='sl') -> str:
        return self.client.translate(text, src=from_lang, dst=to_lang)