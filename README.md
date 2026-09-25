# 🕉️ Personal Vedic Panchang

A comprehensive, precise Hindu Panchang and Kaal clock web application built with **Streamlit** and astronomical calculations powered by **PyEphem**.

---

## 🌟 Key Features

- **Accurate Astronomical Timings**: Ephem-powered sunrise, sunset, moonrise, and moonset calculations based on exact observer latitude, longitude, and elevation.
- **24-Hour Kaal Cycle Visualization**: Interactive donut chart breaking down Kartavya Kaal, Anand Kaal, Prarabdh Kaal, and Bhagya Kaal periods throughout the day.
- **Vedic Tithi & Nakshatra Calculations**: Complete boundary crossing calculations for Tithi, Paksha, Nakshatra, and their attributes (Nadi, Tattva, Adhipati, Swabhava).
- **Swara Yoga**: Dynamic calculation of waking swara, sunrise swara, and sunset swara (Ida / Pingala).
- **Naad Sadhana & Sandhya Timings**: 2-hour Sandhya windows (Morning, Midday, Evening, Midnight) and Naad Sadhana meditation windows.
- **Global & Indian City Geocoding**: Automatic timezone and coordinate detection with pre-cached top cities and manual coordinate override.
- **Auto-Refresh Live Clock**: Live refreshing local clock.

---

## 🚀 How to Run Locally

1. **Clone the repository:**
   ```bash
   git clone https://github.com/lambdaft/panchang.git
   cd panchang
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Launch the Streamlit app:**
   ```bash
   streamlit run streamlit_app.py
   ```

---

## 🌐 How to Deploy Online on Streamlit Cloud (Free)

1. Push your latest code to your GitHub repository:
   ```bash
   git add .
   git commit -m "Configure Streamlit online deployment"
   git push origin main
   ```

2. Go to **[share.streamlit.io](https://share.streamlit.io)** and log in with your GitHub account.

3. Click **"New app"** and select:
   - **Repository**: `lambdaft/panchang` (or your repo name)
   - **Branch**: `main` (or `master`)
   - **Main file path**: `streamlit_app.py`

4. Click **Deploy!** 🎉
   Your Panchang app will be live with a public URL (e.g. `https://panchang.streamlit.app`).

---

## 📦 Tech Stack

- **Framework**: Streamlit
- **Ephemeris Calculations**: PyEphem
- **Data & Visualizations**: Pandas, Altair
- **Geolocation**: Geopy (Nominatim), TimezoneFinder, PyTZ
