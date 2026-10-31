import streamlit as st
import pandas as pd
import math

# Set page configuration for a modern, wide layout
st.set_page_config(
    page_title="The Ultimate AI Running Calculator",
    page_icon="🏃‍♂️",
    layout="wide"
)

# App Title & Header
st.title("🏃‍♂️ The Ultimate AI Running Calculator & Pace Converter")
st.markdown("Streamlined pacing, GAP calculations, unit conversions, and VO2 Max metrics for modern runners.")

# --- HELPER FUNCTIONS FOR CALCULATIONS ---

def time_to_seconds(hours, minutes, seconds):
    """Convert hours, minutes, seconds into total seconds."""
    return (hours * 3600) + (minutes * 60) + seconds

def seconds_to_hhmmss(total_seconds):
    """Convert total seconds back into a formatted HH:MM:SS string."""
    if total_seconds < 0:
        return "00:00"
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    return f"{minutes:02d}:{seconds:02d}"

def calculate_gap_factor(grade_percent):
    """Calculate the Grade-Adjusted Pace adjustment factor."""
    g = grade_percent / 100.0
    if g >= 0:
        factor = 1.0 + (3.5 * g) + (10.0 * g**2)
    else:
        factor = max(0.6, 1.0 + (2.0 * g) - (5.0 * g**2))
    return factor

def estimate_vdot(distance_meters, time_minutes):
    """Estimate VDOT / VO2 Max using the standard Daniels and Gilbert formula."""
    v = distance_meters / time_minutes
    o2_cost = -4.60 + 0.182258 * v + 0.000104 * v**2
    fraction = 0.8 + 0.2989558 * math.exp(-0.1932605 * time_minutes) + 0.1418958 * math.exp(-0.0125916 * time_minutes)
    vdot = o2_cost / fraction
    return round(vdot, 2)

# --- MAIN NAVIGATION TABS ---
tab1, tab2, tab3, tab4 = st.tabs([
    "⏱️ Race Time to Pace Calculator", 
    "⛰️ Grade-Adjusted Pace (GAP) Converter", 
    "🔄 Pace Unit Flippers",
    "🫁 VO2 Max & VDOT Estimator"
])

# ==========================================
# TAB 1: RACE TIME TO PACE CALCULATOR
# ==========================================
with tab1:
    st.header("Race Time to Pace Calculator")
    st.markdown("Determine your target pacing and generate milestone split tables for your next race.")
    
    col1, col2 = st.columns()
    
    with col1:
        st.subheader("Race Settings")
        distance_option = st.selectbox(
            "Select Race Distance",
            ["5k", "10k", "Half Marathon (21.0975 km)", "Full Marathon (42.195 km)", "Custom"],
            key="race_dist_select"
        )
        
        if distance_option == "5k":
            dist_km = 5.0
            dist_mi = 5.0 / 1.609344
        elif distance_option == "10k":
            dist_km = 10.0
            dist_mi = 10.0 / 1.609344
        elif distance_option == "Half Marathon (21.0975 km)":
            dist_km = 21.0975
            dist_mi = 13.1094
        elif distance_option == "Full Marathon (42.195 km)":
            dist_km = 42.195
            dist_mi = 26.2188
        else:
            dist_unit = st.radio("Custom Distance Unit", ["Kilometers", "Miles"], horizontal=True)
            custom_dist = st.number_input("Enter Distance", min_value=0.1, value=5.0, step=0.1)
            if dist_unit == "Kilometers":
                dist_km = custom_dist
                dist_mi = custom_dist / 1.609344
            else:
                dist_mi = custom_dist
                dist_km = custom_dist * 1.609344

        st.write("---")
        st.subheader("Target Time")
        t_col1, t_col2, t_col3 = st.columns(3)
        with t_col1:
            h_input = st.number_input("Hours", min_value=0, max_value=24, value=0, step=1, key="race_h")
        with t_col2:
            m_input = st.number_input("Minutes", min_value=0, max_value=59, value=25, step=1, key="race_m")
        with t_col3:
            s_input = st.number_input("Seconds", min_value=0, max_value=59, value=0, step=1, key="race_s")

    with col2:
        total_seconds = time_to_seconds(h_input, m_input, s_input)
        
        if total_seconds > 0:
            sec_per_km = total_seconds / dist_km
            sec_per_mi = total_seconds / dist_mi
            
            st.subheader("Required Paces")
            p_col1, p_col2 = st.columns(2)
            with p_col1:
                st.metric("Pace per Kilometer", f"{seconds_to_hhmmss(sec_per_km)} /km")
            with p_col2:
                st.metric("Pace per Mile", f"{seconds_to_hhmmss(sec_per_mi)} /mile")
            
            st.write("---")
            st.subheader("Even Split Tables")
            
            split_unit = st.radio("View splits by:", ["Kilometers", "Miles"], horizontal=True)
            splits_data = []
            
            if split_unit == "Kilometers":
                full_units = math.floor(dist_km)
                for i in range(1, full_units + 1):
                    splits_data.append({
                        "Split": f"KM {i}",
                        "Cumulative Time": seconds_to_hhmmss(sec_per_km * i)
                    })
                if dist_km > full_units:
                    splits_data.append({
                        "Split": f"Finish ({dist_km:.2f} km)",
                        "Cumulative Time": seconds_to_hhmmss(total_seconds)
                    })
            else:
                full_units = math.floor(dist_mi)
                for i in range(1, full_units + 1):
                    splits_data.append({
                        "Split": f"Mile {i}",
                        "Cumulative Time": seconds_to_hhmmss(sec_per_mi * i)
                    })
                if dist_mi > full_units:
                    splits_data.append({
                        "Split": f"Finish ({dist_mi:.2f} miles)",
                        "Cumulative Time": seconds_to_hhmmss(total_seconds)
                    })
            
            df_splits = pd.DataFrame(splits_data)
            st.dataframe(df_splits, use_container_width=True, hide_index=True)
        else:
            st.warning("Please enter a target time greater than 0 to generate pacing profiles.")

