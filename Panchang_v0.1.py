# my_personal_panchang.py — FINAL: Dynamic Location, Colored 24-Hour Kaal Clock, Precise Astro Times, Rasi Added
import streamlit as st
from datetime import datetime, date, timedelta, time
import pytz
import math
import ephem  # REQUIRES: pip install ephem
from streamlit_autorefresh import st_autorefresh
from typing import Dict, Any, Optional, List
import pandas as pd
import altair as alt

# NEW DEPENDENCIES FOR GEOLOCATION & TIMEZONE DETECTING
# REQUIRES: pip install geopy timezonefinder
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder

st.set_page_config(page_title="Personal Panchang", layout="centered")

# --- CUSTOM CSS FOR BLACK/WHITE THEME ---
st.markdown(
    """
    <style>
    .stApp {
        background-color: #ffffff;
        color: #000000;
    }
    h1, h2, h3, h4, h5, h6, p, div, span, label, legend, .st-bh, .st-bb, .st-b9, .st-ba {
        color: #000000 !important;
    }
    table, th, td, tr {
        color: #000000 !important;
        background-color: #ffffff !important;
        border-color: #000000 !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Main Title (Black)
st.markdown(
    "<h1 style='text-align: center; font-family: serif; font-size: 36px; margin-bottom: 5px; color: black;'>Personal Panchang</h1>",
    unsafe_allow_html=True,
)

# --- NEW: DYNAMIC LOCATION AND TIMEZONE INPUT ---
st.markdown(
    "<h4 style='color: black; margin-bottom: 0px;'>Location Settings</h4>",
    unsafe_allow_html=True,
)
city_input = st.text_input(
    "Enter your City (e.g., Kolhapur, Mumbai, London)", value="Kolhapur"
)


@st.cache_data(show_spinner="Locating city...")
def get_location_details(city_name: str):
    try:
        geolocator = Nominatim(user_agent="panchang_app_v1")
        location = geolocator.geocode(city_name, addressdetails=True)
        if location:
            tf = TimezoneFinder()
            tz_str = tf.timezone_at(lng=location.longitude, lat=location.latitude)
            # Default elevation to 0 if not fetched, or keep an approximate default
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
    except Exception as e:
        pass
    # Fallback to Kolhapur defaults if search fails
    return {
        "lat": "16.7050",
        "lon": "74.2433",
        "elevation": 569,
        "tz": "Asia/Kolkata",
        "display_name": "Kolhapur, India (Fallback)",
    }


loc_details = get_location_details(city_input)

LATITUDE = loc_details["lat"]
LONGITUDE = loc_details["lon"]
ELEVATION = loc_details["elevation"]
TZ = pytz.timezone(loc_details["tz"])

# Show detected location data to the user subtly
st.markdown(
    f"<p style='font-size: 13px; color: gray; margin-top: -10px;'>Using: {loc_details['display_name']} | Timezone: {loc_details['tz']}</p>",
    unsafe_allow_html=True,
)

# --- DATE SELECTION ---
selected_date = st.date_input("Date", value=date.today())
now = datetime.now(TZ)

# --- COLOR MAPS ---
KAAL_COLORS = {
    "Kartavya Kaal": "#FFC300",  # Amber/Yellow (Solar)
    "Anand Kaal": "#4682B4",  # Steel Blue (Lunar)
    "Prarabdh Kaal": "#800080",  # Purple (Combined)
    "Bhagya Kaal": "#8B4513",  # Brown (Neutral/Earth)
}

# ---------- RASI (ZODIAC) DEFINITIONS ----------
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

# ---------- NAKSHATRA ATTRIBUTES ----------
NAKSHATRA_ATTRIBUTES: Dict[str, Dict[str, str]] = {
    "Aśvinī": {"Nadi": "Ida", "Tattva": "Vayu", "Adhipati": "Ketu", "Swabhava": "Guru"},
    "Bharanī": {
        "Nadi": "Pingala",
        "Tattva": "Agni",
        "Adhipati": "Shukra",
        "Swabhava": "Shukra",
    },
    "Kṛttikā": {
        "Nadi": "Ida",
        "Tattva": "Agni",
        "Adhipati": "Ravi",
        "Swabhava": "Shukra",
    },
    "Rohiṇī": {
        "Nadi": "Pingala",
        "Tattva": "Prithvi",
        "Adhipati": "Chandra",
        "Swabhava": "Budh",
    },
    "Mṛgaśīrṣa": {
        "Nadi": "Ida",
        "Tattva": "Vayu",
        "Adhipati": "Mangala",
        "Swabhava": "Guru",
    },
    "Ārdrā": {
        "Nadi": "Ida",
        "Tattva": "Jala",
        "Adhipati": "Rahu",
        "Swabhava": "Chandra",
    },
    "Punarvasu": {
        "Nadi": "Pingala",
        "Tattva": "Vayu",
        "Adhipati": "Guru",
        "Swabhava": "Shukra",
    },
    "Puṣya": {"Nadi": "Ida", "Tattva": "Agni", "Adhipati": "Shani", "Swabhava": "Guru"},
    "Āśleṣā": {
        "Nadi": "Ida",
        "Tattva": "Jala",
        "Adhipati": "Budh",
        "Swabhava": "Chandra",
    },
    "Maghā": {
        "Nadi": "Ida",
        "Tattva": "Agni",
        "Adhipati": "Ketu",
        "Swabhava": "Shukra",
    },
    "Pūrva Phalgunī": {
        "Nadi": "Pingala",
        "Tattva": "Agni",
        "Adhipati": "Shukra",
        "Swabhava": "Mangala",
    },
    "Uttara Phalgunī": {
        "Nadi": "Pingala",
        "Tattva": "Vayu",
        "Adhipati": "Ravi",
        "Swabhava": "Rahu",
    },
    "Hasta": {
        "Nadi": "Pingala",
        "Tattva": "Vayu",
        "Adhipati": "Chandra",
        "Swabhava": "Rahu",
    },
    "Citrā": {
        "Nadi": "Pingala",
        "Tattva": "Vayu",
        "Adhipati": "Mangala",
        "Swabhava": "Rahu",
    },
    "Svātī": {
        "Nadi": "Pingala",
        "Tattva": "Vayu",
        "Adhipati": "Rahu",
        "Swabhava": "Mangala",
    },
    "Viśākhā": {
        "Nadi": "Pingala",
        "Tattva": "Vayu",
        "Adhipati": "Guru",
        "Swabhava": "Rahu",
    },
    "Anurādhā": {
        "Nadi": "Ida",
        "Tattva": "Prithvi",
        "Adhipati": "Shani",
        "Swabhava": "Ravi",
    },
    "Jyeṣṭha": {
        "Nadi": "Pingala",
        "Tattva": "Prithvi",
        "Adhipati": "Budh",
        "Swabhava": "Ravi",
    },
    "Mūla": {
        "Nadi": "Pingala",
        "Tattva": "Jala",
        "Adhipati": "Ketu",
        "Swabhava": "Shani",
    },
    "Pūrvāṣāḍhā": {
        "Nadi": "Ida",
        "Tattva": "Jala",
        "Adhipati": "Shukra",
        "Swabhava": "Budh",
    },
    "Uttarāṣāḍhā": {
        "Nadi": "Ida",
        "Tattva": "Prithvi",
        "Adhipati": "Ravi",
        "Swabhava": "Budh",
    },
    "Śravaṇa": {
        "Nadi": "Ida",
        "Tattva": "Prithvi",
        "Adhipati": "Chandra",
        "Swabhava": "Budh",
    },
    "Dhaniṣṭhā": {
        "Nadi": "Ida",
        "Tattva": "Prithvi",
        "Adhipati": "Mangala",
        "Swabhava": "Budh",
    },
    "Śatabhiṣā": {
        "Nadi": "Ida",
        "Tattva": "Jala",
        "Adhipati": "Rahu",
        "Swabhava": "Shani",
    },
    "Pūrva Bhādrapadā": {
        "Nadi": "Ida",
        "Tattva": "Agni",
        "Adhipati": "Guru",
        "Swabhava": "Shukra",
    },
    "Uttara Bhādrapadā": {
        "Nadi": "Pingala",
        "Tattva": "Jala",
        "Adhipati": "Shani",
        "Swabhava": "Guru",
    },
    "Revatī": {
        "Nadi": "Pingala",
        "Tattva": "Jala",
        "Adhipati": "Budh",
        "Swabhava": "Chandra",
    },
}

# ---------- TITHI & SWARA MAPPING ----------
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
    "Aśvinī",
    "Bharanī",
    "Kṛttikā",
    "Rohiṇī",
    "Mṛgaśīrṣa",
    "Ārdrā",
    "Punarvasu",
    "Puṣya",
    "Āśleṣā",
    "Maghā",
    "Pūrva Phalgunī",
    "Uttara Phalgunī",
    "Hasta",
    "Citrā",
    "Svātī",
    "Viśākhā",
    "Anurādhā",
    "Jyeṣṭha",
    "Mūla",
    "PūrvāṣāBDhā",
    "Uttarāṣāḍhā",
    "Śravaṇa",
    "Dhaniṣṭhā",
    "Śatabhiṣā",
    "Pūrva Bhādrapadā",
    "Uttara Bhādrapadā",
    "Revatī",
]
# Fixing potential typos from raw encoding copy for Nakshatras names
NAKSHATRA_NAMES[19] = "Pūrvāṣāḍhā"

NAKSHATRA_ARC = 360.0 / 27.0


# --- Helper Functions ---
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
        return "#4169E1"  # Royal Blue (Lunar/Cool)
    elif swara == "Pingala":
        return "#FF4500"  # Orange Red (Solar/Hot)
    else:
        return "#000000"  # Black (Neutral/Sushumna)


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


def to_ephem_date(dt: datetime) -> ephem.Date:
    """Convert timezone-aware or naive datetime to ephem.Date (UTC)."""
    utc_dt = dt.astimezone(pytz.utc) if dt.tzinfo else pytz.utc.localize(dt)
    return ephem.Date(utc_dt)


def to_local_datetime(ephem_d: ephem.Date) -> datetime:
    """Convert ephem.Date back to local timezone datetime."""
    return pytz.utc.localize(ephem_d.datetime()).astimezone(TZ)


def get_ayanamsa_deg(ephem_d: ephem.Date) -> float:
    """Calculate Lahiri (Chitra Paksha) Ayanamsa for the given ephem date."""
    jd_val = ephem.julian_date(ephem_d)
    t = (jd_val - 2451545.0) / 36525.0
    return (23.8570922 + 1.3969713 * t + 0.0003086 * t * t) % 360.0


def get_moon_sun_elongation(ephem_d: ephem.Date) -> float:
    """Calculate Moon - Sun apparent ecliptic longitude elongation in degrees [0, 360)."""
    sun = ephem.Sun(ephem_d)
    moon = ephem.Moon(ephem_d)
    sun_lon = math.degrees(ephem.Ecliptic(sun).lon) % 360.0
    moon_lon = math.degrees(ephem.Ecliptic(moon).lon) % 360.0
    return (moon_lon - sun_lon) % 360.0


def get_sidereal_moon_lon(ephem_d: ephem.Date) -> float:
    """Calculate Moon sidereal (Nirayana) longitude in degrees [0, 360)."""
    moon = ephem.Moon(ephem_d)
    moon_lon = math.degrees(ephem.Ecliptic(moon).lon) % 360.0
    ayan = get_ayanamsa_deg(ephem_d)
    return (moon_lon - ayan + 360.0) % 360.0


def get_sidereal_sun_lon(ephem_d: ephem.Date) -> float:
    """Calculate Sun sidereal (Nirayana) longitude in degrees [0, 360)."""
    sun = ephem.Sun(ephem_d)
    sun_lon = math.degrees(ephem.Ecliptic(sun).lon) % 360.0
    ayan = get_ayanamsa_deg(ephem_d)
    return (sun_lon - ayan + 360.0) % 360.0


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
            "Pratipada",
            "Dvitīya",
            "Tṛtīya",
            "Caturthī",
            "Pañchamī",
            "Ṣaṣṭhī",
            "Saptamī",
            "Aṣṭamī",
            "Navamī",
            "Daśamī",
            "Ekādaśī",
            "Dvādaśī",
            "Trayodaśī",
            "Caturdaśī",
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
    obs.lat, obs.lon, obs.elevation = LATITUDE, LONGITUDE, ELEVATION
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


# --- Waking Swara ---
weekday = selected_date.weekday()
day_index = (weekday + 1) % 7
swara_at_waking = ["Pingala", "Ida", "Pingala", "Ida", "Ida", "Ida", "Pingala"][
    day_index
]

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


# --- Calculate Midpoints ---
def calculate_madhyamas(sunrise_dt: datetime, sunset_dt: datetime, next_sunrise_dt: datetime) -> Dict[str, datetime]:
    day_duration = sunset_dt - sunrise_dt
    day_madhyama = sunrise_dt + (day_duration / 2)
    night_duration = next_sunrise_dt - sunset_dt
    night_madhyama = sunset_dt + (night_duration / 2)
    return {"day_madhyama": day_madhyama, "night_madhyama": night_madhyama}


madhyamas = calculate_madhyamas(sunrise, sunset, next_sunrise)
midday = madhyamas["day_madhyama"]
midnight = madhyamas["night_madhyama"]

tithi_at_sunrise = get_tithi_at(sunrise)
tithi_at_sunset = get_tithi_at(sunset)

sunrise_swaras = get_swaras_from_tithi(tithi_at_sunrise)
sunset_swaras = get_swaras_from_tithi(tithi_at_sunset)
sunrise_swara_color = get_swara_color(sunrise_swaras["sunrise"])
sunset_swara_color = get_swara_color(sunset_swaras["sunset"])


# --- Naad Sadhana Times ---
def calculate_naad_sadhana_times(
    midday: datetime, current_date: date, tithi_data: Dict[str, Any]
):
    minutes_to_subtract = midday.minute
    adjustment = timedelta(minutes=minutes_to_subtract)
    tithi_key = (tithi_data["paksha"], tithi_data["name"])
    base_time_str = NAAD_SADHANA_BASE_TIMES.get(tithi_key)
    if not base_time_str:
        return {"morning_sadhana": None, "evening_sadhana": None}
    try:
        base_h, base_m = map(int, base_time_str.split(":"))
        morning_base_dt = TZ.localize(
            datetime(
                current_date.year, current_date.month, current_date.day, base_h, base_m
            )
        )
        morning_sadhana = morning_base_dt - adjustment
        evening_base_dt = morning_base_dt + timedelta(hours=12)
        evening_sadhana = evening_base_dt - adjustment
        if morning_sadhana.date() < morning_base_dt.date():
            morning_sadhana += timedelta(days=1)
        return {"morning_sadhana": morning_sadhana, "evening_sadhana": evening_sadhana}
    except ValueError:
        return {"morning_sadhana": None, "evening_sadhana": None}


naad_sadhana_times = calculate_naad_sadhana_times(
    midday, selected_date, tithi_at_sunrise
)
morning_sadhana = naad_sadhana_times["morning_sadhana"]
evening_sadhana = naad_sadhana_times["evening_sadhana"]


# --- Sandhya Times ---
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


# --- KAAL Calculation ---
def calculate_kaal_periods(
    day_start_dt, day_end_dt, sunrise_dt, sunset_dt, moon_rise_dt, moon_set_dt
):
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

    events = sorted(
        [e for e in events if day_start_dt <= e[0] <= day_end_dt], key=lambda x: x[0]
    )
    periods = []

    def is_moon_up_at(dt_check):
        obs_check = ephem.Observer()
        obs_check.lat, obs_check.lon, obs_check.elevation = (
            LATITUDE,
            LONGITUDE,
            ELEVATION,
        )
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
kaal_periods = calculate_kaal_periods(
    day_start_dt, day_end_dt, sunrise, sunset, moon_rise, moon_set
)

# Chart Data
chart_data = []
for p in kaal_periods:
    duration = (p["End"] - p["Start"]).total_seconds() / 3600
    chart_data.append(
        {
            "Kaal": p["Kaal"],
            "Duration": duration,
            "Start": p["Start"].strftime("%H:%M"),
            "End": p["End"].strftime("%H:%M"),
        }
    )
df_chart = pd.DataFrame(chart_data)

# ---------- DISPLAY ----------
st.markdown("<div style='margin-top: -15px;'>", unsafe_allow_html=True)
st.markdown("<hr style='border-top: 1px solid black;'>", unsafe_allow_html=True)
st.markdown(
    f"<h3 style='text-align: center; color: black; font-size: 28px; margin-bottom: 0px;'>{swara_at_waking} </h3>",
    unsafe_allow_html=True,
)
st.markdown(
    f"<p style='text-align: center; color: black; font-size: 14px; margin-top: 0px;'>{selected_date.strftime('%A • %d %B %Y')}</p>",
    unsafe_allow_html=True,
)
st.markdown("<hr style='border-top: 1px solid black;'>", unsafe_allow_html=True)


# --- PRECISE ASTRONOMICAL RISE/SET TIMINGS ---
def display_astro_time(title, dt: Optional[datetime]):
    time_str = dt.strftime("%I:%M %p") if dt else "N/A"
    st.markdown(
        f"<p style='text-align: center; font-size: 16px; font-weight: bold; color: black; margin-bottom: 0;'>{title}</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<p style='text-align: center; font-size: 24px; color: black; margin-top: 0; margin-bottom: 0;'>{time_str}</p>",
        unsafe_allow_html=True,
    )


st.markdown(
    f"<h4 style='text-align: center; color: black; font-size: 18px; margin-bottom: 5px;'>Precise Astronomical Rise/Set Timings ({loc_details['display_name'].split(',')[0]})</h4>",
    unsafe_allow_html=True,
)
col_sr, col_ss, col_mr, col_ms = st.columns(4)
with col_sr:
    display_astro_time("Sunrise", sunrise)
with col_ss:
    display_astro_time("Sunset", sunset)
with col_mr:
    display_astro_time("Moonrise", moon_rise)
with col_ms:
    display_astro_time("Moonset", moon_set)
st.markdown("<hr style='border-top: 1px solid black;'>", unsafe_allow_html=True)


# --- KAAL VISUALIZATION (Colored 24-Hour Clock) ---
st.markdown(
    "<h4 style='text-align: center; color: black; font-size: 18px; margin-bottom: 5px;'>24-Hour Time Cycle Visualization</h4>",
    unsafe_allow_html=True,
)
if not df_chart.empty:
    domain = list(KAAL_COLORS.keys())
    range_ = list(KAAL_COLORS.values())

    base = alt.Chart(df_chart).encode(
        theta=alt.Theta("Duration", stack=True),
        order=alt.Order("Start"),
    )

    pie = base.mark_arc(outerRadius=120, innerRadius=60).encode(
        color=alt.Color(
            "Kaal",
            scale=alt.Scale(domain=domain, range=range_),
            legend=alt.Legend(
                orient="bottom", columns=2, titleOrient="left", title=None
            ),
        ),
        tooltip=["Kaal", "Start", "End", alt.Tooltip("Duration", format=".1f")],
    )

    now_hour = now.hour + now.minute / 60 + now.second / 3600
    current_time_angle = (now_hour / 24) * 360

    marker_data = pd.DataFrame(
        [{"angle": current_time_angle, "time": now.strftime("%I:%M %p")}]
    )

    current_time_marker = (
        alt.Chart(marker_data)
        .mark_point(
            shape="triangle-up", size=80, fill="black", stroke="black", strokeWidth=1
        )
        .encode(
            theta=alt.Theta("angle", scale=None),
            color=alt.value("black"),
            tooltip=[alt.Tooltip("time", title="Current Time")],
        )
        .properties(title="Current Time: " + now.strftime("%I:%M %p"))
    )

    chart = (pie).properties(width=300, height=300)

    st.altair_chart(chart, use_container_width=True)

    st.markdown(
        "<p style='text-align: center; font-weight: bold; font-size: 14px; color: black;'>Detailed Kaal Timings</p>",
        unsafe_allow_html=True,
    )
    table_html = "<table style='width:100%; border-collapse: collapse; font-size: 14px; color: black; border: 1px solid black;'>"
    table_html += "<tr style='border-bottom: 1px solid black; text-align: left;'><th>Kaal</th><th>Start</th><th>End</th></tr>"
    for p in kaal_periods:
        k_name = p["Kaal"]
        table_html += f"<tr style='border-bottom: 1px solid black;'>"
        table_html += f"<td style='padding: 8px;'>{k_name}</td><td style='padding: 8px;'>{p['Start'].strftime('%I:%M %p')}</td><td style='padding: 8px;'>{p['End'].strftime('%I:%M %p')}</td></tr>"
    table_html += "</table>"
    st.markdown(table_html, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<hr style='border-top: 1px solid black;'>", unsafe_allow_html=True)

# --- RASI (ZODIAC) TIMINGS ---
st.markdown(
    "<h4 style='text-align: center; color: black; font-size: 20px; margin-bottom: 5px;'>Rasi (Zodiac Sign)</h4>",
    unsafe_allow_html=True,
)
col_srasi, col_mrasi = st.columns(2)
with col_srasi:
    st.markdown(
        f"<p style='text-align: center; font-size: 14px; color: black; margin-bottom: 0px;'>Sun Rasi (Surya Rasi)</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<p style='text-align: center; font-size: 18px; color: black; margin-top: 0px; font-weight: bold;'>{today_sun_rasi}</p>",
        unsafe_allow_html=True,
    )
with col_mrasi:
    st.markdown(
        f"<p style='text-align: center; font-size: 14px; color: black; margin-bottom: 0px;'>Moon Rasi (Chandra Rasi)</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<p style='text-align: center; font-size: 18px; color: black; margin-top: 0px; font-weight: bold;'>{today_moon_rasi}</p>",
        unsafe_allow_html=True,
    )
st.markdown("<hr style='border-top: 1px solid black;'>", unsafe_allow_html=True)


# --- MADHYAMA (MIDPOINT) TIMINGS ---
st.markdown(
    "<h4 style='text-align: center; color: black; font-size: 18px; margin-bottom: 5px;'>Madhyama (Midpoint) Timings</h4>",
    unsafe_allow_html=True,
)


def display_madhyama_time(title, median_dt):
    before = median_dt - timedelta(hours=1)
    after = median_dt + timedelta(hours=1)
    st.markdown(
        f"<p style='text-align: center; font-size: 14px; font-weight: bold; color: black; margin-bottom: 0;'>{before.strftime('%I:%M %p')}</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<p style='text-align: center; font-size: 16px; font-weight: bold; color: black; margin-bottom: 0;'>{title}</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<p style='text-align: center; font-size: 20px; color: black; margin-top: 0; margin-bottom: 0;'>{median_dt.strftime('%I:%M %p')}</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<p style='text-align: center; font-size: 14px; font-weight: bold; color: black; margin-top: 0;'>{after.strftime('%I:%M %p')}</p>",
        unsafe_allow_html=True,
    )


col_sr, col_daym, col_ss, col_midn = st.columns(4)
with col_sr:
    display_madhyama_time("Sunrise", sunrise)
with col_daym:
    display_madhyama_time("Midday", midday)
with col_ss:
    display_madhyama_time("Sunset", sunset)
with col_midn:
    display_madhyama_time("Midnight", midnight)
st.markdown("<hr style='border-top: 1px solid black;'>", unsafe_allow_html=True)

# --- SANDHYA TIMINGS ---
st.markdown(
    "<h4 style='text-align: center; color: black; font-size: 18px; margin-bottom: 5px;'>2-Hour Sandhya Windows</h4>",
    unsafe_allow_html=True,
)
col_sandhya1, col_sandhya2 = st.columns(2)
with col_sandhya1:
    st.markdown(
        f"<p style='text-align: center; font-size: 14px; font-weight: bold; color: black; margin-bottom: 0;'>Morning Sandhya</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<p style='text-align: center; font-size: 16px; color: black; margin-top: 0; margin-bottom: 5px;'>{sandhya_times['morning']['start'].strftime('%I:%M %p')} - {sandhya_times['morning']['end'].strftime('%I:%M %p')}</p>",
        unsafe_allow_html=True,
    )
with col_sandhya2:
    st.markdown(
        f"<p style='text-align: center; font-size: 14px; font-weight: bold; color: black; margin-bottom: 0;'>Midday Sandhya</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<p style='text-align: center; font-size: 16px; color: black; margin-top: 0; margin-bottom: 5px;'>{sandhya_times['midday']['start'].strftime('%I:%M %p')} - {sandhya_times['midday']['end'].strftime('%I:%M %p')}</p>",
        unsafe_allow_html=True,
    )
col_sandhya3, col_sandhya4 = st.columns(2)
with col_sandhya3:
    st.markdown(
        f"<p style='text-align: center; font-size: 14px; font-weight: bold; color: black; margin-bottom: 0;'>Evening Sandhya</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<p style='text-align: center; font-size: 16px; color: black; margin-top: 0; margin-bottom: 5px;'>{sandhya_times['evening']['start'].strftime('%I:%M %p')} - {sandhya_times['evening']['end'].strftime('%I:%M %p')}</p>",
        unsafe_allow_html=True,
    )
with col_sandhya4:
    st.markdown(
        f"<p style='text-align: center; font-size: 14px; font-weight: bold; color: black; margin-bottom: 0;'>Midnight Sandhya</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<p style='text-align: center; font-size: 16px; color: black; margin-top: 0; margin-bottom: 5px;'>{sandhya_times['midnight']['start'].strftime('%I:%M %p')} - {sandhya_times['midnight']['end'].strftime('%I:%M %p')}</p>",
        unsafe_allow_html=True,
    )
st.markdown("<hr style='border-top: 1px solid black;'>", unsafe_allow_html=True)


# --- NAAD SADHANA ---
st.markdown(
    "<h4 style='text-align: center; color: black; font-size: 18px; margin-bottom: 5px;'>Naad Sadhana Times</h4>",
    unsafe_allow_html=True,
)
col3, col4 = st.columns(2)
if morning_sadhana and evening_sadhana:
    with col3:
        st.markdown(
            f"<p style='text-align: center; font-size: 14px; font-weight: bold; color: black; margin-bottom: 0;'>Morning Sadhana</p>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<p style='text-align: center; font-size: 18px; color: black; margin-top: 0;'>{morning_sadhana.strftime('%I:%M %p')}</p>",
            unsafe_allow_html=True,
        )
    with col4:
        st.markdown(
            f"<p style='text-align: center; font-size: 14px; font-weight: bold; color: black; margin-bottom: 0;'>Evening Sadhana</p>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<p style='text-align: center; font-size: 18px; color: black; margin-top: 0;'>{evening_sadhana.strftime('%I:%M %p')}</p>",
            unsafe_allow_html=True,
        )
else:
    st.warning("Could not calculate Naad Sadhana times.")

# --- NAKSHATRA & TITHI ---
st.markdown("<hr style='border-top: 1px solid black;'>", unsafe_allow_html=True)
st.markdown(
    "<h4 style='text-align: center; color: black; font-size: 20px; margin-bottom: 0px;'>Nakshatra Timings & Attributes</h4>",
    unsafe_allow_html=True,
)


def display_nakshatra_span(label, nakshatra_data):
    name = nakshatra_data["name"]
    attrs = NAKSHATRA_ATTRIBUTES.get(name, {})
    st.markdown(
        f"<p style='text-align: center; font-size: 14px; font-weight: bold; color: black; margin-bottom: 0;'>{label} Nakshatra: <span style='font-size: 16px;'>{name}</span></p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<p style='text-align: center; font-size: 12px; color: black; margin-top: 0; margin-bottom: 5px;'>Start: {nakshatra_data['start'].strftime('%b %d, %I:%M %p')} End: {nakshatra_data['end'].strftime('%b %d, %I:%M %p')}</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<p style='text-align: center; font-size: 12px; color: black; margin-top: 0; margin-bottom: 10px; line-height: 1.2;'>Nadi: <b>{attrs.get('Nadi','')}</b> · Tattva: <b>{attrs.get('Tattva','')}</b> · Adhipati: <b>{attrs.get('Adhipati','')}</b> · Swabhava: <b>{attrs.get('Swabhava','')}</b></p>",
        unsafe_allow_html=True,
    )


display_nakshatra_span("Yesterday's", yesterday_nakshatra)
display_nakshatra_span("Today's", today_nakshatra)
display_nakshatra_span("Tomorrow's", tomorrow_nakshatra)

st.markdown("<hr style='border-top: 1px solid black;'>", unsafe_allow_html=True)
st.markdown(
    "<h4 style='text-align: center; color: black; font-size: 20px; margin-bottom: 0px;'>Tithi Timings</h4>",
    unsafe_allow_html=True,
)


def display_tithi_span(label, tithi_data):
    st.markdown(
        f"<p style='text-align: center; font-size: 14px; font-weight: bold; color: black; margin-bottom: 0;'>{label} Tithi: <span style='font-size: 16px;'>{tithi_data['name']} ({tithi_data['paksha']})</span></p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<p style='text-align: center; font-size: 12px; color: black; margin-top: 0; margin-bottom: 10px;'>Start: {tithi_data['start'].strftime('%b %d, %I:%M %p')} End: {tithi_data['end'].strftime('%b %d, %I:%M %p')}</p>",
        unsafe_allow_html=True,
    )


display_tithi_span("Yesterday's", yesterday_tithi)
display_tithi_span("Today's", today_tithi)
display_tithi_span("Tomorrow's", tomorrow_tithi)

st.markdown("<hr style='border-top: 1px solid black;'>", unsafe_allow_html=True)
st.markdown(
    "<h4 style='text-align: center; color: black; font-size: 20px; margin-bottom: 5px;'>Tithi-Based Swara</h4>",
    unsafe_allow_html=True,
)
st.markdown(
    f"<p style='text-align: center; font-size: 14px; color: black; margin-top: 0; margin-bottom: 0px;'>At Sunrise ({tithi_at_sunrise['name']} {tithi_at_sunrise['paksha']}): <span style='color: {sunrise_swara_color}; font-weight: bold;'>{sunrise_swaras['sunrise']}</span></p>",
    unsafe_allow_html=True,
)
st.markdown(
    f"<p style='text-align: center; font-size: 14px; color: black; margin-top: 5px; margin-bottom: 0px;'>At Sunset ({tithi_at_sunset['name']} {tithi_at_sunset['paksha']}): <span style='color: {sunset_swara_color}; font-weight: bold;'>{sunset_swaras['sunset']}</span></p>",
    unsafe_allow_html=True,
)

st.markdown("<hr style='border-top: 1px solid black;'>", unsafe_allow_html=True)
st.markdown(
    f"<h1 style='text-align: center; color: black; font-size: 36px; margin-bottom: 0;'>{now.strftime('%I:%M:%S %p')}</h1>",
    unsafe_allow_html=True,
)
st_autorefresh(interval=60000, key="refresh")
st.markdown(
    f"<p style='text-align: center; color: black; font-size: 12px; margin-top: 5px;'>{loc_details['display_name']} • Tithi, Nakshatra, Swara, Rasi & Naad Sadhana</p>",
    unsafe_allow_html=True,
)
st.markdown("</div>", unsafe_allow_html=True)
