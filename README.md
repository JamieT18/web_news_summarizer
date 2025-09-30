# Smart News Summarizer

## 🚀 Project Overview

**Smart News Summarizer** is an advanced Python tool designed to automatically extract, clean, and summarize news articles using state-of-the-art Natural Language Processing (NLP) techniques. It leverages powerful AI models from Hugging Face, provides robust web scraping and text cleaning, and offers a flexible interface for both individual and batch processing. Summaries can be exported in TXT, Markdown, or JSON formats, making this tool ideal for research, journalism, or anyone wanting quick and reliable news digests.

---

## ✨ Features

- **Automated Web Scraping & Cleaning:**  
  Extracts clean, readable article text from URLs using `newspaper3k` and `readability-lxml`.

- **AI-Powered Summarization:**  
  Generates concise abstractive summaries with top models like BART, T5, Pegasus, or multilingual options from Hugging Face.

- **Batch Processing:**  
  Summarize single articles or multiple URLs from a file in one go.

- **Smart Chunking:**  
  Splits long articles by sentence (using NLTK) for more coherent summaries.

- **Customizable Output:**  
  Export summaries as plain text, Markdown, or JSON. Specify output directory and file formats.

- **Command-Line & Interactive Modes:**  
  Use via direct command-line arguments, batch files, or interactive prompts.

- **Progress Visualization:**  
  Track summarization progress with clear progress bars (`tqdm`).

- **Flexible Configuration:**  
  Choose model, summary length, chunk size, and output format with CLI flags.

- **Robust Logging & Error Handling:**  
  Detailed feedback for smooth troubleshooting and diagnostics.

---

## 🛠️ Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/JamieT18/summarizer.git
   cd summarizer
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. *(Optional, if prompted)* Download NLTK tokenizers:
   ```bash
   python -m nltk.downloader punkt
   ```

---

## 💡 Usage

### Summarize a Single Article

```bash
python news_summarizer_plus.py "https://www.bbc.com/news/world-12345678"
```

### Summarize Multiple Articles from a File

Create a file (e.g. `articles.txt`) with one URL per line:

```text
https://www.bbc.com/news/world-12345678
https://www.nytimes.com/2025/09/29/world/europe/news-headline.html
```

Run:

```bash
python news_summarizer_plus.py articles.txt
```

### Export Summaries to a Directory

```bash
python news_summarizer_plus.py articles.txt -o summaries -f md
```
- Supported formats: `txt`, `md`, `json`

### Choose a Different Summarization Model

```bash
python news_summarizer_plus.py "https://..." -m google/pegasus-xsum
```
Or for multilingual articles:
```bash
python news_summarizer_plus.py "https://..." -m facebook/mbart-large-50-many-to-many-mmt
```

### Adjust Summary Length & Chunking

```bash
python news_summarizer_plus.py "https://..." --max-length 80 --min-length 20 --chunk-size 600
```

### Interactive Mode

If you run the script without arguments, it will prompt you for a URL interactively.

---

## 📦 Output Formats

- **TXT:** Simple text file with title, URL, and summary.
- **Markdown:** Well-formatted, link-rich Markdown for publishing or note-taking.
- **JSON:** Machine-readable, for data pipelines or analysis.

---

## 🔍 Troubleshooting

- **NLTK Errors:**  
  If you see errors about missing `punkt`, run:  
  ```bash
  python -m nltk.downloader punkt
  ```

- **Model Loading Issues:**  
  Ensure you’re connected to the internet and have permissions for Hugging Face’s cache directories.

- **Non-English Articles:**  
  Use a multilingual model (see above).

- **No Output Directory:**  
  The script creates one if you specify with `-o`.

---

## 📝 Example Output

**Text:**
```text
--- Title: Breakthrough in Renewable Energy ---
Summary:
Scientists have developed a new solar panel that is twice as efficient...
-----------------
```

**Markdown:**
```markdown
# Breakthrough in Renewable Energy

**URL:** [link](https://...)

## Summary

Scientists have developed a new solar panel that is twice as efficient...
```

**JSON:**
```json
{
  "title": "Breakthrough in Renewable Energy",
  "url": "https://...",
  "summary": "Scientists have developed a new solar panel that is twice as efficient..."
}
```

---

## 🧩 Extending

This tool is modular and can be adapted for:
- Streamlit/Flask web apps
- News aggregation dashboards
- API integration
- Slack/email notifications

---

## 📚 Credits

- [newspaper3k](https://github.com/codelucas/newspaper)
- [readability-lxml](https://github.com/buriy/python-readability)
- [transformers](https://github.com/huggingface/transformers)
- [nltk](https://www.nltk.org/)
- [tqdm](https://tqdm.github.io/)

---

## ⚖️ License

MIT

---
