import os
from PIL import Image
import streamlit as st

def load_css(file_name):
    css_path = os.path.join(os.getcwd(), 'styles', file_name)
    try:
        with open(css_path, 'r') as f:
            css_content = f.read()
            st.markdown(f'<style>{css_content}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"CSS file '{file_name}' not found at {css_path}")

def load_image(image_name):
    image_path = os.path.join(os.getcwd(), 'images', image_name)
    try:
        return Image.open(image_path)
    except FileNotFoundError:
        st.error(f"Image '{image_name}' not found at {image_path}")
        return None