"""
Custom CSS styles for improved readability.
Enhancement 3 - WPP Financial Modeler v1.1
"""
import streamlit as st


def apply_custom_styles():
    """
    Apply custom CSS styles to improve readability throughout the application.
    
    Enhancement 3: Improves text contrast in blue information panels by setting
    text color to white (#FFFFFF) for better readability.
    """
    st.markdown("""
        <style>
        /* Enhancement 3: Improve guidance text contrast on blue info panels */
        
        /* Target all text elements within info alerts */
        [data-testid="stAlert"] [data-testid="stMarkdownContainer"],
        [data-testid="stAlert"] [data-testid="stMarkdownContainer"] p,
        [data-testid="stAlert"] [data-testid="stMarkdownContainer"] li,
        [data-testid="stAlert"] [data-testid="stMarkdownContainer"] ul,
        [data-testid="stAlert"] [data-testid="stMarkdownContainer"] strong,
        [data-testid="stAlert"] [data-testid="stMarkdownContainer"] em,
        [data-testid="stAlert"] [data-testid="stMarkdownContainer"] span,
        [data-testid="stAlert"] [data-testid="stMarkdownContainer"] div,
        [data-testid="stAlert"] p,
        [data-testid="stAlert"] li,
        [data-testid="stAlert"] strong,
        [data-testid="stAlert"] em,
        [data-testid="stAlert"] span {
            color: #FFFFFF !important;
        }
        
        /* Specifically target info-type alerts */
        div[data-testid="stNotificationContentInfo"],
        div[data-testid="stNotificationContentInfo"] *,
        div[data-testid="stNotificationContentInfo"] p,
        div[data-testid="stNotificationContentInfo"] li,
        div[data-testid="stNotificationContentInfo"] strong,
        div[data-testid="stNotificationContentInfo"] em,
        div[data-testid="stNotificationContentInfo"] span,
        div[data-testid="stNotificationContentInfo"] div {
            color: #FFFFFF !important;
        }
        
        /* Target the stAlert component with info styling */
        .stAlert[data-baseweb="notification"],
        .stAlert[data-baseweb="notification"] *,
        .stAlert[data-baseweb="notification"] p,
        .stAlert[data-baseweb="notification"] li,
        .stAlert[data-baseweb="notification"] strong,
        .stAlert[data-baseweb="notification"] em {
            color: #FFFFFF !important;
        }
        
        /* Ensure links in info panels are also white but underlined */
        [data-testid="stAlert"] a,
        div[data-testid="stNotificationContentInfo"] a {
            color: #FFFFFF !important;
            text-decoration: underline !important;
        }
        </style>
    """, unsafe_allow_html=True)
