from abc import ABC, abstractmethod

class LayoutBase(ABC):
    @abstractmethod
    def init(self, cfg: dict):
        pass


    @abstractmethod
    def get_layout(self, text: str):
        """
        Translates a given string into another language.

        Parameters:
        - text (str): The text to be translated.

        Returns:
        - str: The translated text.

        This method needs to be implemented by subclasses.
        """
        pass
