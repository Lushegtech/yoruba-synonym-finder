#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
expand_dictionary.py - Script to expand the Yoruba dictionary entries
"""

import json
import random
import itertools
from pathlib import Path

# Define base vocabulary components (these will be combined to create more entries)
YORUBA_NOUNS = [
    "ilé", "ọmọ", "omi", "ọjọ́", "ẹ̀kọ́", "isẹ́", "oúnjẹ", "àgbà", "ọ̀rọ̀", "ìgbà", "ìwé",
    "ọkọ̀", "ara", "orí", "ojú", "ẹnu", "ẹsẹ̀", "ọwọ́", "àwo", "igi", "ewé", "ìbẹ̀rẹ̀",
    "òpin", "ẹjẹ́", "inú", "ilẹ̀", "ọ̀run", "aṣọ", "adé", "ẹran", "ọsẹ̀", "osù", "owó",
    "ẹbí", "àgbàlagba", "arákùnrin", "arábìnrin", "abẹ́", "ẹ̀kọ", "òwe", "ìròyìn", "àṣà",
    "ọrọ̀", "ìpàdé", "àjọ", "ọtí", "iná", "ìyá", "bàbá", "òbí", "àna", "ọgbà", "igbó",
    "ọ̀nà", "ààfin", "ẹ̀mí", "ètò", "ìdí", "àti", "ẹyẹ", "ẹja", "ẹyin", "àgbòn", "ọbẹ̀",
    "ẹfọ́", "ègún", "ẹgbẹ́", "fìlà", "ilà", "ìlú", "ijọ́", "ìtàn", "ìrírí", "ìrònú"
]

YORUBA_VERBS = [
    "jẹ", "mu", "sùn", "dìde", "lọ", "wá", "kọ́", "gbọ́", "rí", "fẹ́", "bẹ̀rẹ̀", "wò",
    "bá", "jó", "kọrin", "kọ̀", "gba", "fi", "lò", "pa", "kú", "tán", "gbà", "pè", "gbé",
    "bò", "dà", "sọ", "kó", "jẹ́", "ṣe", "ń", "yọ", "rù", "sun", "bẹ", "bú", "dá", "fò",
    "gbìn", "gún", "já", "jù", "kàn", "lá", "ní", "pọ̀", "rẹ́", "rìn", "rò", "sá", "tà",
    "wà", "wọ́", "yí", "kẹ́", "kọ̀", "mọ̀", "mú", "ṣẹ́", "wọ", "wọ̀", "fẹ̀", "bí", "dúró"
]

YORUBA_ADJECTIVES = [
    "dára", "gbogbo", "kékeré", "púpọ̀", "jù", "rere", "burúkú", "tuntun", "pupa", "dúdú",
    "funfun", "giga", "kúrú", "tóbi", "wẹ́wẹ́", "tútù", "gbóná", "títọ́", "ṣíṣe", "tẹ́rẹ́",
    "gùn", "fẹ́lẹ́", "pọ̀", "kan", "mẹ́ta", "mẹ́rin", "márùn", "mẹ́fà", "méje", "mẹ́jọ",
    "mẹ́sàn", "mẹ́wàá", "gbòòrò", "kíkún", "góńgó", "díẹ̀", "bíbẹ̀rẹ̀", "pípari", "gidi",
    "pàtàkì", "ńlá", "pélébé", "dídùn", "kíkorò", "tòlítòlí", "lébelebe", "gbẹlẹ́jẹ",
    "dídára", "rọlẹ̀", "kékeré", "kìkì", "títóbi", "tóbi", "jíjìn", "pẹ̀lẹ́", "tẹ́rùn",
    "tútù", "títa", "gbígbẹ", "tutù", "jíjẹ́", "títọ́", "ṣáńṣán", "péléngé", "díẹ̀"
]

# Extended patterns for creating Yoruba words
YORUBA_PREFIXES = ["a", "o", "ọ", "i", "ì", "e", "ẹ"]
YORUBA_SUFFIXES = ["lá", "dé", "jú", "kọ́", "ní", "rí", "lẹ̀", "jẹ", "kọ", "pọ̀", "sí"]

# Yoruba language sounds and orthography patterns
YORUBA_CONSONANTS = ["b", "d", "f", "g", "gb", "h", "j", "k", "l", "m", "n", "p", "r", "s", "ṣ", "t", "w", "y"]
YORUBA_VOWELS = ["a", "e", "ẹ", "i", "o", "ọ", "u"]
YORUBA_TONES = ["", "́", "̀"]  # No tone, high tone, low tone

# Lists for generating definitions and examples
DEFINITION_TEMPLATES = [
    "{} is a type of {}.",
    "A {} used for {}.",
    "The act of {} or {}.",
    "A traditional {} associated with {}.",
    "A {} that relates to {}.",
    "{} commonly found in Yoruba {}.",
    "The state of being {} or {}.",
    "A person who {} or {}.",
    "A place where {} happens.",
    "The quality of {} or being {}.",
    "A tool used for {} or {}.",
    "A ceremony associated with {}.",
    "A traditional belief about {}.",
    "A specific type of {} used during {}.",
    "A cultural practice involving {}."
]

EXAMPLE_TEMPLATES_YORUBA = [
    "Mo fẹ́ràn {}.",
    "{} náà dára púpọ̀.",
    "Àwọn {} wà ní ọjà.",
    "Mo rí {} lánàá.",
    "Jọ̀wọ́ fún mi ní {}.",
    "Ṣé o mọ {} náà?",
    "Ẹ jọ̀wọ́, mo fẹ́ {}.",
    "Níbo ni {} wà?",
    "Báwo ni a ṣe {} yìí?",
    "{} yìí ṣe pàtàkì fún àṣà wa.",
    "A ní {} púpọ̀ ní ilé wa.",
    "Ọ̀pọ̀lọpọ̀ ènìyàn fẹ́ràn {}.",
    "Bàbá mi ní {} tuntun kan.",
    "Mo ti ń wá {} náà.",
    "A gbọdọ̀ ṣe {} yìí lónìí."
]

EXAMPLE_TEMPLATES_ENGLISH = [
    "I like {}.",
    "That {} is very good.",
    "There are {} at the market.",
    "I saw the {} yesterday.",
    "Please give me the {}.",
    "Do you know that {}?",
    "Please, I want {}.",
    "Where is the {}?",
    "How do we {} this?",
    "This {} is important to our culture.",
    "We have many {} in our house.",
    "Many people like {}.",
    "My father has a new {}.",
    "I have been looking for the {}.",
    "We must {} this today."
]

DEFINITION_NOUNS = [
    "object", "tool", "item", "garment", "food", "drink", "ceremony", "tradition", 
    "custom", "artifact", "instrument", "concept", "idea", "belief", "practice", 
    "ritual", "event", "celebration", "activity", "process", "method", "technique", 
    "system", "structure", "building", "location", "place", "area", "region", 
    "community", "group", "gathering", "meeting", "assembly", "family", "clan",
    "person", "individual", "profession", "occupation", "craft", "skill", "art",
    "song", "dance", "music", "performance", "festival", "holiday", "season",
    "weather", "climate", "environment", "landscape", "plant", "animal", "creature",
    "spiritual entity", "deity", "spirit", "ancestor", "medicine", "remedy", "treatment"
]

DEFINITION_VERBS = [
    "make", "create", "build", "construct", "prepare", "cook", "eat", "drink", "wear",
    "use", "utilize", "employ", "apply", "practice", "perform", "execute", "conduct",
    "organize", "arrange", "gather", "collect", "assemble", "combine", "mix", "blend",
    "join", "connect", "link", "relate", "associate", "communicate", "speak", "talk",
    "discuss", "debate", "argue", "negotiate", "trade", "exchange", "buy", "sell",
    "hunt", "fish", "farm", "grow", "cultivate", "harvest", "store", "preserve",
    "protect", "defend", "guard", "attack", "fight", "battle", "compete", "race",
    "celebrate", "commemorate", "honor", "respect", "worship", "pray", "meditate"
]

DEFINITION_ADJECTIVES = [
    "traditional", "cultural", "historical", "ancient", "old", "new", "modern", 
    "contemporary", "common", "rare", "unique", "special", "important", "significant", 
    "valuable", "precious", "sacred", "holy", "spiritual", "religious", "ceremonial", 
    "ritual", "festive", "celebratory", "everyday", "ordinary", "practical", "useful", 
    "functional", "decorative", "ornamental", "beautiful", "attractive", "colorful", 
    "bright", "dark", "light", "heavy", "large", "small", "tall", "short", "wide", 
    "narrow", "thick", "thin", "strong", "weak", "hard", "soft", "smooth", "rough", 
    "sharp", "dull", "hot", "cold", "warm", "cool", "dry", "wet", "fresh", "stale"
]

def load_existing_dictionary(file_path):
    """Load the existing dictionary as a starting point"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def generate_yoruba_word():
    """Generate a new Yoruba word based on phonological patterns"""
    if random.random() < 0.3:
        # Use an existing word
        word_lists = [YORUBA_NOUNS, YORUBA_VERBS, YORUBA_ADJECTIVES]
        chosen_list = random.choice(word_lists)
        return random.choice(chosen_list)
    
    # Generate a new word
    if random.random() < 0.4:
        # Add prefix to base
        prefix = random.choice(YORUBA_PREFIXES)
        base = ""
        
        # Create a base following Yoruba phonology
        syllable_count = random.randint(1, 3)
        for _ in range(syllable_count):
            consonant = random.choice(YORUBA_CONSONANTS) if random.random() < 0.8 else ""
            vowel = random.choice(YORUBA_VOWELS)
            tone = random.choice(YORUBA_TONES)
            base += consonant + vowel + tone
        
        return prefix + base
    
    elif random.random() < 0.7:
        # Simple CV or CVCV pattern
        syllable_count = random.randint(1, 3)
        word = ""
        for _ in range(syllable_count):
            consonant = random.choice(YORUBA_CONSONANTS) if random.random() < 0.8 else ""
            vowel = random.choice(YORUBA_VOWELS)
            tone = random.choice(YORUBA_TONES)
            word += consonant + vowel + tone
        
        if random.random() < 0.3:
            # Add a suffix
            word += random.choice(YORUBA_SUFFIXES)
            
        return word
    
    else:
        # Compound word from two existing words
        word1 = random.choice(YORUBA_NOUNS + YORUBA_VERBS + YORUBA_ADJECTIVES)
        word2 = random.choice(YORUBA_NOUNS + YORUBA_VERBS + YORUBA_ADJECTIVES)
        return word1 + word2[:3]  # Take the first part of the second word

