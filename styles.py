def get_css():
    """
    Returns the CSS styles for the application
    """
    return """
    <style>
        /* Main app styling */
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        
        /* Editor styling */
        .stAce {
            border-radius: 8px;
            border: 1px solid #E0E0E0;
            margin-bottom: 1rem;
        }
        
        /* Button styling */
        .stButton button {
            border-radius: 4px;
            padding: 0.3rem 1rem;
            font-weight: 500;
        }
        
        /* File operations section */
        .sidebar .block-container {
            padding-top: 2rem;
        }
        
        /* Footer styling */
        .footer {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            padding: 0.5rem;
            background-color: #f8f9fa;
            text-align: center;
            font-size: 0.8rem;
            color: #6c757d;
            border-top: 1px solid #dee2e6;
        }
        
        /* Header styling */
        h1 {
            font-size: 2.2rem !important;
            margin-bottom: 1rem !important;
        }
        
        /* Logo container */
        .logo-container {
            display: flex;
            align-items: center;
            margin-bottom: 1rem;
        }
        
        /* Logo styling */
        .logo {
            width: 50px;
            height: 50px;
            margin-right: 1rem;
        }
        
        /* Make expanders more compact */
        .streamlit-expanderHeader {
            font-size: 1rem;
            font-weight: 500;
        }
        
        /* Custom scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 10px;
        }
        
        ::-webkit-scrollbar-thumb {
            background: #888;
            border-radius: 10px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: #555;
        }
    </style>
    """

def get_dark_mode_css():
    """
    Returns the dark mode CSS styles
    """
    return """
    <style>
        body {
            color: #f0f0f0 !important;
            background-color: #1E1E1E !important;
        }
        
        .stApp {
            background-color: #1E1E1E !important;
        }
        
        /* Dark sidebar */
        .css-1d391kg, .css-1lcbmhc {
            background-color: #252526 !important;
        }
        
        /* Dark inputs and selects */
        input, select, .stTextInput input, .stSelectbox select {
            background-color: #3C3C3C !important;
            color: #f0f0f0 !important;
            border-color: #555 !important;
        }
        
        .stTextInput label, .stSelectbox label {
            color: #f0f0f0 !important;
        }
        
        /* Dark buttons */
        .stButton button {
            background-color: #3C3C3C !important;
            color: #f0f0f0 !important;
            border-color: #555 !important;
        }
        
        /* Dark expanders */
        .streamlit-expanderHeader {
            background-color: #3C3C3C !important;
            color: #f0f0f0 !important;
        }
        
        .streamlit-expanderContent {
            background-color: #252526 !important;
            color: #f0f0f0 !important;
        }
        
        /* Dark footer */
        .footer {
            background-color: #252526 !important;
            color: #aaa !important;
            border-color: #444 !important;
        }
        
        /* Dark scrollbar */
        ::-webkit-scrollbar-track {
            background: #333 !important;
        }
        
        ::-webkit-scrollbar-thumb {
            background: #666 !important;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: #888 !important;
        }
    </style>
    """

def get_logo_svg():
    """
    Returns the SVG code for the logo
    """
    return """
    <svg width="50" height="50" viewBox="0 0 128 128" xmlns="http://www.w3.org/2000/svg">
        <linearGradient id="pywrite" x1="70.252" x2="170.659" y1="1237.476" y2="1151.089" gradientTransform="matrix(.563 0 0 -.568 -29.215 707.817)" gradientUnits="userSpaceOnUse">
            <stop offset="0" stop-color="#5A9FD4"/>
            <stop offset="1" stop-color="#306998"/>
        </linearGradient>
        <linearGradient id="pywriteb" x1="209.474" x2="173.62" y1="1098.811" y2="1149.537" gradientTransform="matrix(.563 0 0 -.568 -29.215 707.817)" gradientUnits="userSpaceOnUse">
            <stop offset="0" stop-color="#FFD43B"/>
            <stop offset="1" stop-color="#FFE873"/>
        </linearGradient>
        <path fill="url(#pywrite)" d="M63.391 1.988c-4.222.02-8.252.379-11.8 1.007-10.45 1.846-12.346 5.71-12.346 12.837v9.411h24.693v3.137h-33.961c-7.176 0-13.46 4.313-15.426 12.521-2.268 9.405-2.368 15.275 0 25.096 1.755 7.311 5.947 12.519 13.124 12.519h8.491v-11.282c0-8.151 7.051-15.34 15.426-15.34h24.665c6.866 0 12.346-5.654 12.346-12.548v-23.513c0-6.693-5.646-11.72-12.346-12.837-4.244-.706-8.645-1.027-12.866-1.008zm-13.354 7.569c2.55 0 4.634 2.117 4.634 4.721 0 2.593-2.083 4.69-4.634 4.69-2.56 0-4.633-2.097-4.633-4.69-.001-2.604 2.073-4.721 4.633-4.721z"/>
        <path fill="url(#pywriteb)" d="M91.682 28.38v10.966c0 8.5-7.208 15.655-15.426 15.655h-24.665c-6.756 0-12.346 5.783-12.346 12.549v23.515c0 6.691 5.818 10.628 12.346 12.547 7.816 2.297 15.312 2.713 24.665 0 6.216-1.801 12.346-5.423 12.346-12.547v-9.412h-24.664v-3.138h37.012c7.176 0 9.852-5.005 12.348-12.519 2.578-7.735 2.467-15.174 0-25.096-1.774-7.145-5.161-12.521-12.348-12.521h-9.268zm-13.873 59.547c2.561 0 4.634 2.097 4.634 4.692 0 2.602-2.074 4.719-4.634 4.719-2.55 0-4.633-2.117-4.633-4.719 0-2.595 2.083-4.692 4.633-4.692z"/>
        <path fill="#000" d="M 65.922 12.988 L 82.906 26.488 L 74.406 26.488 L 62.906 17.488 L 62.906 35.988 L 57.406 35.988 L 57.406 12.988 L 65.922 12.988 z" opacity=".2"/>
        <path fill="#000" d="M 71.5 67.5 L 55.292 54.5 L 63.5 54.5 L 75.239 64.058 L 74.865 45.558 L 80.5 45.5 L 80.5 67.5 L 71.5 67.5 z" opacity=".2"/>
    </svg>
    """

