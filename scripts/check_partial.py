#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
check_partial.py - Check the status of a partially generated dictionary
"""

import json
import sys
import random
import os

def check_partial_dictionary(partial_file, num_samples=3):
    """Check and report on a partially generated dictionary"""
    try:
        file_size_mb = os.path.getsize(partial_file) / (1024 * 1024)
        print(f"Partial file size: {file_size_mb:.2f} MB")
        
        with open(partial_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        current_count = len(data)
        print(f"Current entry count: {current_count:,}")
        
        if current_count > 0:
            # Show some random samples
            print("\nRandom samples:")
            keys = list(data.keys())
            sample_keys = random.sample(keys, min(num_samples, len(keys)))
            
            for key in sample_keys:
                entry = data[key]
                print(f"\nHeadword: {entry['headword']} ({entry['pos']})")
                print(f"Synonyms: {', '.join(entry['synonyms'])}")
                print(f"Definition: {entry['definition']}")
                print(f"Example (Yorùbá): {entry['example']['yorùbá']}")
                print(f"Example (English): {entry['example']['en']}")
                print("-" * 50)
                
            # Show distribution of parts of speech
            pos_counts = {}
            for entry in data.values():
                pos = entry['pos']
                pos_counts[pos] = pos_counts.get(pos, 0) + 1
                
            print("\nPart of speech distribution:")
            for pos, count in pos_counts.items():
                percentage = (count / current_count) * 100
                print(f"  {pos}: {count:,} ({percentage:.1f}%)")
                
            # Show synonym stats
            synonym_counts = [len(entry['synonyms']) for entry in data.values()]
            avg_synonyms = sum(synonym_counts) / len(synonym_counts) if synonym_counts else 0
            max_synonyms = max(synonym_counts) if synonym_counts else 0
            min_synonyms = min(synonym_counts) if synonym_counts else 0
            
            print("\nSynonym statistics:")
            print(f"  Average synonyms per entry: {avg_synonyms:.1f}")
            print(f"  Maximum synonyms: {max_synonyms}")
            print(f"  Minimum synonyms: {min_synonyms}")
            
    except Exception as e:
        print(f"Error checking partial dictionary: {e}")
        return 1
        
    return 0

if __name__ == "__main__":
    partial_file = "yoruba_synonyms_massive.json.partial"
    num_samples = 3
    
    if len(sys.argv) > 1:
        partial_file = sys.argv[1]
        
    if len(sys.argv) > 2:
        try:
            num_samples = int(sys.argv[2])
        except ValueError:
            print(f"Invalid number of samples: {sys.argv[2]}")
            sys.exit(1)
            
    sys.exit(check_partial_dictionary(partial_file, num_samples)) 