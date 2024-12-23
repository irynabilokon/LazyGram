import os
import streamlit as st

st.set_page_config(
    page_title="LazyGram",
    page_icon="💤",
    layout="wide"
)

from general_helpers import load_css, load_image
from models_helpers_esens import create_content, LANGUAGES, LLM_MODELS, PLATFORM_IMAGE_LIMITS

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "vertex_ai_apikey.json" 

def main():
    logo = load_image("logo.png")
    if logo:
        st.image(logo, width=150)

    load_css("style.css")

    st.title("LazyGram")
    st.header("Your friendly AI-powered content creator.")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<h3>Choose Content Type</h3>", unsafe_allow_html=True)
        content_type = st.selectbox("Select Content Type", ["Twitter", "Instagram", "LinkedIn"], key="content_type_selectbox")
    with col2:
        st.markdown("<h3>Choose Language</h3>", unsafe_allow_html=True)
        language = st.selectbox("Select Language", list(LANGUAGES.keys()), key="language_select")

    col1, col2 = st.columns(2)
    with col1:
        model_name = st.selectbox("Choose AI Model", list(LLM_MODELS.keys()), key="model_select")
    with col2:
        max_images = PLATFORM_IMAGE_LIMITS.get(content_type, {}).get("max_images", 1)
        num_images = st.number_input(
        "Number of Images", 
        min_value=0, 
        max_value=max_images, 
        value=0, 
        step=1,  # Increment/Decrement step size
        key="image_count_input"
    )
    st.markdown("<h3>Company/Personal Context</h3>", unsafe_allow_html=True)
    company_info = st.text_area( 
        "Provide background about your brand or personal style", 
        key="company_context",
        height = 75
    )

    prompt_key = f"prompt_{content_type}"  
    st.markdown("<h3>Enter your prompt</h3>", unsafe_allow_html=True)
    prompt = st.text_area( 
        f"Describe your {content_type.lower()} content idea here.", 
        key=prompt_key
    )

    if st.button("Generate"):
        with st.spinner("Generating content..."):
            try:
                generated_text = create_content(content_type, language, prompt,  company_info, model_name=model_name)
                if content_type == "Twitter":
                    st.write(generated_text)
                elif content_type == "Instagram":
                    st.write(generated_text)
                elif content_type == "LinkedIn":
                    st.write(generated_text)

            except Exception as e:
                st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()