# ==========================================
# TAB 2: GRADE-ADJUSTED PACE (GAP) CONVERTER
# ==========================================
with tab2:
    st.header("Grade-Adjusted Pace (GAP) Converter")
    st.markdown("Estimate your equivalent flat-ground performance when running up or down hills.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Current Effort Context")
        gap_unit = st.radio("Pace Input Unit", ["min/km", "min/mile"], horizontal=True)
        
        g_col1, g_col2 = st.columns(2)
        with g_col1:
            watch_min = st.number_input("Watch Minutes", min_value=2, max_value=30, value=6, step=1, key="gap_m")
        with g_col2:
            watch_sec = st.number_input("Watch Seconds", min_value=0, max_value=59, value=0, step=1, key="gap_s")
            
        grade = st.slider("Terrain Gradient / Incline (%)", min_value=-10.0, max_value=15.0, value=5.0, step=0.5)
        
    with col2:
        st.subheader("Calculated Flat Equivalent (GAP)")
        watch_seconds_total = (watch_min * 60) + watch_sec
        
        if watch_seconds_total > 0:
            adjustment_factor = calculate_gap_factor(grade)
            gap_seconds_total = watch_seconds_total / adjustment_factor
            formatted_gap = seconds_to_hhmmss(gap_seconds_total)
            
            st.metric(
                label=f"Equivalent Flat Pace ({gap_unit})",
                value=f"{formatted_gap} /{gap_unit.split('/')[-1]}"
            )
            
            st.info(f"Pacing Insight: Running at a {grade}% incline at a {watch_min}:{watch_sec:02d} pace demands an aerobic effort equivalent to running a flat {formatted_gap} pace.")
        else:
            st.error("Please enter a valid base watch pace.")

# ==========================================
# TAB 3: PACE UNIT FLIPPERS
# ==========================================
with tab3:
    st.header("Pace & Speed Unit Flippers")
    st.markdown("Instantly convert variables between imperial and metric running metrics.")
    
    flip_col1, flip_col2 = st.columns(2)
    
    with flip_col1:
        st.subheader("🔄 Metric & Imperial Pace Flipper")
        f_unit = st.selectbox("I want to convert from:", ["min/mile to min/km", "min/km to min/mile"])
        
        p_col1, p_col2 = st.columns(2)
        with p_col1:
            input_min = st.number_input("Minutes", min_value=2, max_value=30, value=5, step=1, key="flip_m")
        with p_col2:
            input_sec = st.number_input("Seconds", min_value=0, max_value=59, value=30, step=1, key="flip_s")
            
        total_flip_seconds = (input_min * 60) + input_sec
        
        if f_unit == "min/mile to min/km":
            output_seconds = total_flip_seconds / 1.609344
            st.success(f"Converted Pace: {seconds_to_hhmmss(output_seconds)} /km")
        else:
            output_seconds = total_flip_seconds * 1.609344
            st.success(f"Converted Pace: {seconds_to_hhmmss(output_seconds)} /mile")
            
    with flip_col2:
        st.subheader("🏃‍♂️ Treadmill Speed ↔️ Running Pace")
        treadmill_mode = st.selectbox("Conversion Mode:", ["Speed to Pace", "Pace to Speed"])
        
        if treadmill_mode == "Speed to Pace":
            speed_unit = st.radio("Treadmill Speed Unit", ["mph", "kph"], horizontal=True)
            speed_val = st.number_input("Treadmill Speed Setting", min_value=1.0, max_value=25.0, value=6.0, step=0.1)
            
            if speed_val > 0:
                if speed_unit == "mph":
                    seconds_per_mile = 3600 / speed_val
                    seconds_per_km = seconds_per_mile / 1.609344
                else:
                    seconds_per_km = 3600 / speed_val
                    seconds_per_mile = seconds_per_km * 1.609344
                    
                st.write(f"Mile Pace: {seconds_to_hhmmss(seconds_per_mile)} /mile")
