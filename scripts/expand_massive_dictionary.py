#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
expand_massive_dictionary.py - Script to generate a massive Yoruba dictionary with 100,000+ entries
"""

import json
import random
import itertools
import os
import sys
import time
from pathlib import Path
from tqdm import tqdm

# Import vocabulary from the original expansion script
from expand_dictionary import (
    YORUBA_NOUNS, YORUBA_VERBS, YORUBA_ADJECTIVES,
    YORUBA_PREFIXES, YORUBA_SUFFIXES,
    YORUBA_CONSONANTS, YORUBA_VOWELS, YORUBA_TONES,
    DEFINITION_TEMPLATES, EXAMPLE_TEMPLATES_YORUBA, EXAMPLE_TEMPLATES_ENGLISH,
    DEFINITION_NOUNS, DEFINITION_VERBS, DEFINITION_ADJECTIVES,
    generate_yoruba_word, generate_definition, generate_example
)

# Additional vowel combinations for word generation
YORUBA_COMPOUND_VOWELS = ["ai", "oi", "ui", "au", "ou", "eu", "ei", "ae"]

# Additional Yoruba vocabulary to increase variety
ADDITIONAL_YORUBA_NOUNS = [
    "ọgbọ́n", "agbára", "ìdájọ́", "ẹbùn", "ìwúrí", "ìrètí", "ìgbàgbọ́", "ìfẹ́",
    "àìlera", "àlááfíà", "ìbárakú", "ìmọ̀lẹ̀", "ọjà", "àṣẹ́wó", "ìwúrà", "àbájọ",
    "ẹṣẹ̀", "ìdí", "orúkọ", "ìyàtọ̀", "ajé", "ìṣèlú", "àmí", "àdúmáadán", "ìjà",
    "ìfarakanra", "èrò", "ìwòran", "ìgbóhùn", "ọtún", "òsì", "ìwájú", "ẹ̀yìn",
    "àṣàrò", "ìtàkùn", "ìlàjà", "àṣírí", "ìbínú", "ẹ̀pè", "ìbúra", "òkú", "igbó",
    "ọdàn", "abẹ́rẹ́", "ìránṣẹ́", "ọkọ̀", "ọkùnrin", "obìnrin", "olólùfẹ́", "òjò"
]

ADDITIONAL_YORUBA_VERBS = [
    "wàásù", "dágbére", "dunú", "júwe", "kápá", "kúnlẹ̀", "dàgbà", "tẹ̀lé", "yíra",
    "jẹ́wọ́", "dènà", "fàṣẹ́", "tọrọ", "gbàgbọ́", "dárí", "kíyè", "síjú", "fojú",
    "jìyà", "kíyèsí", "bùkún", "hànlẹ̀", "tàbí", "pète", "júbà", "yíjú", "sọkún",
    "jábọ̀", "gbàdúrà", "dìde", "yìn", "wọlé", "jáde", "rókè", "rẹ̀hìn", "túká",
    "wàárú", "panu", "padà", "kúrò", "dára", "dọ̀tí", "bímọ", "sanlẹ̀", "sọkò",
    "ṣubú", "táyé", "balẹ̀", "yínbọn", "sáré", "rìn", "tàkìtì", "fọwọ́"
]

ADDITIONAL_YORUBA_ADJECTIVES = [
    "ṣíṣe", "dídá", "dáradára", "bíbẹ̀rẹ̀", "lílé", "títa", "líle", "sísàn",
    "yíyọ", "líla", "ńlá", "kékeré", "gígùn", "kúkúrú", "títóbi", "tínrín",
    "gbígbẹ", "títutù", "dídùn", "kórò", "fífẹ́", "kíkọ", "túútù", "gbígbóná",
    "pípọ̀", "àṣàrò", "ìrẹ̀lẹ̀", "àjèjì", "ìbàntẹ́", "ẹlẹ́rìí", "ológo", "àjànàkú",
    "aláṣejù", "ẹlẹ́gbẹ́", "olóòótọ́", "aláìlera", "rírù", "àgbàlagbà", "ọ̀dọ́",
    "ọlọ́ràn", "oníjó", "onígbàgbọ́", "aláìgbàgbọ́", "tútù", "gbígbẹ", "agídí"
]

# Additional template variations for more diverse content
MORE_DEFINITION_TEMPLATES = [
    "A {} in Yoruba culture related to {}.",
    "The {} of {} in traditional settings.",
    "A {} used in {} ceremonies.",
    "An ancient {} associated with {} practices.",
    "A {} that symbolizes {} in Yoruba culture.",
    "One who is known for {} and {}.",
    "A special kind of {} used by {}.",
    "The {} that occurs during {}.",
    "A sacred {} used for {} purposes.",
    "The process of {} during {}.",
    "A traditional {} worn during {}.",
    "A {} that represents {} in daily life.",
    "The spiritual aspect of {} related to {}.",
    "A {} found in {} regions.",
    "A {} typically made from {}."
]

MORE_EXAMPLE_TEMPLATES_YORUBA = [
    "Àwọn àgbàlagbà máa ń lo {} fún àṣàrò.",
    "Ìdí tí a fi ń lo {} ni pé ó dára.",
    "Ní àṣà Yorùbá, {} jẹ́ ohun pàtàkì.",
    "Ní ọjọ́ àtijọ́, àwọn baba wa lo {}.",
    "Kò sí ènìyàn tí kò mọ ipa tí {} ń kó.",
    "Bí a bá fẹ́ ṣe àṣàrò, a ní láti lo {}.",
    "Gbogbo ìdílé ní ó gbọdọ̀ ní {} kan.",
    "A ti ń lo {} láti ìgbà pípẹ́.",
    "Ẹ jọ̀wọ́, ẹ má ṣe gbàgbé {} nígbà tí ẹ bá lọ.",
    "Ní ilé àwọn Yorùbá, {} wà ní ibi pàtàkì."
]

MORE_EXAMPLE_TEMPLATES_ENGLISH = [
    "Elders often use {} for meditation.",
    "The reason we use {} is because it is good.",
    "In Yoruba culture, {} is important.",
    "In ancient times, our fathers used {}.",
    "There is nobody who doesn't know the role that {} plays.",
    "If we want to meditate, we have to use {}.",
    "Every family must have one {}.",
    "We have been using {} for a long time.",
    "Please, don't forget {} when you go.",
    "In Yoruba homes, {} is kept in an important place."
]

def load_existing_dictionary(file_path):
    """Load the existing dictionary as a starting point"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def generate_enhanced_yoruba_word():
    """Generate a new Yoruba word with enhanced patterns for more variation"""
    # Enhanced word generation with more patterns
    
    # 1. Use existing word (less frequent to allow for more new words)
    if random.random() < 0.15:
        word_lists = [
            YORUBA_NOUNS + ADDITIONAL_YORUBA_NOUNS, 
            YORUBA_VERBS + ADDITIONAL_YORUBA_VERBS, 
            YORUBA_ADJECTIVES + ADDITIONAL_YORUBA_ADJECTIVES
        ]
        chosen_list = random.choice(word_lists)
        return random.choice(chosen_list)
    
    # 2. Generate new word
    if random.random() < 0.3:
        # Add prefix to base
        prefix = random.choice(YORUBA_PREFIXES)
        base = ""
        
        # Create a more complex base
        syllable_count = random.randint(1, 4)
        for _ in range(syllable_count):
            consonant = random.choice(YORUBA_CONSONANTS) if random.random() < 0.8 else ""
            
            # Sometimes use compound vowels
            if random.random() < 0.2:
                vowel = random.choice(YORUBA_COMPOUND_VOWELS)
            else:
                vowel = random.choice(YORUBA_VOWELS)
                
            tone = random.choice(YORUBA_TONES)
            base += consonant + vowel + tone
        
        return prefix + base
    
    elif random.random() < 0.6:
        # Complex syllable patterns
        syllable_count = random.randint(1, 4)
        word = ""
        
        for i in range(syllable_count):
            # First syllable is more likely to have a consonant
            if i == 0:
                consonant = random.choice(YORUBA_CONSONANTS) if random.random() < 0.9 else ""
            else:
                consonant = random.choice(YORUBA_CONSONANTS) if random.random() < 0.8 else ""
                
            # Sometimes use compound vowels for more variety
            if random.random() < 0.2:
                vowel = random.choice(YORUBA_COMPOUND_VOWELS)
            else:
                vowel = random.choice(YORUBA_VOWELS)
                
            tone = random.choice(YORUBA_TONES)
            word += consonant + vowel + tone
        
        # Add suffix sometimes
        if random.random() < 0.4:
            word += random.choice(YORUBA_SUFFIXES)
            
        return word
    
    elif random.random() < 0.8:
        # Compound word (combining two words)
        all_words = (YORUBA_NOUNS + ADDITIONAL_YORUBA_NOUNS + 
                    YORUBA_VERBS + ADDITIONAL_YORUBA_VERBS + 
                    YORUBA_ADJECTIVES + ADDITIONAL_YORUBA_ADJECTIVES)
        
        word1 = random.choice(all_words)
        word2 = random.choice(all_words)
        
        # Several patterns for combining
        if random.random() < 0.4:
            return word1 + word2[:3]  # First word + first part of second
        elif random.random() < 0.7:
            return word1[:3] + word2  # First part of first + second word
        else:
            middle = random.choice(["o", "a", "i", "u", "e"])
            return word1 + middle + word2  # Both words with a vowel in between
    
    else:
        # Reduplication (common in Yoruba)
        base = ""
        syllable_count = random.randint(1, 2)
        
        for _ in range(syllable_count):
            consonant = random.choice(YORUBA_CONSONANTS) if random.random() < 0.8 else ""
            vowel = random.choice(YORUBA_VOWELS)
            tone = random.choice(YORUBA_TONES)
            base += consonant + vowel + tone
            
        # Different patterns of reduplication
        if random.random() < 0.5:
            return base + base  # Full reduplication
        else:
            return base + "-" + base  # Reduplication with hyphen

