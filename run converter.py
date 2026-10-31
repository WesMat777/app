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
st.markdown("Streamlined pacing, GAP calculations, and unit conversions for modern runners.")

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
    """
    Calculate the Grade-Adjusted Pace adjustment factor.
    Using a standard curve approximation where positive grade slows you down.
    A common physiologic curve (like Strava's GAP model) approximates that 
    each 1% of positive gradient increases effort/equivalent flat pace by roughly 3.5% to 4%.
    """
    # grade_percent is given as an integer or float (e.g. 5 for 5%)
    g = grade_percent / 100.0
    if g >= 0:
        # Positive grade: you run slower on an incline, so your GAP (flat equivalent) 
        # is faster than your actual watch pace. watch_pace = gap_pace * factor -> gap_pace = watch_pace / factor
        # Curve approximation for cost of grade
        factor = 1.0 + (3.5 * g) + (10.0 * g**2)
    else:
        # Negative grade (downhill) adjustment (limited to prevent infinite speed scaling)
        factor = max(0.6, 1.0 + (2.0 * g) - (5.0 * g**2))
    return factor

# --- MAIN NAVIGATION TABS ---
tab1, tab2, tab3 = st.tabs([
    "⏱️ Race Time to Pace Calculator", 
    "⛰️ Grade-Adjusted Pace (GAP) Converter", 
    "🔄 Pace Unit Flippers"
])

# ==========================================
# TAB 1: RACE TIME TO PACE CALCULATOR
# ==========================================
with tab1:
    st.header("Race Time to Pace Calculator")
    st.markdown("Determine your target pacing and generate milestone split tables for your next race.")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Race Settings")
        # Distance Selection
        distance_option = st.selectbox(
            "Select Race Distance",
            ["5k", "10k", "Half Marathon (21.0975 km)", "Full Marathon (42.195 km)", "Custom"]
        )
        
        # Determine distance in kilometers and miles based on preset selections
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
            # Custom distance inputs
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
        # Time inputs spread across three columns for mobile-responsiveness
        t_col1, t_col2, t_col3 = st.columns(3)
        with t_col1:
            h_input = st.number_input("Hours", min_value=0, max_value=24, value=0, step=1)
        with t_col2:
            m_input = st.number_input("Minutes", min_value=0, max_value=59, value=25, step=1)
        with t_col3:
            s_input = st.number_input("Seconds", min_value=0, max_value=59, value=0, step=1)

    with col2:
        total_seconds = time_to_seconds(h_input, m_input, s_input)
        
        if total_seconds > 0:
            # Pace Calculations
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
            
            # Generate split data dynamically
            split_unit = st.radio("View splits by:", ["Kilometers", "Miles"], horizontal=True)
            splits_data = []
            
            if split_unit == "Kilometers":
                full_units = math.floor(dist_km)
                for i in range(1, full_units + 1):
                    splits_data.append({
                        "Split": f"KM {i}",
                        "Cumulative Time": seconds_to_hhmmss(sec_per_km * i)
                    })
                # Add fractional final split if necessary
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
    st.markdown(
        "Estimate your equivalent flat-ground performance when running up or down hills. "
        "Useful for treadmill incline workouts and trail runs."
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Current Effort Context")
        gap_unit = st.radio("Pace Input Unit", ["min/km", "min/mile"], horizontal=True)
        
        # Pace inputs
        g_col1, g_col2 = st.columns(2)
        with g_col1:
            watch_min = st.number_input("Watch Minutes", min_value=2, max_value=30, value=6, step=1, key="gap_m")
        with g_col2:
            watch_sec = st.number_input("Watch Seconds", min_value=0, max_value=59, value=0, step=1, key="gap_s")
            
        # Incline / Gradient slider
        grade = st.slider("Terrain Gradient / Incline (%)", min_value=-10.0, max_value=15.0, value=5.0, step=0.5)
        
    with col2:
        st.subheader("Calculated Flat Equivalent (GAP)")
        
        # Total seconds for watch pace
        watch_seconds_total = (watch_min * 60) + watch_sec
        
        if watch_seconds_total > 0:
            # GAP calculation logic using physics approximation factor
            adjustment_factor = calculate_gap_factor(grade)
            gap_seconds_total = watch_seconds_total / adjustment_factor
            
            formatted_gap = seconds_to_hhmmss(gap_seconds_total)
            
            st.metric(
                label=f"Equivalent Flat Pace ({gap_unit})",
                value=f"{formatted_gap} /{gap_unit.split('/')[-1]}"
            )
            
            # Physics breakdown explanation text
            st.info(
                f"💡 **Pacing Insight:** Running at a **{grade}%** incline at a {watch_min}:{watch_sec:02d} pace "
                f"demands an aerobic effort equivalent to running a flat **{formatted_gap}** pace."
            )
        else:
            st.error("Please enter a valid base watch pace.")

# ==========================================
# TAB 3: PACE UNIT FLIPPERS
# ==========================================
with tab3:
    st.header("Pace & Speed Unit Flippers")
    st.markdown("Instantly convert variables between imperial and metric running metrics.")
    
    flip_col1, flip_col2 = st.columns(2)
    
    # Sub-section 1: min/mile <-> min/km
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
            # 1 mile = 1.609344 km -> pace becomes faster per km
            output_seconds = total_flip_seconds / 1.609344
            st.success(f"🎯 **Converted Pace:** {seconds_to_hhmmss(output_seconds)} /km")
        else:
			# 1 km = 0.621371 miles -> pace becomes slower per mile
			output_seconds = total_flip_seconds * 1.609344
			st.success(f"🎯 Converted Pace: {seconds_to_hhmmss(output_seconds)} /mile")
	
	# Sub-section 2: Treadmill Speed <-> Running Pace
		with flip_col2:
			st.subheader("🏃‍♂️ Treadmill Speed ↔️ Running Pace")
			treadmill_mode = st.selectbox("Conversion Mode:", ["Speed to Pace", "Pace to Speed"])
	
		if treadmill_mode == "Speed to Pace":
			speed_unit = st.radio("Treadmill Speed Unit", ["mph", "kph"], horizontal=True)
			speed_val = st.number_input("Treadmill Speed Setting", min_value=1.0, max_value=25.0, value=6.0, step=0.1)
			if speed_val > 0:
				if speed_unit == "mph":
				# Speed in mph to min/mile
				seconds_per_mile = 3600 / speed_val
				seconds_per_km = seconds_per_mile / 1.609344
			else:
				# Speed in kph to min/km
				seconds_per_km = 3600 / speed_val
				seconds_per_mile = seconds_per_km * 1.609344
				st.write(f"⏱️ Mile Pace: {seconds_to_hhmmss(seconds_per_mile)} /mile")
				st.write(f"⏱️ Kilometer Pace: {seconds_to_hhmmss(seconds_per_km)} /km")
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
						st.write(f"⚡ Treadmill Speed: {mph_speed:.1f} mph")
						st.write(f"⚡ Treadmill Speed: {kph_speed:.1f} kph")