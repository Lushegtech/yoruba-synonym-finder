#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
build_index.py - Build a FAISS index for fast semantic search of Yoruba words
"""

import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import argparse

def load_entries(file_path):
    """
    Load the Yoruba entries from the JSONL file.
    """
    entries = []
    headwords = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                entry = json.loads(line)
                entries.append(entry)
                headwords.append(entry["headword"])
                
        return entries, headwords
    except FileNotFoundError:
        raise FileNotFoundError(f"File {file_path} not found. Run generate_entries.py first.")
    except json.JSONDecodeError:
        raise ValueError(f"File {file_path} contains invalid JSON.")

def build_faiss_index(headwords, model_name):
    """
    Build a FAISS index for the Yoruba headwords using sentence transformers.
    """
    print(f"Loading model: {model_name}")
    model = SentenceTransformer(model_name)
    
    print("Encoding headwords...")
    embeddings = []
    
    # Process in batches to show progress
    batch_size = 32
    for i in tqdm(range(0, len(headwords), batch_size)):
        batch = headwords[i:i+batch_size]
        batch_embeddings = model.encode(batch, convert_to_numpy=True)
        embeddings.extend(batch_embeddings)
    
    # Convert to numpy array
    embeddings = np.array(embeddings).astype('float32')
    
    # Normalize vectors for cosine similarity
    faiss.normalize_L2(embeddings)
    
    # Create the index - using IndexFlatIP for inner product (cosine similarity with normalized vectors)
    print("Building FAISS index...")
    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)
    
    return index, embeddings, model

def main():
    parser = argparse.ArgumentParser(description='Build a FAISS index for Yoruba words')
    parser.add_argument('--input', type=str, default='yoruba_synonyms.jsonl',
                        help='Input JSONL file with synonym entries')
    parser.add_argument('--index-output', type=str, default='yoruba_index.faiss',
                        help='Output FAISS index file')
    parser.add_argument('--headwords-output', type=str, default='yoruba_texts.npy',
                        help='Output NumPy file for headwords')
    parser.add_argument('--entries-output', type=str, default='yoruba_entries.npy',
                        help='Output NumPy file for full entries')
    parser.add_argument('--model', type=str, default='all-MiniLM-L6-v2',
                        help='Sentence transformer model to use')
    
    args = parser.parse_args()
    
    print(f"Loading entries from {args.input}...")
    entries, headwords = load_entries(args.input)
    print(f"Loaded {len(headwords)} entries")
    
    # Build the index
    index, embeddings, model = build_faiss_index(headwords, args.model)
    
    # Save the index
    print(f"Saving index to {args.index_output}...")
    faiss.write_index(index, args.index_output)
    
    # Save the headwords and entries
    print(f"Saving headwords to {args.headwords_output}...")
    np.save(args.headwords_output, np.array(headwords, dtype=object))
    
    # Save the complete entries for later retrieval
    print(f"Saving complete entries to {args.entries_output}...")
    np.save(args.entries_output, np.array(entries, dtype=object))
    
    # Save model information
    model_info = {"name": args.model}
    with open("model_info.json", "w") as f:
        json.dump(model_info, f)
    
    print("Index building complete! You can now query the index using query.py.")

if __name__ == "__main__":
    main() 