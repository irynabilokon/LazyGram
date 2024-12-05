import streamlit as st
import os
from dotenv import load_dotenv
import base64
import vertexai
from vertexai.preview.generative_models import GenerativeModel
import google.cloud.aiplatform as aiplatform
from general_helpers import load_css

load_dotenv()

def init_vertex_ai():
    PROJECT_ID = os.getenv('VERTEX_PROJECT_ID')
    REGION = "europe-west4"
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
LLM_MODELS = {
    "Gemini 1.5 Pro": {
        "engine": "vertex",
        "model_name": "gemini-1.5-pro-002",
        "function": "generate_text_gemini"
    },
    "Mistral Nemo Minitron 8B": {
        "engine": "mistral",
        "model_name": "mistral-nemo-minitron-8b",
        "function": "generate_text_mistral"
    }
}

PLATFORM_CONSTRAINTS = {
    "Twitter": {
        "max_chars": 280,
        "prefix": "Create a concise tweet",
    },
    "Instagram": {
        "max_chars": 2200,
        "prefix": "Create an engaging Instagram post",
    },
    "LinkedIn": {
        "max_chars": 3000,
        "prefix": "Create a professional LinkedIn post",
    },
    "Blog": {
        "max_chars": 10000,
        "prefix": "Create a well-structured post for a blog on selected topic",
    },
    "ScientificArticle": {
        "max_chars": 15000,
        "prefix": "Write a detailed and informative scientific article. Focus on accuracy and clarity.",
    }
}

PLATFORM_IMAGE_LIMITS = {
    "Twitter": {
        "max_images": 2
    },
    "Instagram": {
        "max_images": 10
    },
    "LinkedIn": {
        "max_images": 3
    },
    "Blog": {
        "max_images": 5
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

def generate_text_gemini(content_type, language, prompt, company_info=""):
    init_vertex_ai()

    primary_model_name = "gemini-1.5-pro-002"
    fallback_model_name = "gemini-1.5-flash-002"

    instruction = language_instructions.get(language, "Write a clear and engaging post.")
    platform_instruction = instruction.format(platform=content_type)
    prefix = PLATFORM_CONSTRAINTS.get(content_type, {}).get("prefix", "Create social media content")

    full_prompt = f"{prefix}. {platform_instruction}. Company/Personal Context: {company_info}. {prompt}"

    try:
        # Attempt with the primary model
        generative_multimodal_model = GenerativeModel(primary_model_name)
        response = generative_multimodal_model.generate_content([full_prompt])
        generated_text = response.text if response else "No text generated."
        return generated_text
    except Exception as primary_error:
        print(f"Error with primary model ({primary_model_name}): {primary_error}")
        print("Falling back to the flash model...")

        try:
            # Attempt with the fallback model
            generative_multimodal_model = GenerativeModel(fallback_model_name)
            response = generative_multimodal_model.generate_content([full_prompt])
            generated_text = response.text if response else "No text generated."
            return generated_text
        except Exception as fallback_error:
            raise Exception(
                f"Both models failed. Primary error: {primary_error}. Fallback error: {fallback_error}"
            )
'''
def generate_text_mistral(content_type, language, prompt, company_info=""):
    try:
        PROJECT_ID = os.getenv('VERTEX_PROJECT_ID')
        aiplatform.init(project=PROJECT_ID, location="europe-west1")

        ENDPOINT_ID = os.getenv("MISTRAL_ENDPOINT_ID")
        if not ENDPOINT_ID:
            raise ValueError("Mistral Endpoint ID not found in Streamlit secrets")

        endpoint = aiplatform.Endpoint(endpoint_name=ENDPOINT_ID)

        # Prepare instructions and prompt
        instruction = language_instructions.get(language, "Write a clear and engaging post.")
        platform_config = PLATFORM_CONSTRAINTS.get(content_type, {})
        platform_instruction = instruction.format(platform=content_type)
        prefix = platform_config.get("prefix", "Create social media content")

        max_chars = platform_config.get("max_chars", 1000) 
        avg_chars_per_token = 4  
        max_tokens = max_chars // avg_chars_per_token

        full_prompt = f"{prefix}. {platform_instruction}. Company/Personal Context: {company_info}. {prompt}"

        # Correct structure for Mistral
        instances = [
            {
                "inputs": full_prompt,  # Replaced "prompt" with "inputs"
                "parameters": {
                    "temperature": 0.7,
                    "max_output_tokens": max_tokens  # Changed to "max_output_tokens"
                }
            }
        ]

        # Call the endpoint
        prediction = endpoint.predict(instances=instances)

        # Directly access the generated text
        generated_text = prediction.predictions[0] if prediction.predictions else "No text generated."
        return generated_text

    except Exception as e:
        raise Exception(f"Error generating text with Mistral via Vertex AI: {e}")
'''
def generate_images(prompt, num_images=1):
    try:
        PROJECT_ID = os.getenv('VERTEX_PROJECT_ID')
        aiplatform.init(project=PROJECT_ID, location="europe-west4")

        ENDPOINT_ID = os.getenv('IMAGE_GEN_ENDPOINT_ID')

        endpoint = aiplatform.Endpoint(endpoint_name=ENDPOINT_ID)

        instances = [prompt] * num_images

        prediction = endpoint.predict(instances=instances)

        generated_images = []
        for pred in prediction.predictions:
            generated_images.append(pred)
        
        return generated_images
    
    except Exception as e:
        print(f"Error generating images: {e}")
        return []

def update_create_content(content_type, language, prompt, company_info="", num_images=0, model_name="Gemini 1.5 Pro"):
    st.subheader(f"{content_type} Content Generator")
    try:
        model_info = LLM_MODELS.get(model_name, LLM_MODELS["Gemini 1.5 Pro"])
        text_generation_func = globals()[model_info["function"]]

        generated_text = text_generation_func(content_type, language, prompt, company_info)
        generated_images = []
        if num_images > 0:
            image_prompt = f"Illustrative image for a {content_type} post about {prompt}"

            generated_images = generate_images(image_prompt, num_images)

        st.write(generated_text)

        if generated_images:
            cols = st.columns(len(generated_images))
            for i, img in enumerate(generated_images):
                with cols[i]:
                    img_data = base64.b64decode(img)
                    st.image(img_data)

    except Exception as e:
        st.error(f"Error generating content: {e}")

create_content = update_create_content