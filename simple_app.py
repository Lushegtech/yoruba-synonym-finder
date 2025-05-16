#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
simple_app.py - Streamlit web app for the Yoruba synonym finder using a static dictionary
"""

import streamlit as st
import json
import difflib

# --- Dictionary Loading and Search Functions ---

def load_dictionary(dict_file):
    """
    Load the Yoruba synonyms dictionary from a JSON file.
    """
    try:
        with open(dict_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        st.error(f"Error loading dictionary: {e}")
        return {}

def normalize_word(word):
    """
    Normalize a Yoruba word for matching: lowercase and strip whitespace.
    """
    return word.lower().strip()

def search_synonyms(query, dictionary, max_results=3):
    """
    Search for synonyms of the given query word using the static dictionary.
    """
    query = normalize_word(query)
    
    # Direct match - check if word exists directly in the dictionary
    if query in dictionary:
        return [{"rank": 1, "similarity": 1.0, "entry": dictionary[query]}]
    
    # Fuzzy match - find closest matches for unknown words
    results = []
    
    # Check if query is in any of the synonyms
    for headword, entry in dictionary.items():
        for synonym in entry["synonyms"]:
            if normalize_word(synonym) == query:
                results.append({
                    "rank": 1,
                    "similarity": 1.0,
                    "entry": entry
                })
                return results  # Found exact match in synonyms
    
    # Use difflib to find fuzzy matches
    matches = difflib.get_close_matches(query, dictionary.keys(), n=max_results, cutoff=0.6)
    
    for i, match in enumerate(matches):
        # Calculate a similarity score (1.0 to 0.0)
        similarity = 1.0 - (0.1 * i)  # Simple ranking by match order
        results.append({
            "rank": i + 1,
            "similarity": similarity,
            "entry": dictionary[match]
        })
    
    return results

# --- Streamlit App ---

def main():
    # Set the page configuration
    st.set_page_config(
        page_title="Yorùbá Synonym Finder",
        page_icon="🌍",
        layout="centered"
    )
    
    # Custom CSS for styling
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');
    body {
        font-family: 'Poppins', sans-serif;
        background: linear-gradient(135deg, #fefefe 0%, #e8f4ff 100%);
    }

    .title {
        text-align: center;
        color: #2c3e50;
    }

    .hero {
        text-align: center;
        margin-top: 20px;
        margin-bottom: 30px;
    }
    .hero h1 {
        font-size: 2.8rem;
        font-weight: 700;
        color: #2c3e50;
        margin: 0;
    }
    .hero p {
        font-size: 1.1rem;
        color: #555;
        margin-top: 8px;
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

    .syn-list {
        color: #2c3e50; /* Ensure synonyms are visible on both light and dark themes */
    }

    .footer {
        text-align: center;
        color: #555;
        font-size: 0.8em;
        margin-top: 50px;
    }

    /* Custom gradient text for title */
    .gradient-text {
        background: linear-gradient(90deg, #A0E7E5 0%, #FBE7C6 50%, #FFAEBC 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        display: inline;
        font-weight: 700;
    }

    /* Custom logo */
    .logo-wrapper {
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 20px auto;
        width: 100%;
        text-align: center;
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

    /* Subtitle styling */
    .subtitle {
        text-align: center;
        color: #adb5bd;
        font-size: 1.2rem;
        font-weight: 300;
        margin: 15px auto 30px auto;
        max-width: 600px;
        padding: 0 20px;
        letter-spacing: 0.5px;
        position: relative;
    }
    
    .subtitle:before,
    .subtitle:after {
        content: "";
        height: 1px;
        width: 30px;
        background: rgba(255,255,255,0.15);
        display: inline-block;
        position: relative;
        vertical-align: middle;
        margin: 0 10px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Hero header
    st.markdown("""
    <div class='hero'>
        <div style="width:100%; display:flex; justify-content:center;">
            <div class='logo-wrapper'>
                <div class='logo-letter logo-y'>Y</div>
                <div class='logo-letter logo-s'>S</div>
                <div class='logo-letter logo-f'>F</div>
            </div>
        </div>
        <h1><span class='gradient-text'>Yorùbá Synonym Finder</span></h1>
        <div class="subtitle">Discover beautiful Yorùbá words &amp; their meanings</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Load the dictionary
    dictionary = load_dictionary('yoruba_synonyms_static.json')
    
    if not dictionary:
        st.error("Could not load the dictionary file. Please check that 'yoruba_synonyms_static.json' exists.")
        return
    
    # Create the search interface
    col1, col2 = st.columns([3, 1])
    
    with col1:
        query = st.text_input("Enter a Yorùbá word:", 
                             placeholder="e.g. ilé, ọmọ, omi",
                             help="Type a Yorùbá word to find its synonyms")
    
    with col2:
        max_results = st.selectbox("Max results:", [1, 2, 3, 5], index=2)
    
    # Add a search button
    search_button = st.button("Find Synonyms", type="primary")
    
    # Display dictionary info
    with st.expander("Dictionary Information"):
        st.info(f"Loaded static dictionary with {len(dictionary)} entries.")
        
        # Show available words
        st.write("Available words:")
        
        num_cols = 3
        cols = st.columns(num_cols)
        
        # Sort the headwords alphabetically
        sorted_words = sorted(dictionary.keys())
        
        # Display words in multiple columns
        for i, word in enumerate(sorted_words):
            cols[i % num_cols].write(f"• {word}")
    
    # Process search when button is clicked
    if search_button and query:
        with st.spinner("Searching..."):
            results = search_synonyms(query, dictionary, max_results=max_results)
            
            if not results:
                st.warning(f"No synonyms found for '{query}'.")
                
                # Suggest some available words
                st.write("Try one of these words instead:")
                suggestions = sorted(dictionary.keys())[:10]
                for suggestion in suggestions:
                    st.write(f"• {suggestion}")
            else:
                st.success(f"Found {len(results)} results for '{query}'")
                
                # Display results
                for result in results:
                    entry = result["entry"]
                    similarity = result["similarity"]
                    
                    with st.container():
                        synonyms_html = ' '.join([f"<span class='chip'>{s}</span>" for s in entry['synonyms']])
                        st.markdown(f"""
                        <div class='result-card'>
                            <h3>{entry['headword']} <span style='color:#555; font-size:0.8em;'>({entry['pos']})</span></h3>
                            <p><span class='highlight'>Synonyms:</span> {synonyms_html}</p>
                            <p><span class='highlight'>Definition:</span> {entry['definition']}</p>
                            <p class='example'><span class='highlight'>Example (Yorùbá):</span> {entry['example']['yorùbá']}</p>
                            <p class='example'><span class='highlight'>Example (English):</span> {entry['example']['en']}</p>
                            <p style='color:#777; font-size:0.8em;'>Match score: {similarity:.2f}</p>
                        </div>
                        """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
    <div class='footer'>
        <p>Yorùbá Synonym Finder - A simplified dictionary-based approach</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 