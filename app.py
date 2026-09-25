# app.py — Entry point wrapper for Streamlit
import runpy

if __name__ == "__main__":
    runpy.run_module("streamlit_app", run_name="__main__")
else:
    import streamlit_app
