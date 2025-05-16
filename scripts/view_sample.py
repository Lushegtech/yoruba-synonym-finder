#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
view_sample.py - View a sample of the expanded dictionary
"""

import json
import sys

def view_sample(dict_file, num_entries=5):
    """View a sample of entries from the dictionary"""
    try:
        with open(dict_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        print(f"Dictionary contains {len(data)} entries")
        print(f"\nShowing {min(num_entries, len(data))} sample entries:\n")
        
        # Get a list of the first few items
        items = list(data.items())[:num_entries]
        
        for headword, entry in items:
            print(f"Headword: {headword} ({entry['pos']})")
            print(f"Synonyms: {', '.join(entry['synonyms'])}")
            print(f"Definition: {entry['definition']}")
            print(f"Example (Yorùbá): {entry['example']['yorùbá']}")
            print(f"Example (English): {entry['example']['en']}")
            print("-" * 50)
    
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    dict_file = "yoruba_synonyms_expanded.json"
    num_entries = 5
    
    if len(sys.argv) > 1:
        dict_file = sys.argv[1]
    
    if len(sys.argv) > 2:
        try:
            num_entries = int(sys.argv[2])
        except ValueError:
            print(f"Invalid number of entries: {sys.argv[2]}")
            sys.exit(1)
    
    sys.exit(view_sample(dict_file, num_entries)) 