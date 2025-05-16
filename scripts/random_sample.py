#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
random_sample.py - View random entries from the expanded dictionary
"""

import json
import sys
import random

def view_random_sample(dict_file, num_entries=5):
    """View random entries from the dictionary"""
    try:
        with open(dict_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        print(f"Dictionary contains {len(data)} entries")
        print(f"\nShowing {min(num_entries, len(data))} random entries:\n")
        
        # Get a list of all keys
        keys = list(data.keys())
        
        # Select random keys
        random_keys = random.sample(keys, min(num_entries, len(keys)))
        
        for key in random_keys:
            entry = data[key]
            print(f"Headword: {entry['headword']} ({entry['pos']})")
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
    
    sys.exit(view_random_sample(dict_file, num_entries)) 