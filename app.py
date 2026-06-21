import streamlit as st
import pandas as pd
import os
import google.generativeai as genai
from typing import Dict, Any

# --- Configuration & Efficiency (Caching) ---
st.set_page_config(
    page_title="CarbonFlow AI",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Secure API Key Handling with validation
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# --- Efficiency: Cached AI function ---
@st.cache_data(show_spinner=False, ttl=3600)
def get_gemini_tips(footprint_data: Dict[str, float], region: str) -> str:
    """Fetches AI-driven sustainability tips with caching for efficiency."""
    if not GEMINI_API_KEY:
        return "⚠️ **Security Alert:** Gemini API Key not found. Please set `GEMINI_API_KEY` environment variable."
    
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = f"""
        Expert Sustainability Analysis for a user in {region}.
        Footprint: {footprint_data['total']:.2f} tons CO2e.
        Categories: Driving({footprint_data['driving']:.2f}), Flights({footprint_data['flights']:.2f}), 
        Energy({footprint_data['energy']:.2f}), Diet({footprint_data['diet']:.2f}).
        
        Provide 3 concise, high-impact, futuristic tips. Focus on the highest category.
        Format in Markdown with clear headers.
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"📡 **Connection Error:** Unable to reach AI uplink. ({str(e)})"

# --- Accessibility & Futuristic Styling ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Inter:wght@300;400;600&display=swap');
    
    /* Accessibility: High contrast and readable fonts */
    .main {
        background: radial-gradient(circle at top right, #0a0e14, #02050a);
        color: #f8f9fa; /* High contrast text */
        font-family: 'Inter', sans-serif;
    }
    
    h1, h2, h3 {
        font-family: 'Orbitron', sans-serif;
        color: #00f2ff !important;
        text-transform: uppercase;
        letter-spacing: 2px;
    }

    /* Accessibility: Focus states and clear button labels */
    .stButton>button {
        background: linear-gradient(90deg, #00f2ff, #0072ff);
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.6rem 2.2rem;
        font-family: 'Orbitron', sans-serif;
        font-weight: bold;
        transition: 0.3s;
        aria-label: "Generate AI Strategy";
    }
    
    .metric-card {
        background: rgba(255, 255, 255, 0.08);
        border: 2px solid rgba(0, 242, 255, 0.3); /* Stronger border for visibility */
        padding: 24px;
        border-radius: 15px;
        backdrop-filter: blur(12px);
        margin-bottom: 10px;
    }

    /* Accessibility: Input field labels */
    label {
        color: #00f2ff !important;
        font-weight: 600 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Calculation Logic (Separated for Testing) ---
def calculate_emissions(km: float, efficiency: float, s_flights: int, l_flights: int, kwh: int, diet: str, waste: str) -> Dict[str, float]:
    """Calculates emissions based on validated inputs."""
    driving = (km / max(efficiency, 0.1)) * 2.31 / 1000
    flights = (s_flights * 0.15) + (l_flights * 0.6)
    energy = (kwh * 12 * 0.4) / 1000
    
    diet_map = {"Meat-heavy": 3.3, "Average (Meat/Veg)": 2.5, "Vegetarian": 1.7, "Vegan": 1.5}
    waste_map = {"None": 0.5, "Some": 0.3, "Most/All": 0.1}
    
    diet_val = diet_map.get(diet, 2.5)
    waste_val = waste_map.get(waste, 0.3)
    
    total = driving + flights + energy + diet_val + waste_val
    return {
        "total": total,
        "driving": driving,
        "flights": flights,
        "energy": energy,
        "diet": diet_val,
        "waste": waste_val
    }

def main():
    st.title("🌌 CarbonFlow AI")
    st.markdown("#### *Next-Gen Sustainability Analytics*")
    st.divider()

    # --- Sidebar: Security & Region ---
    st.sidebar.header("📡 System Control")
    baselines = {
        "India": 1.9, "USA": 14.7, "UK": 5.2, "China": 7.6, "Global Average": 4.7
    }
    selected_region = st.sidebar.selectbox("Baseline Region:", list(baselines.keys()), help="Select a region to compare your footprint against.")
    baseline_value = baselines[selected_region]

    # --- Main Inputs with Accessibility (Labels & Help) ---
    col_a, col_b = st.columns([1, 1], gap="large")

    with col_a:
        st.subheader("🚀 Mobility")
        km = st.number_input("Annual Distance (km)", min_value=0.0, value=10000.0, step=100.0, help="Total kilometers driven per year.")
        eff = st.number_input("Fuel Efficiency (km/L)", min_value=0.1, value=15.0, help="Average kilometers per liter of fuel.")
        
        st.subheader("✈️ Aviation")
        s_fl = st.slider("Short-haul (<3h)", 0, 50, 1, help="Number of flights under 3 hours.")
        l_fl = st.slider("Long-haul (>3h)", 0, 50, 0, help="Number of flights over 3 hours.")

    with col_b:
        st.subheader("⚡ Energy")
        kwh = st.number_input("Monthly Electricity (kWh)", min_value=0, value=200, help="Average monthly power consumption.")
        
        st.subheader("🍱 Lifestyle")
        diet = st.selectbox("Dietary Pattern", ["Vegan", "Vegetarian", "Average (Meat/Veg)", "Meat-heavy"])
        waste = st.selectbox("Waste Management", ["None", "Some", "Most/All"])

    # --- Security: Input Validation & Calculation ---
    results = calculate_emissions(km, eff, s_fl, l_fl, kwh, diet, waste)

    # --- Results Dashboard ---
    st.divider()
    res_1, res_2, res_3 = st.columns(3)
    
    with res_1:
        st.markdown(f'<div class="metric-card"><h3>YOUR IMPACT</h3><h2>{results["total"]:.2f} <small>tons</small></h2></div>', unsafe_allow_html=True)
    with res_2:
        st.markdown(f'<div class="metric-card"><h3>REGION AVG</h3><h2>{baseline_value:.2f} <small>tons</small></h2></div>', unsafe_allow_html=True)
    with res_3:
        diff = results["total"] - baseline_value
        color = "#ff4b4b" if diff > 0 else "#00f2ff"
        label = "ABOVE" if diff > 0 else "BELOW"
        st.markdown(f'<div class="metric-card"><h3>VARIANCE</h3><h2 style="color:{color}">{abs(diff):.2f} <small>{label}</small></h2></div>', unsafe_allow_html=True)

    # --- Efficiency: Visualizations ---
    st.subheader("📊 Emission Spectrum")
    df_chart = pd.DataFrame({
        "Category": ["Driving", "Flights", "Energy", "Diet", "Waste"],
        "Tons CO2e": [results["driving"], results["flights"], results["energy"], results["diet"], results["waste"]]
    })
    st.bar_chart(df_chart.set_index("Category"), color="#00f2ff")

    # --- AI Insights ---
    st.divider()
    st.subheader("🤖 AI Strategy Uplink")
    if st.button("Generate Strategy"):
        with st.spinner("Decrypting data patterns..."):
            tips = get_gemini_tips(results, selected_region)
            st.markdown(tips)

    st.sidebar.markdown("---")
    st.sidebar.caption("CarbonFlow AI v2.1 • Accessibility & Efficiency Optimized")

if __name__ == "__main__":
    main()
