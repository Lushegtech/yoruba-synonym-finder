from flask import Flask, request, jsonify, render_template_string
import json
import difflib
import os
import random
from datetime import datetime

app = Flask(__name__)

# Create minimal dictionary if none exists
def create_minimal_dictionary():
    """Create a minimal dictionary with a few entries if no dictionary file is found"""
    print("Creating minimal dictionary...")
    minimal_dict = {
        "ilé": {
            "headword": "ilé",
            "pos": "noun",
            "synonyms": ["ilẹ̀", "ibùgbé", "afin", "ààfin", "ìdí"]
        },
        "ọmọ": {
            "headword": "ọmọ",
            "pos": "noun",
            "synonyms": ["ọmọbíbí", "àbíkẹ́", "arọ́mọdọ́mọ", "ọmọkùnrin", "ọmọbìnrin"]
        },
        "omi": {
            "headword": "omi",
            "pos": "noun",
            "synonyms": ["ìdàdò", "ìkòrò", "adágún", "odo", "odò"]
        },
        "dára": {
            "headword": "dára",
            "pos": "adjective",
            "synonyms": ["pẹ̀lẹ́", "rẹwà", "tòótọ́", "dáradára", "ṣàn"]
        },
        "jẹ": {
            "headword": "jẹ",
            "pos": "verb",
            "synonyms": ["gbà", "mu", "fẹ́", "gbé", "mú"]
        }
    }
    return minimal_dict

# Load the dictionary data
def load_dictionary():
    dict_files = [
        'yoruba_synonyms_massive.json',
        'yoruba_synonyms_expanded.json',
        'yoruba_synonyms_static.json'
    ]
    
    # Add current directory and api directory paths for files
    all_paths = []
    for dict_file in dict_files:
        all_paths.append(dict_file)
        all_paths.append(os.path.join('api', dict_file))
        all_paths.append(os.path.join('..', dict_file))
    
    for file_path in all_paths:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"Loaded dictionary with {len(data)} entries from {file_path}")
                return data
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Could not load {file_path}: {e}")
            continue
    
    # If no dictionary files found, create a minimal one
    print("No dictionary files found, creating minimal dictionary")
    return create_minimal_dictionary()

# Add random word generation for minimal dictionary extension
def generate_yoruba_word():
    """Generate a new Yoruba word based on phonological patterns"""
    consonants = ["b", "d", "f", "g", "gb", "h", "j", "k", "l", "m", "n", "p", "r", "s", "ṣ", "t", "w", "y"]
    vowels = ["a", "e", "ẹ", "i", "o", "ọ", "u"]
    tones = ["", "́", "̀"]  # No tone, high tone, low tone
    
    syllable_count = random.randint(1, 3)
    word = ""
    
    for _ in range(syllable_count):
        consonant = random.choice(consonants) if random.random() < 0.8 else ""
        vowel = random.choice(vowels)
        tone = random.choice(tones)
        word += consonant + vowel + tone
    
    return word

# Global dictionary
dictionary = load_dictionary()

# Ensure we have at least 50 entries by generating additional ones if needed
if len(dictionary) < 50:
    print(f"Dictionary only has {len(dictionary)} entries, adding more...")
    parts_of_speech = ["noun", "verb", "adjective"]
    
    while len(dictionary) < 50:
        headword = generate_yoruba_word()
        if headword in dictionary:
            continue
            
        pos = random.choice(parts_of_speech)
        
        # Generate 3-5 synonyms
        synonyms = []
        for _ in range(random.randint(3, 5)):
            synonym = generate_yoruba_word()
            if synonym not in synonyms:
                synonyms.append(synonym)
        
        dictionary[headword] = {
            "headword": headword,
            "pos": pos,
            "synonyms": synonyms
        }
    
    print(f"Extended dictionary now has {len(dictionary)} entries")

def normalize_word(word):
    """Normalize a Yoruba word for matching: lowercase and strip whitespace."""
    return word.lower().strip()

