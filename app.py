# Data Sweeper - Full Featured Streamlit App

import streamlit as st
import pandas as pd
import os
from io import BytesIO
import plotly.express as px

# Page Setup
st.set_page_config(page_title="Data Sweeper", layout='wide')

# Custom CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Aclonica&display=swap');
    html, body {
        font-family: 'Aclonica', serif;
        background-color: #2c2c2c;
        color: white;
    }
    .block-container {
        background-color: #3b3b3b;
        border-radius: 15px;
        padding: 2rem;
        margin: 2rem 0;
        box-shadow: 0 5px 20px rgba(0,0,0,0.3);
    }
    h1, h2, h3 {
        color: #b39ddb;
    }
    .stButton>button, .stDownloadButton>button {
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-size: 1rem;
        transition: 0.3s ease;
        background-color: #FF5F1F;
        color: white;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.4);
    }
    .stButton>button:hover, .stDownloadButton>button:hover {
        background-color: #FF5733;
    }
    .stDownloadButton>button {
        background-color: #7e57c2;
    }
    .stDownloadButton>button:hover {
        background-color: #6a45a1;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📊 Data Sweeper")
st.write("Easily transform, clean, and convert your CSV and Excel files!")

# File loading function
def load_file(file):
    ext = os.path.splitext(file.name)[-1].lower()
    if ext == ".csv":
        return pd.read_csv(file)
    elif ext == ".xlsx":
        return pd.read_excel(file)
    else:
        return None

# Data cleaning function
def clean_data(df, remove_duplicates=False, fill_missing=False):
    if remove_duplicates:
        df.drop_duplicates(inplace=True)
    if fill_missing:
        numeric_cols = df.select_dtypes(include=['number']).columns
        df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
    return df

# File uploader
uploaded_files = st.file_uploader("📁 Upload CSV or Excel files", type=["csv", "xlsx"], accept_multiple_files=True)

if uploaded_files:
    for idx, file in enumerate(uploaded_files):
        df = load_file(file)
        if df is None:
            st.error(f"❌ Unsupported file: {file.name}")
            continue

        st.subheader(f"📄 File: {file.name}")
        st.write(f"Size: {file.size / 1024:.2f} KB")
        st.dataframe(df.head())

        with st.expander("📈 Data Summary"):
            st.dataframe(df.describe())
            st.write("**Missing Values per Column**")
            st.dataframe(df.isnull().sum())

        with st.expander("🧪 Data Info"):
            info_df = pd.DataFrame({
                "Column": df.columns,
                "Type": df.dtypes,
                "Missing Values": df.isnull().sum(),
                "Unique Values": df.nunique()
            })
            st.dataframe(info_df)

        with st.expander("🗑 Drop Columns"):
            drop_cols = st.multiselect("Select columns to drop", df.columns, key=f"drop_{idx}")
            if drop_cols:
                df.drop(columns=drop_cols, inplace=True)
                st.success(f"Dropped columns: {', '.join(drop_cols)}")

        with st.expander("🛠 Fill Missing Values (Advanced)"):
            fill_method = st.selectbox("Choose fill method", ["Mean", "Median", "Mode"], key=f"fill_{idx}")
            target_cols = st.multiselect("Select columns to fill", df.columns, key=f"fill_cols_{idx}")
            if st.button("Apply Fill Method", key=f"fill_btn_{idx}"):
                for col in target_cols:
                    if fill_method == "Mean":
                        df[col] = df[col].fillna(df[col].mean())
                    elif fill_method == "Median":
                        df[col] = df[col].fillna(df[col].median())
                    elif fill_method == "Mode":
                        df[col] = df[col].fillna(df[col].mode()[0])
                st.success("Missing values filled!")

        with st.expander("🧮 Select Columns"):
            selected_cols = st.multiselect("Pick columns to keep", df.columns.tolist(), default=df.columns.tolist(), key=f"cols_{idx}")
            df = df[selected_cols]

        with st.expander("📊 Advanced Visualization"):
            num_cols = df.select_dtypes(include='number').columns
            if len(num_cols) >= 2:
                x_axis = st.selectbox("X-Axis", num_cols, key=f"x_{idx}")
                y_axis = st.selectbox("Y-Axis", num_cols, key=f"y_{idx}")
                fig = px.bar(df, x=x_axis, y=y_axis, title=f"{y_axis} by {x_axis}")
                st.plotly_chart(fig)
            else:
                st.warning("Need at least 2 numeric columns for advanced charts.")

        with st.expander("🔁 Convert and Download"):
            convert_to = st.radio("Convert to", ["CSV", "Excel"], key=f"conv_{idx}")
            if st.button("Convert", key=f"convert_btn_{idx}"):
                buffer = BytesIO()
                new_ext = ".csv" if convert_to == "CSV" else ".xlsx"
                mime = "text/csv" if convert_to == "CSV" else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                if convert_to == "CSV":
                    df.to_csv(buffer, index=False)
                else:
                    df.to_excel(buffer, index=False, engine="openpyxl")
                buffer.seek(0)
                st.download_button(
                    label=f"⬇ Download as {convert_to}",
                    data=buffer,
                    file_name=file.name.replace(os.path.splitext(file.name)[-1], new_ext),
                    mime=mime
                )

st.success("✅ All files processed!")