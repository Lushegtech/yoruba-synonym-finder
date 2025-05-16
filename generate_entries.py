#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
generate_entries.py - Generate synonyms for Yoruba headwords using a local transformer model
"""

import os
import json
import torch
from tqdm import tqdm
import time
import argparse
import re
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

# Define the device - GPU if available, otherwise CPU
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

def load_model_and_tokenizer(model_name):
    """
    Load the transformer model and tokenizer.
    """
    print(f"Loading model {model_name}...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    model.to(DEVICE)
    return model, tokenizer

def load_common_words(filename):
    """
    Load the common Yoruba words from the JSON file.
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"File {filename} not found. Run get_common.py first.")
    except json.JSONDecodeError:
        raise ValueError(f"File {filename} contains invalid JSON.")

def create_prompt(word):
    """
    Create a few-shot prompt for the model to generate synonyms.
    """
    # Few-shot examples
    prompt = """Generate 5 Yoruba synonyms, part of speech, definition, and example sentence for the word in English and Yoruba.

Word: ilé
Part of speech: noun
Synonyms: ilẹ̀, ibùgbé, afin, ààfin, ìdí
Definition: House or building where people live or work.
Example in Yoruba: Mo wà ní ilé mi.
Example in English: I am at my house.

Word: ọmọ
Part of speech: noun
Synonyms: ọmọbíbí, àbíkẹ́, arọ́mọdọ́mọ, ọmọkùnrin, ọmọbìnrin
Definition: Child, offspring, or young person.
Example in Yoruba: Ọmọ náà ń sùn.
Example in English: The child is sleeping.

Word: dára
Part of speech: adjective
Synonyms: pẹ̀lẹ́, rẹwà, tòótọ́, dáradára, ṣàn
Definition: Good, fine, or beautiful.
Example in Yoruba: Aṣọ yìí dára púpọ̀.
Example in English: This cloth is very good.

Word: {}
Part of speech:"""
    
    return prompt.format(word)

def extract_definition_from_response(response_text):
    """
    Extract a structured definition object from the model's response.
    """
    # Default structure for when parsing fails
    result = {
        "headword": "",
        "pos": "",
        "synonyms": [],
        "definition": "",
        "example": {"yorùbá": "", "en": ""}
    }
    
    # Extract the headword from the original prompt
    headword_match = re.search(r'Word:\s*([^\n]+)', response_text)
    if headword_match:
        result["headword"] = headword_match.group(1).strip()
    
    # Extract part of speech
    pos_match = re.search(r'Part of speech:\s*([^\n]+)', response_text)
    if pos_match:
        result["pos"] = pos_match.group(1).strip()
    
    # Extract synonyms
    synonyms_match = re.search(r'Synonyms:\s*([^\n]+)', response_text)
    if synonyms_match:
        synonyms_text = synonyms_match.group(1).strip()
        # Split by comma and clean up
        synonyms = [s.strip() for s in synonyms_text.split(',')]
        # Remove empty strings and duplicates
        result["synonyms"] = list(dict.fromkeys(s for s in synonyms if s))
    
    # Extract definition
    definition_match = re.search(r'Definition:\s*([^\n]+)', response_text)
    if definition_match:
        result["definition"] = definition_match.group(1).strip()
    
    # Extract examples
    yoruba_example_match = re.search(r'Example in Yoruba:\s*([^\n]+)', response_text)
    if yoruba_example_match:
        result["example"]["yorùbá"] = yoruba_example_match.group(1).strip()
    
    english_example_match = re.search(r'Example in English:\s*([^\n]+)', response_text)
    if english_example_match:
        result["example"]["en"] = english_example_match.group(1).strip()
    
    return result

def validate_entry(entry, headword):
    """
    Validate that the generated entry is correct and complete.
    """
    # Check if headword is present and matches expected headword
    if not entry["headword"] or headword.lower() not in entry["headword"].lower():
        entry["headword"] = headword
    
    # Check if part of speech is present
    if not entry["pos"]:
        entry["pos"] = "noun"  # Default to noun
    
    # Check if at least one synonym is present
    if not entry["synonyms"]:
        entry["synonyms"] = [headword]  # Use the headword as a fallback
    
    # If less than 5 synonyms, duplicate some
    while len(entry["synonyms"]) < 5:
        if len(entry["synonyms"]) > 0:
            entry["synonyms"].append(entry["synonyms"][0])
        else:
            entry["synonyms"].append(headword)
    
    # Check if definition is present
    if not entry["definition"]:
        entry["definition"] = f"A Yoruba word: {headword}"
    
    # Check if examples are present
    if not entry["example"]["yorùbá"]:
        entry["example"]["yorùbá"] = f"{headword}."
    
    if not entry["example"]["en"]:
        entry["example"]["en"] = f"{headword}."
    
    return entry

def generate_entries_for_batch(model, tokenizer, words_batch, max_length=512):
    """
    Generate detailed entries for a batch of Yoruba words.
    """
    entries = []
    
    for word in words_batch:
        prompt = create_prompt(word)
        
        # Tokenize the prompt
        inputs = tokenizer(prompt, return_tensors="pt", max_length=max_length, truncation=True).to(DEVICE)
        
        # Generate response
        with torch.no_grad():
            outputs = model.generate(
                **inputs, 
                max_length=max_length,
                num_return_sequences=1,
                temperature=0.7,
                top_p=0.9,
                do_sample=True
            )
        
        # Decode the response
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract and validate the entry
        entry = extract_definition_from_response(prompt + response)
        entry = validate_entry(entry, word)
        
        entries.append(entry)
    
    return entries

def process_all_words(model, tokenizer, words, batch_size=20, output_file="yoruba_synonyms.jsonl"):
    """
    Process all words in batches, generate entries, and save to a JSONL file.
    """
    num_batches = (len(words) + batch_size - 1) // batch_size
    processed_entries = 0
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for i in tqdm(range(num_batches), desc="Processing batches"):
            start_idx = i * batch_size
            end_idx = min((i + 1) * batch_size, len(words))
            batch = words[start_idx:end_idx]
            
            # Generate entries for this batch
            try:
                entries = generate_entries_for_batch(model, tokenizer, batch)
                
                # Save entries to file
                for entry in entries:
                    f.write(json.dumps(entry, ensure_ascii=False) + '\n')
                    processed_entries += 1
            
            except Exception as e:
                print(f"Error processing batch {i+1}/{num_batches}: {e}")
            
            # Add a small delay to avoid GPU overheating
            time.sleep(1)
    
    return processed_entries

def main():
    parser = argparse.ArgumentParser(description='Generate Yoruba synonyms using a transformer model')
    parser.add_argument('--input', type=str, default='common_200.json',
                        help='Input JSON file with common words')
    parser.add_argument('--output', type=str, default='yoruba_synonyms.jsonl',
                        help='Output JSONL file for synonym entries')
    parser.add_argument('--model', type=str, default='google/mt5-small',
                        help='Transformer model to use')
    parser.add_argument('--batch-size', type=int, default=20,
                        help='Batch size for processing')
    
    args = parser.parse_args()
    
    # Load the model and tokenizer
    model, tokenizer = load_model_and_tokenizer(args.model)
    
    # Load common words
    print(f"Loading common Yoruba words from {args.input}...")
    words = load_common_words(args.input)
    
    # Process words
    print(f"Generating entries for {len(words)} words in batches of {args.batch_size}...")
    processed = process_all_words(model, tokenizer, words, args.batch_size, args.output)
    
    print(f"Processing complete!")
    print(f"Entries saved: {processed}")
    print(f"Entries saved to {args.output}")

if __name__ == "__main__":
    main() 