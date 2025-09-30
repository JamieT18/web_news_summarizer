import sys
import argparse
import logging
from typing import List, Tuple, Optional
import newspaper
from newspaper import Article
from readability import Document
import requests
import nltk
from transformers import pipeline
from tqdm import tqdm
import json
import os

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

# Download nltk punkt if not present
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

def load_summarization_model(model_name:str="facebook/bart-large-cnn"):
    """
    Loads the summarization pipeline model from Hugging Face.
    Returns:
        summarizer pipeline object or None if error occurs.
    """
    try:
        summarizer = pipeline("summarization", model=model_name)
        return summarizer
    except Exception as e:
        logging.error(
            "Failed to load summarization model '%s': %s\n"
            "Please check your internet connection and dependencies.",
            model_name, e
        )
        return None

def clean_article_text(url:str) -> Tuple[Optional[str], Optional[str]]:
    """
    Extracts and cleans article content using newspaper3k and readability-lxml.
    Returns:
        tuple: (title: str, text: str), or (None, None) if error occurs.
    """
    try:
        article = Article(url)
        article.download()
        article.parse()
        # Use readability-lxml for additional cleaning
        response = requests.get(url, timeout=15)
        doc = Document(response.text)
        cleaned_text = doc.summary()
        # Fallback: use newspaper3k text if readability fails
        main_text = article.text if article.text else cleaned_text
        if not main_text.strip():
            raise ValueError("No article text found.")
        return article.title, main_text
    except Exception as e:
        logging.error("Error fetching or parsing article from URL '%s': %s", url, e)
        return None, None

def chunk_sentences(text:str, chunk_size:int=500) -> List[str]:
    """
    Splits text into chunks of sentences, not raw words.
    Returns:
        List of string chunks.
    """
    sentences = nltk.sent_tokenize(text)
    chunks = []
    current_chunk = []
    current_len = 0
    for sent in sentences:
        sent_words = len(sent.split())
        if current_len + sent_words > chunk_size and current_chunk:
            chunks.append(' '.join(current_chunk))
            current_chunk = []
            current_len = 0
        current_chunk.append(sent)
        current_len += sent_words
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    return chunks

def summarize_chunks(summarizer, chunks:List[str], max_length:int=150, min_length:int=30) -> str:
    """
    Summarizes each chunk and combines.
    """
    summaries = []
    for idx, chunk in enumerate(tqdm(chunks, desc="Summarizing chunks")):
        try:
            summary = summarizer(chunk, max_length=max_length, min_length=min_length, do_sample=False)[0]['summary_text']
            summaries.append(summary)
        except Exception as e:
            logging.warning("Chunk %d summarization failed: %s", idx + 1, e)
    return '\n'.join(summaries)

def summarize_text(summarizer, text:str, max_length:int=150, min_length:int=50, chunk_size:int=500) -> Optional[str]:
    """
    Summarizes text using Hugging Face pipeline. Handles long texts by splitting.
    """
    if len(text.split()) > chunk_size:
        chunks = chunk_sentences(text, chunk_size=chunk_size)
        return summarize_chunks(summarizer, chunks, max_length=max_length, min_length=min_length)
    try:
        summary = summarizer(text, max_length=max_length, min_length=min_length, do_sample=False)
        return summary[0]['summary_text']
    except Exception as e:
        logging.error("Summarization failed: %s", e)
        return None

def export_summary(title:str, url:str, summary:str, output:str, fmt:str):
    """
    Export summary in desired format.
    """
    if fmt == "txt":
        with open(output, "w", encoding="utf-8") as f:
            f.write(f"Title: {title}\nURL: {url}\n\nSummary:\n{summary}\n")
    elif fmt == "md":
        with open(output, "w", encoding="utf-8") as f:
            f.write(f"# {title}\n\n**URL:** [{url}]({url})\n\n## Summary\n\n{summary}\n")
    elif fmt == "json":
        with open(output, "w", encoding="utf-8") as f:
            json.dump({"title": title, "url": url, "summary": summary}, f, indent=2, ensure_ascii=False)
    else:
        logging.error("Unsupported export format: %s", fmt)

def process_article(url:str, summarizer, args) -> Tuple[str,str,str]:
    """
    Fetches, cleans, summarizes an article.
    Returns: (title, url, summary)
    """
    title, article_text = clean_article_text(url)
    if not article_text:
        return ("(Failed to fetch)", url, "Could not process the article.")
    summary = summarize_text(
        summarizer, article_text, max_length=args.max_length, min_length=args.min_length, chunk_size=args.chunk_size
    )
    if not summary:
        summary = "Could not generate summary."
    return (title, url, summary)

def batch_process(urls:List[str], summarizer, args):
    """
    Processes a batch of URLs and exports results.
    """
    for url in tqdm(urls, desc="Processing articles"):
        title, url, summary = process_article(url, summarizer, args)
        print(f"\n--- {title} ---\n{summary}\n")
        if args.output_dir:
            basename = f"{title or 'article'}".replace(" ", "_").replace("/", "_")[:40]
            ext = args.export_format
            output_path = os.path.join(args.output_dir, f"{basename}.{ext}")
            export_summary(title, url, summary, output_path, ext)
            logging.info("Exported summary to %s", output_path)

def main():
    parser = argparse.ArgumentParser(description="Smart News Summarizer - Enhanced Edition")
    parser.add_argument("urls", nargs="*", help="List of article URLs or a file containing URLs")
    parser.add_argument("-m", "--model", default="facebook/bart-large-cnn", help="Summarization model (default: bart-large-cnn)")
    parser.add_argument("-o", "--output-dir", help="Directory to export summaries")
    parser.add_argument("-f", "--export-format", choices=["txt", "md", "json"], default="txt", help="Export format")
    parser.add_argument("--max-length", type=int, default=150, help="Max summary length")
    parser.add_argument("--min-length", type=int, default=50, help="Min summary length")
    parser.add_argument("--chunk-size", type=int, default=500, help="Chunk size for long texts (words)")
    args = parser.parse_args()

    # If a single file is provided, treat as batch file
    if len(args.urls) == 1 and args.urls[0].endswith(".txt"):
        with open(args.urls[0], "r", encoding="utf-8") as f:
            urls = [line.strip() for line in f if line.strip()]
    elif args.urls:
        urls = args.urls
    else:
        # Interactive mode
        url = input("Please enter the URL of a news article: ").strip()
        urls = [url]

    summarizer = load_summarization_model(args.model)
    if not summarizer:
        print("Could not load summarization model. Exiting.")
        sys.exit(1)

    if args.output_dir and not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    batch_process(urls, summarizer, args)

if __name__ == "__main__":
    main()
