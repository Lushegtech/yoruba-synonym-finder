# Yorùbá Synonym Finder (Simplified)

A lightweight, dictionary-based Yoruba Synonym Finder that works offline without needing external APIs or complex model dependencies.

## Overview

This project creates a simple Yoruba synonym finder using a static dictionary approach:
1. **Static Dictionary**: A pre-built JSON dictionary with common Yoruba words and their synonyms
2. **CLI Interface**: A command-line tool for searching synonyms
3. **Web Interface**: A Streamlit web app for a user-friendly search experience

## Prerequisites

- Python 3.6+
- pip (Python package manager)

Required Python packages (minimal dependencies):
```bash
pip install -r requirements.txt
```

## Usage

### Command Line Interface

Query the synonym finder from the command line:

```bash
python simple_query.py
```

This runs an interactive REPL where you can type Yoruba words and see their synonyms.

You can also run a single query directly:

```bash
python simple_query.py --query "ilé"
```

### Web Interface

Launch the Streamlit web app:

```bash
streamlit run simple_app.py
```

This starts a web server (typically at http://localhost:8501) where you can search for synonyms through a user-friendly interface.

## Dictionary Structure

The system uses a static JSON dictionary (`yoruba_synonyms_static.json`) with the following structure:

```json
{
  "ilé": {
    "headword": "ilé",
    "pos": "noun",
    "synonyms": ["ilẹ̀", "ibùgbé", "afin", "ààfin", "ìdí"],
    "definition": "House or building where people live or work.",
    "example": {
      "yorùbá": "Mo wà ní ilé mi.",
      "en": "I am at my house."
    }
  },
  ...
}
```

## Project Structure

```
├── simple_query.py          # CLI for querying synonyms
├── simple_app.py            # Streamlit web app
├── yoruba_synonyms_static.json  # Static dictionary with synonyms
└── requirements.txt         # Minimal dependencies
```

## Search Features

The system searches for synonyms in several ways:
- **Exact Match**: Finds exact matches for headwords
- **Synonym Match**: Checks if the query word appears in any synonym list
- **Fuzzy Match**: Uses string similarity to find close matches for unknown words

## Extending the Dictionary

To add more words to the dictionary, simply edit the `yoruba_synonyms_static.json` file following the same format:

```json
"new_word": {
  "headword": "new_word",
  "pos": "noun",
  "synonyms": ["synonym1", "synonym2", "synonym3", "synonym4", "synonym5"],
  "definition": "Definition of the word.",
  "example": {
    "yorùbá": "Example sentence in Yoruba.",
    "en": "Example sentence in English."
  }
}
```

## Troubleshooting

- If tone marks don't display correctly, ensure your terminal and browser support Unicode.
- This version uses pure Python and doesn't require external APIs or complex models, which avoids many of the previous compatibility issues.

## Legacy System

The original implementation using transformer models and FAISS search is still available in the following files:
- `get_common.py` - Extract common Yoruba words
- `generate_entries.py` - Generate synonym entries with transformer models
- `build_index.py` - Build FAISS search index
- `query.py` - CLI for the model-based version
- `app.py` - Streamlit web app for the model-based version

To use the legacy system, follow the instructions in the original README, but be aware that it requires more dependencies and external models. 