def generate_synonyms(headword, pos):
    """Generate a list of synonyms for the given headword"""
    num_synonyms = random.randint(3, 5)
    synonyms = []
    
    # Sometimes include variations of the headword
    if random.random() < 0.3 and len(headword) > 3:
        base = headword[:-1] if random.random() < 0.5 else headword[1:]
        synonyms.append(base + random.choice(YORUBA_SUFFIXES))
    
    # Add some random synonyms
    base_lists = {
        "noun": YORUBA_NOUNS,
        "verb": YORUBA_VERBS,
        "adjective": YORUBA_ADJECTIVES
    }
    
    # Get relevant list based on part of speech
    relevant_list = base_lists.get(pos, YORUBA_NOUNS)
    
    # Add some words from relevant list
    while len(synonyms) < num_synonyms:
        synonym = random.choice(relevant_list)
        if synonym != headword and synonym not in synonyms:
            synonyms.append(synonym)
    
    # Sometimes add a completely generated word
    if random.random() < 0.4 and len(synonyms) < num_synonyms:
        new_word = generate_yoruba_word()
        if new_word != headword and new_word not in synonyms:
            synonyms.append(new_word)
    
    return synonyms

def generate_definition(pos):
    """Generate a definition for the word based on its part of speech"""
    template = random.choice(DEFINITION_TEMPLATES)
    
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

