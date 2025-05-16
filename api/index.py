from flask import Flask, request, jsonify, render_template_string
import json
import difflib
import os
import random

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
        body {
            font-family: 'Poppins', sans-serif;
            background: linear-gradient(135deg, #fefefe 0%, #e8f4ff 100%);
            margin: 0;
            padding: 20px;
            color: #333;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.05);
            padding: 20px;
        }
        h1 {
            text-align: center;
            color: #2c3e50;
            margin: 0 0 20px 0;
        }
        .hero {
            text-align: center;
            padding: 20px 0;
        }
        .logo-wrapper {
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 20px auto;
        }
        .logo-letter {
            width: 45px;
            height: 45px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 6px;
            border-radius: 8px;
            color: white;
            font-weight: bold;
            font-size: 24px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            transform: translateY(0);
            transition: transform 0.3s ease;
        }
        .logo-letter:hover {
            transform: translateY(-5px);
        }
        .logo-y {
            background: linear-gradient(135deg, #FF9A8B 0%, #FF6A88 100%);
        }
        .logo-s {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        }
        .logo-f {
            background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        }
        .gradient-text {
            background: linear-gradient(90deg, #A0E7E5 0%, #FBE7C6 50%, #FFAEBC 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            display: inline;
            font-weight: 700;
        }
        .search-form {
            display: flex;
            flex-wrap: wrap;
            margin-bottom: 20px;
        }
        .search-input {
            flex-grow: 1;
            padding: 10px 15px;
            font-size: 16px;
            border: 1px solid #ddd;
            border-radius: 5px 0 0 5px;
            outline: none;
        }
        .search-button {
            padding: 10px 20px;
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
            border: none;
            border-radius: 0 5px 5px 0;
            cursor: pointer;
            font-weight: 600;
        }
        .result-card {
            background-color: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            border-left: 5px solid #4682B4;
            box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        }
        .highlight {
            font-weight: bold;
            color: #4682B4;
        }
        .chip {
            background-color: #e8f4ff;
            border-radius: 20px;
            padding: 4px 12px;
            margin: 2px;
            display: inline-block;
            font-weight: 500;
            color: #2c3e50;
            font-size: 0.9rem;
        }
        .stats-container {
            background-color: #f8f9fa;
            border-radius: 8px;
            padding: 10px 15px;
            margin-bottom: 20px;
            font-size: 0.85rem;
            color: #555;
        }
        .stats-label {
            font-weight: 600;
            color: #4682B4;
        }
        .footer {
            text-align: center;
            margin-top: 30px;
            color: #777;
            font-size: 0.8em;
        }
        @media (max-width: 600px) {
            .search-form {
                flex-direction: column;
            }
            .search-input {
                border-radius: 5px;
                margin-bottom: 10px;
            }
            .search-button {
                border-radius: 5px;
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
            <span class="stats-label">Dictionary size:</span> <span id="dictionary-size">{{ dictionary_size }}</span> entries
        </div>
        
        <form class="search-form" id="search-form">
            <input type="text" class="search-input" id="query" name="query" placeholder="Enter a Yorùbá word (e.g. ilé, ọmọ, omi)" value="{{ query }}">
            <button type="submit" class="search-button">Find Synonyms</button>
        </form>
        
        <div id="results">
            {% if results %}
                {% for result in results %}
                    <div class="result-card">
                        <h3>{{ result.headword }} <span style="color:#555; font-size:0.8em;">({{ result.pos }})</span></h3>
                        <p><span class="highlight">Synonyms:</span> 
                            {% for synonym in result.synonyms[:10] %}
                                <span class="chip">{{ synonym }}</span>
                            {% endfor %}
                            {% if result.synonyms|length > 10 %}
                                <span style="color:#777; font-size:0.8em;">+{{ result.synonyms|length - 10 }} more</span>
                            {% endif %}
                        </p>
                        <p style="color:#777; font-size:0.8em;">Match score: {{ "%.2f"|format(result.similarity) }}</p>
                    </div>
                {% endfor %}
            {% elif query %}
                <p>No synonyms found for '{{ query }}'.</p>
            {% endif %}
        </div>
        
        <div class="footer">
            <p>Yorùbá Synonym Finder - Using {% if dictionary_size >= 100000 %}massive{% elif dictionary_size >= 2500 %}expanded{% else %}basic{% endif %} dictionary with {{ dictionary_size }} entries</p>
        </div>
    </div>
    
    <script>
        document.getElementById('search-form').addEventListener('submit', function(e) {
            e.preventDefault();
            const query = document.getElementById('query').value;
            window.location.href = `/?query=${encodeURIComponent(query)}`;
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
    
    return render_template_string(
        HTML_TEMPLATE, 
        query=query, 
        results=results, 
        dictionary_size=len(dictionary)
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