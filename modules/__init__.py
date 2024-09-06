

def load_translator(cfg: dict):
    if cfg['type'] == 'openai':
        from .translate.openai_gpt import TranslateOpenAIGPT
        translator = TranslateOpenAIGPT()
        translator.init(cfg)
        return translator
    
    raise("unknown translator")

def load_layout_engine(cfg: dict):
    if cfg['type'] == 'dit':
        from .layout.ditod import DiTLayout
        engine = DiTLayout()
        engine.init(cfg)
        return engine
    
    raise("unknown layout engine")

def load_ocr_engine(cfg: dict):
    if cfg['type'] == 'paddle':
        from .ocr.paddle import PaddleOCR
        engine = PaddleOCR()
        engine.init(cfg)
        return engine
    
    raise("unknown ocr engine")

def load_font_engine(cfg: dict):
    if cfg['type'] == 'simple':
        from .font.simple import SimpleFont
        engine = SimpleFont()
        engine.init(cfg)
        return engine
    
    raise("unknown ocr engine")
