import os
import google.generativeai as genai
from PIL import Image
import streamlit as st

# Configure Gemini API
def configure_gemini(api_key):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-pro-vision')
    return model

def generate_assamese_caption(model, image):
    try:
        response = model.generate_content([
            "You are an expert in Assamese language. Analyze this image and provide a detailed description in Assamese language. Make the description natural and fluent.",
            image
        ])
        return response.text
    except Exception as e:
        return f"Error generating caption: {str(e)}"

def main():
    st.title("Image to Assamese Caption Generator")
    st.write("Upload an image and get its description in Assamese language")
    
    # API Key input
    api_key = st.text_input("Enter your Gemini API Key:", type="password")
    
    if api_key:
        model = configure_gemini(api_key)
        
        # Image upload
        uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
        
        if uploaded_file is not None:
            # Display uploaded image
            image = Image.open(uploaded_file)
            st.image(image, caption='Uploaded Image', use_column_width=True)
            
            # Generate caption button
            if st.button("Generate Assamese Caption"):
                with st.spinner("Generating caption..."):
                    caption = generate_assamese_caption(model, image)
                    st.write("### Assamese Caption:")
                    st.write(caption)

if __name__ == "__main__":
    main()
