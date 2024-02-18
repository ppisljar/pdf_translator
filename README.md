# PDF Translator

<h5 align="center">
  This repository offers an WebUI and API endpoint that translates PDF files using openai GPT, preserving the original layout.
</h5>

<p align="center">
  <img src="./assets/example.png" width=70%>
</p>

## Features


## Installation

1. **Clone this repository**

```bash
   git clone https://github.com/ppisljar/pdf_translator.git
   cd pdf_translator
```

2. **Edit config.yaml and enter openai api key**

### venv installation

3. **create venv and activte**

```bash
python3 -m venv .
source bin/activate
```

4. **install requirements**

```bash
pip3 install -r requirements.txt
```

5. **run**

```bash
python3 server.py
```


### docker installation

3. **Build the docker image via Makefile**

```bash
   make build
```

4. **Run the docker container via Makefile**

```bash
   make run
```

## GUI Usage

Access to GUI via browser.

```bash
http://localhost:8765
```

## Requirements

- NVIDIA GPU **(currently only support NVIDIA GPU)**
- Docker

## License

**This repository does not allow commercial use.**

This repository is licensed under CC BY-NC 4.0. See [LICENSE](./LICENSE.md) for more information.

## TODOs

- [ ] Make possible to highlight the translated text
- [ ] Support M1 Mac or CPU
- [ ] switch to VGT for layout detection
- [ ] add font detection (family/style/color/size/alignment)
- [ ] add support for translating lists
- [ ] add support for translating tables
- [ ] add support for translating text within images

      
## References

- based on https://github.com/discus0434/pdf-translator

- For PDF layout analysis, using [DiT](https://github.com/microsoft/unilm).

- For PDF to text conversion, using [PaddlePaddle](https://github.com/PaddlePaddle/PaddleOCR) model.

