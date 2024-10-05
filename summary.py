import streamlit as st
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
from string import punctuation
import heapq
import PyPDF2

# Load the SpaCy language model
nlp = spacy.load("en_core_web_sm")

# Function to summarize the text while maintaining sentence order
def summarize_text(text):
    doc = nlp(text)
    word_freq = {}
    for word in doc:
        if word.text.lower() not in STOP_WORDS and word.text.lower() not in punctuation:
            if word.text.lower() not in word_freq:
                word_freq[word.text.lower()] = 1
            else:
                word_freq[word.text.lower()] += 1
    max_freq = max(word_freq.values())
    for word in word_freq:
        word_freq[word] = word_freq[word] / max_freq

    sent_scores = {}
    for sent in doc.sents:
        for word in sent:
            if word.text.lower() in word_freq:
                if sent not in sent_scores:
                    sent_scores[sent] = word_freq[word.text.lower()]
                else:
                    sent_scores[sent] += word_freq[word.text.lower()]

    # Select the top 7 sentences
    summary_sentences = heapq.nlargest(7, sent_scores, key=sent_scores.get)
    
    # Sort the selected sentences by their order of appearance in the original text
    summary_sentences = sorted(summary_sentences, key=lambda x: x.start)
    
    # Join the sorted sentences into the final summary
    summary = ' '.join([sent.text for sent in summary_sentences])
    
    return summary

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    all_text = ""
    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        all_text += page.extract_text()
    return all_text

# Streamlit UI
st.title("Text Summarizer App")
st.markdown("""
Welcome to the **Text Summarizer App**! You can either upload a PDF file or manually input text, and this app will generate a summary using NLP.
""")

# Initialize raw_text variable as an empty string to avoid any issues
raw_text = ""

# Sidebar options
st.sidebar.header("Choose Input Method")
input_option = st.sidebar.radio("Select how you want to input the text:", ("Type Text", "Upload PDF"))

# Handle PDF upload option
if input_option == "Upload PDF":
    # File uploader for PDF
    uploaded_file = st.sidebar.file_uploader("Choose a PDF file", type="pdf")
    
    if uploaded_file is not None:
        raw_text = extract_text_from_pdf(uploaded_file)
        st.subheader("Extracted Text from PDF")
        st.text_area("Full Text", raw_text[:2000], height=300)  # Show only part of the text

# Handle typing text manually option
else:
    raw_text = st.text_area("Type or Paste your Text Below", height=300)

# Generate summary if text is available
if raw_text:
    summary = summarize_text(raw_text)
    st.subheader("Summarized Text")
    st.write(summary)

# Footer
st.markdown("""
---
Developed with ❤️ by arkaydatainsights.
This app extracts the main ideas from large bodies of text and presents them in a concise summary. Powered by SpaCy and NLP.
""")
