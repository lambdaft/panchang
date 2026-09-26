# streamlit_app.py — Personal Vedic Panchang App
import streamlit as st
from datetime import datetime, date, timedelta, time
import pytz
import math
import ephem
from streamlit_autorefresh import st_autorefresh
from typing import Dict, Any, Optional
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

def render_html(html: str):
    """Render raw HTML safely in Streamlit without markdown indent interpretation."""
    cleaned = "\n".join(line.strip() for line in html.strip().splitlines() if line.strip())
    st.markdown(cleaned, unsafe_allow_html=True)

# Custom Styling
render_html("""
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

.custom-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.9rem;
    margin: 8px 0;
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
    color: #1F2937;
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
""")

# Header
render_html("""
<div class="panchang-header">
    <h1 class="panchang-title">🕉️ Personal Panchang</h1>
    <div class="panchang-subtitle">Accurate Ephem Timings • Kaal Cycle • Swara • Naad Sadhana</div>
</div>
""")

# Pre-cached popular cities for cloud resiliency
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
    if clean_city in KNOWN_CITIES:
        return KNOWN_CITIES[clean_city]
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
    return {
        "lat": "16.7050",
        "lon": "74.2433",
        "elevation": 569,
        "tz": "Asia/Kolkata",
        "display_name": f"{city_name.capitalize()} (Kolhapur default)",
    }

# Location & Date Inputs
col_loc, col_dt = st.columns([3, 2])
with col_loc:
    city_input = st.text_input("📍 City / Location", value="Kolhapur", help="Enter city name (e.g. Kolhapur, Mumbai, New York)")
with col_dt:
    selected_date = st.date_input("📅 Date", value=date.today())

loc_details = get_location_details(city_input)

with st.expander("⚙️ Location & Coordinate Settings"):
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
st.caption(f"Location: **{loc_details['display_name']}** | Timezone: `{custom_tz}` | Lat: `{LATITUDE}`, Lon: `{LONGITUDE}`")

# Constants & Mappings
KAAL_COLORS = {
    "Kartavya Kaal": "#F59E0B",
    "Anand Kaal": "#3B82F6",
    "Prarabdh Kaal": "#8B5CF6",
    "Bhagya Kaal": "#78350F",
}

