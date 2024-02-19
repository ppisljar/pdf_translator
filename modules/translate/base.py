from abc import ABC, abstractmethod

class TranslateBase(ABC):
    @abstractmethod
    def init(self, cfg: dict):
        pass

    @abstractmethod
    def get_languages(self):
        pass

    def translate_all(self, layout, from_lang, to_lang):
        for line in layout:
            if line.text:
                line.translated_text = self.translate(line.text, from_lang, to_lang)

        return layout

    @abstractmethod
    def translate(self, text: str) -> str:
        """
        Translates a given string into another language.

        Parameters:
        - text (str): The text to be translated.

        Returns:
        - str: The translated text.

        This method needs to be implemented by subclasses.
        """
        pass
