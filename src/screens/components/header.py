import streamlit as st

def header_home():
    logo_url="https://i.ibb.co/YTYGn5qV/logo.png";
    st.markdown(f"""
                <div style="display:flex;justify-content:center;align-items:center;flex-direction:column; margin-bottom:3px; margin-top:10px;">
                <img src='{logo_url}' style='height:100px'>
                <h1 style='text-align:center;color:#E0E3FF;'>SNAP<br>CLASS</br></h1>
                </div>
                """,unsafe_allow_html=True);

def header_dashboard():

    logo_url = "https://i.ibb.co/YTYGn5qV/logo.png"

    st.markdown(f"""
        <div style="display:flex; align-items:center; justify-content:center; gap:10px">
            <img src='{logo_url}' style='height:85px;' />
            <h2 style='text-align:left; color:#5865F2'>SNAP<br/>CLASS</h2>
        </div>

                """, unsafe_allow_html=True)