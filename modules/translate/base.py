from abc import ABC, abstractmethod

class TranslateBase(ABC):
    @abstractmethod
    def init(self, cfg: dict):
        pass

    @abstractmethod
    def get_languages(self):
        pass

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
