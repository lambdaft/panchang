# Panchang_v0.2.py - Modern Astro Dashboard
import streamlit as st
from datetime import datetime, date, timedelta, time
import pytz
import math
import ephem  # REQUIRES: pip install ephem
import json
from typing import Dict, Any, Optional, List
import pandas as pd

# NEW DEPENDENCIES FOR GEOLOCATION & TIMEZONE DETECTING
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder

# Page configuration
st.set_page_config(page_title="Personal Panchang v0.2", layout="wide")

# --- CUSTOM CSS FOR MODERN COSMIC THEME ---
st.markdown(
    """
    <style>
    /* Custom Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700;800&family=Outfit:wght@300;400;500;600;700&display=swap');

    /* Main App Background */
    .stApp {
        background: radial-gradient(circle at center, #0b0f19 0%, #03050a 100%) !important;
        color: #f1f5f9 !important;
        font-family: 'Outfit', 'Inter', sans-serif !important;
    }

    /* Override vertical spacing */
    div[data-testid="stVerticalBlock"] > div {
        background-color: transparent;
    }

    /* Custom CSS Cards */
    .astro-card {
        background: rgba(13, 20, 35, 0.75);
        border: 1px solid rgba(212, 175, 55, 0.25);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        backdrop-filter: blur(12px);
        transition: transform 0.3s ease, border-color 0.3s ease;
    }
    .astro-card:hover {
        border-color: rgba(212, 175, 55, 0.45);
        transform: translateY(-2px);
    }

    .astro-card-title {
        font-family: 'Cinzel', 'Playfair Display', serif;
        font-size: 1.25rem;
        font-weight: 700;
        color: #fcd34d; /* Pale Gold */
        margin-bottom: 18px;
        border-bottom: 1.5px solid rgba(212, 175, 55, 0.3);
        padding-bottom: 8px;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .astro-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
        gap: 16px;
        margin-top: 8px;
    }

    .astro-item {
        text-align: center;
        padding: 14px 10px;
        background: rgba(255, 255, 255, 0.02);
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        transition: background 0.3s ease;
    }
    .astro-item:hover {
        background: rgba(255, 255, 255, 0.04);
    }

    .astro-label {
        font-size: 0.72rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 6px;
    }

    .astro-value {
        font-size: 1.2rem;
        font-weight: 700;
        color: #ffffff;
    }

    .astro-value-highlight {
        color: #fcd34d;
    }

    .astro-subtext {
        font-size: 0.75rem;
        color: #64748b;
        margin-top: 6px;
        line-height: 1.3;
    }

    /* Styled table for Kaals */
    .kaal-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.9rem;
        margin-top: 10px;
    }
    .kaal-table th {
        border-bottom: 1px solid rgba(212, 175, 55, 0.3);
        padding: 10px;
        text-align: left;
        color: #94a3b8;
        font-weight: 600;
        text-transform: uppercase;
        font-size: 0.75rem;
        letter-spacing: 0.05em;
    }
    .kaal-table td {
        padding: 12px 10px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        color: #e2e8f0;
    }
    .kaal-table tr:hover {
        background: rgba(255, 255, 255, 0.02);
    }

    /* Hide Streamlit components for standalone dashboard look */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Presets buttons styling */
    .stButton>button {
        background-color: rgba(212, 175, 55, 0.08) !important;
        color: #fcd34d !important;
        border: 1px solid rgba(212, 175, 55, 0.25) !important;
        border-radius: 8px !important;
        padding: 4px 12px !important;
        font-size: 0.85rem !important;
        transition: all 0.25s ease !important;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: rgba(212, 175, 55, 0.2) !important;
        border-color: #fcd34d !important;
        color: #ffffff !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 10px rgba(0,0,0,0.25);
    }

    /* Inputs style */
    div[data-baseweb="input"] {
        background-color: rgba(15, 23, 42, 0.6) !important;
        border: 1px solid rgba(212, 175, 55, 0.2) !important;
        border-radius: 8px !important;
    }
    div[data-baseweb="input"] input {
        color: #ffffff !important;
        font-family: 'Outfit', sans-serif !important;
    }

    /* Date selector widget overlay color */
    div[data-baseweb="calendar"] {
        background-color: #0d1527 !important;
        color: #ffffff !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Header Title
st.markdown(
    "<h1 style='text-align: center; font-family: Cinzel, serif; font-weight: 800; font-size: 38px; margin-top: 10px; margin-bottom: 5px; color: #fcd34d; text-shadow: 0 4px 12px rgba(0,0,0,0.5);'>Vedic Astro Dashboard</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align: center; font-size: 14px; color: #94a3b8; margin-top: 0; margin-bottom: 25px; letter-spacing: 0.08em; text-transform: uppercase;'>Solar/Lunar Cycles, Kaal Visualizer & Precise Muhurtas</p>",
    unsafe_allow_html=True,
)

# Initialize Session State
if "city" not in st.session_state:
    st.session_state.city = "Kolhapur"

# Location & Settings Card
st.markdown("<div class='astro-card'>", unsafe_allow_html=True)
st.markdown("<div class='astro-card-title'>🧭 Space & Time Reference</div>", unsafe_allow_html=True)

col_inputs, col_presets = st.columns([2, 3])

with col_inputs:
    city_input = st.text_input("Enter City Name", value=st.session_state.city)
    if city_input != st.session_state.city:
        st.session_state.city = city_input
        st.rerun()
    
    selected_date = st.date_input("Target Date", value=date.today())

with col_presets:
    st.markdown("<p style='font-size: 0.85rem; color: #94a3b8; margin-bottom: 10px;'>Quick Presets:</p>", unsafe_allow_html=True)
    p_cols = st.columns(3)
    presets = ["Kolhapur", "Mumbai", "London", "New York", "San Francisco", "Tokyo"]
    for i, p_name in enumerate(presets):
        with p_cols[i % 3]:
            if st.button(p_name, key=f"p_{p_name}"):
                st.session_state.city = p_name
                st.rerun()

st.markdown("</div>", unsafe_allow_html=True)


# --- GEOLOCATION RESOLUTION ---
@st.cache_data(show_spinner="Resolving city details...")
def get_location_details(city_name: str):
    try:
        geolocator = Nominatim(user_agent="panchang_app_v2")
        location = geolocator.geocode(city_name, addressdetails=True)
        if location:
            tf = TimezoneFinder()
            tz_str = tf.timezone_at(lng=location.longitude, lat=location.latitude)
            elevation = 0
            if "altitude" in location.raw and location.raw["altitude"]:
                elevation = float(location.raw["altitude"])

            return {
                "lat": str(location.latitude),
                "lon": str(location.longitude),
                "elevation": elevation,
                "tz": tz_str if tz_str else "Asia/Kolkata",
                "display_name": location.address.split(",")[0]
                + ", "
                + location.address.split(",")[-1].strip(),
            }
    except Exception:
        pass
    # Fallback to Kolhapur defaults
    return {
        "lat": "16.7050",
        "lon": "74.2433",
        "elevation": 569,
        "tz": "Asia/Kolkata",
        "display_name": "Kolhapur, India (Fallback)",
    }


loc_details = get_location_details(st.session_state.city)

LATITUDE = loc_details["lat"]
LONGITUDE = loc_details["lon"]
ELEVATION = loc_details["elevation"]
TZ = pytz.timezone(loc_details["tz"])
now = datetime.now(TZ)

# Show dynamic location summary bar
st.markdown(
    f"<p style='font-size: 13px; color: #fcd34d; opacity: 0.8; margin-top: -15px; margin-bottom: 20px; text-align: center;'>🌐 Coordinates: {float(LATITUDE):.4f}°N, {float(LONGITUDE):.4f}°E | Timezone: {loc_details['tz']} ({now.strftime('%Z %z')})</p>",
    unsafe_allow_html=True,
)

# --- CONSTANTS & COLOR MAPS ---
KAAL_COLORS = {
    "Kartavya Kaal": "#FFC300",  # Amber/Yellow (Solar)
    "Anand Kaal": "#4682B4",  # Steel Blue (Lunar)
    "Prarabdh Kaal": "#800080",  # Purple (Combined)
    "Bhagya Kaal": "#3a3f47",  # Dark grey (Neutral/Earth)
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
    "pratipada": "Pratipada",
    "dvitiya": "Dvitīya",
    "tritiya": "Tṛtīya",
    "chaturthi": "Caturthī",
    "panchami": "Pañchamī",
    "shashthi": "Ṣaṣṭhī",
    "saptami": "Saptamī",
    "ashtami": "Aṣṭamī",
    "navami": "Navamī",
    "dashami": "Daśamī",
    "ekadashi": "Ekādaśī",
    "dvadashi": "Dvādaśī",
    "trayodashi": "Trayodaśī",
    "chaturdashi": "Caturdaśī",
    "pūrṇimā": "Pūrṇimā",
    "amāvasyā": "Amāvasyā",
}

NAAD_SADHANA_BASE_TIMES: Dict[tuple, str] = {
    ("Śukla", "Pratipada"): "5:32",
    ("Śukla", "Dvitīya"): "5:39",
    ("Śukla", "Tṛtīya"): "5:46",
    ("Śukla", "Caturthī"): "5:53",
    ("Śukla", "Pañchamī"): "6:00",
    ("Śukla", "Ṣaṣṭhī"): "6:07",
    ("Śukla", "Saptamī"): "6:14",
    ("Śukla", "Aṣṭamī"): "6:21",
    ("Śukla", "Navamī"): "6:28",
    ("Śukla", "Daśamī"): "6:35",
    ("Śukla", "Ekādaśī"): "6:42",
    ("Śukla", "Dvādaśī"): "6:49",
    ("Śukla", "Trayodaśī"): "6:56",
    ("Śukla", "Caturdaśī"): "7:03",
    ("Śukla", "Pūrṇimā"): "7:10",
    ("Kṛṣṇa", "Pratipada"): "7:03",
    ("Kṛṣṇa", "Dvitīya"): "6:56",
    ("Kṛṣṇa", "Tṛtīya"): "6:49",
    ("Kṛṣṇa", "Caturthī"): "6:42",
    ("Kṛṣṇa", "Pañchamī"): "6:35",
    ("Kṛṣṇa", "Ṣaṣṭhī"): "6:28",
    ("Kṛṣṇa", "Saptamī"): "6:21",
    ("Kṛṣṇa", "Aṣṭamī"): "6:14",
    ("Kṛṣṇa", "Navamī"): "6:07",
    ("Kṛṣṇa", "Daśamī"): "6:00",
    ("Kṛṣṇa", "Ekādaśī"): "5:53",
    ("Kṛṣṇa", "Dvādaśī"): "5:46",
    ("Kṛṣṇa", "Trayodaśī"): "5:39",
    ("Kṛṣṇa", "Caturdaśī"): "5:32",
    ("Kṛṣṇa", "Amāvasyā"): "5:25",
}

NAKSHATRA_NAMES = [
    "Aśvinī", "Bharanī", "Kṛttikā", "Rohiṇī", "Mṛgaśīrṣa", "Ārdrā", "Punarvasu", "Puṣya", "Āśleṣā",
    "Maghā", "Pūrva Phalgunī", "Uttara Phalgunī", "Hasta", "Citrā", "Svātī", "Viśākhā", "Anurādhā",
    "Jyeṣṭha", "Mūla", "Pūrvāṣāḍhā", "Uttarāṣāḍhā", "Śravaṇa", "Dhaniṣṭhā", "Śatabhiṣā",
    "Pūrva Bhādrapadā", "Uttara Bhādrapadā", "Revatī"
]
NAKSHATRA_ARC = 360.0 / 27.0


# --- CELESTIAL CALCULATIONS (EPHEM/ASTRO) ---
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

def find_boundary_crossing(ref_jd: float, boundary_idx: float, period_val_func, cycle_length: int) -> float:
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
    return datetime.fromtimestamp((jd_val - 2440587.5) * 86400, tz=TZ)

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
            "Pratipada", "Dvitīya", "Tṛtīya", "Caturthī", "Pañchamī", "Ṣaṣṭhī", "Saptamī",
            "Aṣṭamī", "Navamī", "Daśamī", "Ekādaśī", "Dvādaśī", "Trayodaśī", "Caturdaśī"
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
    start_jd = find_boundary_crossing(jd_noon, current_nakshatra_idx, nakshatra_value, 27)
    end_jd = find_boundary_crossing(jd_noon, current_nakshatra_idx + 1, nakshatra_value, 27)
    return {
        "idx": current_nakshatra_idx,
        "name": name,
        "start": dt_from_jd(start_jd),
        "end": dt_from_jd(end_jd),
    }

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

def get_swara_color(swara):
    if swara == "Ida":
        return "#4682B4"  # Steel Blue (Lunar/Cool)
    elif swara == "Pingala":
        return "#FF8C00"  # Dark Orange (Solar/Hot)
    else:
        return "#94a3b8"

# Waking Swara
weekday = selected_date.weekday()
day_index = (weekday + 1) % 7
swara_at_waking = ["Pingala", "Ida", "Pingala", "Ida", "Ida", "Ida", "Pingala"][day_index]

# Calculate basic Panchang data
yesterday_tithi = get_tithi_span(selected_date - timedelta(days=1))
today_tithi = get_tithi_span(selected_date)
tomorrow_tithi = get_tithi_span(selected_date + timedelta(days=1))

yesterday_nakshatra = get_nakshatra_span(selected_date - timedelta(days=1))
today_nakshatra = get_nakshatra_span(selected_date)
tomorrow_nakshatra = get_nakshatra_span(selected_date + timedelta(days=1))

today_sun_rasi = get_sun_rasi(selected_date)
today_moon_rasi = get_moon_rasi(selected_date)

# Precise Rise/Set Timings (using ephem)
def get_accurate_astro_times(target_date):
    obs = ephem.Observer()
    obs.lat, obs.lon, obs.elevation = LATITUDE, LONGITUDE, ELEVATION
    target_dt_ist = TZ.localize(datetime.combine(target_date, time(0, 0, 0)))
    target_dt_utc = target_dt_ist.astimezone(pytz.utc)
    obs.date = target_dt_utc

    sun = ephem.Sun()
    moon = ephem.Moon()

    sunrise_utc = obs.next_rising(sun).datetime()
    sunset_utc = obs.next_setting(sun).datetime()

    moon_rise_utc = None
    try:
        moon_rise_utc = obs.next_rising(moon).datetime()
    except Exception:
        pass

    moon_set_utc = None
    try:
        moon_set_utc = obs.next_setting(moon).datetime()
    except Exception:
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
def calculate_madhyamas(sunrise: datetime, sunset: datetime) -> Dict[str, datetime]:
    day_duration = sunset - sunrise
    day_madhyama = sunrise + (day_duration / 2)
    next_sunrise = sunrise + timedelta(days=1)
    night_duration = next_sunrise - sunset
    night_madhyama = sunset + (night_duration / 2)
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
sunrise_swara_color = get_swara_color(sunrise_swaras["sunrise"])
sunset_swara_color = get_swara_color(sunset_swaras["sunset"])

# Naad Sadhana Calculations
def calculate_naad_sadhana_times(midday: datetime, current_date: date, tithi_data: Dict[str, Any]):
    minutes_to_subtract = midday.minute
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

# Sandhya Times (2-hour windows centered on sunrise, midday, sunset, midnight)
def calculate_sandhya_times(sunrise, midday, sunset, midnight):
    return {
        "morning": {
            "start": sunrise - timedelta(hours=1),
            "end": sunrise + timedelta(hours=1),
        },
        "midday": {
            "start": midday - timedelta(hours=1),
            "end": midday + timedelta(hours=1),
        },
        "evening": {
            "start": sunset - timedelta(hours=1),
            "end": sunset + timedelta(hours=1),
        },
        "midnight": {
            "start": midnight - timedelta(hours=1),
            "end": midnight + timedelta(hours=1),
        },
    }

sandhya_times = calculate_sandhya_times(sunrise, midday, sunset, midnight)

# --- DYNAMIC MUHURTAS & PLANETARY KAALS (1/8th Day Divisions) ---
def calculate_muhurtas_and_kaals(sunrise: datetime, sunset: datetime, weekday_idx: int):
    day_duration = sunset - sunrise
    
    # 1. Abhijit Muhurta (8th of 15 divisions of the daytime)
    muhurta_len = day_duration / 15
    abhijit_start = sunrise + 7 * muhurta_len
    abhijit_end = sunrise + 8 * muhurta_len
    
    # 2. Planetary divisions (1/8th of daytime)
    part_len = day_duration / 8
    
    def get_part_window(part_num: int):
        start = sunrise + (part_num - 1) * part_len
        end = sunrise + part_num * part_len
        return start, end
        
    # Weekday index mappings: Mon=0, Tue=1, Wed=2, Thu=3, Fri=4, Sat=5, Sun=6
    rahu_part = [2, 7, 5, 6, 4, 3, 8][weekday_idx]
    yamaganda_part = [5, 4, 3, 2, 8, 7, 6][weekday_idx]
    gulika_part = [6, 5, 4, 3, 2, 1, 7][weekday_idx]
    
    rahu_start, rahu_end = get_part_window(rahu_part)
    yamaganda_start, yamaganda_end = get_part_window(yamaganda_part)
    gulika_start, gulika_end = get_part_window(gulika_part)
    
    return {
        "abhijit": (abhijit_start, abhijit_end),
        "rahu": (rahu_start, rahu_end),
        "yamaganda": (yamaganda_start, yamaganda_end),
        "gulika": (gulika_start, gulika_end),
    }

muhurtas = calculate_muhurtas_and_kaals(sunrise, sunset, selected_date.weekday())

# --- KAAL Calculation (24h Astro cycle) ---
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
        obs_check.lat, obs_check.lon, obs_check.elevation = LATITUDE, LONGITUDE, ELEVATION
        obs_check.date = dt_check.astimezone(pytz.utc)
        m = ephem.Moon()
        m.compute(obs_check)
        return m.alt > 0

    for i in range(len(events) - 1):
        start, end = events[i][0], events[i + 1][0]
        mid = start + (end - start) / 2
        is_sun = sunrise_dt <= mid < sunset_dt
        is_moon = is_moon_up_at(mid)
        kaal = "Unknown"
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


# --- SVG CLOCK MARKUP GENERATOR ---
def get_svg_arc_path(cx, cy, r_out, r_in, start_angle, end_angle):
    # Adjust rotation so 0 deg is at the top (-90 degrees in standard SVG math)
    rad1 = math.radians(start_angle - 90)
    rad2 = math.radians(end_angle - 90)
    
    x1_out = cx + r_out * math.cos(rad1)
    y1_out = cy + r_out * math.sin(rad1)
    x2_out = cx + r_out * math.cos(rad2)
    y2_out = cy + r_out * math.sin(rad2)
    
    x1_in = cx + r_in * math.cos(rad1)
    y1_in = cy + r_in * math.sin(rad1)
    x2_in = cx + r_in * math.cos(rad2)
    y2_in = cy + r_in * math.sin(rad2)
    
    diff = (end_angle - start_angle) % 360
    large_arc = 1 if diff > 180 else 0
    
    path = f"M {x1_out:.2f} {y1_out:.2f} "
    path += f"A {r_out} {r_out} 0 {large_arc} 1 {x2_out:.2f} {y2_out:.2f} "
    path += f"L {x2_in:.2f} {y2_in:.2f} "
    path += f"A {r_in} {r_in} 0 {large_arc} 0 {x1_in:.2f} {y1_in:.2f} "
    path += "Z"
    return path

# Prepare Kaal periods JSON and Arc paths
kaal_js_data = []
arc_paths_html = ""
for p in kaal_periods:
    h_start = (p["Start"] - day_start_dt).total_seconds() / 3600.0
    h_end = (p["End"] - day_start_dt).total_seconds() / 3600.0
    
    ang_start = (h_start / 24.0) * 360.0
    ang_end = (h_end / 24.0) * 360.0
    
    color = KAAL_COLORS.get(p["Kaal"], "#3a3f47")
    kaal_js_data.append({
        "name": p["Kaal"],
        "start": h_start,
        "end": h_end,
        "color": color
    })
    
    arc_paths_html += f'<path d="{get_svg_arc_path(150, 150, 110, 80, ang_start, ang_end)}" fill="{color}" opacity="0.85"/>\n'

# Hour Ticks and labels (24h format clock face)
hour_ticks_html = ""
for h in range(24):
    angle = (h / 24) * 360
    rad = math.radians(angle - 90)
    is_major = h % 6 == 0
    is_medium = h % 3 == 0 and not is_major
    
    r_start = 110
    r_end = 118 if is_major else (115 if is_medium else 113)
    stroke_w = 2.0 if is_major else (1.5 if is_medium else 1.0)
    stroke_c = "#d4af37" if (is_major or is_medium) else "#64748b"
    opacity = 0.9 if (is_major or is_medium) else 0.4
    
    x1 = 150 + r_start * math.cos(rad)
    y1 = 150 + r_start * math.sin(rad)
    x2 = 150 + r_end * math.cos(rad)
    y2 = 150 + r_end * math.sin(rad)
    
    hour_ticks_html += f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke_c}" stroke-width="{stroke_w}" opacity="{opacity}"/>\n'
    
    if is_major:
        r_text = 129
        tx = 150 + r_text * math.cos(rad)
        ty = 150 + r_text * math.sin(rad)
        labels = {0: "12 AM", 6: "6 AM", 12: "12 PM", 18: "6 PM"}
        hour_ticks_html += f'<text x="{tx:.1f}" y="{ty+3.5:.1f}" text-anchor="middle" font-family="\'Outfit\', sans-serif" font-size="9" font-weight="700" fill="#fcd34d" opacity="0.85">{labels[h]}</text>\n'

# Coordinates for Sunrise and Sunset dots
sunrise_hour = (sunrise - day_start_dt).total_seconds() / 3600.0
sunset_hour = (sunset - day_start_dt).total_seconds() / 3600.0
sr_x = 150 + 110 * math.cos(math.radians((sunrise_hour / 24.0) * 360.0 - 90))
sr_y = 150 + 110 * math.sin(math.radians((sunrise_hour / 24.0) * 360.0 - 90))
ss_x = 150 + 110 * math.cos(math.radians((sunset_hour / 24.0) * 360.0 - 90))
ss_y = 150 + 110 * math.sin(math.radians((sunset_hour / 24.0) * 360.0 - 90))

# Compile entire HTML page with client-side clock script
clock_html_content = f"""
<!DOCTYPE html>
<html>
<head>
<style>
body {{
    margin: 0;
    padding: 0;
    background: transparent;
    overflow: hidden;
}}
.clock-container {{
    display: flex;
    justify-content: center;
    align-items: center;
    height: 330px;
    background: transparent;
}}
</style>
</head>
<body>
<div class="clock-container">
    <svg width="300" height="300" viewBox="0 0 300 300">
        <defs>
            <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
                <feGaussianBlur stdDeviation="3" result="blur" />
                <feComposite in="SourceGraphic" in2="blur" operator="over" />
            </filter>
            <filter id="shadow" x="-10%" y="-10%" width="120%" height="120%">
                <feDropShadow dx="0" dy="3" stdDeviation="4" flood-color="#000" flood-opacity="0.6"/>
            </filter>
        </defs>
        
        <!-- Render Kaal arc segments -->
        {arc_paths_html}
        
        <!-- Inner & Outer Gold Rings -->
        <circle cx="150" cy="150" r="110" fill="none" stroke="#d4af37" stroke-width="1.2" opacity="0.3"/>
        <circle cx="150" cy="150" r="80" fill="none" stroke="#d4af37" stroke-width="1.2" opacity="0.3"/>
        
        <!-- Render clock face ticks -->
        {hour_ticks_html}
        
        <!-- Sunrise and Sunset Dots -->
        <circle cx="{sr_x:.2f}" cy="{sr_y:.2f}" r="7" fill="#f59e0b" stroke="#ffffff" stroke-width="1" filter="url(#shadow)"/>
        <circle cx="{ss_x:.2f}" cy="{ss_y:.2f}" r="7" fill="#3b82f6" stroke="#ffffff" stroke-width="1" filter="url(#shadow)"/>
        
        <!-- Central Display Face -->
        <circle cx="150" cy="150" r="77" fill="#0b0f19" stroke="#d4af37" stroke-width="1.5" filter="url(#shadow)"/>
        
        <!-- Dynamic Clock Info Texts -->
        <text id="clock-date" x="150" y="112" text-anchor="middle" font-family="'Outfit', sans-serif" font-size="10" font-weight="600" fill="#94a3b8" letter-spacing="0.08em">--</text>
        <text id="clock-time" x="150" y="146" text-anchor="middle" font-family="'Outfit', sans-serif" font-size="22" font-weight="800" fill="#ffffff">--:--:--</text>
        <text id="clock-kaal" x="150" y="174" text-anchor="middle" font-family="'Outfit', sans-serif" font-size="11" font-weight="700" fill="#d4af37" letter-spacing="0.06em">LOADING</text>
        
        <!-- Hour Needle -->
        <g id="clock-needle">
            <line x1="150" y1="150" x2="150" y2="42" stroke="#d4af37" stroke-width="2.5" stroke-linecap="round" filter="url(#shadow)"/>
            <circle cx="150" cy="42" r="3.5" fill="#ffffff" stroke="#d4af37" stroke-width="1.5"/>
        </g>
        
        <!-- Central Center Pivot Pin -->
        <circle cx="150" cy="150" r="4" fill="#d4af37"/>
    </svg>
</div>

<script>
const kaalPeriods = {json.dumps(kaal_js_data)};
const tzString = "{loc_details['tz']}";

function updateClock() {{
    try {{
        // Fetch localized date/time
        const options = {{ timeZone: tzString, hour: 'numeric', minute: 'numeric', second: 'numeric', hour12: false }};
        const formatter = new Intl.DateTimeFormat([], options);
        const parts = formatter.formatToParts(new Date());
        let hour = 0, minute = 0, second = 0;
        for (const part of parts) {{
            if (part.type === 'hour') hour = parseInt(part.value, 10);
            if (part.type === 'minute') minute = parseInt(part.value, 10);
            if (part.type === 'second') second = parseInt(part.value, 10);
        }}
        
        const decimalTime = hour + minute / 60 + second / 3600;
        const rotateAngle = (decimalTime / 24) * 360;
        
        // Update needle rotation
        const needleNode = document.getElementById('clock-needle');
        if (needleNode) {{
            needleNode.setAttribute('transform', `rotate(${{rotateAngle}}, 150, 150)`);
        }}
        
        // Formatted display clock
        const ampm = hour >= 12 ? 'PM' : 'AM';
        let displayHr = hour % 12;
        displayHr = displayHr ? displayHr : 12;
        const displayMin = minute < 10 ? '0' + minute : minute;
        const displaySec = second < 10 ? '0' + second : second;
        
        const timeField = document.getElementById('clock-time');
        if (timeField) {{
            timeField.textContent = `${{displayHr}}:${{displayMin}}:${{displaySec}} ${{ampm}}`;
        }}
        
        // Formatted Date
        const dateOptions = {{ timeZone: tzString, weekday: 'short', month: 'short', day: 'numeric' }};
        const dateField = document.getElementById('clock-date');
        if (dateField) {{
            const dFormatter = new Intl.DateTimeFormat([], dateOptions);
            dateField.textContent = dFormatter.format(new Date()).toUpperCase();
        }}
        
        // Current Kaal state check
        const activeKaal = kaalPeriods.find(p => decimalTime >= p.start && decimalTime < p.end);
        const kaalField = document.getElementById('clock-kaal');
        if (activeKaal && kaalField) {{
            kaalField.textContent = activeKaal.name.toUpperCase();
            kaalField.setAttribute('fill', activeKaal.color);
        }}
    }} catch (e) {{
        console.error("Clock update error: ", e);
    }}
}}
setInterval(updateClock, 1000);
updateClock();
</script>
</body>
</html>
"""


# --- SCREEN DISPLAY ---

col_dashboard_left, col_dashboard_right = st.columns([1, 1], gap="medium")

with col_dashboard_left:
    # 1. Custom SVG Clock Container
    st.markdown("<div class='astro-card' style='display:flex; justify-content:center; align-items:center;'>", unsafe_allow_html=True)
    st.components.v1.html(clock_html_content, height=330)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 2. Detailed Kaal Timings List
    st.markdown("<div class='astro-card'>", unsafe_allow_html=True)
    st.markdown("<div class='astro-card-title'>📅 Daily Kaal Periods</div>", unsafe_allow_html=True)
    
    kaal_rows = ""
    for p in kaal_periods:
        k_name = p["Kaal"]
        k_color = KAAL_COLORS.get(k_name, "#ffffff")
        duration = (p["End"] - p["Start"]).total_seconds() / 3600
        
        kaal_rows += f"""
        <tr>
            <td style="font-weight: 600;"><span style="color: {k_color};">●</span> {k_name}</td>
            <td>{p["Start"].strftime("%I:%M %p")}</td>
            <td>{p["End"].strftime("%I:%M %p")}</td>
            <td style="color: #94a3b8;">{duration:.1f} hrs</td>
        </tr>
        """
        
    st.markdown(
        f"""
        <table class="kaal-table">
            <thead>
                <tr>
                    <th>Kaal Type</th>
                    <th>Start</th>
                    <th>End</th>
                    <th>Duration</th>
                </tr>
            </thead>
            <tbody>
                {kaal_rows}
            </tbody>
        </table>
        """,
        unsafe_allow_html=True
    )
    st.markdown("</div>", unsafe_allow_html=True)

with col_dashboard_right:
    # 3. Astro Rise/Set Times
    st.markdown("<div class='astro-card'>", unsafe_allow_html=True)
    st.markdown("<div class='astro-card-title'>☀️ Astronomical Rise/Set</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='astro-grid'>", unsafe_allow_html=True)
    
    sr_str = sunrise.strftime("%I:%M %p") if sunrise else "N/A"
    ss_str = sunset.strftime("%I:%M %p") if sunset else "N/A"
    mr_str = moon_rise.strftime("%I:%M %p") if moon_rise else "N/A"
    ms_str = moon_set.strftime("%I:%M %p") if moon_set else "N/A"
    
    st.markdown(f"""
    <div class='astro-item'>
        <div class='astro-label'>Sunrise</div>
        <div class='astro-value astro-value-highlight'>{sr_str}</div>
    </div>
    <div class='astro-item'>
        <div class='astro-label'>Sunset</div>
        <div class='astro-value astro-value-highlight'>{ss_str}</div>
    </div>
    <div class='astro-item'>
        <div class='astro-label'>Moonrise</div>
        <div class='astro-value'>{mr_str}</div>
    </div>
    <div class='astro-item'>
        <div class='astro-label'>Moonset</div>
        <div class='astro-value'>{ms_str}</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # 4. Muhurtas & Auspicious/Inauspicious Windows
    st.markdown("<div class='astro-card'>", unsafe_allow_html=True)
    st.markdown("<div class='astro-card-title'>⏳ Auspicious / Planetary Timings</div>", unsafe_allow_html=True)
    
    ab_start, ab_end = muhurtas["abhijit"]
    rh_start, rh_end = muhurtas["rahu"]
    ym_start, ym_end = muhurtas["yamaganda"]
    gl_start, gl_end = muhurtas["gulika"]
    
    st.markdown(f"""
    <div class='astro-grid'>
        <div class='astro-item' style='border: 1px solid rgba(245, 158, 11, 0.4); background: rgba(245, 158, 11, 0.03);'>
            <div class='astro-label' style='color: #f59e0b;'>Abhijit Muhurta</div>
            <div class='astro-value' style='color: #f59e0b;'>{ab_start.strftime("%I:%M %p")} - {ab_end.strftime("%I:%M %p")}</div>
            <div class='astro-subtext'>Highly auspicious daily solar window. Ideal for starting tasks.</div>
        </div>
        <div class='astro-item' style='border: 1px solid rgba(239, 68, 68, 0.4); background: rgba(239, 68, 68, 0.03);'>
            <div class='astro-label' style='color: #ef4444;'>Rahu Kaal</div>
            <div class='astro-value' style='color: #ef4444;'>{rh_start.strftime("%I:%M %p")} - {rh_end.strftime("%I:%M %p")}</div>
            <div class='astro-subtext'>Inauspicious Rahu period. Avoid launching major projects.</div>
        </div>
    </div>
    <div class='astro-grid' style='margin-top: 16px;'>
        <div class='astro-item'>
            <div class='astro-label'>Gulika Kaal</div>
            <div class='astro-value'>{gl_start.strftime("%I:%M %p")} - {gl_end.strftime("%I:%M %p")}</div>
            <div class='astro-subtext'>Mande Kaal. Best for long-term investments or buying property.</div>
        </div>
        <div class='astro-item'>
            <div class='astro-label'>Yamaganda Kaal</div>
            <div class='astro-value'>{ym_start.strftime("%I:%M %p")} - {ym_end.strftime("%I:%M %p")}</div>
            <div class='astro-subtext'>Ketu period. Inauspicious for initiating travel or new contracts.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # 5. Core Astro attributes (Tithi, Nakshatra, Rasi)
    st.markdown("<div class='astro-card'>", unsafe_allow_html=True)
    st.markdown("<div class='astro-card-title'>🌌 Constellation & Zodiac Details</div>", unsafe_allow_html=True)
    
    nak_attrs = NAKSHATRA_ATTRIBUTES.get(today_nakshatra["name"], {})
    nak_attrs_str = f"Nadi: {nak_attrs.get('Nadi','N/A')} · Tattva: {nak_attrs.get('Tattva','N/A')} · Ruler: {nak_attrs.get('Adhipati','N/A')}"
    
    st.markdown(f"""
    <div class='astro-grid'>
        <div class='astro-item'>
            <div class='astro-label'>Active Tithi</div>
            <div class='astro-value astro-value-highlight'>{today_tithi["name"]} ({today_tithi["paksha"]})</div>
            <div class='astro-subtext'>Ends: {today_tithi["end"].strftime("%b %d, %I:%M %p")}</div>
        </div>
        <div class='astro-item'>
            <div class='astro-label'>Active Nakshatra</div>
            <div class='astro-value astro-value-highlight'>{today_nakshatra["name"]}</div>
            <div class='astro-subtext'>Ends: {today_nakshatra["end"].strftime("%b %d, %I:%M %p")}<br><span style='color: #a8a29e;'>{nak_attrs_str}</span></div>
        </div>
    </div>
    <div class='astro-grid' style='margin-top: 16px;'>
        <div class='astro-item'>
            <div class='astro-label'>Sun Rasi (Surya Rasi)</div>
            <div class='astro-value'>{today_sun_rasi}</div>
            <div class='astro-subtext'>Current transit constellation of the Sun</div>
        </div>
        <div class='astro-item'>
            <div class='astro-label'>Moon Rasi (Chandra Rasi)</div>
            <div class='astro-value'>{today_moon_rasi}</div>
            <div class='astro-subtext'>Transit constellation of the Moon</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# 6. Swara Yoga & Midpoint Sadhanas
st.markdown("<div class='astro-card'>", unsafe_allow_html=True)
st.markdown("<div class='astro-card-title'>🧘 Swara Yoga & Meditation Windows</div>", unsafe_allow_html=True)

col_sw_left, col_sw_right = st.columns(2)

with col_sw_left:
    st.markdown(f"""
    <div class='astro-grid'>
        <div class='astro-item'>
            <div class='astro-label'>Waking Swara</div>
            <div class='astro-value' style='color: {get_swara_color(swara_at_waking)};'>{swara_at_waking}</div>
            <div class='astro-subtext'>Natural nostril dominance upon waking for this weekday</div>
        </div>
        <div class='astro-item'>
            <div class='astro-label'>Sunrise Swara</div>
            <div class='astro-value' style='color: {sunrise_swara_color};'>{sunrise_swaras["sunrise"]}</div>
            <div class='astro-subtext'>({tithi_at_sunrise["name"]} {tithi_at_sunrise["paksha"]})</div>
        </div>
        <div class='astro-item'>
            <div class='astro-label'>Sunset Swara</div>
            <div class='astro-value' style='color: {sunset_swara_color};'>{sunset_swaras["sunset"]}</div>
            <div class='astro-subtext'>({tithi_at_sunset["name"]} {tithi_at_sunset["paksha"]})</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_sw_right:
    sadhana_grid = ""
    if morning_sadhana and evening_sadhana:
        sadhana_grid = f"""
        <div class='astro-item'>
            <div class='astro-label'>Morning Naad Sadhana</div>
            <div class='astro-value astro-value-highlight'>{morning_sadhana.strftime("%I:%M %p")}</div>
            <div class='astro-subtext'>Optimal time for pranayama & vocal practice</div>
        </div>
        <div class='astro-item'>
            <div class='astro-label'>Evening Naad Sadhana</div>
            <div class='astro-value astro-value-highlight'>{evening_sadhana.strftime("%I:%M %p")}</div>
            <div class='astro-subtext'>Optimal evening meditation and resonance focus</div>
        </div>
        """
    else:
        sadhana_grid = "<div class='astro-item'><div class='astro-value'>Sadhana times not available</div></div>"

    st.markdown(f"""
    <div class='astro-grid'>
        {sadhana_grid}
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='margin-top: 16px;' class='astro-grid'>", unsafe_allow_html=True)
st.markdown(f"""
<div class='astro-item'>
    <div class='astro-label'>Morning Sandhya</div>
    <div class='astro-value'>{sandhya_times['morning']['start'].strftime('%I:%M %p')} - {sandhya_times['morning']['end'].strftime('%I:%M %p')}</div>
</div>
<div class='astro-item'>
    <div class='astro-label'>Midday Sandhya</div>
    <div class='astro-value'>{sandhya_times['midday']['start'].strftime('%I:%M %p')} - {sandhya_times['midday']['end'].strftime('%I:%M %p')}</div>
</div>
<div class='astro-item'>
    <div class='astro-label'>Evening Sandhya</div>
    <div class='astro-value'>{sandhya_times['evening']['start'].strftime('%I:%M %p')} - {sandhya_times['evening']['end'].strftime('%I:%M %p')}</div>
</div>
<div class='astro-item'>
    <div class='astro-label'>Midnight Sandhya</div>
    <div class='astro-value'>{sandhya_times['midnight']['start'].strftime('%I:%M %p')} - {sandhya_times['midnight']['end'].strftime('%I:%M %p')}</div>
</div>
""", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# Footer bar (replaces autorefresh)
col_foot1, col_foot2 = st.columns(2)
with col_foot1:
    st.markdown(f"<p style='font-size: 11px; color: #64748b; margin-top: 20px;'>Dashboard Location: {loc_details['display_name']} • Tithi, Nakshatra, Swara, Rasi & Sadhana Details</p>", unsafe_allow_html=True)
with col_foot2:
    if st.button("🔄 Refresh Calculation Engine", key="btn_refresh_engine"):
        st.rerun()
