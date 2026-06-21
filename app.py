import streamlit as st
import pandas as pd
import os
import google.generativeai as genai

# --- Configuration ---
st.set_page_config(
    page_title="CarbonFlow AI",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Secure API Key Handling
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# --- Futuristic Styling ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Inter:wght@300;400;600&display=swap');
    
    .main {
        background: radial-gradient(circle at top right, #0a0e14, #02050a);
        color: #e0e0e0;
        font-family: 'Inter', sans-serif;
    }
    
    h1, h2, h3 {
        font-family: 'Orbitron', sans-serif;
        color: #00f2ff !important;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    
    .stButton>button {
        background: linear-gradient(90deg, #00f2ff, #0072ff);
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 2rem;
        font-family: 'Orbitron', sans-serif;
        transition: 0.3s;
    }
    
    .stButton>button:hover {
        box-shadow: 0 0 15px #00f2ff;
        transform: scale(1.02);
    }
    
    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(0, 242, 255, 0.2);
        padding: 20px;
        border-radius: 15px;
        backdrop-filter: blur(10px);
    }
    
    .sidebar .sidebar-content {
        background-color: #0a0e14;
    }
    </style>
    """, unsafe_allow_html=True)

def get_fallback_tips(footprint_data):
    """Rule-based tips used when Gemini API is unavailable."""
    tips = []
    if footprint_data['driving'] > 1.0:
        tips.append("🚗 **Mobility:** Your driving emissions are significant. Consider carpooling, public transit, or an electric vehicle to cut this down.")
    if footprint_data['flights'] > 0.3:
        tips.append("✈️ **Aviation:** Flights are a major contributor. Try combining trips or choosing direct flights to reduce per-trip emissions.")
    if footprint_data['energy'] > 0.8:
        tips.append("⚡ **Energy:** Switch to LED lighting, unplug idle electronics, and consider renewable energy plans where available.")
    if footprint_data['diet'] > 2.0:
        tips.append("🥗 **Diet:** Reducing meat intake by even 2 days a week can meaningfully lower your dietary footprint.")
    if not tips:
        tips.append("✅ Your footprint is well-optimized across all categories. Keep up the sustainable habits!")
    return "\n\n".join(tips)

def get_gemini_tips(footprint_data, region):
    if not GEMINI_API_KEY:
        return get_fallback_tips(footprint_data)
    
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = f"""
        You are an environmental sustainability expert. 
        A user in {region} has an annual carbon footprint of {footprint_data['total']:.2f} tons CO2e.
        Breakdown: Driving: {footprint_data['driving']:.2f}, Flights: {footprint_data['flights']:.2f}, 
        Energy: {footprint_data['energy']:.2f}, Diet: {footprint_data['diet']:.2f}.
        
        Provide 3 concise, high-impact, and futuristic tips to reduce their footprint. 
        Keep it professional, encouraging, and specific to their highest emission categories.
        Format in Markdown.
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return get_fallback_tips(footprint_data)


def main():
    # --- Header ---
    st.title("🌌 CarbonFlow AI")
    st.markdown("#### *Precision Environmental Analytics for the Next Era*")
    st.divider()

    # --- Sidebar: Regional Baselines ---
    st.sidebar.header("📡 Regional Uplink")
    baselines = {
        "India": 1.9,
        "USA": 14.7,
        "UK": 5.2,
        "China": 7.6,
        "Global Average": 4.7
    }
    selected_region = st.sidebar.selectbox("Target Region Baseline:", list(baselines.keys()))
    baseline_value = baselines[selected_region]
    
    st.sidebar.info(f"Current {selected_region} Baseline: {baseline_value} tons/year")

    # --- Main Input Layout ---
    col_a, col_b = st.columns([1, 1], gap="large")

    with col_a:
        st.subheader("🚀 Mobility")
        km_per_year = st.number_input("Annual distance driven (km)", min_value=0, value=10000)
        fuel_efficiency = st.number_input("Fuel efficiency (km per liter)", min_value=1.0, value=15.0)
        
        st.subheader("✈️ Aviation")
        flights_short = st.slider("Short-haul flights (<3h)", 0, 20, 1)
        flights_long = st.slider("Long-haul flights (>3h)", 0, 10, 0)

    with col_b:
        st.subheader("⚡ Energy Matrix")
        electricity_kwh = st.number_input("Monthly electricity usage (kWh)", min_value=0, value=200)
        
        st.subheader("🍱 Consumption")
        diet_type = st.select_slider(
            "Dietary Profile",
            options=["Vegan", "Vegetarian", "Average (Meat/Veg)", "Meat-heavy"],
            value="Average (Meat/Veg)"
        )
        waste_recycling = st.selectbox("Waste Management Strategy", ["None", "Some", "Most/All"])

    # --- Calculation Logic ---
    transport_co2 = (km_per_year / fuel_efficiency) * 2.31 / 1000
    flight_co2 = (flights_short * 0.15) + (flights_long * 0.6)
    energy_co2 = (electricity_kwh * 12 * 0.4) / 1000
    
    diet_factors = {"Meat-heavy": 3.3, "Average (Meat/Veg)": 2.5, "Vegetarian": 1.7, "Vegan": 1.5}
    diet_co2 = diet_factors[diet_type]
    
    waste_factors = {"None": 0.5, "Some": 0.3, "Most/All": 0.1}
    waste_co2 = waste_factors[waste_recycling]

    total_co2 = transport_co2 + flight_co2 + energy_co2 + diet_co2 + waste_co2
    
    footprint_data = {
        "total": total_co2,
        "driving": transport_co2,
        "flights": flight_co2,
        "energy": energy_co2,
        "diet": diet_co2
    }

    # --- Results Dashboard ---
    st.divider()
    
    res_1, res_2, res_3 = st.columns(3)
    
    with res_1:
        st.markdown(f'<div class="metric-card"><h3>YOUR IMPACT</h3><h2>{total_co2:.2f} <small>tons</small></h2></div>', unsafe_allow_html=True)
    
    with res_2:
        st.markdown(f'<div class="metric-card"><h3>REGION AVG</h3><h2>{baseline_value:.2f} <small>tons</small></h2></div>', unsafe_allow_html=True)
        
    with res_3:
        diff = total_co2 - baseline_value
        status = "ABOVE" if diff > 0 else "BELOW"
        color = "#ff4b4b" if diff > 0 else "#00f2ff"
        st.markdown(f'<div class="metric-card"><h3>VARIANCE</h3><h2 style="color:{color}">{abs(diff):.2f} <small>{status}</small></h2></div>', unsafe_allow_html=True)

    # --- Visualization ---
    st.subheader("📊 Emission Spectrum")
    breakdown = pd.DataFrame({
        "Category": ["Driving", "Flights", "Energy", "Diet", "Waste"],
        "Emissions": [transport_co2, flight_co2, energy_co2, diet_co2, waste_co2]
    })
    st.bar_chart(breakdown.set_index("Category"), color="#00f2ff")

    # --- AI Insights Section ---
    st.divider()
    st.subheader("🤖 AI Sustainability Uplink")
    
    if st.button("Generate Personalized Strategy"):
        with st.spinner("Analyzing data streams via Gemini AI..."):
            tips = get_gemini_tips(footprint_data, selected_region)
            st.markdown(tips)

    st.sidebar.markdown("---")
    st.sidebar.caption("Powered by Gemini 1.5 Flash • v2.0-Futuristic")

if __name__ == "__main__":
    main()