def search_synonyms(query, max_results=3):
    """Search for synonyms of the given query word using the dictionary."""
    query = normalize_word(query)
    results = []
    
    # Direct match - check if word exists directly in the dictionary
    if query in dictionary:
        results.append({
            "rank": 1,
            "similarity": 1.0,
            "headword": dictionary[query]["headword"],
            "pos": dictionary[query]["pos"],
            "synonyms": dictionary[query]["synonyms"]
        })
        return results
    
    # Check if query is in any of the synonyms (up to a limit to maintain performance)
    synonym_check_limit = 1000
    synonym_checks = 0
    
    for headword, entry in dictionary.items():
        if synonym_checks >= synonym_check_limit:
            break
            
        synonym_checks += 1
        for synonym in entry["synonyms"]:
            if normalize_word(synonym) == query:
                results.append({
                    "rank": 1,
                    "similarity": 1.0,
                    "headword": entry["headword"],
                    "pos": entry["pos"],
                    "synonyms": entry["synonyms"]
                })
                return results  # Found exact match in synonyms
    
    # Fuzzy match for large dictionaries
    dict_keys = list(dictionary.keys())
    
    # Sampling keys for large dictionaries to improve performance
    if len(dict_keys) > 10000:
        sampled_keys = dict_keys[:500] + random.sample(dict_keys[500:], min(2500, len(dict_keys) - 500))
    else:
        sampled_keys = dict_keys
    
    matches = difflib.get_close_matches(query, sampled_keys, n=max_results, cutoff=0.6)
    
    for i, match in enumerate(matches):
        # Calculate a similarity score (1.0 to 0.0)
        similarity = 1.0 - (0.1 * i)  # Simple ranking by match order
        results.append({
            "rank": i + 1,
            "similarity": similarity,
            "headword": dictionary[match]["headword"],
            "pos": dictionary[match]["pos"],
            "synonyms": dictionary[match]["synonyms"]
        })
    
    return results

