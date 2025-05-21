import streamlit as st
import pandas as pd
from utils import generate_description, ModelGenerationError
from prompts import build_prompt

st.set_page_config(page_title="GenAI Product Description Generator", layout="wide")
st.title("E-commerce AI Description Generator")

# Tone selector
tone = st.selectbox("Choose a writing tone:", ["Professional", "Casual", "Luxury", "Minimal", "Playful"])

# File uploader
uploaded_file = st.file_uploader("Upload a CSV (columns: product_name, brand, material, features)", type="csv")

df = None
generate_ab = False

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
else:
    st.subheader("Or enter product info manually")
    product_name = st.text_input("Product Name")
    brand = st.text_input("Brand")
    material = st.text_input("Material")
    features = st.text_area("Features (comma-separated)")

    if product_name and brand and material and features:
        df = pd.DataFrame([{
            "product_name": product_name,
            "brand": brand,
            "material": material,
            "features": features
        }])

# Continue only if we have product data
if df is not None:
    # Initialize generate_ab before it's potentially used by the button
    current_generate_ab_setting = st.checkbox("Generate two versions per product (A/B testing)", value=generate_ab)

    if st.button("Generate Descriptions"):
        generate_ab = current_generate_ab_setting # Update generate_ab with the checkbox value when button is clicked
        with st.spinner("Generating..."):
            version_a, version_b = [], []
            error_occurred = False # Flag to track if an error happened

            for _, row in df.iterrows():
                try:
                    prompt = build_prompt(row, tone)
                    a = generate_description(prompt)
                    version_a.append(a)
                    if generate_ab:
                        # Only call again if we need version B
                        b = generate_description(prompt) 
                        version_b.append(b)
                    else:
                        version_b.append("")
                except ModelGenerationError as e:
                    st.error(f"Could not generate description for {row['product_name']}: {e}")
                    version_a.append("Error generating description.")
                    version_b.append("")
                    error_occurred = True
                    # Optionally, you could break here or decide how to handle partial failures
                except Exception as e:
                    st.error(f"An unexpected error occurred for {row['product_name']}: {e}")
                    version_a.append("Unexpected error.")
                    version_b.append("")
                    error_occurred = True

            df['Version A'] = version_a
            df['Version B'] = version_b

        if not error_occurred:
            st.success("Descriptions generated!")
        else:
            st.warning("Some descriptions could not be generated. Please check messages above.")

        for i, row in df.iterrows():
            st.markdown(f"### 🛍️ {row['product_name']}")
            st.markdown("**Version A:**")
            st.info(row["Version A"])
            if generate_ab and row["Version B"]:
                st.markdown("**Version B:**")
                st.warning(row["Version B"])
            st.markdown("---")

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Download CSV", csv, "descriptions_ab.csv", "text/csv")
