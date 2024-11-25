import os
import streamlit as st
import vertexai
from vertexai.preview.generative_models import GenerativeModel
from general_helpers import load_css

def init_vertex_ai():
    PROJECT_ID = "llm-ib" 
    REGION = "europe-southwest1"
    vertexai.init(project=PROJECT_ID, location=REGION)

load_css("style.css")

LANGUAGES = {
    "English": "en",
    "Italian": "it",
    "French": "fr",
    "Dutch": "nl",
    "Spanish": "es",
    "Ukrainian": "uk",
}

PLATFORM_CONSTRAINTS = {
    "Twitter": {
        "max_chars": 280,
        "prefix": "Create a concise tweet",
    },
    "Instagram": {
        "max_chars": 2200,
        "prefix": "Create an engaging Instagram post",
    }
}

language_instructions = {
    "Ukrainian": "Write in Ukrainian. Create a {platform} post reflecting contemporary language.",
    "English": "Write a clear, engaging {platform} post.",
    "Spanish": "Write in Spanish. Develop a {platform} post using natural, conversational language appropriate to the context.",
    "French": "Write in French. Develop a {platform} post using elegant and culturally appropriate tone.",
    "Italian": "Write in Italian. Develop a {platform} post capturing the expressive and melodic nature of the language.",
    "Dutch": "Write in Dutch. Develop a {platform} post using straightforward, direct language.",
}

def truncate_content(content: str, platform: str) -> str:
    max_chars = PLATFORM_CONSTRAINTS.get(platform, {}).get("max_chars", 280)
    return content[:max_chars]

def generate_text_gemini(content_type, language, prompt):

    init_vertex_ai()

    generative_multimodal_model = GenerativeModel("gemini-1.5-pro-002")

    instruction = language_instructions.get(language, "Write a clear and engaging post.")
    platform_instruction = instruction.format(platform=content_type)
    prefix = PLATFORM_CONSTRAINTS.get(content_type, {}).get("prefix", "Create social media content")

    full_prompt = f"{prefix}. {platform_instruction} {prompt}"

    try:
        response = generative_multimodal_model.generate_content([full_prompt])
        generated_text = response.text if response else "No text generated."
        return generated_text
    except Exception as e:
        st.error(f"Error generating text: {e}")
        return None

def create_content(content_type, language, prompt, num_images=0):
    st.subheader(f"{content_type} Content Generator")

    try:
        generated_text = generate_text_gemini(content_type, language, prompt)

        if content_type == "Instagram":
            st.write(generated_text)
        elif content_type == "Twitter":
            st.write(generated_text)

    except Exception as e:
        st.error(f"Error generating content: {e}")
