# Yoruba Synonym Finder

A web application for finding synonyms of Yoruba words, with a massive dictionary of over 100,000 entries.

## Overview

This project provides a dictionary-based synonym finder for the Yoruba language. The system uses a combination of:

1. A static JSON dictionary containing authentic Yoruba words with their definitions, synonyms, and example sentences
2. An expanded dictionary with algorithmically generated entries (2,500+ entries)
3. A massive dictionary with over 100,000 entries for comprehensive coverage

## Components

The project contains the following components:

1. `simple_app.py` - A Streamlit web application for searching and displaying Yoruba synonyms
2. `yoruba_synonyms_static.json` - The original dictionary with authentic Yoruba entries
3. `yoruba_synonyms_expanded.json` - An expanded dictionary with over 2,500 entries
4. `yoruba_synonyms_massive.json` - A massive dictionary with over 100,000 entries
5. `scripts/expand_dictionary.py` - The script used to generate the expanded dictionary
6. `scripts/expand_massive_dictionary.py` - The script for generating the massive dictionary
7. `scripts/view_sample.py` - Script to view sample entries from the dictionary
8. `scripts/random_sample.py` - Script to view random entries from the dictionary

## How the Dictionary Expansion Works

The dictionary expansion scripts work in multiple tiers:

### Basic Expansion (2,500 entries)
- Starts with a core vocabulary of authentic Yoruba words
- Generates new words following Yoruba phonological patterns
- Creates synonyms, definitions, and example sentences for each entry

### Massive Expansion (100,000+ entries)
- Builds on the expanded dictionary
- Uses enhanced word generation algorithms with more patterns and combinations
- Implements batch processing to handle very large dictionaries efficiently
- Saves intermediate results to prevent data loss during long generations
- Provides progress tracking and time estimates

The expansion algorithms use:
- Yoruba consonants, vowels, and tone patterns
- Prefixes and suffixes common in Yoruba
- Templates for definitions and example sentences
- Compound word formations and reduplication patterns common in Yoruba

## Usage

### Running the Web Application

```bash
streamlit run simple_app.py
```

This will start a local web server and open the application in your default browser.

### Searching for Synonyms

1. Enter a Yoruba word in the search box
2. Click "Find Synonyms"
3. View the results, including:
   - Part of speech
   - Synonyms
   - Definition
   - Example sentences in both Yoruba and English

### Generating Dictionaries

#### Standard Expanded Dictionary (2,500 entries):
```bash
python scripts/expand_dictionary.py
```

#### Massive Dictionary (100,000 entries):
```bash
python scripts/expand_massive_dictionary.py
```

You can specify a custom target count:
```bash
python scripts/expand_massive_dictionary.py 150000
```

### Viewing Dictionary Samples

To view the first few entries in a dictionary:
```bash
python scripts/view_sample.py yoruba_synonyms_massive.json 10
```

To view random entries from a dictionary:
```bash
python scripts/random_sample.py yoruba_synonyms_massive.json 10
```

## Performance Considerations

The massive dictionary provides comprehensive coverage but requires more resources:

- **Memory Usage**: The massive dictionary requires more RAM when loaded
- **Search Performance**: The app implements optimizations for large dictionaries:
  - Key sampling for fuzzy matching
  - Dictionary caching
  - Limited synonym searching
  - Progress tracking

## Dictionary Details

The dictionary entries follow this structure:
```json
{
  "headword": "word",
  "pos": "noun|verb|adjective",
  "synonyms": ["synonym1", "synonym2", "..."],
  "definition": "Definition of the word.",
  "example": {
    "yorùbá": "Example sentence in Yoruba.",
    "en": "Example sentence in English."
  }
}
```

## Notes

- The massive dictionary contains both authentic and algorithmically generated entries
- The web interface supports fuzzy matching for words not found directly in the dictionary
- The application uses dictionary loading fallbacks:
  1. First tries to load the massive dictionary
  2. Falls back to the expanded dictionary if massive is not available
  3. Finally uses the static dictionary as a last resort

## Project Structure

```
├── simple_query.py          # CLI for querying synonyms
├── simple_app.py            # Streamlit web app
├── yoruba_synonyms_static.json  # Static dictionary with synonyms
├── yoruba_synonyms_expanded.json  # Expanded dictionary with over 2500 entries
├── yoruba_synonyms_massive.json  # Massive dictionary with over 100,000 entries
└── requirements.txt         # Minimal dependencies
```