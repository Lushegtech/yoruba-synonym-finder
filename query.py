#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
query.py - CLI tool for querying the Yoruba synonym finder
"""

import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import argparse

def load_resources(index_file, texts_file, entries_file, model_name=None):
    """
    Load the FAISS index, headwords, entries, and initialize the model.
    """
    try:
        # Load the index
        index = faiss.read_index(index_file)
        
        # Load the headwords
        headwords = np.load(texts_file, allow_pickle=True)
        
        # Load the entries
        entries = np.load(entries_file, allow_pickle=True)
        
        # Get model name if not provided
        if not model_name:
            try:
                with open("model_info.json", "r") as f:
                    model_info = json.load(f)
                    model_name = model_info.get("name", "all-MiniLM-L6-v2")
            except (FileNotFoundError, json.JSONDecodeError):
                model_name = "all-MiniLM-L6-v2"
        
        # Load the model
        model = SentenceTransformer(model_name)
        
        return index, headwords, entries, model
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Make sure you've run build_index.py first to create the necessary files.")
        exit(1)

def search_synonyms(query, index, headwords, entries, model, top_k=3):
    """
    Search for synonyms of the given query word.
    """
    # Encode the query
    query_embedding = model.encode([query], convert_to_numpy=True)
    
    # Normalize the query embedding for cosine similarity
    faiss.normalize_L2(query_embedding)
    
    # Search the index
    distances, indices = index.search(query_embedding, top_k)
    
    results = []
    for i, idx in enumerate(indices[0]):
        if idx < len(entries):
            entry = entries[idx]
            similarity = distances[0][i]
            results.append({
                "rank": i + 1,
                "similarity": float(similarity),
                "entry": entry
            })
    
    return results

def display_results(results):
    """
    Display the search results in a readable format.
    """
    if not results:
        print("No results found.")
        return
    
    print("\n" + "="*60)
    for result in results:
        entry = result["entry"]
        similarity = result["similarity"]
        
        print(f"Rank {result['rank']} (similarity: {similarity:.4f})")
        print(f"Headword: {entry['headword']} ({entry['pos']})")
        print(f"Synonyms: {', '.join(entry['synonyms'])}")
        print(f"Definition: {entry['definition']}")
        print(f"Example (Yoruba): {entry['example']['yorùbá']}")
        print(f"Example (English): {entry['example']['en']}")
        print("-"*60)

def interactive_search(index_file, texts_file, entries_file, model_name=None):
    """
    Run an interactive search loop.
    """
    print("Loading resources... This might take a moment.")
    index, headwords, entries, model = load_resources(index_file, texts_file, entries_file, model_name)
    print("Resources loaded!")
    
    print("\nYorùbá Synonym Finder")
    print("="*60)
    print("Type 'q' or 'quit' to exit.")
    
    while True:
        query = input("\nEnter a Yoruba word to find synonyms: ")
        query = query.strip()
        
        if query.lower() in ('q', 'quit', 'exit'):
            print("Goodbye!")
            break
        
        if not query:
            print("Please enter a word.")
            continue
        
        try:
            results = search_synonyms(query, index, headwords, entries, model)
            display_results(results)
        except Exception as e:
            print(f"Error: {e}")

def main():
    parser = argparse.ArgumentParser(description='Query the Yoruba synonym finder')
    parser.add_argument('--index', type=str, default='yoruba_index.faiss',
                        help='Path to the FAISS index file')
    parser.add_argument('--headwords', type=str, default='yoruba_texts.npy',
                        help='Path to the headwords NumPy file')
    parser.add_argument('--entries', type=str, default='yoruba_entries.npy',
                        help='Path to the entries NumPy file')
    parser.add_argument('--model', type=str, default=None,
                        help='Sentence transformer model name (optional)')
    parser.add_argument('--query', type=str,
                        help='Single query to run (optional, otherwise interactive mode)')
    
    args = parser.parse_args()
    
    # If a query was provided, run it and exit
    if args.query:
        index, headwords, entries, model = load_resources(
            args.index, args.headwords, args.entries, args.model
        )
        results = search_synonyms(args.query, index, headwords, entries, model)
        display_results(results)
    else:
        # Otherwise run in interactive mode
        interactive_search(args.index, args.headwords, args.entries, args.model)

if __name__ == "__main__":
    main() 