import streamlit as st
import cv2
from PIL import Image
import numpy as np
import pandas as pd
from streamlit_image_coordinates import streamlit_image_coordinates
import base64
from io import BytesIO

# ---------------------------- SETUP ----------------------------
st.set_page_config(layout="wide", page_title="Color Detector 🎨")

# ---------------------------- STYLE ----------------------------
st.markdown("""
    <style>
    /* Background gradient with subtle animation */
    body {
        margin: 0;
        min-height: 100vh;
        background: linear-gradient(270deg, #ff9a9e, #fad0c4, #fad0c4, #ff9a9e);
        background-size: 800% 800%;
        animation: gradientBG 20s ease infinite;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: #222222;
    }

    @keyframes gradientBG {
        0%{background-position:0% 50%}
        50%{background-position:100% 50%}
        100%{background-position:0% 50%}
    }

    /* Main container styling */
    .main {
        background-color: rgba(255, 255, 255, 0.85);
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.12);
        margin-bottom: 2rem;
    }

    /* Color box with shadow and smooth border */
    .color-box {
        width: 120px;
        height: 120px;
        border-radius: 15px;
        border: 3px solid #444444;
        box-shadow: 0 4px 10px rgba(0,0,0,0.15);
        margin-bottom: 15px;
        transition: transform 0.3s ease;
    }
    .color-box:hover {
        transform: scale(1.1);
    }

    /* Footer styling */
    .footer {
        text-align: center;
        padding-top: 20px;
        font-size: 1rem;
        color: #444444;
        font-weight: 600;
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(135deg, #89f7fe 0%, #66a6ff 100%);
        color: #111;
        padding: 1.5rem 1rem 2rem 1rem;
        border-radius: 0 15px 15px 0;
        box-shadow: 4px 0 15px rgba(0,0,0,0.1);
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #222222;
    }
    [data-testid="stSidebar"] .stButton>button {
        background-color: #4a90e2;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 8px 15px;
        font-weight: 600;
        transition: background-color 0.3s ease;
    }
    [data-testid="stSidebar"] .stButton>button:hover {
        background-color: #357abd;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------- FUNCTIONS ----------------------------
@st.cache_data
def load_colors(csv_path):
    return pd.read_csv(csv_path)

def get_closest_color(R, G, B, df):
    minimum = float('inf')
    closest_color = None
    for _, row in df.iterrows():
        d = abs(R - row["R"]) + abs(G - row["G"]) + abs(B - row["B"])
        if d < minimum:
            minimum = d
            closest_color = row
    return closest_color

def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

# ---------------------------- SIDEBAR ----------------------------
st.sidebar.image("https://img.icons8.com/color/96/color-palette.png", width=100)
st.sidebar.title("🎨 Color Detector")
st.sidebar.markdown("Upload an image and click on any point to detect the color name and RGB value.")
st.sidebar.markdown("---")

st.sidebar.markdown("✅ Built with `OpenCV`, `PIL`, `Streamlit`")

# ---------------------------- MAIN ----------------------------
st.markdown('<div class="main">', unsafe_allow_html=True)
st.title("🌈 Color Detection from Image")

uploaded_file = st.file_uploader("📤 Upload an image (JPG/PNG)", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    st.sidebar.image(image, caption="Uploaded Image", use_column_width=True)

    st.subheader("🖱️ Click anywhere on the image below to detect color")

    coords = streamlit_image_coordinates(image, key="click")

    col1, col2 = st.columns([2, 1])
    with col1:
        st.image(image, use_column_width=True)

    with col2:
        if coords:
            x, y = int(coords['x']), int(coords['y'])
            img_array = np.array(image)
            pixel = img_array[y, x]
            R, G, B = int(pixel[0]), int(pixel[1]), int(pixel[2])

            colors_df = load_colors("colors.csv")
            match = get_closest_color(R, G, B, colors_df)

            st.success("🎯 Color Detected!")
            st.markdown(f"**📛 Color Name:** `{match['color_name']}`")
            st.markdown(f"**🔢 RGB:** ({R}, {G}, {B})")
            st.markdown(f"**🟩 HEX Code:** `{match['hex']}`")

            st.markdown("**🎨 Preview:**")
            st.markdown(
                f"<div class='color-box' style='background-color:rgb({R},{G},{B});'></div>",
                unsafe_allow_html=True
            )
        else:
            st.info("👆 Click on the image to detect a color.")
else:
    st.warning("📁 Please upload an image to start detecting colors.")
st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------- TABS FOR EXTRA FEATURES ----------------------------
if "color_history" in st.session_state and st.session_state.color_history:
    with st.expander("📜 Detected Color History"):
        df_history = pd.DataFrame(st.session_state.color_history)
        st.dataframe(df_history)

        csv_data = convert_df_to_csv(df_history)
        st.download_button("📥 Download Color History as CSV", data=csv_data, file_name="color_history.csv", mime="text/csv")

# ---------------------------- FOOTER ----------------------------
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<div class='footer'>Developed by Srinithija 💖 | Enhanced with History & Styling 🌟</div>", unsafe_allow_html=True)
