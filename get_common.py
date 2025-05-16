#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
get_common.py - Extract and count the most common Yoruba words from Wikipedia dump
"""

import os
import json
import re
import glob
from collections import Counter
import unicodedata
import argparse
from tqdm import tqdm

def is_yoruba_word(word):
    """
    Check if a word is likely a valid Yoruba word by checking for tone marks
    and other Yoruba-specific characters.
    """
    # Remove punctuation and digits
    word = re.sub(r'[^\w\s]', '', word)
    word = re.sub(r'\d+', '', word)
    
    if not word or len(word) < 2:
        return False
    
    # Characters used in Yoruba
    yoruba_chars = set('abcdeẹfgihkjlmnopqrstuúwxyzàáèéẹ̀ẹ́ìíòóọ̀ọ́ùúṣ̀ṣ́')
    
    # Check if all characters are in yoruba_chars
    return all(c.lower() in yoruba_chars for c in word)

def normalize_yoruba_word(word):
    """
    Normalize a Yoruba word: lowercase and preserve tone marks.
    """
    # Lowercase the word
    word = word.lower()
    
    # Remove non-alphabetic characters except tone marks
    word = re.sub(r'[^a-zẹọṣàáèéẹ̀ẹ́ìíòóọ̀ọ́ùú]', '', word)
    
    return word

def extract_tokens_from_file(file_path):
    """
    Extract tokens from a single file.
    """
    tokens = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    # Parse the JSON line if it's in JSON format
                    try:
                        data = json.loads(line)
                        text = data.get('text', '')
                    except json.JSONDecodeError:
                        # If not JSON, just use the line as text
                        text = line
                    
                    # Tokenize the text - split by whitespace and punctuation
                    words = re.findall(r'\b\w+\b', text)
                    
                    # Filter for Yoruba words and normalize
                    for word in words:
                        if is_yoruba_word(word):
                            normalized = normalize_yoruba_word(word)
                            if normalized:
                                tokens.append(normalized)
                except Exception as e:
                    continue
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
    
    return tokens

def main():
    parser = argparse.ArgumentParser(description='Extract common Yoruba words from text files')
    parser.add_argument('--input-dir', type=str, default='extracted_wiki', 
                        help='Directory with extracted text files')
    parser.add_argument('--output', type=str, default='common_200.json',
                        help='Output JSON file for common words')
    parser.add_argument('--top-n', type=int, default=200,
                        help='Number of top words to extract')
    parser.add_argument('--fallback', action='store_true',
                        help='Use fallback list if no files found or words extracted')
    
    args = parser.parse_args()
    
    # Find all the text files
    files = []
    if os.path.exists(args.input_dir):
        files = glob.glob(os.path.join(args.input_dir, '**', '*.json'), recursive=True)
        if not files:
            files = glob.glob(os.path.join(args.input_dir, '**', 'wiki_*'), recursive=True)
        if not files:
            files = glob.glob(os.path.join(args.input_dir, '**', '*.txt'), recursive=True)
    
    if not files:
        print(f"No files found in {args.input_dir}")
        if not args.fallback:
            print("To download and extract the Yoruba Wikipedia dump, run:")
            print("wget https://dumps.wikimedia.org/yowiki/latest/yowiki-latest-pages-articles.xml.bz2")
            print("python -m wikiextractor.WikiExtractor yowiki-latest-pages-articles.xml.bz2 --output extracted_wiki --json")
            print("Or use the --fallback flag to generate a basic word list.")
            return
        else:
            print("Using fallback word list...")
            # Basic Yoruba words for fallback
            fallback_words = [
                "ọjọ́", "ilé", "ẹ̀kọ́", "ọmọ", "isẹ́", "oúnjẹ", "àgbà", "ọ̀rọ̀", "ìgbà", "ìwé",
                "omi", "olú", "ẹnu", "ọkọ̀", "ọ̀rẹ́", "ilẹ̀", "ojú", "ọwọ́", "orí", "inú",
                "ẹsẹ̀", "ọjọ́", "alẹ́", "owó", "itọ́", "ẹ̀kọ́", "ọkùnrin", "obìnrin", "ọdún", "ìdí",
                "igbó", "òkè", "ìlú", "ẹran", "ẹjẹ", "ìfẹ́", "ìgbàlà", "àìsàn", "àìlera", "àlàáfíà",
                "ẹ̀mí", "ará", "ìmọ́", "ìṣe", "ẹlẹ́rìí", "ìjọba", "ìlera", "ìdàjọ́", "ìṣọ̀kan", "ìdàgbàsókè",
                "ìrìn", "èdè", "ìṣẹ̀dálẹ̀", "gbogbo", "kékeré", "púpọ̀", "díẹ̀", "tó", "jù"
            ]
            if len(fallback_words) < args.top_n:
                # Duplicate words to reach desired count
                multiplier = (args.top_n + len(fallback_words) - 1) // len(fallback_words)
                fallback_words = fallback_words * multiplier
            
            top_words = fallback_words[:args.top_n]
            
            # Save to JSON
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(top_words, f, ensure_ascii=False, indent=2)
            
            print(f"Successfully created fallback list with {len(top_words)} words in {args.output}")
            return
    
    print(f"Processing {len(files)} files...")
    token_counter = Counter()
    
    # Process each file
    for file_path in tqdm(files):
        tokens = extract_tokens_from_file(file_path)
        token_counter.update(tokens)
    
    # Get the top N most common words
    top_words = [word for word, _ in token_counter.most_common(args.top_n)]
    
    # If we don't have enough words, use fallback
    if len(top_words) < args.top_n and args.fallback:
        print(f"Only found {len(top_words)} words, adding some fallback words to reach {args.top_n}")
        fallback_words = [
            "ọjọ́", "ilé", "ẹ̀kọ́", "ọmọ", "isẹ́", "oúnjẹ", "àgbà", "ọ̀rọ̀", "ìgbà", "ìwé",
            "omi", "olú", "ẹnu", "ọkọ̀", "ọ̀rẹ́", "ilẹ̀", "ojú", "ọwọ́", "orí", "inú"
        ]
        for word in fallback_words:
            if word not in top_words:
                top_words.append(word)
                if len(top_words) >= args.top_n:
                    break
    
    # Save to JSON
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(top_words, f, ensure_ascii=False, indent=2)
    
    print(f"Successfully extracted {len(top_words)} common words to {args.output}")
    if len(top_words) < args.top_n:
        print(f"Warning: Only found {len(top_words)} words, fewer than requested {args.top_n}")
        print("Consider using the --fallback flag to supplement with basic words.")

if __name__ == "__main__":
    main() 