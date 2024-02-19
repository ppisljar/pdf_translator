

def load_translator(cfg: dict):
    if cfg['type'] == 'openai':
        from .translate.openai_gpt import TranslateOpenAIGPT
        translator = TranslateOpenAIGPT()
        translator.init(cfg)
        return translator
    elif cfg['type'] == 'google_translate':
        from .translate.google_translate import TranslateGoogleTranslate
        translator = TranslateGoogleTranslate()
        translator.init(cfg)
        return translator
    
    raise("unknown translator")