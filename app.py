#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
app.py - Streamlit web interface for the Yoruba synonym finder
"""

import streamlit as st
import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import os

# Set page configuration and title
st.set_page_config(
    page_title="Yorùbá Synonym Finder",
    page_icon="📚",
    layout="wide"
)

# Cache the resource loading for better performance
@st.cache_resource
def load_resources(index_file="yoruba_index.faiss", texts_file="yoruba_texts.npy", 
                  entries_file="yoruba_entries.npy", model_name=None):
    """
    Load the FAISS index, headwords, entries, and initialize the model.
    """
    # Check if files exist
    files_exist = os.path.exists(index_file) and os.path.exists(texts_file) and os.path.exists(entries_file)
    
    if not files_exist:
        return None, None, None, None
    
    # Get model name if not provided
    if not model_name:
        try:
            with open("model_info.json", "r") as f:
                model_info = json.load(f)
                model_name = model_info.get("name", "all-MiniLM-L6-v2")
        except (FileNotFoundError, json.JSONDecodeError):
            model_name = "all-MiniLM-L6-v2"
    
    # Load the index
    index = faiss.read_index(index_file)
    
    # Load the headwords
    headwords = np.load(texts_file, allow_pickle=True)
    
    # Load the entries
    entries = np.load(entries_file, allow_pickle=True)
    
    # Load the model
    model = SentenceTransformer(model_name)
    
    return index, headwords, entries, model

def search_synonyms(query, index, headwords, entries, model, top_k=3):
    """
    Search for synonyms of the given query word.
    """
    # Encode the query
    query_embedding = model.encode([query], convert_to_numpy=True)
    
    # Normalize the query embedding for cosine similarity
    faiss.normalize_L2(query_embedding)
    
    # Search the index
    distances, indices = index.search(query_embedding, top_k)
    
    results = []
    for i, idx in enumerate(indices[0]):
        if idx < len(entries):
            entry = entries[idx]
            similarity = distances[0][i]
            results.append({
                "rank": i + 1,
                "similarity": float(similarity),
                "entry": entry
            })
    
    return results

# App title and header
st.title("Yorùbá Synonym Finder")
st.markdown("""
This application helps you find synonyms for Yoruba words. 
Enter a Yoruba word in the search box below and click the search button.
""")

# Check if resources exist or give setup instructions
index, headwords, entries, model = load_resources()

if index is None:
    st.error("Required resources not found. Please run the setup scripts first:")
    st.code("""
    # 1. Extract common Yoruba words from text sources
    python get_common.py --fallback
    
    # 2. Generate synonyms using the transformer model
    python generate_entries.py
    
    # 3. Build the search index
    python build_index.py
    """)
    st.stop()

# Search interface
col1, col2 = st.columns([3, 1])

with col1:
    query = st.text_input("Enter a Yoruba word:", placeholder="e.g. ilé, ọmọ, àgbà")

with col2:
    search_button = st.button("Find Synonyms", type="primary")

# Display loading spinner during search
if search_button and query:
    with st.spinner("Searching..."):
        results = search_synonyms(query.strip(), index, headwords, entries, model)
    
    # Display results
    if not results:
        st.warning("No results found. Try another word.")
    else:
        for result in results:
            entry = result["entry"]
            similarity = result["similarity"]
            
            # Create a card-like display for each result
            with st.container():
                col1, col2 = st.columns([1, 4])
                
                with col1:
                    st.markdown(f"### Rank {result['rank']}")
                    st.markdown(f"Similarity: {similarity:.4f}")
                
                with col2:
                    st.markdown(f"### {entry['headword']} ({entry['pos']})")
                    st.markdown(f"**Synonyms:** {', '.join(entry['synonyms'])}")
                    st.markdown(f"**Definition:** {entry['definition']}")
                    st.markdown(f"**Example (Yoruba):** {entry['example']['yorùbá']}")
                    st.markdown(f"**Example (English):** {entry['example']['en']}")
                
                st.markdown("---")

# Footer
st.markdown("---")
st.markdown("© 2023 Yorùbá Synonym Finder - Built with Streamlit, FAISS, and Sentence Transformers") 