st.write(f"Kilometer Pace: {seconds_to_hhmmss(seconds_per_km)} /km")
else:
pace_unit_target = st.radio("Your Pace Unit Type", ["min/mile", "min/km"], horizontal=True)
tc_col1, tc_col2 = st.columns(2)
with tc_col1:
t_min = st.number_input("Minutes", min_value=2, max_value=30, value=8, step=1, key="t_m")
with tc_col2:
t_sec = st.number_input("Seconds", min_value=0, max_value=59, value=0, step=1, key="t_s")
total_t_seconds = (t_min * 60) + t_sec
if total_t_seconds > 0:
if pace_unit_target == "min/mile":
mph_speed = 3600 / total_t_seconds
kph_speed = mph_speed * 1.609344
else:
kph_speed = 3600 / total_t_seconds
mph_speed = kph_speed / 1.609344
st.write(f"Treadmill Speed: {mph_speed:.1f} mph")
st.write(f"Treadmill Speed: {kph_speed:.1f} kph")

==========================================


TAB 4: VO2 MAX & VDOT ESTIMATOR


==========================================

with tab4:
st.header("🫁 VO2 Max & VDOT Cardiorespiratory Estimator")
st.markdown("Estimate your maximum oxygen uptake based on your training or race performances.")
method = st.radio("Choose Estimation Method:", ["Recent Race Performance (VDOT)", "Cooper 12-Minute Test"], horizontal=True)
v_col1, v_col2 = st.columns(2)
if method == "Recent Race Performance (VDOT)":
with v_col1:
st.subheader("Performance Inputs")
v_dist_opt = st.selectbox("Race Distance", ["5k", "10k", "Half Marathon", "Full Marathon"])
if v_dist_opt == "5k":
m_distance = 5000
elif v_dist_opt == "10k":
m_distance = 10000
elif v_dist_opt == "Half Marathon":
m_distance = 21097.5
else:
m_distance = 42195
st.write("Race Finish Time:")
vt_col1, vt_col2, vt_col3 = st.columns(3)
with vt_col1:
v_h = st.number_input("Hours", min_value=0, value=0, key="vdot_h")
with vt_col2:
v_m = st.number_input("Minutes", min_value=0, max_value=59, value=22, key="vdot_m")
with vt_col3:
v_s = st.number_input("Seconds", min_value=0, max_value=59, value=30, key="vdot_s")
total_v_minutes = (time_to_seconds(v_h, v_m, v_s)) / 60.0
with v_col2:
st.subheader("Your Aerobic Profile")
if total_v_minutes > 0:
vdot_score = estimate_vdot(m_distance, total_v_minutes)
st.metric("Estimated VDOT / VO2 Max", f"{vdot_score} ml/kg/min")
st.caption("Calculated using the Jack Daniels VDOT oxygen-kinetics algorithm.")
if vdot_score < 35:
cat = "Fitness Builder"
elif vdot_score < 45:
cat = "Intermediate Runner"
elif vdot_score < 55:
cat = "Advanced Competitor"
else:
cat = "Elite Tier"
st.success(f"Aerobic Capacity Category: {cat}")
else:
st.warning("Please provide a finishing time greater than 0.")
else:
with v_col1:
st.subheader("Cooper Test Inputs")
cooper_unit = st.radio("Distance Unit", ["Meters", "Miles"], horizontal=True)
cooper_dist = st.number_input("Distance Covered in 12 Minutes", min_value=100.0, value=2400.0, step=50.0)
with v_col2:
st.subheader("Cooper Test Result")
if cooper_unit == "Meters":
cooper_vo2 = (cooper_dist - 504.9) / 44.73
else:
cooper_vo2 = (35.97 * cooper_dist) - 11.29
st.metric("Estimated VO2 Max", f"{round(cooper_vo2, 1)} ml/kg/min")
st.info("The Cooper 12-minute track metric evaluates VO2 max based on systemic oxygen consumption curves at maximum sustained velocity.")