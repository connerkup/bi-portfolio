#!/usr/bin/env python3
"""
Debug script to understand the Streamlit Cloud deployment environment.
"""

import os
import streamlit as st
from pathlib import Path

st.title("🔍 Deployment Debug")

# Check current working directory
st.write(f"**Current working directory:** {os.getcwd()}")

# List all files in current directory
st.write("**Files in current directory:**")
current_files = os.listdir(".")
for file in sorted(current_files):
    if os.path.isfile(file):
        size = os.path.getsize(file)
        st.write(f"- {file} ({size:,} bytes)")
    else:
        st.write(f"- {file}/ (directory)")

# Check if portfolio.duckdb exists
db_path = "portfolio.duckdb"
if os.path.exists(db_path):
    size = os.path.getsize(db_path)
    st.success(f"✅ Database found: {db_path} ({size:,} bytes)")
else:
    st.error(f"❌ Database not found: {db_path}")

# Check parent directory
parent_files = os.listdir("..") if os.path.exists("..") else []
st.write("**Files in parent directory:**")
for file in sorted(parent_files):
    if os.path.isfile(f"../{file}"):
        size = os.path.getsize(f"../{file}")
        st.write(f"- {file} ({size:,} bytes)")
    else:
        st.write(f"- {file}/ (directory)")

# Check data directory if it exists
if os.path.exists("../data"):
    st.write("**Files in data directory:**")
    data_files = os.listdir("../data")
    for file in sorted(data_files):
        file_path = f"../data/{file}"
        if os.path.isfile(file_path):
            size = os.path.getsize(file_path)
            st.write(f"- {file} ({size:,} bytes)")
        else:
            st.write(f"- {file}/ (directory)") 