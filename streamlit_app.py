# streamlit_app.py — Personal Vedic Panchang App
# Accurate Astronomical Calculations with Ephem, Geolocation, Kaal Timings, Swara, and Sandhya
import streamlit as st
from datetime import datetime, date, timedelta, time
import pytz
import math
import ephem
from streamlit_autorefresh import st_autorefresh
from typing import Dict, Any, Optional, List
import pandas as pd
import altair as alt

from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder

# Page Configuration
st.set_page_config(
    page_title="Personal Panchang",
    page_icon="🕉️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# --- MODERN STYLING ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@500;700&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .panchang-header {
        text-align: center;
        margin-bottom: 1.5rem;
        padding-top: 0.5rem;
    }
    
    .panchang-title {
        font-family: 'Cinzel', serif;
        font-size: 2.2rem;
        font-weight: 700;
        letter-spacing: 1px;
        color: #B45309;
        margin: 0;
    }
    
    .panchang-subtitle {
        font-size: 0.95rem;
        color: #6B7280;
        margin-top: 4px;
    }
    
    .card-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
        gap: 12px;
        margin: 1rem 0;
    }
    
    .panchang-card {
        background: #FAF8F5;
        border: 1px solid #EAE3D9;
        border-radius: 12px;
        padding: 12px 14px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    
    .panchang-card-title {
        font-size: 0.8rem;
        font-weight: 600;
        color: #78350F;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 4px;
    }
    
    .panchang-card-val {
        font-size: 1.15rem;
        font-weight: 700;
        color: #1F2937;
    }
    
    .panchang-card-sub {
        font-size: 0.75rem;
        color: #6B7280;
        margin-top: 2px;
    }
    
    .section-title {
        font-family: 'Cinzel', serif;
        font-size: 1.25rem;
        font-weight: 700;
        color: #92400E;
        text-align: center;
        margin-top: 1.5rem;
        margin-bottom: 0.8rem;
        border-bottom: 2px solid #F3E8DC;
        padding-bottom: 6px;
    }
    
    .swara-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.9rem;
    }
    
    .swara-ida {
        background-color: #DBEAFE;
        color: #1E40AF;
        border: 1px solid #93C5FD;
    }
    
    .swara-pingala {
        background-color: #FEE2E2;
        color: #991B1B;
        border: 1px solid #FCA5A5;
    }
    
    .table-container {
        width: 100%;
        overflow-x: auto;
        margin: 12px 0;
    }
    
    .custom-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.88rem;
    }
    
    .custom-table th {
        background-color: #F5EFEB;
        color: #78350F;
        padding: 8px 12px;
        text-align: left;
        font-weight: 600;
        border-bottom: 2px solid #E5D5C5;
    }
    
    .custom-table td {
        padding: 8px 12px;
        border-bottom: 1px solid #F0E6DC;
    }
    
    .clock-banner {
        background: linear-gradient(135deg, #FFFBEB 0%, #FEF3C7 100%);
        border: 1px solid #FDE68A;
        border-radius: 14px;
        padding: 16px;
        text-align: center;
        margin: 1.5rem 0;
    }
    
    .clock-time {
        font-size: 2.2rem;
        font-weight: 700;
        color: #78350F;
        font-family: 'Cinzel', serif;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Header
st.markdown(
    """
    <div class="panchang-header">
        <h1 class="panchang-title">🕉️ Personal Vedic Panchang</h1>
        <div class="panchang-subtitle">Accurate Ephem Timings • Kaal Cycle • Swara • Naad Sadhana</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- POPULAR CITIES PRELOADED (Offline / Cloud Resilient) ---
KNOWN_CITIES = {
    "kolhapur": {"lat": "16.7050", "lon": "74.2433", "elevation": 569, "tz": "Asia/Kolkata", "display_name": "Kolhapur, Maharashtra, India"},
    "mumbai": {"lat": "19.0760", "lon": "72.8777", "elevation": 14, "tz": "Asia/Kolkata", "display_name": "Mumbai, Maharashtra, India"},
    "pune": {"lat": "18.5204", "lon": "73.8567", "elevation": 560, "tz": "Asia/Kolkata", "display_name": "Pune, Maharashtra, India"},
    "delhi": {"lat": "28.6139", "lon": "77.2090", "elevation": 216, "tz": "Asia/Kolkata", "display_name": "New Delhi, Delhi, India"},
    "bengaluru": {"lat": "12.9716", "lon": "77.5946", "elevation": 920, "tz": "Asia/Kolkata", "display_name": "Bengaluru, Karnataka, India"},
    "bangalore": {"lat": "12.9716", "lon": "77.5946", "elevation": 920, "tz": "Asia/Kolkata", "display_name": "Bengaluru, Karnataka, India"},
    "hyderabad": {"lat": "17.3850", "lon": "78.4867", "elevation": 542, "tz": "Asia/Kolkata", "display_name": "Hyderabad, Telangana, India"},
    "chennai": {"lat": "13.0827", "lon": "80.2707", "elevation": 6, "tz": "Asia/Kolkata", "display_name": "Chennai, Tamil Nadu, India"},
    "kolkata": {"lat": "22.5726", "lon": "88.3639", "elevation": 9, "tz": "Asia/Kolkata", "display_name": "Kolkata, West Bengal, India"},
    "ahmedabad": {"lat": "23.0225", "lon": "72.5714", "elevation": 53, "tz": "Asia/Kolkata", "display_name": "Ahmedabad, Gujarat, India"},
    "varanasi": {"lat": "25.3176", "lon": "82.9739", "elevation": 81, "tz": "Asia/Kolkata", "display_name": "Varanasi, Uttar Pradesh, India"},
    "jaipur": {"lat": "26.9124", "lon": "75.7873", "elevation": 431, "tz": "Asia/Kolkata", "display_name": "Jaipur, Rajasthan, India"},
    "ayodhya": {"lat": "26.7922", "lon": "82.1998", "elevation": 93, "tz": "Asia/Kolkata", "display_name": "Ayodhya, Uttar Pradesh, India"},
    "ujjain": {"lat": "23.1765", "lon": "75.7885", "elevation": 491, "tz": "Asia/Kolkata", "display_name": "Ujjain, Madhya Pradesh, India"},
    "london": {"lat": "51.5074", "lon": "-0.1278", "elevation": 11, "tz": "Europe/London", "display_name": "London, United Kingdom"},
    "new york": {"lat": "40.7128", "lon": "-74.0060", "elevation": 10, "tz": "America/New_York", "display_name": "New York, USA"},
    "san francisco": {"lat": "37.7749", "lon": "-122.4194", "elevation": 16, "tz": "America/Los_Angeles", "display_name": "San Francisco, USA"},
    "dubai": {"lat": "25.2048", "lon": "55.2708", "elevation": 5, "tz": "Asia/Dubai", "display_name": "Dubai, UAE"},
    "singapore": {"lat": "1.3521", "lon": "103.8198", "elevation": 15, "tz": "Asia/Singapore", "display_name": "Singapore"},
    "sydney": {"lat": "-33.8688", "lon": "151.2093", "elevation": 19, "tz": "Australia/Sydney", "display_name": "Sydney, Australia"},
    "toronto": {"lat": "43.6532", "lon": "-79.3832", "elevation": 76, "tz": "America/Toronto", "display_name": "Toronto, Canada"},
}

@st.cache_data(show_spinner=False, ttl=86400)
def get_location_details(city_name: str):
    clean_city = city_name.strip().lower()
    
    # 1. Fast local cache lookup
    if clean_city in KNOWN_CITIES:
        return KNOWN_CITIES[clean_city]
    
    # 2. Try Nominatim Geocoder
    try:
        geolocator = Nominatim(user_agent="vedic_panchang_streamlit_app_v1", timeout=5)
        location = geolocator.geocode(city_name, addressdetails=True)
        if location:
            tf = TimezoneFinder()
            tz_str = tf.timezone_at(lng=location.longitude, lat=location.latitude)
            elevation = 0
            if "altitude" in location.raw and location.raw["altitude"]:
                elevation = float(location.raw["altitude"])
            
            parts = [p.strip() for p in location.address.split(",")]
            short_name = f"{parts[0]}, {parts[-1]}" if len(parts) > 1 else location.address
            
            return {
                "lat": str(location.latitude),
                "lon": str(location.longitude),
                "elevation": elevation,
                "tz": tz_str if tz_str else "Asia/Kolkata",
                "display_name": short_name,
            }
    except Exception:
        pass
        
    # 3. Safe fallback
    return {
        "lat": "16.7050",
        "lon": "74.2433",
        "elevation": 569,
        "tz": "Asia/Kolkata",
        "display_name": f"{city_name.capitalize()} (Defaulting to Kolhapur coordinates)",
    }

# --- CONTROLS SECTION ---
col_loc, col_dt = st.columns([3, 2])
with col_loc:
    city_input = st.text_input("📍 City / Location", value="Kolhapur", help="Enter city name, e.g., Kolhapur, Mumbai, New York")
with col_dt:
    selected_date = st.date_input("📅 Date", value=date.today())

loc_details = get_location_details(city_input)

# Optional Manual Location Adjustment expander
with st.expander("⚙️ Location & Coordinate Details"):
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        custom_lat = st.text_input("Latitude", value=loc_details["lat"])
    with c2:
        custom_lon = st.text_input("Longitude", value=loc_details["lon"])
    with c3:
        custom_tz = st.text_input("Timezone", value=loc_details["tz"])
    with c4:
        custom_elev = st.number_input("Elevation (m)", value=int(loc_details["elevation"]), min_value=0, max_value=8000)

LATITUDE = str(custom_lat)
LONGITUDE = str(custom_lon)
ELEVATION = float(custom_elev)

try:
    TZ = pytz.timezone(custom_tz)
except Exception:
    TZ = pytz.timezone("Asia/Kolkata")

now = datetime.now(TZ)

st.caption(f"Using location: **{loc_details['display_name']}** | Timezone: `{custom_tz}` | Lat: `{LATITUDE}`, Lon: `{LONGITUDE}`")

# --- COLOR MAPS ---
KAAL_COLORS = {
    "Kartavya Kaal": "#F59E0B",  # Amber/Yellow (Solar)
    "Anand Kaal": "#3B82F6",     # Steel Blue (Lunar)
    "Prarabdh Kaal": "#8B5CF6",  # Purple (Combined)
    "Bhagya Kaal": "#78350F",    # Earth/Brown (Neutral)
}

RASHI_NAMES = [
    "Meṣa (Aries)",
    "Vṛṣabha (Taurus)",
    "Mithuna (Gemini)",
    "Karka (Cancer)",
    "Siṁha (Leo)",
    "Kanyā (Virgo)",
    "Tulā (Libra)",
    "Vṛścika (Scorpio)",
    "Dhanu (Sagittarius)",
    "Makara (Capricorn)",
    "Kumbha (Aquarius)",
    "Mīna (Pisces)",
]

NAKSHATRA_NAMES = [
    "Aśvinī", "Bharanī", "Kṛttikā", "Rohiṇī", "Mṛgaśīrṣa", "Ārdrā", "Punarvasu",
    "Puṣya", "Āśleṣā", "Maghā", "Pūrva Phalgunī", "Uttara Phalgunī", "Hasta",
    "Citrā", "Svātī", "Viśākhā", "Anurādhā", "Jyeṣṭha", "Mūla", "Pūrvāṣāḍhā",
    "Uttarāṣāḍhā", "Śravaṇa", "Dhaniṣṭhā", "Śatabhiṣā", "Pūrva Bhādrapadā",
    "Uttara Bhādrapadā", "Revatī"
]

NAKSHATRA_ATTRIBUTES: Dict[str, Dict[str, str]] = {
    "Aśvinī": {"Nadi": "Ida", "Tattva": "Vayu", "Adhipati": "Ketu", "Swabhava": "Guru"},
    "Bharanī": {"Nadi": "Pingala", "Tattva": "Agni", "Adhipati": "Shukra", "Swabhava": "Shukra"},
    "Kṛttikā": {"Nadi": "Ida", "Tattva": "Agni", "Adhipati": "Ravi", "Swabhava": "Shukra"},
    "Rohiṇī": {"Nadi": "Pingala", "Tattva": "Prithvi", "Adhipati": "Chandra", "Swabhava": "Budh"},
    "Mṛgaśīrṣa": {"Nadi": "Ida", "Tattva": "Vayu", "Adhipati": "Mangala", "Swabhava": "Guru"},
    "Ārdrā": {"Nadi": "Ida", "Tattva": "Jala", "Adhipati": "Rahu", "Swabhava": "Chandra"},
    "Punarvasu": {"Nadi": "Pingala", "Tattva": "Vayu", "Adhipati": "Guru", "Swabhava": "Shukra"},
    "Puṣya": {"Nadi": "Ida", "Tattva": "Agni", "Adhipati": "Shani", "Swabhava": "Guru"},
    "Āśleṣā": {"Nadi": "Ida", "Tattva": "Jala", "Adhipati": "Budh", "Swabhava": "Chandra"},
    "Maghā": {"Nadi": "Ida", "Tattva": "Agni", "Adhipati": "Ketu", "Swabhava": "Shukra"},
    "Pūrva Phalgunī": {"Nadi": "Pingala", "Tattva": "Agni", "Adhipati": "Shukra", "Swabhava": "Mangala"},
    "Uttara Phalgunī": {"Nadi": "Pingala", "Tattva": "Vayu", "Adhipati": "Ravi", "Swabhava": "Rahu"},
    "Hasta": {"Nadi": "Pingala", "Tattva": "Vayu", "Adhipati": "Chandra", "Swabhava": "Rahu"},
    "Citrā": {"Nadi": "Pingala", "Tattva": "Vayu", "Adhipati": "Mangala", "Swabhava": "Rahu"},
    "Svātī": {"Nadi": "Pingala", "Tattva": "Vayu", "Adhipati": "Rahu", "Swabhava": "Mangala"},
    "Viśākhā": {"Nadi": "Pingala", "Tattva": "Vayu", "Adhipati": "Guru", "Swabhava": "Rahu"},
    "Anurādhā": {"Nadi": "Ida", "Tattva": "Prithvi", "Adhipati": "Shani", "Swabhava": "Ravi"},
    "Jyeṣṭha": {"Nadi": "Pingala", "Tattva": "Prithvi", "Adhipati": "Budh", "Swabhava": "Ravi"},
    "Mūla": {"Nadi": "Pingala", "Tattva": "Jala", "Adhipati": "Ketu", "Swabhava": "Shani"},
    "Pūrvāṣāḍhā": {"Nadi": "Ida", "Tattva": "Jala", "Adhipati": "Shukra", "Swabhava": "Budh"},
    "Uttarāṣāḍhā": {"Nadi": "Ida", "Tattva": "Prithvi", "Adhipati": "Ravi", "Swabhava": "Budh"},
    "Śravaṇa": {"Nadi": "Ida", "Tattva": "Prithvi", "Adhipati": "Chandra", "Swabhava": "Budh"},
    "Dhaniṣṭhā": {"Nadi": "Ida", "Tattva": "Prithvi", "Adhipati": "Mangala", "Swabhava": "Budh"},
    "Śatabhiṣā": {"Nadi": "Ida", "Tattva": "Jala", "Adhipati": "Rahu", "Swabhava": "Shani"},
    "Pūrva Bhādrapadā": {"Nadi": "Ida", "Tattva": "Agni", "Adhipati": "Guru", "Swabhava": "Shukra"},
    "Uttara Bhādrapadā": {"Nadi": "Pingala", "Tattva": "Jala", "Adhipati": "Shani", "Swabhava": "Guru"},
    "Revatī": {"Nadi": "Pingala", "Tattva": "Jala", "Adhipati": "Budh", "Swabhava": "Chandra"},
}

SWARA_MAPPING: Dict[tuple, Dict[str, str]] = {
    ("Śukla", "Pratipada"): {"sunrise": "Ida", "sunset": "Pingala"},
    ("Śukla", "Dvitīya"): {"sunrise": "Ida", "sunset": "Pingala"},
    ("Śukla", "Tṛtīya"): {"sunrise": "Ida", "sunset": "Pingala"},
    ("Śukla", "Caturthī"): {"sunrise": "Pingala", "sunset": "Ida"},
    ("Śukla", "Pañchamī"): {"sunrise": "Ida", "sunset": "Pingala"},
    ("Śukla", "Ṣaṣṭhī"): {"sunrise": "Pingala", "sunset": "Ida"},
    ("Śukla", "Saptamī"): {"sunrise": "Ida", "sunset": "Pingala"},
    ("Śukla", "Aṣṭamī"): {"sunrise": "Pingala", "sunset": "Ida"},
    ("Śukla", "Navamī"): {"sunrise": "Ida", "sunset": "Pingala"},
    ("Śukla", "Daśamī"): {"sunrise": "Pingala", "sunset": "Ida"},
    ("Śukla", "Ekādaśī"): {"sunrise": "Ida", "sunset": "Pingala"},
    ("Śukla", "Dvādaśī"): {"sunrise": "Pingala", "sunset": "Ida"},
    ("Śukla", "Trayodaśī"): {"sunrise": "Ida", "sunset": "Pingala"},
    ("Śukla", "Caturdaśī"): {"sunrise": "Pingala", "sunset": "Ida"},
    ("Śukla", "Pūrṇimā"): {"sunrise": "Ida", "sunset": "Pingala"},
    ("Kṛṣṇa", "Pratipada"): {"sunrise": "Pingala", "sunset": "Ida"},
    ("Kṛṣṇa", "Dvitīya"): {"sunrise": "Pingala", "sunset": "Ida"},
    ("Kṛṣṇa", "Tṛtīya"): {"sunrise": "Pingala", "sunset": "Ida"},
    ("Kṛṣṇa", "Caturthī"): {"sunrise": "Ida", "sunset": "Pingala"},
    ("Kṛṣṇa", "Pañchamī"): {"sunrise": "Pingala", "sunset": "Ida"},
    ("Kṛṣṇa", "Ṣaṣṭhī"): {"sunrise": "Ida", "sunset": "Pingala"},
    ("Kṛṣṇa", "Saptamī"): {"sunrise": "Pingala", "sunset": "Ida"},
    ("Kṛṣṇa", "Aṣṭamī"): {"sunrise": "Ida", "sunset": "Pingala"},
    ("Kṛṣṇa", "Navamī"): {"sunrise": "Pingala", "sunset": "Ida"},
    ("Kṛṣṇa", "Daśamī"): {"sunrise": "Ida", "sunset": "Pingala"},
    ("Kṛṣṇa", "Ekādaśī"): {"sunrise": "Pingala", "sunset": "Ida"},
    ("Kṛṣṇa", "Dvādaśī"): {"sunrise": "Ida", "sunset": "Pingala"},
    ("Kṛṣṇa", "Trayodaśī"): {"sunrise": "Pingala", "sunset": "Ida"},
    ("Kṛṣṇa", "Caturdaśī"): {"sunrise": "Ida", "sunset": "Pingala"},
    ("Kṛṣṇa", "Amāvasyā"): {"sunrise": "Pingala", "sunset": "Ida"},
}

TITHI_NAME_MAP = {
    "pratipada": "Pratipada", "dvitiya": "Dvitīya", "tritiya": "Tṛtīya",
    "chaturthi": "Caturthī", "panchami": "Pañchamī", "shashthi": "Ṣaṣṭhī",
    "saptami": "Saptamī", "ashtami": "Aṣṭamī", "navami": "Navamī",
    "dashami": "Daśamī", "ekadashi": "Ekādaśī", "dvadashi": "Dvādaśī",
    "trayodashi": "Trayodaśī", "chaturdashi": "Caturdaśī",
    "pūrṇimā": "Pūrṇimā", "amāvasyā": "Amāvasyā",
}

NAAD_SADHANA_BASE_TIMES: Dict[tuple, str] = {
    ("Śukla", "Pratipada"): "5:32", ("Śukla", "Dvitīya"): "5:39", ("Śukla", "Tṛtīya"): "5:46",
    ("Śukla", "Caturthī"): "5:53", ("Śukla", "Pañchamī"): "6:00", ("Śukla", "Ṣaṣṭhī"): "6:07",
    ("Śukla", "Saptamī"): "6:14", ("Śukla", "Aṣṭamī"): "6:21", ("Śukla", "Navamī"): "6:28",
    ("Śukla", "Daśamī"): "6:35", ("Śukla", "Ekādaśī"): "6:42", ("Śukla", "Dvādaśī"): "6:49",
    ("Śukla", "Trayodaśī"): "6:56", ("Śukla", "Caturdaśī"): "7:03", ("Śukla", "Pūrṇimā"): "7:10",
    ("Kṛṣṇa", "Pratipada"): "7:03", ("Kṛṣṇa", "Dvitīya"): "6:56", ("Kṛṣṇa", "Tṛtīya"): "6:49",
    ("Kṛṣṇa", "Caturthī"): "6:42", ("Kṛṣṇa", "Pañchamī"): "6:35", ("Kṛṣṇa", "Ṣaṣṭhī"): "6:28",
    ("Kṛṣṇa", "Saptamī"): "6:21", ("Kṛṣṇa", "Aṣṭamī"): "6:14", ("Kṛṣṇa", "Navamī"): "6:07",
    ("Kṛṣṇa", "Daśamī"): "6:00", ("Kṛṣṇa", "Ekādaśī"): "5:53", ("Kṛṣṇa", "Dvādaśī"): "5:46",
    ("Kṛṣṇa", "Trayodaśī"): "5:39", ("Kṛṣṇa", "Caturdaśī"): "5:32", ("Kṛṣṇa", "Amāvasyā"): "5:25",
}

NAKSHATRA_ARC = 360.0 / 27.0

# --- Helper Astronomical Functions ---
def get_swaras_from_tithi(tithi_data: Dict[str, Any]) -> Dict[str, str]:
    default_swara = {"sunrise": "Unknown", "sunset": "Unknown"}
    try:
        tithi_name = tithi_data["name"]
        paksha = tithi_data["paksha"]
        paksha_lower = paksha.lower()
        if paksha_lower.startswith("kṛṣṇa") or paksha_lower.startswith("krishna"):
            standard_paksha = "Kṛṣṇa"
        elif paksha_lower.startswith("śukla") or paksha_lower.startswith("shukla"):
            standard_paksha = "Śukla"
        else:
            return default_swara
        tithi_key = tithi_name.strip().lower().replace(".", "")
        normalized_tithi_key = TITHI_NAME_MAP.get(tithi_key, tithi_name.strip())
        key = (standard_paksha, normalized_tithi_key)
        return SWARA_MAPPING.get(key, default_swara)
    except KeyError:
        return default_swara

def jd(dt):
    y, m, d = dt.year, dt.month, dt.day
    if m <= 2:
        y -= 1
        m += 12
    a = y // 100
    b = 2 - a + (a // 4)
    return (
        int(365.25 * (y + 4716))
        + int(30.6001 * (m + 1))
        + d
        + b
        - 1524.5
        + (dt.hour + dt.minute / 60.0 + dt.second / 3600.0) / 24
    )

def sun_long(jd_val):
    return (280.46646 + 36000.76983 * ((jd_val - 2451545.0) / 36525)) % 360

def moon_long(jd_val):
    return (218.31617 + 481267.8813 * ((jd_val - 2451545.0) / 36525)) % 360

def ayanamsa(jd_val):
    return (23.853 + 0.01397 * ((jd_val - 2451545.0) / 36525)) % 360

def sidereal(l, jd_val):
    return (l - ayanamsa(jd_val) + 360) % 360

def tithi(jd_val):
    s = sidereal(sun_long(jd_val), jd_val)
    m = sidereal(moon_long(jd_val), jd_val)
    diff = (m - s + 360) % 360
    return diff / 12.0

def nakshatra_value(jd_val):
    m_long = sidereal(moon_long(jd_val), jd_val)
    return m_long / NAKSHATRA_ARC

def get_rasi_name(sidereal_longitude: float) -> str:
    rasi_index = int(sidereal_longitude / 30) % 12
    return RASHI_NAMES[rasi_index]

def get_sun_rasi(ref_date):
    noon = TZ.localize(datetime(ref_date.year, ref_date.month, ref_date.day, 12, 0))
    jd_noon = jd(noon)
    s_long = sun_long(jd_noon)
    s_sidereal = sidereal(s_long, jd_noon)
    return get_rasi_name(s_sidereal)

def get_moon_rasi(ref_date):
    noon = TZ.localize(datetime(ref_date.year, ref_date.month, ref_date.day, 12, 0))
    jd_noon = jd(noon)
    m_long = moon_long(jd_noon)
    m_sidereal = sidereal(m_long, jd_noon)
    return get_rasi_name(m_sidereal)

def find_boundary_crossing(
    ref_jd: float, boundary_idx: float, period_val_func, cycle_length: int
) -> float:
    B = boundary_idx
    V_ref = period_val_func(ref_jd)
    delta = V_ref - B
    B_prime = B + round(delta / cycle_length) * cycle_length
    lo = ref_jd - 1.5
    hi = ref_jd + 1.5
    for _ in range(50):
        mid = (lo + hi) / 2
        value = period_val_func(mid)
        if value < B_prime:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2

def dt_from_jd(jd_val):
    utc_epoch = datetime(1970, 1, 1, tzinfo=pytz.utc)
    return (utc_epoch + timedelta(days=jd_val - 2440587.5)).astimezone(TZ)

def get_tithi_span(ref_date):
    noon = TZ.localize(datetime(ref_date.year, ref_date.month, ref_date.day, 12, 0))
    jd_noon = jd(noon)
    current_tithi_val = tithi(jd_noon)
    current_tithi_idx = int(current_tithi_val)
    if current_tithi_idx == 14:
        name_key = "Pūrṇimā"
        paksha = "Śukla"
    elif current_tithi_idx == 29:
        name_key = "Amāvasyā"
        paksha = "Kṛṣṇa"
    else:
        tithi_names = [
            "Pratipada", "Dvitīya", "Tṛtīya", "Caturthī", "Pañchamī",
            "Ṣaṣṭhī", "Saptamī", "Aṣṭamī", "Navamī", "Daśamī",
            "Ekādaśī", "Dvādaśī", "Trayodaśī", "Caturdaśī",
        ]
        name_key = tithi_names[current_tithi_idx % 15]
        paksha = "Śukla" if current_tithi_idx < 15 else "Kṛṣṇa"
    start_jd = find_boundary_crossing(jd_noon, current_tithi_idx, tithi, 30)
    end_jd = find_boundary_crossing(jd_noon, current_tithi_idx + 1, tithi, 30)
    return {
        "idx": current_tithi_idx,
        "name": name_key,
        "paksha": paksha,
        "start": dt_from_jd(start_jd),
        "end": dt_from_jd(end_jd),
    }

def get_nakshatra_span(ref_date):
    noon = TZ.localize(datetime(ref_date.year, ref_date.month, ref_date.day, 12, 0))
    jd_noon = jd(noon)
    current_nakshatra_val = nakshatra_value(jd_noon)
    current_nakshatra_idx = int(current_nakshatra_val) % 27
    name = NAKSHATRA_NAMES[current_nakshatra_idx]
    start_jd = find_boundary_crossing(
        jd_noon, current_nakshatra_idx, nakshatra_value, 27
    )
    end_jd = find_boundary_crossing(
        jd_noon, current_nakshatra_idx + 1, nakshatra_value, 27
    )
    return {
        "idx": current_nakshatra_idx,
        "name": name,
        "start": dt_from_jd(start_jd),
        "end": dt_from_jd(end_jd),
    }

# --- Calculation Data ---
weekday = selected_date.weekday()
day_index = (weekday + 1) % 7
swara_at_waking = ["Pingala", "Ida", "Pingala", "Ida", "Ida", "Ida", "Pingala"][day_index]

yesterday_tithi = get_tithi_span(selected_date - timedelta(days=1))
today_tithi = get_tithi_span(selected_date)
tomorrow_tithi = get_tithi_span(selected_date + timedelta(days=1))

yesterday_nakshatra = get_nakshatra_span(selected_date - timedelta(days=1))
today_nakshatra = get_nakshatra_span(selected_date)
tomorrow_nakshatra = get_nakshatra_span(selected_date + timedelta(days=1))

today_sun_rasi = get_sun_rasi(selected_date)
today_moon_rasi = get_moon_rasi(selected_date)

# --- ASTRONOMICAL CALCULATIONS (EPHEM) ---
def get_accurate_astro_times(target_date):
    obs = ephem.Observer()
    obs.lat = LATITUDE
    obs.lon = LONGITUDE
    obs.elevation = ELEVATION
    target_dt_local = TZ.localize(datetime.combine(target_date, time(0, 0, 0)))
    target_dt_utc = target_dt_local.astimezone(pytz.utc)
    obs.date = target_dt_utc

    sun = ephem.Sun()
    moon = ephem.Moon()

    sunrise_utc = obs.next_rising(sun).datetime()
    sunset_utc = obs.next_setting(sun).datetime()

    moon_rise_utc = None
    try:
        moon_rise_utc = obs.next_rising(moon).datetime()
    except (ephem.NeverUpError, ephem.AlwaysUpError):
        pass

    moon_set_utc = None
    try:
        moon_set_utc = obs.next_setting(moon).datetime()
    except (ephem.NeverUpError, ephem.AlwaysUpError):
        pass

    def to_local(utc_dt):
        if utc_dt is None:
            return None
        return pytz.utc.localize(utc_dt).astimezone(TZ)

    return {
        "sunrise": to_local(sunrise_utc),
        "sunset": to_local(sunset_utc),
        "moon_rise": to_local(moon_rise_utc),
        "moon_set": to_local(moon_set_utc),
    }

astro_data = get_accurate_astro_times(selected_date)
sunrise = astro_data["sunrise"]
sunset = astro_data["sunset"]
moon_rise = astro_data["moon_rise"]
moon_set = astro_data["moon_set"]

# Midpoint Calculations
def calculate_madhyamas(sunrise_dt: datetime, sunset_dt: datetime) -> Dict[str, datetime]:
    day_duration = sunset_dt - sunrise_dt
    day_madhyama = sunrise_dt + (day_duration / 2)
    next_sunrise = sunrise_dt + timedelta(days=1)
    night_duration = next_sunrise - sunset_dt
    night_madhyama = sunset_dt + (night_duration / 2)
    return {"day_madhyama": day_madhyama, "night_madhyama": night_madhyama}

madhyamas = calculate_madhyamas(sunrise, sunset)
midday = madhyamas["day_madhyama"]
midnight = madhyamas["night_madhyama"]

tithi_at_sunrise = (
    today_tithi
    if sunrise >= today_tithi["start"] and sunrise < today_tithi["end"]
    else (yesterday_tithi if sunrise < today_tithi["start"] else tomorrow_tithi)
)
tithi_at_sunset = (
    today_tithi
    if sunset >= today_tithi["start"] and sunset < today_tithi["end"]
    else (yesterday_tithi if sunset < today_tithi["start"] else tomorrow_tithi)
)

sunrise_swaras = get_swaras_from_tithi(tithi_at_sunrise)
sunset_swaras = get_swaras_from_tithi(tithi_at_sunset)

# Naad Sadhana Times
def calculate_naad_sadhana_times(midday_dt: datetime, current_date: date, tithi_data: Dict[str, Any]):
    minutes_to_subtract = midday_dt.minute
    adjustment = timedelta(minutes=minutes_to_subtract)
    tithi_key = (tithi_data["paksha"], tithi_data["name"])
    base_time_str = NAAD_SADHANA_BASE_TIMES.get(tithi_key)
    if not base_time_str:
        return {"morning_sadhana": None, "evening_sadhana": None}
    try:
        base_h, base_m = map(int, base_time_str.split(":"))
        morning_base_dt = TZ.localize(
            datetime(current_date.year, current_date.month, current_date.day, base_h, base_m)
        )
        morning_sadhana = morning_base_dt - adjustment
        evening_base_dt = morning_base_dt + timedelta(hours=12)
        evening_sadhana = evening_base_dt - adjustment
        if morning_sadhana.date() < morning_base_dt.date():
            morning_sadhana += timedelta(days=1)
        return {"morning_sadhana": morning_sadhana, "evening_sadhana": evening_sadhana}
    except ValueError:
        return {"morning_sadhana": None, "evening_sadhana": None}

naad_sadhana_times = calculate_naad_sadhana_times(midday, selected_date, tithi_at_sunrise)
morning_sadhana = naad_sadhana_times["morning_sadhana"]
evening_sadhana = naad_sadhana_times["evening_sadhana"]

# Sandhya Times
sandhya_times = {
    "morning": {"start": sunrise - timedelta(hours=1), "end": sunrise + timedelta(hours=1)},
    "midday": {"start": midday - timedelta(hours=1), "end": midday + timedelta(hours=1)},
    "evening": {"start": sunset - timedelta(hours=1), "end": sunset + timedelta(hours=1)},
    "midnight": {"start": midnight - timedelta(hours=1), "end": midnight + timedelta(hours=1)},
}

# Kaal Calculations
def calculate_kaal_periods(day_start_dt, day_end_dt, sunrise_dt, sunset_dt, moon_rise_dt, moon_set_dt):
    events = [
        (day_start_dt, "START"),
        (day_end_dt, "END"),
        (sunrise_dt, "SUN_RISE"),
        (sunset_dt, "SUN_SET"),
    ]
    if moon_rise_dt:
        events.append((moon_rise_dt, "MOON_RISE"))
    if moon_set_dt:
        events.append((moon_set_dt, "MOON_SET"))

    events = sorted([e for e in events if day_start_dt <= e[0] <= day_end_dt], key=lambda x: x[0])
    periods = []

    def is_moon_up_at(dt_check):
        obs_check = ephem.Observer()
        obs_check.lat = LATITUDE
        obs_check.lon = LONGITUDE
        obs_check.elevation = ELEVATION
        obs_check.date = dt_check.astimezone(pytz.utc)
        m = ephem.Moon()
        m.compute(obs_check)
        return m.alt > 0

    for i in range(len(events) - 1):
        start, end = events[i][0], events[i + 1][0]
        mid = start + (end - start) / 2
        is_sun = sunrise_dt <= mid < sunset_dt
        is_moon = is_moon_up_at(mid)
        if is_sun and is_moon:
            kaal = "Prarabdh Kaal"
        elif is_sun and not is_moon:
            kaal = "Kartavya Kaal"
        elif not is_sun and is_moon:
            kaal = "Anand Kaal"
        else:
            kaal = "Bhagya Kaal"
        periods.append({"Kaal": kaal, "Start": start, "End": end})

    merged = []
    for p in periods:
        if merged and merged[-1]["Kaal"] == p["Kaal"]:
            merged[-1]["End"] = p["End"]
        else:
            merged.append(p)
    return merged

day_start_dt = TZ.localize(datetime.combine(selected_date, time(0, 0)))
day_end_dt = day_start_dt + timedelta(days=1)
kaal_periods = calculate_kaal_periods(day_start_dt, day_end_dt, sunrise, sunset, moon_rise, moon_set)

chart_data = []
for p in kaal_periods:
    duration = (p["End"] - p["Start"]).total_seconds() / 3600
    chart_data.append({
        "Kaal": p["Kaal"],
        "Duration": duration,
        "Start": p["Start"].strftime("%H:%M"),
        "Start_dt": p["Start"],
        "End": p["End"].strftime("%H:%M"),
        "End_dt": p["End"],
        "TimeRange": f"{p['Start'].strftime('%I:%M %p')} - {p['End'].strftime('%I:%M %p')}"
    })
df_chart = pd.DataFrame(chart_data)

# --- UI PRESENTATION ---

# 1. Day Summary Banner
waking_badge_class = "swara-ida" if swara_at_waking == "Ida" else "swara-pingala"
st.markdown(
    f"""
    <div style="background: #FAF8F5; border: 1px solid #EAE3D9; border-radius: 14px; padding: 18px; text-align: center; margin-top: 0.5rem; margin-bottom: 1.5rem;">
        <div style="font-size: 0.95rem; font-weight: 600; color: #78350F; text-transform: uppercase; letter-spacing: 0.8px;">Waking Swara of the Day</div>
        <div style="margin: 8px 0;"><span class="swara-badge {waking_badge_class}" style="font-size: 1.3rem; padding: 6px 18px;">🌬️ {swara_at_waking} Swara</span></div>
        <div style="font-size: 1.05rem; font-weight: 600; color: #1F2937;">{selected_date.strftime('%A, %d %B %Y')}</div>
        <div style="font-size: 0.85rem; color: #6B7280; margin-top: 4px;">Today's Tithi: <b>{today_tithi['name']} ({today_tithi['paksha']})</b> • Nakshatra: <b>{today_nakshatra['name']}</b></div>
    </div>
    """,
    unsafe_allow_html=True,
)

# 2. Key Astro Rise/Set Cards
st.markdown('<div class="section-title">☀️ Astronomical Rise & Set</div>', unsafe_allow_html=True)
col_sr, col_ss, col_mr, col_ms = st.columns(4)

with col_sr:
    st.markdown(f"""
    <div class="panchang-card">
        <div class="panchang-card-title">🌅 Sunrise</div>
        <div class="panchang-card-val">{sunrise.strftime('%I:%M %p') if sunrise else 'N/A'}</div>
    </div>
    """, unsafe_allow_html=True)

with col_ss:
    st.markdown(f"""
    <div class="panchang-card">
        <div class="panchang-card-title">🌇 Sunset</div>
        <div class="panchang-card-val">{sunset.strftime('%I:%M %p') if sunset else 'N/A'}</div>
    </div>
    """, unsafe_allow_html=True)

with col_mr:
    st.markdown(f"""
    <div class="panchang-card">
        <div class="panchang-card-title">🌙 Moonrise</div>
        <div class="panchang-card-val">{moon_rise.strftime('%I:%M %p') if moon_rise else 'N/A'}</div>
    </div>
    """, unsafe_allow_html=True)

with col_ms:
    st.markdown(f"""
    <div class="panchang-card">
        <div class="panchang-card-title">🌘 Moonset</div>
        <div class="panchang-card-val">{moon_set.strftime('%I:%M %p') if moon_set else 'N/A'}</div>
    </div>
    """, unsafe_allow_html=True)

# 3. 24-Hour Kaal Cycle Wheel & Table
st.markdown('<div class="section-title">⌛ 24-Hour Kaal Cycle</div>', unsafe_allow_html=True)

if not df_chart.empty:
    col_chart, col_tbl = st.columns([1, 1])
    
    with col_chart:
        domain = list(KAAL_COLORS.keys())
        range_ = list(KAAL_COLORS.values())

        pie = (
            alt.Chart(df_chart)
            .mark_arc(innerRadius=65, outerRadius=115, stroke="#ffffff", strokeWidth=2)
            .encode(
                theta=alt.Theta("Duration:Q", stack=True),
                order=alt.Order("Start:O"),
                color=alt.Color(
                    "Kaal:N",
                    scale=alt.Scale(domain=domain, range=range_),
                    legend=alt.Legend(orient="bottom", columns=2, title=None)
                ),
                tooltip=[
                    alt.Tooltip("Kaal:N", title="Kaal"),
                    alt.Tooltip("TimeRange:N", title="Time Window"),
                    alt.Tooltip("Duration:Q", format=".2f", title="Duration (hrs)")
                ]
            )
            .properties(height=280)
        )
        st.altair_chart(pie, use_container_width=True)

    with col_tbl:
        table_html = """
        <div class="table-container">
            <table class="custom-table">
                <thead>
                    <tr><th>Kaal Period</th><th>Start</th><th>End</th><th>Hrs</th></tr>
                </thead>
                <tbody>
        """
        for p in kaal_periods:
            k_name = p["Kaal"]
            color_dot = KAAL_COLORS.get(k_name, "#78350F")
            dur = (p["End"] - p["Start"]).total_seconds() / 3600
            table_html += f"""
                <tr>
                    <td><span style="display:inline-block;width:10px;height:10px;border-radius:50%;background-color:{color_dot};margin-right:6px;"></span><b>{k_name}</b></td>
                    <td>{p['Start'].strftime('%I:%M %p')}</td>
                    <td>{p['End'].strftime('%I:%M %p')}</td>
                    <td>{dur:.1f}h</td>
                </tr>
            """
        table_html += "</tbody></table></div>"
        st.markdown(table_html, unsafe_allow_html=True)

# 4. Zodiac & Rasi
st.markdown('<div class="section-title">♈ Zodiac Sign (Rasi)</div>', unsafe_allow_html=True)
col_srasi, col_mrasi = st.columns(2)
with col_srasi:
    st.markdown(f"""
    <div class="panchang-card">
        <div class="panchang-card-title">☀️ Surya Rasi (Sun Sign)</div>
        <div class="panchang-card-val" style="color: #B45309;">{today_sun_rasi}</div>
    </div>
    """, unsafe_allow_html=True)
with col_mrasi:
    st.markdown(f"""
    <div class="panchang-card">
        <div class="panchang-card-title">🌙 Chandra Rasi (Moon Sign)</div>
        <div class="panchang-card-val" style="color: #1E40AF;">{today_moon_rasi}</div>
    </div>
    """, unsafe_allow_html=True)

# 5. Sandhya & Madhyama Timings
st.markdown('<div class="section-title">⏱️ Sandhya Windows & Midpoints</div>', unsafe_allow_html=True)
cs1, cs2, cs3, cs4 = st.columns(4)
with cs1:
    st.markdown(f"""
    <div class="panchang-card">
        <div class="panchang-card-title">Morning Sandhya</div>
        <div class="panchang-card-val" style="font-size:0.95rem;">{sandhya_times['morning']['start'].strftime('%I:%M %p')} - {sandhya_times['morning']['end'].strftime('%I:%M %p')}</div>
        <div class="panchang-card-sub">Mid: {sunrise.strftime('%I:%M %p')}</div>
    </div>
    """, unsafe_allow_html=True)
with cs2:
    st.markdown(f"""
    <div class="panchang-card">
        <div class="panchang-card-title">Midday Sandhya</div>
        <div class="panchang-card-val" style="font-size:0.95rem;">{sandhya_times['midday']['start'].strftime('%I:%M %p')} - {sandhya_times['midday']['end'].strftime('%I:%M %p')}</div>
        <div class="panchang-card-sub">Mid: {midday.strftime('%I:%M %p')}</div>
    </div>
    """, unsafe_allow_html=True)
with cs3:
    st.markdown(f"""
    <div class="panchang-card">
        <div class="panchang-card-title">Evening Sandhya</div>
        <div class="panchang-card-val" style="font-size:0.95rem;">{sandhya_times['evening']['start'].strftime('%I:%M %p')} - {sandhya_times['evening']['end'].strftime('%I:%M %p')}</div>
        <div class="panchang-card-sub">Mid: {sunset.strftime('%I:%M %p')}</div>
    </div>
    """, unsafe_allow_html=True)
with cs4:
    st.markdown(f"""
    <div class="panchang-card">
        <div class="panchang-card-title">Midnight Sandhya</div>
        <div class="panchang-card-val" style="font-size:0.95rem;">{sandhya_times['midnight']['start'].strftime('%I:%M %p')} - {sandhya_times['midnight']['end'].strftime('%I:%M %p')}</div>
        <div class="panchang-card-sub">Mid: {midnight.strftime('%I:%M %p')}</div>
    </div>
    """, unsafe_allow_html=True)

# 6. Naad Sadhana Times
st.markdown('<div class="section-title">🔔 Naad Sadhana Times</div>', unsafe_allow_html=True)
if morning_sadhana and evening_sadhana:
    cn1, cn2 = st.columns(2)
    with cn1:
        st.markdown(f"""
        <div class="panchang-card">
            <div class="panchang-card-title">🌅 Morning Naad Sadhana</div>
            <div class="panchang-card-val" style="color: #B45309;">{morning_sadhana.strftime('%I:%M %p')}</div>
        </div>
        """, unsafe_allow_html=True)
    with cn2:
        st.markdown(f"""
        <div class="panchang-card">
            <div class="panchang-card-title">🌇 Evening Naad Sadhana</div>
            <div class="panchang-card-val" style="color: #78350F;">{evening_sadhana.strftime('%I:%M %p')}</div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.warning("Could not compute exact Naad Sadhana times for the selected date.")

# 7. Nakshatra Timeline & Attributes
st.markdown('<div class="section-title">✨ Nakshatra Timings & Attributes</div>', unsafe_allow_html=True)
for label, n_data in [("Yesterday's", yesterday_nakshatra), ("Today's", today_nakshatra), ("Tomorrow's", tomorrow_nakshatra)]:
    attrs = NAKSHATRA_ATTRIBUTES.get(n_data["name"], {})
    is_today = label == "Today's"
    highlight_style = "border-left: 4px solid #B45309; background: #FAF5F0;" if is_today else "background: #FAF8F5;"
    st.markdown(
        f"""
        <div style="{highlight_style} border: 1px solid #EAE3D9; border-radius: 10px; padding: 12px 16px; margin-bottom: 8px;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                <div>
                    <span style="font-size: 0.8rem; font-weight: 600; color: #78350F; text-transform: uppercase;">{label}</span>
                    <span style="font-size: 1.1rem; font-weight: 700; color: #1F2937; margin-left: 8px;">{n_data['name']}</span>
                </div>
                <div style="font-size: 0.85rem; color: #4B5563;">
                    {n_data['start'].strftime('%b %d, %I:%M %p')} → {n_data['end'].strftime('%b %d, %I:%M %p')}
                </div>
            </div>
            <div style="font-size: 0.82rem; color: #6B7280; margin-top: 6px;">
                Nadi: <b>{attrs.get('Nadi','—')}</b> • Tattva: <b>{attrs.get('Tattva','—')}</b> • Adhipati: <b>{attrs.get('Adhipati','—')}</b> • Swabhava: <b>{attrs.get('Swabhava','—')}</b>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# 8. Tithi Timeline & Swara
st.markdown('<div class="section-title">🌘 Tithi & Swara Transitions</div>', unsafe_allow_html=True)
for label, t_data in [("Yesterday's", yesterday_tithi), ("Today's", today_tithi), ("Tomorrow's", tomorrow_tithi)]:
    is_today = label == "Today's"
    highlight_style = "border-left: 4px solid #B45309; background: #FAF5F0;" if is_today else "background: #FAF8F5;"
    st.markdown(
        f"""
        <div style="{highlight_style} border: 1px solid #EAE3D9; border-radius: 10px; padding: 12px 16px; margin-bottom: 8px;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                <div>
                    <span style="font-size: 0.8rem; font-weight: 600; color: #78350F; text-transform: uppercase;">{label}</span>
                    <span style="font-size: 1.1rem; font-weight: 700; color: #1F2937; margin-left: 8px;">{t_data['name']} ({t_data['paksha']} Paksha)</span>
                </div>
                <div style="font-size: 0.85rem; color: #4B5563;">
                    {t_data['start'].strftime('%b %d, %I:%M %p')} → {t_data['end'].strftime('%b %d, %I:%M %p')}
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# Swara at Sunrise & Sunset
sr_swara = sunrise_swaras.get('sunrise', 'Unknown')
ss_swara = sunset_swaras.get('sunset', 'Unknown')
sr_class = "swara-ida" if sr_swara == "Ida" else "swara-pingala"
ss_class = "swara-ida" if ss_swara == "Ida" else "swara-pingala"

csw1, csw2 = st.columns(2)
with csw1:
    st.markdown(f"""
    <div class="panchang-card">
        <div class="panchang-card-title">Sunrise Swara ({tithi_at_sunrise['name']})</div>
        <div style="margin-top: 6px;"><span class="swara-badge {sr_class}">🌬️ {sr_swara}</span></div>
    </div>
    """, unsafe_allow_html=True)
with csw2:
    st.markdown(f"""
    <div class="panchang-card">
        <div class="panchang-card-title">Sunset Swara ({tithi_at_sunset['name']})</div>
        <div style="margin-top: 6px;"><span class="swara-badge {ss_class}">🌬️ {ss_swara}</span></div>
    </div>
    """, unsafe_allow_html=True)

# Live Clock Banner
st.markdown(
    f"""
    <div class="clock-banner">
        <div style="font-size: 0.85rem; font-weight: 600; color: #78350F; text-transform: uppercase; letter-spacing: 1px;">Current Local Time ({loc_details['tz']})</div>
        <div class="clock-time">{now.strftime('%I:%M:%S %p')}</div>
        <div style="font-size: 0.85rem; color: #6B7280; margin-top: 4px;">{loc_details['display_name']} • Live Refresh Active</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Auto refresh every 60s
st_autorefresh(interval=60000, key="panchang_live_refresh")
