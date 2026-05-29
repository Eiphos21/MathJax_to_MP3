# MathJax to MP3

Converts MathJax-rendered maths webpages into accessible MP3 audio files.

Built as part of an accessibility project for [STARMAST](https://starmast.org).

## What does it do?

1. Opens a MathJax webpage using a headless Chrome browser
2. Extracts all maths equations and converts them to spoken language using the Speech Rule Engine
3. Extracts the readable text content from the page
4. Combines them into a clean text script
5. Converts the script to an MP3 using Google Text-to-Speech

## Requirements

- Python 3
- Google Chrome
- Node.js

## Usage

Open `mathjax_to_audio.py` and update the configuration block at the top:

```python
URL          = "http://your-webpage-here"
START_MARKER = "Your page title"
END_MARKER   = "Further reading"
OUTPUT_FILE  = "output"
```

Then run:
```bash
python mathjax_to_audio.py
```

This will produce `output.txt` and `output.mp3`.

## Notes

- The webpage must use MathJax for maths rendering
- `START_MARKER` and `END_MARKER` are used to trim the output to the relevant content
- Tested on Quarto-generated study guides