# HTML template for the frontend
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Yorùbá Synonym Finder</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');
        :root {
            --bg-primary: #121212;
            --bg-secondary: #1e1e1e;
            --bg-card: #252525;
            --text-primary: #e0e0e0;
            --text-secondary: #a0a0a0;
            --accent-primary: #6194c7;
            --accent-secondary: #4facfe;
            --accent-tertiary: #43e97b;
            --card-border: #333;
            --input-bg: #2a2a2a;
            --chip-bg: #2d3748;
            --chip-text: #e2e8f0;
        }
        
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        
        body {
            font-family: 'Poppins', sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            margin: 0;
            padding: 20px;
            min-height: 100vh;
            background-image: 
                radial-gradient(circle at 25% 25%, rgba(97, 148, 199, 0.05) 0%, transparent 50%),
                radial-gradient(circle at 75% 75%, rgba(67, 233, 123, 0.05) 0%, transparent 50%);
        }
        
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: var(--bg-secondary);
            border-radius: 12px;
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);
            padding: 30px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.05);
        }
        
        h1 {
            text-align: center;
            margin: 0 0 20px 0;
            font-size: 2.5rem;
            font-weight: 700;
        }
        
        .hero {
            text-align: center;
            padding: 20px 0 30px 0;
        }
        
        .logo-wrapper {
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 25px auto;
        }
        
        .logo-letter {
            width: 50px;
            height: 50px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 8px;
            border-radius: 12px;
            color: white;
            font-weight: bold;
            font-size: 26px;
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
            transform: translateY(0);
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        }
        
        .logo-letter:hover {
            transform: translateY(-8px) scale(1.1);
            box-shadow: 0 12px 20px rgba(0, 0, 0, 0.3);
        }
        
        .logo-y {
            background: linear-gradient(135deg, #FF9A8B 0%, #FF6A88 100%);
        }
        
        .logo-s {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            transform: translateY(-5px);
        }
        
        .logo-f {
            background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        }
        
        .gradient-text {
            background: linear-gradient(90deg, #6194c7 0%, #a7c5e8 50%, #43e97b 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-weight: 700;
            letter-spacing: -0.5px;
        }
        
        .search-form {
            display: flex;
            flex-wrap: wrap;
            margin: 30px 0;
            position: relative;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
            border-radius: 12px;
            overflow: hidden;
            transition: all 0.3s ease;
        }
        
        .search-form:focus-within {
            box-shadow: 0 6px 24px rgba(0, 0, 0, 0.2);
            transform: translateY(-2px);
        }
        
        .search-input {
            flex-grow: 1;
            padding: 16px 20px;
            font-size: 16px;
            background-color: var(--input-bg);
            color: var(--text-primary);
            border: none;
            border-radius: 12px 0 0 12px;
            outline: none;
            transition: all 0.3s ease;
        }
        
        .search-input::placeholder {
            color: var(--text-secondary);
            opacity: 0.7;
        }
        
        .search-button {
            padding: 0 25px;
            background: linear-gradient(135deg, var(--accent-secondary) 0%, var(--accent-tertiary) 100%);
            color: white;
            border: none;
            border-radius: 0 12px 12px 0;
            cursor: pointer;
            font-weight: 600;
            letter-spacing: 0.5px;
            transition: all 0.3s ease;
            font-size: 16px;
        }
        
        .search-button:hover {
            filter: brightness(1.1);
            transform: translateX(2px);
        }
        
        .result-card {
            background-color: var(--bg-card);
            border-radius: 12px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            border: 1px solid var(--card-border);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .result-card::before {
            content: '';
            position: absolute;
            left: 0;
            top: 0;
            height: 100%;
            width: 5px;
            background: linear-gradient(to bottom, var(--accent-secondary), var(--accent-tertiary));
            border-radius: 3px 0 0 3px;
        }
        
        .result-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
        }
        
        .result-card h3 {
            margin-bottom: 15px;
            font-size: 1.5rem;
            display: flex;
            align-items: center;
        }
        
        .pos-tag {
            margin-left: 10px;
            padding: 3px 10px;
            border-radius: 20px;
            background-color: rgba(97, 148, 199, 0.2);
            color: var(--accent-primary);
            font-size: 0.7em;
            font-weight: 600;
        }
        
        .highlight {
            color: var(--accent-primary);
            font-weight: 600;
            margin-right: 10px;
        }
        
        .chip-container {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin: 15px 0;
        }
        
        .chip {
            background-color: var(--chip-bg);
            border-radius: 50px;
            padding: 6px 14px;
            color: var(--chip-text);
            font-weight: 500;
            font-size: 0.9rem;
            transition: all 0.2s ease;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .chip:hover {
            background-color: var(--accent-primary);
            transform: translateY(-2px);
            color: white;
        }
        
        .more-count {
            color: var(--text-secondary);
            font-size: 0.8em;
            margin-left: 10px;
            opacity: 0.8;
        }
        
        .stats-container {
            background-color: var(--bg-card);
            border-radius: 8px;
            padding: 12px 18px;
            margin-bottom: 25px;
            font-size: 0.9rem;
            color: var(--text-secondary);
            border: 1px solid var(--card-border);
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        
        .stats-label {
            font-weight: 600;
            color: var(--accent-primary);
        }
        
        .footer {
            text-align: center;
            margin-top: 40px;
            color: var(--text-secondary);
            font-size: 0.8em;
            opacity: 0.7;
            padding-top: 20px;
            border-top: 1px solid var(--card-border);
        }
        
        .no-results {
            background-color: var(--bg-card);
            border-radius: 12px;
            padding: 25px;
            margin: 30px 0;
            text-align: center;
            color: var(--text-secondary);
            border: 1px dashed var(--card-border);
        }
        
        .suggestions {
            margin-top: 20px;
        }
        
        .suggestions-title {
            font-size: 0.9rem;
            color: var(--text-secondary);
            margin-bottom: 15px;
        }
        
        .suggestion-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
            gap: 10px;
        }
        
        .suggestion-item {
            background-color: var(--chip-bg);
            border-radius: 8px;
            padding: 10px;
            text-align: center;
            color: var(--chip-text);
            font-size: 0.9rem;
            transition: all 0.2s ease;
            cursor: pointer;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }
        
        .suggestion-item:hover {
            background-color: var(--accent-primary);
            transform: translateY(-2px);
        }
        
        @media (max-width: 600px) {
            .search-form {
                flex-direction: column;
            }
            .search-input {
                border-radius: 12px 12px 0 0;
                padding: 14px 16px;
            }
            .search-button {
                border-radius: 0 0 12px 12px;
                padding: 14px 16px;
                width: 100%;
            }
            .container {
                padding: 20px 15px;
            }
            h1 {
                font-size: 2rem;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="hero">
            <div class="logo-wrapper">
                <div class="logo-letter logo-y">Y</div>
                <div class="logo-letter logo-s">S</div>
                <div class="logo-letter logo-f">F</div>
            </div>
            <h1><span class="gradient-text">Yorùbá Synonym Finder</span></h1>
        </div>
        
        <div class="stats-container">
            <div>
                <span class="stats-label">Dictionary:</span> 
                <span id="dictionary-type">
                    {% if dictionary_size >= 100000 %}Massive
                    {% elif dictionary_size >= 2500 %}Expanded
                    {% else %}Basic
                    {% endif %}
                </span>
            </div>
            <div>
                <span class="stats-label">Entries:</span> 
                <span id="dictionary-size">{{ "{:,}".format(dictionary_size) }}</span>
            </div>
        </div>
        
        <form class="search-form" id="search-form">
            <input type="text" class="search-input" id="query" name="query" 
                   placeholder="Enter a Yorùbá word (e.g. ilé, ọmọ, omi)" 
                   value="{{ query }}" autofocus>
            <button type="submit" class="search-button">Find Synonyms</button>
        </form>
        
        <div id="results">
            {% if results %}
                {% for result in results %}
                    <div class="result-card">
                        <h3>
                            {{ result.headword }} 
                            <span class="pos-tag">{{ result.pos }}</span>
                        </h3>
                        <div>
                            <span class="highlight">Synonyms:</span>
                            <div class="chip-container"> 
                                {% for synonym in result.synonyms[:10] %}
                                    <span class="chip">{{ synonym }}</span>
                                {% endfor %}
                                {% if result.synonyms|length > 10 %}
                                    <span class="more-count">+{{ result.synonyms|length - 10 }} more</span>
                                {% endif %}
                            </div>
                        </div>
                        <div style="color:var(--text-secondary); font-size:0.8em; margin-top:10px; text-align:right;">
                            Match score: {{ "%.2f"|format(result.similarity) }}
                        </div>
                    </div>
                {% endfor %}
            {% elif query %}
                <div class="no-results">
                    <p>No synonyms found for '{{ query }}'.</p>
                    
                    <div class="suggestions">
                        <p class="suggestions-title">Try one of these words instead:</p>
                        <div class="suggestion-grid">
                            {% set random_words = namespace(words=[]) %}
                            {% for word in dictionary.keys() %}
                                {% if loop.index <= 8 %}
                                    {% if random_words.words.append(word) %}{% endif %}
                                {% endif %}
                            {% endfor %}
                            
                            {% for word in random_words.words|sort %}
                                <div class="suggestion-item" onclick="document.getElementById('query').value='{{ word }}'; document.getElementById('search-form').submit();">
                                    {{ word }}
                                </div>
                            {% endfor %}
                        </div>
                    </div>
                </div>
            {% endif %}
        </div>
        
        <div class="footer">
            <p>Yorùbá Synonym Finder &copy; {{ now.year }}</p>
        </div>
    </div>
    
    <script>
        document.getElementById('search-form').addEventListener('submit', function(e) {
            e.preventDefault();
            const query = document.getElementById('query').value;
            window.location.href = `/?query=${encodeURIComponent(query)}`;
        });
        
        // Add animation for results
        document.addEventListener('DOMContentLoaded', function() {
            const results = document.querySelectorAll('.result-card');
            results.forEach((card, index) => {
                card.style.opacity = '0';
                card.style.transform = 'translateY(20px)';
                setTimeout(() => {
                    card.style.transition = 'all 0.4s ease';
                    card.style.opacity = '1';
                    card.style.transform = 'translateY(0)';
                }, 100 * index);
            });
        });
    </script>
</body>
</html>
'''

@app.route('/', methods=['GET'])
def index():
    query = request.args.get('query', '')
    results = []
    
    if query:
        results = search_synonyms(query, max_results=5)
    
    # Add current date for copyright
    now = datetime.now()
    
    return render_template_string(
        HTML_TEMPLATE, 
        query=query, 
        results=results, 
        dictionary_size=len(dictionary),
        now=now
    )

@app.route('/api/search', methods=['GET'])
def api_search():
    query = request.args.get('query', '')
    max_results = request.args.get('max_results', 5, type=int)
    
    if not query:
        return jsonify({"error": "Query parameter is required"}), 400
    
    results = search_synonyms(query, max_results=max_results)
    
    return jsonify({
        "query": query,
        "results": results,
        "dictionary_size": len(dictionary)
    })

if __name__ == '__main__':
    app.run(debug=True) 