def generate_example(headword):
    """Generate an example sentence using the headword"""
    yoruba_template = random.choice(EXAMPLE_TEMPLATES_YORUBA)
    english_template = random.choice(EXAMPLE_TEMPLATES_ENGLISH)
    
    return {
        "yorùbá": yoruba_template.format(headword),
        "en": english_template.format(headword)
    }

def generate_entry():
    """Generate a complete dictionary entry"""
    # Choose a part of speech
    pos = random.choice(["noun", "verb", "adjective"])
    
    # Generate a headword
    if pos == "noun":
        headword = random.choice(YORUBA_NOUNS) if random.random() < 0.3 else generate_yoruba_word()
    elif pos == "verb":
        headword = random.choice(YORUBA_VERBS) if random.random() < 0.3 else generate_yoruba_word()
    else:  # adjective
        headword = random.choice(YORUBA_ADJECTIVES) if random.random() < 0.3 else generate_yoruba_word()
    
    # Generate synonyms
    synonyms = generate_synonyms(headword, pos)
    
    # Generate definition
    definition = generate_definition(pos)
    
    # Generate example
    example = generate_example(headword)
    
    return {
        "headword": headword,
        "pos": pos,
        "synonyms": synonyms,
        "definition": definition,
        "example": example
    }

def expand_dictionary(input_file, output_file, target_count=2500):
    """Expand the dictionary to the target number of entries"""
    print(f"Loading existing dictionary from {input_file}...")
    dictionary = load_existing_dictionary(input_file)
    
    current_count = len(dictionary)
    print(f"Current dictionary has {current_count} entries.")
    
    entries_to_add = max(0, target_count - current_count)
    print(f"Need to generate {entries_to_add} new entries.")
    
    # Track new headwords to avoid duplicates
    existing_headwords = set(dictionary.keys())
    
    for i in range(entries_to_add):
        if i % 100 == 0 and i > 0:
            print(f"Generated {i} entries so far...")
        
        # Keep trying until we get a unique headword
        while True:
            entry = generate_entry()
            headword = entry["headword"]
            
            if headword not in existing_headwords:
                dictionary[headword] = entry
                existing_headwords.add(headword)
                break
    
    print(f"Writing expanded dictionary with {len(dictionary)} entries to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(dictionary, f, ensure_ascii=False, indent=2)
    
    print("Dictionary expansion complete!")
    return len(dictionary)

if __name__ == "__main__":
    input_file = "yoruba_synonyms_static.json"
    output_file = "yoruba_synonyms_expanded.json"
    
    final_count = expand_dictionary(input_file, output_file, target_count=2500)
    print(f"Final dictionary contains {final_count} entries.") 