def generate_enhanced_synonyms(headword, pos):
    """Generate a more extensive list of synonyms"""
    num_synonyms = random.randint(4, 7)  # More synonyms per entry
    synonyms = []
    
    # Include variations of the headword
    if len(headword) > 3:
        variations = []
        
        # Suffix variation
        if random.random() < 0.5:
            base = headword[:-1] if random.random() < 0.5 else headword[1:]
            variations.append(base + random.choice(YORUBA_SUFFIXES))
            
        # Prefix variation
        if random.random() < 0.5:
            new_prefix = random.choice(YORUBA_PREFIXES)
            if headword.startswith(tuple(YORUBA_PREFIXES)):
                # Replace existing prefix
                variations.append(new_prefix + headword[1:])
            else:
                # Add new prefix
                variations.append(new_prefix + headword)
                
        # Add a few variations
        for var in variations:
            if var != headword and var not in synonyms:
                synonyms.append(var)
    
    # Add words from standard lists
    base_lists = {
        "noun": YORUBA_NOUNS + ADDITIONAL_YORUBA_NOUNS,
        "verb": YORUBA_VERBS + ADDITIONAL_YORUBA_VERBS,
        "adjective": YORUBA_ADJECTIVES + ADDITIONAL_YORUBA_ADJECTIVES
    }
    
    # Get relevant list based on part of speech
    relevant_list = base_lists.get(pos, YORUBA_NOUNS + ADDITIONAL_YORUBA_NOUNS)
    
    # Add some words from relevant list
    attempt_count = 0
    while len(synonyms) < num_synonyms and attempt_count < 30:
        attempt_count += 1
        synonym = random.choice(relevant_list)
        if synonym != headword and synonym not in synonyms:
            synonyms.append(synonym)
    
    # Add generated words to fill remaining slots
    while len(synonyms) < num_synonyms:
        new_word = generate_enhanced_yoruba_word()
        if new_word != headword and new_word not in synonyms:
            synonyms.append(new_word)
    
    return synonyms

