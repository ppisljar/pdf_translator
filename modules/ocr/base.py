from abc import ABC, abstractmethod

class OCRBase(ABC):
    @abstractmethod
    def init(self, cfg: dict):
        pass


    @abstractmethod
    def get_text(self, image):
        """
        Translates a given string into another language.

        Parameters:
        - text (str): The text to be translated.

        Returns:
        - str: The translated text.

        This method needs to be implemented by subclasses.
        """
        pass


    @abstractmethod
    def get_all_text(self, layout):
        """
        Translates a given string into another language.

        Parameters:
        - text (str): The text to be translated.

        Returns:
        - str: The translated text.

        This method needs to be implemented by subclasses.
        """
        pass

