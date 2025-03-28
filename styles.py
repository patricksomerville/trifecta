
def get_css():
    """
    Returns the CSS styles for the application
    """
    return """
    <style>
        /* Main app styling */
        .main .block-container {
            padding: 3rem 2rem;
            max-width: 1200px;
            margin: 0 auto;
        }
        
        /* Editor styling */
        .stAce {
            border-radius: 12px;
            border: 1px solid rgba(224, 224, 224, 0.3);
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: box-shadow 0.3s ease;
        }
        
        .stAce:hover {
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
        }
        
        /* Button styling */
        .stButton button {
            border-radius: 8px;
            padding: 0.5rem 1.5rem;
            font-weight: 600;
            transition: all 0.2s ease;
            border: none;
            background: linear-gradient(135deg, #4a9eff 0%, #2d7ad6 100%);
            color: white;
        }
        
        .stButton button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(45, 122, 214, 0.3);
        }
        
        /* File operations section */
        .sidebar .block-container {
            padding-top: 2rem;
            background: linear-gradient(180deg, rgba(248,249,250,0.1) 0%, rgba(248,249,250,0) 100%);
        }
        
        /* Footer styling */
        .footer {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            padding: 1rem;
            background-color: rgba(248,249,250,0.9);
            backdrop-filter: blur(10px);
            text-align: center;
            font-size: 0.9rem;
            color: #6c757d;
            border-top: 1px solid rgba(222,226,230,0.3);
            z-index: 100;
        }
        
        /* Header styling */
        h1 {
            font-size: 2.5rem !important;
            margin-bottom: 1.5rem !important;
            background: linear-gradient(135deg, #2d7ad6 0%, #4a9eff 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 700 !important;
        }
        
        /* Logo container */
        .logo-container {
            display: flex;
            align-items: center;
            margin-bottom: 2rem;
            padding: 1rem;
            background: rgba(255,255,255,0.05);
            border-radius: 12px;
            backdrop-filter: blur(10px);
        }
        
        /* Logo styling */
        .logo {
            width: 60px;
            height: 60px;
            margin-right: 1.5rem;
            filter: drop-shadow(0 4px 6px rgba(0,0,0,0.1));
            transition: transform 0.3s ease;
        }
        
        .logo:hover {
            transform: scale(1.1) rotate(5deg);
        }
        
        /* Make expanders more modern */
        .streamlit-expanderHeader {
            font-size: 1.1rem;
            font-weight: 600;
            background: rgba(255,255,255,0.05);
            border-radius: 8px;
            transition: all 0.2s ease;
        }
        
        .streamlit-expanderHeader:hover {
            background: rgba(255,255,255,0.1);
        }
        
        /* Custom scrollbar */
        ::-webkit-scrollbar {
            width: 10px;
            height: 10px;
        }
        
        ::-webkit-scrollbar-track {
            background: rgba(241,241,241,0.1);
            border-radius: 10px;
        }
        
        ::-webkit-scrollbar-thumb {
            background: rgba(136,136,136,0.5);
            border-radius: 10px;
            border: 2px solid rgba(241,241,241,0.1);
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: rgba(85,85,85,0.8);
        }

        /* Input and select styling */
        input, select, .stTextInput input, .stSelectbox select {
            border-radius: 8px !important;
            border: 1px solid rgba(224, 224, 224, 0.3) !important;
            padding: 0.5rem 1rem !important;
            transition: all 0.2s ease !important;
        }

        input:focus, select:focus, .stTextInput input:focus, .stSelectbox select:focus {
            border-color: #4a9eff !important;
            box-shadow: 0 0 0 2px rgba(74, 158, 255, 0.2) !important;
        }

        /* Card-like containers */
        .stMarkdown div {
            border-radius: 12px;
            transition: transform 0.2s ease;
        }

        /* File list styling */
        .file-list {
            background: rgba(255,255,255,0.02);
            border-radius: 12px;
            padding: 1rem;
            border: 1px solid rgba(224, 224, 224, 0.1);
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
            color: #e0e0e0 !important;
            background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%) !important;
        }
        
        .stApp {
            background: transparent !important;
        }
        
        .css-1d391kg, .css-1lcbmhc {
            background-color: rgba(37,37,38,0.8) !important;
            backdrop-filter: blur(10px);
        }
        
        input, select, .stTextInput input, .stSelectbox select {
            background-color: rgba(60,60,60,0.5) !important;
            color: #e0e0e0 !important;
            border-color: rgba(85,85,85,0.3) !important;
        }
        
        .stTextInput label, .stSelectbox label {
            color: #e0e0e0 !important;
        }
        
        .stButton button {
            background: linear-gradient(135deg, #4a9eff 0%, #2d7ad6 100%) !important;
            color: white !important;
        }
        
        .streamlit-expanderHeader {
            background-color: rgba(60,60,60,0.3) !important;
            color: #e0e0e0 !important;
        }
        
        .streamlit-expanderContent {
            background-color: rgba(37,37,38,0.5) !important;
            color: #e0e0e0 !important;
        }
        
        .footer {
            background-color: rgba(37,37,38,0.8) !important;
            color: #aaa !important;
            border-color: rgba(68,68,68,0.3) !important;
            backdrop-filter: blur(10px);
        }
        
        ::-webkit-scrollbar-track {
            background: rgba(51,51,51,0.3) !important;
        }
        
        ::-webkit-scrollbar-thumb {
            background: rgba(102,102,102,0.5) !important;
            border-color: rgba(51,51,51,0.3) !important;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: rgba(136,136,136,0.8) !important;
        }

        .file-list {
            background: rgba(0,0,0,0.2);
            border-color: rgba(255,255,255,0.1);
        }
    </style>
    """

