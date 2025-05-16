#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
simple_query.py - Simplified CLI tool for querying the Yoruba synonym finder
"""

import json
import argparse
import difflib

def load_dictionary(dict_file):
    """
    Load the Yoruba synonyms dictionary from a JSON file.
    """
    try:
        with open(dict_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Dictionary file {dict_file} not found.")
        exit(1)
    except json.JSONDecodeError:
        print(f"Error: Dictionary file {dict_file} contains invalid JSON.")
        exit(1)

def normalize_word(word):
    """
    Normalize a Yoruba word for matching: lowercase and strip whitespace.
    """
    return word.lower().strip()

def search_synonyms(query, dictionary, max_results=3):
    """
    Search for synonyms of the given query word using the static dictionary.
    """
    query = normalize_word(query)
    
    # Direct match - check if word exists directly in the dictionary
    if query in dictionary:
        return [{"rank": 1, "similarity": 1.0, "entry": dictionary[query]}]
    
    # Fuzzy match - find closest matches for unknown words
    results = []
    
    # Check if query is in any of the synonyms
    for headword, entry in dictionary.items():
        for i, synonym in enumerate(entry["synonyms"]):
            if normalize_word(synonym) == query:
                results.append({
                    "rank": 1,
                    "similarity": 1.0,
                    "entry": entry
                })
                return results  # Found exact match in synonyms
    
    # Use difflib to find fuzzy matches
    matches = difflib.get_close_matches(query, dictionary.keys(), n=max_results, cutoff=0.6)
    
    for i, match in enumerate(matches):
        # Calculate a similarity score (1.0 to 0.0)
        similarity = 1.0 - (0.1 * i)  # Simple ranking by match order
        results.append({
            "rank": i + 1,
            "similarity": similarity,
            "entry": dictionary[match]
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

def interactive_search(dictionary_file):
    """
    Run an interactive search loop.
    """
    print("Loading dictionary...")
    dictionary = load_dictionary(dictionary_file)
    print("Dictionary loaded!")
    
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
            results = search_synonyms(query, dictionary)
            display_results(results)
        except Exception as e:
            print(f"Error: {e}")

def main():
    parser = argparse.ArgumentParser(description='Query the Yoruba synonym finder')
    parser.add_argument('--dictionary', type=str, default='yoruba_synonyms_static.json',
                        help='Path to the dictionary JSON file')
    parser.add_argument('--query', type=str,
                        help='Single query to run (optional, otherwise interactive mode)')
    
    args = parser.parse_args()
    
    # If a query was provided, run it and exit
    if args.query:
        dictionary = load_dictionary(args.dictionary)
        results = search_synonyms(args.query, dictionary)
        display_results(results)
    else:
        # Otherwise run in interactive mode
        interactive_search(args.dictionary)

if __name__ == "__main__":
    main() 