import os
import streamlit as st

st.set_page_config(
    page_title="LazyGram",
    page_icon="💤",
    layout="wide"
)

from general_helpers import load_css, load_image
from models_helpers import create_content, LANGUAGES, LLM_MODELS, PLATFORM_IMAGE_LIMITS
from rag_helpers import fetch_relevant_documents, create_retrieval_system, retrieve_and_generate, SCIENTIFIC_TOPICS, PUBLIC_CONTEXT

load_css("style.css")

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "vertex_ai_apikey.json" 

def generate_scientific_content():
    st.subheader("Scientific Content Generator (RAG)")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<h3>Choose Topic </h3>", unsafe_allow_html=True)
        topic = st.selectbox(
        "Select Scientific Topic", 
        list(SCIENTIFIC_TOPICS.keys()), 
        key="scientific_topic_select"
    )
    with col2:
        st.markdown("<h3>Choose Public Context Level</h3>", unsafe_allow_html=True)
        public_level = st.selectbox(
            "Select Explanation Level", 
            list(PUBLIC_CONTEXT.keys()), 
            key="public_context_select",
            index=3
        )
    st.markdown("<h3>Enter your prompt</h3>", unsafe_allow_html=True)
    user_query = st.text_area("Describe your content idea", key="scientific_query_input")
        
    if st.button("Generate Scientific Content"):
        with st.spinner("Retrieving and synthesizing content..."):
            try:
                if topic:
                    relevant_docs = fetch_relevant_documents(topic, max_results=10)
                    retrieval_system = create_retrieval_system(relevant_docs)

                    result = retrieve_and_generate(user_query, retrieval_system, public_level=public_level)
                    st.markdown(f"### Generated Content:\n{result}")
                else:
                    st.error("Please enter a valid topic.")

            except Exception as e:
                st.error(f"An error occurred: {e}")

def main():
    logo = load_image("logo.png")
    if logo:
        st.image(logo, width=150)

    st.title("Your friendly AI-powered content creator.")

    tab1, tab2 = st.tabs(["Content Creation", "Scientific Content Creation"])
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("<h3>Choose Content Type</h3>", unsafe_allow_html=True)
            content_type = st.selectbox("Select Content Type", ["Twitter", "Instagram", "LinkedIn", "Blog"], key="content_type_selectbox")
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
            step=1,
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
                    generated_text = create_content(
                        content_type, 
                        language, 
                        prompt, 
                        company_info, 
                        num_images=num_images,
                        model_name=model_name
                    )
                except Exception as e:
                    st.error(f"An error occurred: {e}")

        with tab2:
            generate_scientific_content()

    st.markdown('---')
    st.markdown("© 2024 LazyGram - Effortless Creativity at Your Fingertips. All rights reserved.")

if __name__ == "__main__":
    main()