def get_logo_svg():
    """
    Returns the SVG code for the logo
    """
    return """
    <svg width="60" height="60" viewBox="0 0 128 128" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <linearGradient id="pywrite" x1="70.252" x2="170.659" y1="1237.476" y2="1151.089" gradientTransform="matrix(.563 0 0 -.568 -29.215 707.817)" gradientUnits="userSpaceOnUse">
                <stop offset="0" stop-color="#5A9FD4"/>
                <stop offset="1" stop-color="#306998"/>
            </linearGradient>
            <linearGradient id="pywriteb" x1="209.474" x2="173.62" y1="1098.811" y2="1149.537" gradientTransform="matrix(.563 0 0 -.568 -29.215 707.817)" gradientUnits="userSpaceOnUse">
                <stop offset="0" stop-color="#FFD43B"/>
                <stop offset="1" stop-color="#FFE873"/>
            </linearGradient>
            <filter id="shadow">
                <feDropShadow dx="0" dy="2" stdDeviation="2" flood-color="#000" flood-opacity="0.3"/>
            </filter>
        </defs>
        <g filter="url(#shadow)">
            <path fill="url(#pywrite)" d="M63.391 1.988c-4.222.02-8.252.379-11.8 1.007-10.45 1.846-12.346 5.71-12.346 12.837v9.411h24.693v3.137h-33.961c-7.176 0-13.46 4.313-15.426 12.521-2.268 9.405-2.368 15.275 0 25.096 1.755 7.311 5.947 12.519 13.124 12.519h8.491v-11.282c0-8.151 7.051-15.34 15.426-15.34h24.665c6.866 0 12.346-5.654 12.346-12.548v-23.513c0-6.693-5.646-11.72-12.346-12.837-4.244-.706-8.645-1.027-12.866-1.008zm-13.354 7.569c2.55 0 4.634 2.117 4.634 4.721 0 2.593-2.083 4.69-4.634 4.69-2.56 0-4.633-2.097-4.633-4.69-.001-2.604 2.073-4.721 4.633-4.721z"/>
            <path fill="url(#pywriteb)" d="M91.682 28.38v10.966c0 8.5-7.208 15.655-15.426 15.655h-24.665c-6.756 0-12.346 5.783-12.346 12.549v23.515c0 6.691 5.818 10.628 12.346 12.547 7.816 2.297 15.312 2.713 24.665 0 6.216-1.801 12.346-5.423 12.346-12.547v-9.412h-24.664v-3.138h37.012c7.176 0 9.852-5.005 12.348-12.519 2.578-7.735 2.467-15.174 0-25.096-1.774-7.145-5.161-12.521-12.348-12.521h-9.268zm-13.873 59.547c2.561 0 4.634 2.097 4.634 4.692 0 2.602-2.074 4.719-4.634 4.719-2.55 0-4.633-2.117-4.633-4.719 0-2.595 2.083-4.692 4.633-4.692z"/>
        </g>
    </svg>
    """