def generate_enhanced_definition(pos):
    """Generate a more varied definition"""
    # Combine both template lists for more variety
    all_templates = DEFINITION_TEMPLATES + MORE_DEFINITION_TEMPLATES
    template = random.choice(all_templates)
    
    if pos == "noun":
        word1 = random.choice(DEFINITION_NOUNS)
        word2 = random.choice(DEFINITION_NOUNS)
    elif pos == "verb":
        word1 = random.choice(DEFINITION_VERBS)
        word2 = random.choice(DEFINITION_VERBS)
    else:  # adjective
        word1 = random.choice(DEFINITION_ADJECTIVES)
        word2 = random.choice(DEFINITION_ADJECTIVES)
    
    return template.format(word1, word2)

def generate_enhanced_example(headword):
    """Generate more varied example sentences"""
    # Combine both template lists for more variety
    all_yoruba_templates = EXAMPLE_TEMPLATES_YORUBA + MORE_EXAMPLE_TEMPLATES_YORUBA
    all_english_templates = EXAMPLE_TEMPLATES_ENGLISH + MORE_EXAMPLE_TEMPLATES_ENGLISH
    
    yoruba_template = random.choice(all_yoruba_templates)
    english_template = random.choice(all_english_templates)
    
    return {
        "yorùbá": yoruba_template.format(headword),
        "en": english_template.format(headword)
    }

def generate_enhanced_entry():
    """Generate a complete dictionary entry with enhanced variety"""
    # Choose a part of speech
    pos = random.choice(["noun", "verb", "adjective"])
    
    # Generate a headword using the enhanced method
    headword = generate_enhanced_yoruba_word()
    
    # Generate enhanced synonyms
    synonyms = generate_enhanced_synonyms(headword, pos)
    
    # Generate enhanced definition
    definition = generate_enhanced_definition(pos)
    
    # Generate enhanced example
    example = generate_enhanced_example(headword)
    
    return {
        "headword": headword,
        "pos": pos,
        "synonyms": synonyms,
        "definition": definition,
        "example": example
    }

