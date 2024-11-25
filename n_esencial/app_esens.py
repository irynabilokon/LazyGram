import os
import streamlit as st

st.set_page_config(
    page_title="LazyGram",
    page_icon="💤",
    layout="wide"
)

from general_helpers import load_css, load_image
from models_helpers_esens import create_content, LANGUAGES

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "vertex_ai_apikey.json" 

def main():
    logo = load_image("logo.png")
    if logo:
        st.image(logo, width=150)

    load_css("style.css")

    st.title("LazyGram")
    st.header("Your friendly AI-powered content creator.")

    content_type = st.radio("Choose Content Type", ["Twitter", "Instagram"], key="content_type_radio")

    language = st.selectbox("Choose Language", list(LANGUAGES.keys()), key="language_select")
    prompt_key = f"prompt_{content_type}"  
    prompt = st.text_area(
        "Enter your prompt", 
        f"Describe your {content_type.lower()} content idea here.", 
        key=prompt_key
    )

    if st.button("Generate"):
        with st.spinner("Generating content..."):
            try:
                generated_text = create_content(content_type, language, prompt)
                if content_type == "Twitter":
                    st.write(generated_text)
                elif content_type == "Instagram":
                    st.write(generated_text)

            except Exception as e:
                st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()