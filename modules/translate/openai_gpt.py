from .base import TranslateBase 
from openai import OpenAI

def system_prompt(from_lang, to_lang):
    p  = "You are an %s-to-%s translator. " % (from_lang, to_lang)
    p += "Keep all special characters and HTML tags as in the source text. Return only %s translation." % to_lang
    return p

langs = [
    "Albanian",
    "Arabic",
    "Armenian",
    "Awadhi",
    "Azerbaijani",
    "Bashkir",
    "Basque",
    "Belarusian",
    "Bengali",
    "Bhojpuri",
    "Bosnian",
    "Brazilian Portuguese",
    "Bulgarian",
    "Cantonese (Yue)",
    "Catalan",
    "Chhattisgarhi",
    "Chinese",
    "Croatian",
    "Czech",
    "Danish",
    "Dogri",
    "Dutch",
    "English",
    "Estonian",
    "Faroese",
    "Finnish",
    "French",
    "Galician",
    "Georgian",
    "German",
    "Greek",
    "Gujarati",
    "Haryanvi",
    "Hindi",
    "Hungarian",
    "Indonesian",
    "Irish",
    "Italian",
    "Japanese",
    "Javanese",
    "Kannada",
    "Kashmiri",
    "Kazakh",
    "Konkani",
    "Korean",
    "Kyrgyz",
    "Latvian",
    "Lithuanian",
    "Macedonian",
    "Maithili",
    "Malay",
    "Maltese",
    "Mandarin",
    "Mandarin Chinese",
    "Marathi",
    "Marwari",
    "Min Nan",
    "Moldovan",
    "Mongolian",
    "Montenegrin",
    "Nepali",
    "Norwegian",
    "Oriya",
    "Pashto",
    "Persian (Farsi)",
    "Polish",
    "Portuguese",
    "Punjabi",
    "Rajasthani",
    "Romanian",
    "Russian",
    "Sanskrit",
    "Santali",
    "Serbian",
    "Sindhi",
    "Sinhala",
    "Slovak",
    "Slovene",
    "Slovenian",
    "Ukrainian",
    "Urdu",
    "Uzbek",
    "Vietnamese",
    "Welsh",
    "Wu"
]

class TranslateOpenAIGPT(TranslateBase):
    def init(self, cfg: dict):
        self.client = OpenAI(api_key=cfg['openai_api_key'])

    def get_languages():
        return langs

    def translate(self, text: str, from_lang='ENGLISH', to_lang='SLOVENIAN') -> str:
        response = self.client.chat.completions.create(
            model='gpt-4-1106-preview',
            temperature=0.2,
            messages=[
                { 'role': 'system', 'content': system_prompt(from_lang, to_lang) },
                { 'role': 'user', 'content': text },
            ]
        )

        translated_text = response.choices[0].message.content
        return translated_text