def expand_massive_dictionary(input_file, output_file, target_count=100000, batch_size=1000):
    """Expand the dictionary to a massive number of entries, saving in batches"""
    print(f"Loading existing dictionary from {input_file}...")
    dictionary = load_existing_dictionary(input_file)
    
    current_count = len(dictionary)
    print(f"Current dictionary has {current_count} entries.")
    
    entries_to_add = max(0, target_count - current_count)
    print(f"Need to generate {entries_to_add} new entries.")
    
    if entries_to_add == 0:
        print("Dictionary already contains the target number of entries.")
        return current_count
    
    # Track new headwords to avoid duplicates
    existing_headwords = set(dictionary.keys())
    
    # Set up progress bar
    pbar = tqdm(total=entries_to_add, desc="Generating entries")
    
    # Track time
    start_time = time.time()
    
    # Generate in batches and save intermediate results
    for batch_start in range(0, entries_to_add, batch_size):
        batch_end = min(batch_start + batch_size, entries_to_add)
        batch_size_actual = batch_end - batch_start
        
        for _ in range(batch_size_actual):
            # Keep trying until we get a unique headword
            attempt_count = 0
            while attempt_count < 50:  # Limit attempts to avoid infinite loops
                attempt_count += 1
                entry = generate_enhanced_entry()
                headword = entry["headword"]
                
                if headword not in existing_headwords:
                    dictionary[headword] = entry
                    existing_headwords.add(headword)
                    pbar.update(1)
                    break
            
            # If we couldn't find a unique headword after many attempts, add a random suffix
            if attempt_count >= 50:
                headword = headword + str(random.randint(1, 999))
                entry["headword"] = headword
                dictionary[headword] = entry
                existing_headwords.add(headword)
                pbar.update(1)
        
        # Calculate and display stats
        elapsed_time = time.time() - start_time
        entries_per_second = (batch_start + batch_size_actual) / elapsed_time if elapsed_time > 0 else 0
        estimated_remaining = (entries_to_add - (batch_start + batch_size_actual)) / entries_per_second if entries_per_second > 0 else 0
        
        print(f"\nBatch {batch_start+1}-{batch_end} complete. " + 
              f"Speed: {entries_per_second:.2f} entries/sec. " + 
              f"Est. remaining time: {estimated_remaining/60:.1f} minutes.")
        
        # Save intermediate results
        intermediate_file = f"{output_file}.partial"
        print(f"Saving intermediate dictionary with {len(dictionary)} entries...")
        with open(intermediate_file, 'w', encoding='utf-8') as f:
            json.dump(dictionary, f, ensure_ascii=False, indent=None)  # Use compact JSON to save space
    
    pbar.close()
    
    # Final save with pretty formatting
    print(f"Writing final dictionary with {len(dictionary)} entries to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(dictionary, f, ensure_ascii=False, indent=2)
    
    # Clean up intermediate file
    if os.path.exists(intermediate_file):
        os.remove(intermediate_file)
    
    # Report stats
    total_time = time.time() - start_time
    print(f"\nDictionary expansion complete!")
    print(f"Total time: {total_time/60:.2f} minutes")
    print(f"Average speed: {entries_to_add/total_time:.2f} entries/second")
    print(f"Final dictionary contains {len(dictionary)} entries.")
    
    return len(dictionary)

if __name__ == "__main__":
    input_file = "yoruba_synonyms_expanded.json"
    output_file = "yoruba_synonyms_massive.json"
    target_count = 100000
    batch_size = 1000
    
    # Parse command line arguments if provided
    if len(sys.argv) > 1:
        try:
            target_count = int(sys.argv[1])
        except ValueError:
            print(f"Invalid target count: {sys.argv[1]}")
            print(f"Using default: {target_count}")
    
    # Show warning for very large dictionaries
    if target_count > 100000:
        print("\n⚠️ WARNING: Generating a very large dictionary may:")
        print("  - Take a significant amount of time")
        print("  - Use substantial disk space")
        print("  - Require significant memory")
        print("\nThe process can be stopped at any time with Ctrl+C, and partial results will be saved.")
        
        # Ask for confirmation
        confirm = input(f"\nAre you sure you want to generate {target_count} entries? (y/n): ")
        if confirm.lower() != 'y':
            print("Operation cancelled.")
            sys.exit(0)
    
    print(f"\nStarting massive dictionary expansion to {target_count} entries...")
    print(f"Input file: {input_file}")
    print(f"Output file: {output_file}")
    print(f"Batch size: {batch_size}\n")
    
    try:
        final_count = expand_massive_dictionary(input_file, output_file, target_count, batch_size)
        print(f"Final dictionary contains {final_count} entries.")
    except KeyboardInterrupt:
        print("\nProcess interrupted by user. Partial results may have been saved.")
        sys.exit(1) 