RASHI_NAMES = [
    "Meṣa (Aries)", "Vṛṣabha (Taurus)", "Mithuna (Gemini)", "Karka (Cancer)",
    "Siṁha (Leo)", "Kanyā (Virgo)", "Tulā (Libra)", "Vṛścika (Scorpio)",
    "Dhanu (Sagittarius)", "Makara (Capricorn)", "Kumbha (Aquarius)", "Mīna (Pisces)",
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

# Astronomical Calculations
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

def to_ephem_date(dt: datetime) -> ephem.Date:
    """Convert timezone-aware or naive datetime to ephem.Date (UTC)."""
    utc_dt = dt.astimezone(pytz.utc) if dt.tzinfo else pytz.utc.localize(dt)
    return ephem.Date(utc_dt)

def to_local_datetime(ephem_d: ephem.Date) -> datetime:
    """Convert ephem.Date back to local timezone datetime."""
    return pytz.utc.localize(ephem_d.datetime()).astimezone(TZ)

# Standard Lahiri (Chitra Paksha) Ayanamsa relative to J2000.0 equinox: 23° 51' 25.53"
LAHIRI_AYANAMSA_J2000 = 23.8570922

def get_moon_sun_elongation(ephem_d: ephem.Date) -> float:
    """Calculate Moon - Sun apparent ecliptic longitude elongation in degrees [0, 360)."""
    sun = ephem.Sun(ephem_d)
    moon = ephem.Moon(ephem_d)
    sun_lon = math.degrees(ephem.Ecliptic(sun).lon) % 360.0
    moon_lon = math.degrees(ephem.Ecliptic(moon).lon) % 360.0
    return (moon_lon - sun_lon + 360.0) % 360.0

def get_sidereal_moon_lon(ephem_d: ephem.Date) -> float:
    """Calculate Moon sidereal (Nirayana) longitude in degrees [0, 360)."""
    moon = ephem.Moon(ephem_d)
    moon_lon = math.degrees(ephem.Ecliptic(moon).lon) % 360.0
    return (moon_lon - LAHIRI_AYANAMSA_J2000 + 360.0) % 360.0

def get_sidereal_sun_lon(ephem_d: ephem.Date) -> float:
    """Calculate Sun sidereal (Nirayana) longitude in degrees [0, 360)."""
    sun = ephem.Sun(ephem_d)
    sun_lon = math.degrees(ephem.Ecliptic(sun).lon) % 360.0
    return (sun_lon - LAHIRI_AYANAMSA_J2000 + 360.0) % 360.0

def find_crossing_time(val_func, target_deg: float, t_start: ephem.Date, t_end: ephem.Date) -> ephem.Date:
    """Find the exact moment when val_func(t) crosses target_deg using continuous angular bisection."""
    def f(t_val):
        d = ephem.Date(t_val)
        current_deg = val_func(d)
        return (current_deg - target_deg + 180.0) % 360.0 - 180.0

    lo = float(t_start)
    hi = float(t_end)
    for _ in range(45):
        mid = (lo + hi) / 2.0
        val = f(mid)
        if val < 0:
            lo = mid
        else:
            hi = mid
    return ephem.Date((lo + hi) / 2.0)

def get_tithi_at(dt: datetime) -> Dict[str, Any]:
    """Calculate the Tithi, Paksha, and precise start/end boundary times at the given datetime."""
    d = to_ephem_date(dt)
    elongation = get_moon_sun_elongation(d)
    tithi_idx = int(elongation / 12.0) % 30

    if tithi_idx == 14:
        name_key = "Pūrṇimā"
        paksha = "Śukla"
    elif tithi_idx == 29:
        name_key = "Amāvasyā"
        paksha = "Kṛṣṇa"
    else:
        tithi_names = [
            "Pratipada", "Dvitīya", "Tṛtīya", "Caturthī", "Pañchamī",
            "Ṣaṣṭhī", "Saptamī", "Aṣṭamī", "Navamī", "Daśamī",
            "Ekādaśī", "Dvādaśī", "Trayodaśī", "Caturdaśī",
        ]
        name_key = tithi_names[tithi_idx % 15]
        paksha = "Śukla" if tithi_idx < 15 else "Kṛṣṇa"

    start_target = tithi_idx * 12.0
    end_target = ((tithi_idx + 1) * 12.0) % 360.0

    start_d = find_crossing_time(get_moon_sun_elongation, start_target, ephem.Date(float(d) - 1.5), d)
    end_d = find_crossing_time(get_moon_sun_elongation, end_target, d, ephem.Date(float(d) + 1.5))

    return {
        "idx": tithi_idx,
        "name": name_key,
        "paksha": paksha,
        "start": to_local_datetime(start_d),
        "end": to_local_datetime(end_d),
    }

def get_nakshatra_at(dt: datetime) -> Dict[str, Any]:
    """Calculate the Nakshatra and precise start/end boundary times at the given datetime."""
    d = to_ephem_date(dt)
    moon_sidereal = get_sidereal_moon_lon(d)
    nak_arc = 360.0 / 27.0
    nak_idx = int(moon_sidereal / nak_arc) % 27
    name = NAKSHATRA_NAMES[nak_idx]

    start_target = nak_idx * nak_arc
    end_target = ((nak_idx + 1) * nak_arc) % 360.0

    start_d = find_crossing_time(get_sidereal_moon_lon, start_target, ephem.Date(float(d) - 1.5), d)
    end_d = find_crossing_time(get_sidereal_moon_lon, end_target, d, ephem.Date(float(d) + 1.5))

    return {
        "idx": nak_idx,
        "name": name,
        "start": to_local_datetime(start_d),
        "end": to_local_datetime(end_d),
    }

def get_sun_rasi(dt: datetime) -> str:
    """Get the sidereal Sun sign (Surya Rasi) at the given datetime."""
    d = to_ephem_date(dt)
    s_sidereal = get_sidereal_sun_lon(d)
    return RASHI_NAMES[int(s_sidereal / 30.0) % 12]

def get_moon_rasi(dt: datetime) -> str:
    """Get the sidereal Moon sign (Chandra Rasi) at the given datetime."""
    d = to_ephem_date(dt)
    m_sidereal = get_sidereal_moon_lon(d)
    return RASHI_NAMES[int(m_sidereal / 30.0) % 12]

def get_accurate_astro_times(target_date: date) -> Dict[str, Optional[datetime]]:
    """Compute accurate sunrise, sunset, moonrise, moonset, and next sunrise for a given date."""
    obs = ephem.Observer()
    obs.lat = LATITUDE
    obs.lon = LONGITUDE
    obs.elevation = ELEVATION

    target_dt_local = TZ.localize(datetime.combine(target_date, time(0, 0, 0)))
    obs.date = to_ephem_date(target_dt_local)

    sun = ephem.Sun()
    moon = ephem.Moon()

    sunrise_ephem = obs.next_rising(sun)
    sunrise_dt = to_local_datetime(sunrise_ephem)

    obs.date = sunrise_ephem
    sunset_ephem = obs.next_setting(sun)
    sunset_dt = to_local_datetime(sunset_ephem)

    obs.date = sunset_ephem
    next_sunrise_ephem = obs.next_rising(sun)
    next_sunrise_dt = to_local_datetime(next_sunrise_ephem)

    # Moon rise & set for the day (from local midnight)
    obs.date = to_ephem_date(target_dt_local)
    moon_rise_dt = None
    try:
        moon_rise_dt = to_local_datetime(obs.next_rising(moon))
    except (ephem.NeverUpError, ephem.AlwaysUpError):
        pass

    moon_set_dt = None
    try:
        moon_set_dt = to_local_datetime(obs.next_setting(moon))
    except (ephem.NeverUpError, ephem.AlwaysUpError):
        pass

    return {
        "sunrise": sunrise_dt,
        "sunset": sunset_dt,
        "next_sunrise": next_sunrise_dt,
        "moon_rise": moon_rise_dt,
        "moon_set": moon_set_dt,
    }

def calculate_madhyamas(sunrise_dt: datetime, sunset_dt: datetime, next_sunrise_dt: datetime) -> Dict[str, datetime]:
    day_duration = sunset_dt - sunrise_dt
    day_madhyama = sunrise_dt + (day_duration / 2)
    night_duration = next_sunrise_dt - sunset_dt
    night_madhyama = sunset_dt + (night_duration / 2)
    return {"day_madhyama": day_madhyama, "night_madhyama": night_madhyama}

# Computations for Selected Date
weekday = selected_date.weekday()
day_index = (weekday + 1) % 7
swara_at_waking = ["Pingala", "Ida", "Pingala", "Ida", "Ida", "Ida", "Pingala"][day_index]

astro_data = get_accurate_astro_times(selected_date)
sunrise = astro_data["sunrise"]
sunset = astro_data["sunset"]
next_sunrise = astro_data["next_sunrise"]
moon_rise = astro_data["moon_rise"]
moon_set = astro_data["moon_set"]

astro_yesterday = get_accurate_astro_times(selected_date - timedelta(days=1))
astro_tomorrow = get_accurate_astro_times(selected_date + timedelta(days=1))
yesterday_sunrise = astro_yesterday["sunrise"]
tomorrow_sunrise = astro_tomorrow["sunrise"]

today_tithi = get_tithi_at(sunrise)
yesterday_tithi = get_tithi_at(yesterday_sunrise)
tomorrow_tithi = get_tithi_at(tomorrow_sunrise)

today_nakshatra = get_nakshatra_at(sunrise)
yesterday_nakshatra = get_nakshatra_at(yesterday_sunrise)
tomorrow_nakshatra = get_nakshatra_at(tomorrow_sunrise)

today_sun_rasi = get_sun_rasi(sunrise)
today_moon_rasi = get_moon_rasi(sunrise)

madhyamas = calculate_madhyamas(sunrise, sunset, next_sunrise)
midday = madhyamas["day_madhyama"]
midnight = madhyamas["night_madhyama"]

tithi_at_sunrise = get_tithi_at(sunrise)
tithi_at_sunset = get_tithi_at(sunset)

sunrise_swaras = get_swaras_from_tithi(tithi_at_sunrise)
sunset_swaras = get_swaras_from_tithi(tithi_at_sunset)

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

sandhya_times = {
    "morning": {"start": sunrise - timedelta(hours=1), "end": sunrise + timedelta(hours=1)},
    "midday": {"start": midday - timedelta(hours=1), "end": midday + timedelta(hours=1)},
    "evening": {"start": sunset - timedelta(hours=1), "end": sunset + timedelta(hours=1)},
    "midnight": {"start": midnight - timedelta(hours=1), "end": midnight + timedelta(hours=1)},
}

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

# --- 1. DAY SUMMARY BANNER ---
waking_badge_class = "swara-ida" if swara_at_waking == "Ida" else "swara-pingala"
render_html(f"""
<div style="background: #FAF8F5; border: 1px solid #EAE3D9; border-radius: 14px; padding: 18px; text-align: center; margin-top: 0.5rem; margin-bottom: 1.5rem;">
    <div style="font-size: 0.95rem; font-weight: 600; color: #78350F; text-transform: uppercase; letter-spacing: 0.8px;">Waking Swara of the Day</div>
    <div style="margin: 8px 0;"><span class="swara-badge {waking_badge_class}" style="font-size: 1.3rem; padding: 6px 18px;">🌬️ {swara_at_waking} Swara</span></div>
    <div style="font-size: 1.05rem; font-weight: 600; color: #1F2937;">{selected_date.strftime('%A, %d %B %Y')}</div>
    <div style="font-size: 0.85rem; color: #6B7280; margin-top: 4px;">Today's Tithi: <b>{today_tithi['name']} ({today_tithi['paksha']})</b> • Nakshatra: <b>{today_nakshatra['name']}</b></div>
</div>
""")

# --- 2. ASTRO RISE/SET CARDS ---
render_html('<div class="section-title">☀️ Astronomical Rise & Set</div>')
col_sr, col_ss, col_mr, col_ms = st.columns(4)
with col_sr:
    render_html(f"""
    <div class="panchang-card">
        <div class="panchang-card-title">🌅 Sunrise</div>
        <div class="panchang-card-val">{sunrise.strftime('%I:%M %p') if sunrise else 'N/A'}</div>
    </div>
    """)
with col_ss:
    render_html(f"""
    <div class="panchang-card">
        <div class="panchang-card-title">🌇 Sunset</div>
        <div class="panchang-card-val">{sunset.strftime('%I:%M %p') if sunset else 'N/A'}</div>
    </div>
    """)
with col_mr:
    render_html(f"""
    <div class="panchang-card">
        <div class="panchang-card-title">🌙 Moonrise</div>
        <div class="panchang-card-val">{moon_rise.strftime('%I:%M %p') if moon_rise else 'N/A'}</div>
    </div>
    """)
with col_ms:
    render_html(f"""
    <div class="panchang-card">
        <div class="panchang-card-title">🌘 Moonset</div>
        <div class="panchang-card-val">{moon_set.strftime('%I:%M %p') if moon_set else 'N/A'}</div>
    </div>
    """)

# --- 3. 24-HOUR KAAL CYCLE CLOCK & TIMINGS ---
render_html('<div class="section-title">⌛ 24-Hour Kaal Cycle Clock</div>')

def generate_kaal_clock_svg(kaal_periods_list, day_start, now_dt, sr_dt, ss_dt):
    cx, cy = 180, 180
    r_in, r_out = 78, 132
    dial_r = 166
    
    svg = []
    svg.append('<svg viewBox="0 0 360 360" width="100%" height="100%" style="max-width:360px; display:block; margin:auto; filter: drop-shadow(0 4px 12px rgba(0,0,0,0.07)); font-family: \'Plus Jakarta Sans\', -apple-system, sans-serif;">')
    
    # 1. Base Dial Face & Outer Ring
    svg.append(f'<circle cx="{cx}" cy="{cy}" r="{dial_r}" fill="#FAF8F5" stroke="#EAE3D9" stroke-width="2.5"/>')
    svg.append(f'<circle cx="{cx}" cy="{cy}" r="{r_out+4}" fill="none" stroke="#D4AF37" stroke-width="1.2" stroke-dasharray="2,3"/>')
    
    # 2. 24-Hour Dial Ticks and Labels
    for h in range(24):
        deg = (h / 24.0) * 360.0
        rad = math.radians(deg - 90)
        is_major = (h % 3 == 0)
        tick_len = 8 if is_major else 4
        stroke_w = 1.8 if is_major else 1.0
        stroke_c = "#78350F" if is_major else "#D1C4B5"
        
        x_start = cx + (r_out + 6) * math.cos(rad)
        y_start = cy + (r_out + 6) * math.sin(rad)
        x_end = cx + (r_out + 6 + tick_len) * math.cos(rad)
        y_end = cy + (r_out + 6 + tick_len) * math.sin(rad)
        svg.append(f'<line x1="{x_start:.2f}" y1="{y_start:.2f}" x2="{x_end:.2f}" y2="{y_end:.2f}" stroke="{stroke_c}" stroke-width="{stroke_w}" stroke-linecap="round"/>')
        
        if is_major:
            lbl_r = dial_r - 14
            x_lbl = cx + lbl_r * math.cos(rad)
            y_lbl = cy + lbl_r * math.sin(rad)
            if h == 0:
                lbl_text = "12 AM"
            elif h == 6:
                lbl_text = "6 AM"
            elif h == 12:
                lbl_text = "12 PM"
            elif h == 18:
                lbl_text = "6 PM"
            elif h < 12:
                lbl_text = f"{h} AM"
            else:
                lbl_text = f"{h-12} PM"
            svg.append(f'<text x="{x_lbl:.2f}" y="{y_lbl+3.5:.2f}" text-anchor="middle" font-size="8.5" font-weight="700" fill="#78350F">{lbl_text}</text>')

    # 3. Underlayed Kala Chakra Windows (Annular Sectors)
    for p in kaal_periods_list:
        s_sec = max(0.0, (p["Start"] - day_start).total_seconds())
        e_sec = min(86400.0, (p["End"] - day_start).total_seconds())
        if e_sec <= s_sec:
            continue
        s_deg = (s_sec / 86400.0) * 360.0
        e_deg = (e_sec / 86400.0) * 360.0
        if e_deg - s_deg >= 360.0:
            e_deg = s_deg + 359.99
            
        rad1 = math.radians(s_deg - 90)
        rad2 = math.radians(e_deg - 90)
        x1_o = cx + r_out * math.cos(rad1)
        y1_o = cy + r_out * math.sin(rad1)
        x2_o = cx + r_out * math.cos(rad2)
        y2_o = cy + r_out * math.sin(rad2)
        x1_i = cx + r_in * math.cos(rad1)
        y1_i = cy + r_in * math.sin(rad1)
        x2_i = cx + r_in * math.cos(rad2)
        y2_i = cy + r_in * math.sin(rad2)
        
        large_arc = 1 if (e_deg - s_deg) > 180.0 else 0
        path_d = f"M {x1_o:.2f} {y1_o:.2f} A {r_out} {r_out} 0 {large_arc} 1 {x2_o:.2f} {y2_o:.2f} L {x2_i:.2f} {y2_i:.2f} A {r_in} {r_in} 0 {large_arc} 0 {x1_i:.2f} {y1_i:.2f} Z"
        color = KAAL_COLORS.get(p["Kaal"], "#78350F")
        time_info = f"{p['Kaal']}: {p['Start'].strftime('%I:%M %p')} - {p['End'].strftime('%I:%M %p')}"
        svg.append(f'<path d="{path_d}" fill="{color}" stroke="#FFFFFF" stroke-width="1.8"><title>{time_info}</title></path>')

    # 4. Sunrise & Sunset Indicators
    if sr_dt and day_start <= sr_dt <= (day_start + timedelta(days=1)):
        sr_sec = (sr_dt - day_start).total_seconds()
        sr_deg = (sr_sec / 86400.0) * 360.0
        sr_rad = math.radians(sr_deg - 90)
        sx = cx + (r_out + 2) * math.cos(sr_rad)
        sy = cy + (r_out + 2) * math.sin(sr_rad)
        svg.append(f'<circle cx="{sx:.2f}" cy="{sy:.2f}" r="4.5" fill="#F59E0B" stroke="#FFFFFF" stroke-width="1.2"><title>Sunrise: {sr_dt.strftime("%I:%M %p")}</title></circle>')

    if ss_dt and day_start <= ss_dt <= (day_start + timedelta(days=1)):
        ss_sec = (ss_dt - day_start).total_seconds()
        ss_deg = (ss_sec / 86400.0) * 360.0
        ss_rad = math.radians(ss_deg - 90)
        sx = cx + (r_out + 2) * math.cos(ss_rad)
        sy = cy + (r_out + 2) * math.sin(ss_rad)
        svg.append(f'<circle cx="{sx:.2f}" cy="{sy:.2f}" r="4.5" fill="#DC2626" stroke="#FFFFFF" stroke-width="1.2"><title>Sunset: {ss_dt.strftime("%I:%M %p")}</title></circle>')

    # 5. Center Hub Dial (Live Digital Time & Active Kaal)
    active_kaal = "—"
    active_color = "#78350F"
    for p in kaal_periods_list:
        if p["Start"] <= now_dt < p["End"]:
            active_kaal = p["Kaal"]
            active_color = KAAL_COLORS.get(active_kaal, "#78350F")
            break
            
    svg.append(f'<circle cx="{cx}" cy="{cy}" r="{r_in-2}" fill="#FFFDFB" stroke="#EAE3D9" stroke-width="2"/>')
    svg.append(f'<circle cx="{cx}" cy="{cy}" r="{r_in-8}" fill="none" stroke="#D4AF37" stroke-width="1" stroke-dasharray="2,3"/>')

    # 6. Current Time Needle (Live Clock Hand)
    now_hours = now_dt.hour + now_dt.minute / 60.0 + now_dt.second / 3600.0
    now_deg = (now_hours / 24.0) * 360.0
    rad_now = math.radians(now_deg - 90)
    rad_perp = math.radians(now_deg)
    
    tip_len = r_out + 12
    tip_x = cx + tip_len * math.cos(rad_now)
    tip_y = cy + tip_len * math.sin(rad_now)
    
    tail_len = 18
    tail_x = cx - tail_len * math.cos(rad_now)
    tail_y = cy - tail_len * math.sin(rad_now)
    
    w = 3.2
    w1_x = cx + w * math.cos(rad_perp)
    w1_y = cy + w * math.sin(rad_perp)
    w2_x = cx - w * math.cos(rad_perp)
    w2_y = cy - w * math.sin(rad_perp)
    
    needle_d = f"M {w1_x:.2f} {w1_y:.2f} L {tip_x:.2f} {tip_y:.2f} L {w2_x:.2f} {w2_y:.2f} L {tail_x:.2f} {tail_y:.2f} Z"
    svg.append(f'<path d="{needle_d}" fill="#DC2626" opacity="0.95" stroke="#991B1B" stroke-width="0.8" style="filter: drop-shadow(0 2px 4px rgba(0,0,0,0.25));"/>')
    svg.append(f'<circle cx="{tip_x:.2f}" cy="{tip_y:.2f}" r="4.5" fill="#FEF08A" stroke="#DC2626" stroke-width="1.5"><title>Current Time: {now_dt.strftime("%I:%M:%S %p")}</title></circle>')
    svg.append(f'<circle cx="{cx}" cy="{cy}" r="6.5" fill="#78350F" stroke="#FDE68A" stroke-width="1.8"/>')
    
    # Center Hub Text
    svg.append(f'<text x="{cx}" y="{cy-22}" text-anchor="middle" font-size="8" font-weight="700" fill="#9CA3AF" letter-spacing="1">CURRENT TIME</text>')
    svg.append(f'<text x="{cx}" y="{cy-2}" text-anchor="middle" font-family="Cinzel, serif" font-size="16" font-weight="700" fill="#1F2937">{now_dt.strftime("%I:%M %p")}</text>')
    svg.append(f'<rect x="{cx-52}" y="{cy+11}" width="104" height="18" rx="9" fill="{active_color}" opacity="0.15"/>')
    svg.append(f'<text x="{cx}" y="{cy+23.5}" text-anchor="middle" font-size="9" font-weight="700" fill="{active_color}">● {active_kaal}</text>')
    
    svg.append('</svg>')
    return "".join(svg)

if not df_chart.empty:
    col_chart, col_tbl = st.columns([1, 1])
    with col_chart:
        clock_svg = generate_kaal_clock_svg(kaal_periods, day_start_dt, now, sunrise, sunset)
        render_html(clock_svg)

    with col_tbl:
        table_rows = []
        for p in kaal_periods:
            k_name = p["Kaal"]
            color_dot = KAAL_COLORS.get(k_name, "#78350F")
            dur = (p["End"] - p["Start"]).total_seconds() / 3600
            is_active = (p["Start"] <= now < p["End"])
            active_badge = '<span style="font-size:0.75rem; background:#DCFCE7; color:#166534; padding:2px 6px; border-radius:10px; margin-left:6px; font-weight:700;">LIVE</span>' if is_active else ''
            table_rows.append(
                f'<tr><td><span style="display:inline-block;width:10px;height:10px;border-radius:50%;background-color:{color_dot};margin-right:6px;"></span><b>{k_name}</b>{active_badge}</td>'
                f'<td>{p["Start"].strftime("%I:%M %p")}</td>'
                f'<td>{p["End"].strftime("%I:%M %p")}</td>'
                f'<td>{dur:.1f}h</td></tr>'
            )
        rows_str = "".join(table_rows)
        render_html(f"""
        <table class="custom-table">
            <thead>
                <tr><th>Kaal Period</th><th>Start</th><th>End</th><th>Duration</th></tr>
            </thead>
            <tbody>
                {rows_str}
            </tbody>
        </table>
        <div style="font-size:0.78rem; color:#6B7280; margin-top:8px; line-height:1.4;">
            🟡 <b>Kartavya Kaal</b> 🔵 <b>Anand Kaal</b><br>
            🟣 <b>Prarabdh Kaal</b> 🟤 <b>Bhagya Kaal</b>
        </div>
        """)

# --- 4. ZODIAC / RASI ---
render_html('<div class="section-title">♈ Zodiac Sign (Rasi)</div>')
col_srasi, col_mrasi = st.columns(2)
with col_srasi:
    render_html(f"""
    <div class="panchang-card">
        <div class="panchang-card-title">☀️ Surya Rasi (Sun Sign)</div>
        <div class="panchang-card-val" style="color: #B45309;">{today_sun_rasi}</div>
    </div>
    """)
with col_mrasi:
    render_html(f"""
    <div class="panchang-card">
        <div class="panchang-card-title">🌙 Chandra Rasi (Moon Sign)</div>
        <div class="panchang-card-val" style="color: #1E40AF;">{today_moon_rasi}</div>
    </div>
    """)

# --- 5. SANDHYA WINDOWS ---
render_html('<div class="section-title">⏱️ Sandhya Windows & Midpoints</div>')
cs1, cs2, cs3, cs4 = st.columns(4)
with cs1:
    render_html(f"""
    <div class="panchang-card">
        <div class="panchang-card-title">Morning Sandhya</div>
        <div class="panchang-card-val" style="font-size:0.92rem;">{sandhya_times['morning']['start'].strftime('%I:%M %p')} - {sandhya_times['morning']['end'].strftime('%I:%M %p')}</div>
        <div class="panchang-card-sub">Mid: {sunrise.strftime('%I:%M %p')}</div>
    </div>
    """)
with cs2:
    render_html(f"""
    <div class="panchang-card">
        <div class="panchang-card-title">Midday Sandhya</div>
        <div class="panchang-card-val" style="font-size:0.92rem;">{sandhya_times['midday']['start'].strftime('%I:%M %p')} - {sandhya_times['midday']['end'].strftime('%I:%M %p')}</div>
        <div class="panchang-card-sub">Mid: {midday.strftime('%I:%M %p')}</div>
    </div>
    """)
with cs3:
    render_html(f"""
    <div class="panchang-card">
        <div class="panchang-card-title">Evening Sandhya</div>
        <div class="panchang-card-val" style="font-size:0.92rem;">{sandhya_times['evening']['start'].strftime('%I:%M %p')} - {sandhya_times['evening']['end'].strftime('%I:%M %p')}</div>
        <div class="panchang-card-sub">Mid: {sunset.strftime('%I:%M %p')}</div>
    </div>
    """)
with cs4:
    render_html(f"""
    <div class="panchang-card">
        <div class="panchang-card-title">Midnight Sandhya</div>
        <div class="panchang-card-val" style="font-size:0.92rem;">{sandhya_times['midnight']['start'].strftime('%I:%M %p')} - {sandhya_times['midnight']['end'].strftime('%I:%M %p')}</div>
        <div class="panchang-card-sub">Mid: {midnight.strftime('%I:%M %p')}</div>
    </div>
    """)

# --- 6. NAAD SADHANA ---
render_html('<div class="section-title">🔔 Naad Sadhana Times</div>')
if morning_sadhana and evening_sadhana:
    cn1, cn2 = st.columns(2)
    with cn1:
        render_html(f"""
        <div class="panchang-card">
            <div class="panchang-card-title">🌅 Morning Naad Sadhana</div>
            <div class="panchang-card-val" style="color: #B45309;">{morning_sadhana.strftime('%I:%M %p')}</div>
        </div>
        """)
    with cn2:
        render_html(f"""
        <div class="panchang-card">
            <div class="panchang-card-title">🌇 Evening Naad Sadhana</div>
            <div class="panchang-card-val" style="color: #78350F;">{evening_sadhana.strftime('%I:%M %p')}</div>
        </div>
        """)
else:
    st.warning("Could not compute exact Naad Sadhana times for the selected date.")

# --- 7. NAKSHATRA ---
render_html('<div class="section-title">✨ Nakshatra Timings & Attributes</div>')
for label, n_data in [("Yesterday's", yesterday_nakshatra), ("Today's", today_nakshatra), ("Tomorrow's", tomorrow_nakshatra)]:
    attrs = NAKSHATRA_ATTRIBUTES.get(n_data["name"], {})
    is_today = label == "Today's"
    highlight_style = "border-left: 4px solid #B45309; background: #FAF5F0;" if is_today else "background: #FAF8F5;"
    render_html(f"""
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
    """)

# --- 8. TITHI & SWARA ---
render_html('<div class="section-title">🌘 Tithi & Swara Transitions</div>')
for label, t_data in [("Yesterday's", yesterday_tithi), ("Today's", today_tithi), ("Tomorrow's", tomorrow_tithi)]:
    is_today = label == "Today's"
    highlight_style = "border-left: 4px solid #B45309; background: #FAF5F0;" if is_today else "background: #FAF8F5;"
    render_html(f"""
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
    """)

sr_swara = sunrise_swaras.get('sunrise', 'Unknown')
ss_swara = sunset_swaras.get('sunset', 'Unknown')
sr_class = "swara-ida" if sr_swara == "Ida" else "swara-pingala"
ss_class = "swara-ida" if ss_swara == "Ida" else "swara-pingala"

csw1, csw2 = st.columns(2)
with csw1:
    render_html(f"""
    <div class="panchang-card">
        <div class="panchang-card-title">Sunrise Swara ({tithi_at_sunrise['name']})</div>
        <div style="margin-top: 6px;"><span class="swara-badge {sr_class}">🌬️ {sr_swara}</span></div>
    </div>
    """)
with csw2:
    render_html(f"""
    <div class="panchang-card">
        <div class="panchang-card-title">Sunset Swara ({tithi_at_sunset['name']})</div>
        <div style="margin-top: 6px;"><span class="swara-badge {ss_class}">🌬️ {ss_swara}</span></div>
    </div>
    """)

# --- 9. LIVE CLOCK ---
render_html(f"""
<div class="clock-banner">
    <div style="font-size: 0.85rem; font-weight: 600; color: #78350F; text-transform: uppercase; letter-spacing: 1px;">Current Local Time ({loc_details['tz']})</div>
    <div class="clock-time">{now.strftime('%I:%M:%S %p')}</div>
    <div style="font-size: 0.85rem; color: #6B7280; margin-top: 4px;">{loc_details['display_name']} • Live Refresh Active</div>
</div>
""")

st_autorefresh(interval=60000, key="panchang_live_refresh")
