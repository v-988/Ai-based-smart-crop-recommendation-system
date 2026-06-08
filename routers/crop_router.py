from fastapi import APIRouter
from fastapi.responses import JSONResponse
import requests
import pandas as pd
from datetime import datetime
import os
import rasterio

from main import (
    soil_avg_df, district_latlon, model,
    tn_crop_prod_df, agri_yield_df, rainfall_df,
    land_use_df, crop_history_df
)

router = APIRouter()

# ==================== HELPER FUNCTION - FULL LOGIC ====================
async def process_location(lat: float, lon: float, city_name: str = None):
    print(f"Processing location: {lat}, {lon}")

    # Weather
    weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={os.getenv('OPENWEATHER_API_KEY')}&units=metric"
    try:
        response = requests.get(weather_url)
        response.raise_for_status()
        weather_data = response.json()
        temp = weather_data["main"]["temp"]
        humidity = weather_data["main"]["humidity"]
        description = weather_data["weather"][0]["description"]
        city = city_name or weather_data.get("name", "Your location")
        weather_info = {"city": city, "temperature": temp, "humidity": humidity, "description": description}
    except:
        return JSONResponse({"status": "error", "message": "Weather API error"}, status_code=500)
    # Rainfall estimation
    rainfall = weather_data.get('rain', {}).get('1h', 0.0)
    if rainfall == 0:
        desc_lower = description.lower()
        main_cond = weather_data["weather"][0]["main"].lower()
        if 'rain' in main_cond or 'drizzle' in desc_lower:
            if 'light' in desc_lower or 'drizzle' in desc_lower:
                rainfall = 1.0
            elif 'moderate' in desc_lower:
                rainfall = 5.0
            elif 'heavy' in desc_lower or 'shower' in desc_lower:
                rainfall = 15.0
            else:
                rainfall = 2.0
        elif 'thunderstorm' in desc_lower:
            rainfall = 20.0

    # AgroMonitoring soil
    soil_info = {"ph": 7.0, "n": 200, "p": 40, "k": 160, "soil_temperature": 25.0, "soil_moisture": 30.0, "soil_type": "Unknown"}
    try:
        soil_url = f"https://api.agromonitoring.com/agro/1.0/soil?lat={lat}&lon={lon}&appid={os.getenv('AGROMONITORING_APPID')}"
        soil_response = requests.get(soil_url)
        soil_response.raise_for_status()
        soil_data = soil_response.json()
        soil_moisture = soil_data.get('moisture', 30.0)
        soil_temp_k = soil_data.get('t0', 298.15)
        soil_temp = soil_temp_k - 273.15
        soil_info = {
            "ph": round(7.0, 2),
            "n": round(200, 1),
            "p": round(40, 1),
            "k": round(160, 1),
            "soil_temperature": round(soil_temp, 1),
            "soil_moisture": round(soil_moisture, 1),
            "soil_type": "Unknown"
        }
        print(f"AgroMonitoring: Temp {soil_info['soil_temperature']}°C, Moisture {soil_info['soil_moisture']}%")
    except Exception as e:
        print("AgroMonitoring error:", str(e))

    # HWSD soil code & name
    try:
        with rasterio.open("datasets/hwsd/hwsd.bil") as src:
            row, col = src.index(lon, lat)
            soil_code = src.read(1, window=((row, row+1), (col, col+1)))[0][0]
            print(f"HWSD code: {soil_code}")
        lookup_df = pd.read_csv("datasets/hwsd/GLOBAL_Soil.txt")
        soil_name = lookup_df[lookup_df['VALUE'] == soil_code]['NAME'].values
        soil_type = soil_name[0] if len(soil_name) > 0 else "Unknown"
        print(f"Soil type: {soil_type}")
        soil_info["soil_type"] = soil_type
    except Exception as e:
        print("HWSD error:", str(e))
        soil_info["soil_type"] = "Unknown"

    # District matching & nutrient override
    n, p, k, ph = 200, 40, 160, 7.0
    closest_district = None
    if soil_avg_df is not None:
        try:
            min_dist = float('inf')
            for dist_name, (d_lat, d_lon) in district_latlon.items():
                dist = ((d_lat - lat)**2 + (d_lon - lon)**2)**0.5
                if dist < min_dist:
                    min_dist = dist
                    closest_district = dist_name
            if closest_district and closest_district.lower() == "avadi":
                closest_district = "Chennai"
            district_row = soil_avg_df[soil_avg_df['District'].str.lower() == closest_district.lower()]
            if not district_row.empty:
                n = district_row['avg_n'].values[0]
                p = district_row['avg_p'].values[0]
                k = district_row['avg_k'].values[0]
                ph = district_row['avg_ph'].values[0]
                soil_info["n"] = round(n, 1)
                soil_info["p"] = round(p, 1)
                soil_info["k"] = round(k, 1)
                soil_info["ph"] = round(ph, 2)
                print(f"District {closest_district}: N {soil_info['n']}, P {soil_info['p']}, K {soil_info['k']}, pH {soil_info['ph']}")
        except Exception as e:
            print("District error:", str(e))

    # Season adjustment
    month = datetime.now().month
    if month in [10, 11, 12, 1, 2, 3]:
        rainfall *= 0.4
    elif month in [6, 7, 8, 9]:
        rainfall *= 2.0
    else:
        rainfall *= 0.8
    print(f"Final rainfall: {rainfall} mm")

    # NEW: Collect district insights from all uploaded files
    district_insights = {"district": closest_district or "Unknown"}

    # From rainfall_data.csv
    if rainfall_df is not None and closest_district:
        try:
            # Use correct column: Unnamed: 1 (district names)
            district_col = 'Unnamed: 1'
            print(f"Using rainfall district column: '{district_col}'")
            row = rainfall_df[rainfall_df[district_col].astype(str).str.strip().str.lower() == closest_district.lower()]
            if not row.empty:
                current_month_abbr = datetime.now().strftime("%b").upper()  # e.g. "JAN"
                # Find columns containing current month + Normal/Actual/Dev
                normal_col = next((col for col in row.columns if current_month_abbr in col and 'Normal' in col), None)
                actual_col = next((col for col in row.columns if current_month_abbr in col and 'Actual' in col), None)
                dev_col = next((col for col in row.columns if current_month_abbr in col and '% Dev' in col), None)

                if normal_col:
                    district_insights["normal_rainfall_mm"] = row[normal_col].values[0]
                if actual_col:
                    district_insights["actual_rainfall_mm"] = row[actual_col].values[0]
                if dev_col:
                    district_insights["rainfall_dev_percent"] = row[dev_col].values[0]
            else:
                print(f"No row found for district '{closest_district}' in rainfall data")
        except Exception as e:
            print("Rainfall lookup error:", str(e))
            print("Available columns:", rainfall_df.columns.tolist())

    # From Tamilnadu Crop-Production.csv and Tamilnadu agriculture yield data.csv — top crops by area
    top_crops = []
    if tn_crop_prod_df is not None and closest_district:
        df = tn_crop_prod_df[tn_crop_prod_df['District'].str.strip().str.lower() == closest_district.lower()]
        if not df.empty:
            top_crops = df.groupby('Crop')['Area'].sum().nlargest(5).index.tolist()
    if agri_yield_df is not None and closest_district:
        df = agri_yield_df[agri_yield_df['District_Name'].str.strip().str.lower() == closest_district.lower()]
        if not df.empty:
            extra_top = df.groupby('Crop')['Area'].sum().nlargest(5).index.tolist()
            top_crops = list(set(top_crops + extra_top))[:5]
    district_insights["top_crops"] = top_crops

    # From land_use.csv — cultivable area
    if land_use_df is not None and closest_district:
        try:
            # Use correct column: Unnamed: 1 (district names)
            district_col = 'Unnamed: 1'
            print(f"Using land use district column: '{district_col}'")
            row = land_use_df[land_use_df[district_col].astype(str).str.strip().str.lower() == closest_district.lower()]
            if not row.empty:
                # Adjust column names based on your file (look at printed columns)
                # These are examples — replace with actual names from "Land use columns:" print
                district_insights["net_sown_area_ha"] = row.get('Net area sown', pd.Series([None])).values[0]
                district_insights["fallow_lands_ha"] = row.get('Fallow lands other than current fallow', pd.Series([None])).values[0]
            else:
                print(f"No row found for district '{closest_district}' in land use data")
        except Exception as e:
            print("Land use lookup error:", str(e))
            print("Available columns:", land_use_df.columns.tolist())

    # From crop_production_history.csv — historical top crops (example: top 5 by recent years)
    historical_top = []
    if crop_history_df is not None:
        recent_cols = ['2017-18', '2018-19', '2019-20']  # adjust based on your columns
        if all(col in crop_history_df.columns for col in recent_cols):
            crop_history_df['recent_avg'] = crop_history_df[recent_cols].mean(axis=1, numeric_only=True)
            historical_top = crop_history_df.nlargest(5, 'recent_avg')['Crop'].tolist()
    district_insights["historical_top_crops"] = historical_top

    # Predict crop + FULL TAMIL NADU LOGIC (different crops for different districts/villages)
    crop_prediction = None
    if model is not None:
        try:
            input_df = pd.DataFrame([[n, p, k, temp, humidity, ph, rainfall]],
                                    columns=['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall'])

            probabilities = model.predict_proba(input_df)[0]
            top_indices = probabilities.argsort()[-3:][::-1]
            all_crops = model.classes_

            top_crops_list = []
            for idx in top_indices:
                crop_name = all_crops[idx]
                conf = round(probabilities[idx] * 100, 1)
                top_crops_list.append({
                    "crop": crop_name.capitalize(),
                    "confidence": conf
                })

            # Priority 1: Use real district top crops & historical crops (this makes it different for every place)
            district_top = district_insights.get("top_crops", []) + district_insights.get("historical_top_crops", [])
            if district_top:
                for d_crop in district_top[:3]:
                    top_crops_list.insert(0, {
                        "crop": d_crop.capitalize(),
                        "confidence": 82
                    })

            # Only if soil is extremely poor → terrace crops (very rare case)
            soil_moisture = soil_info.get("soil_moisture", 30)
            if soil_moisture < 5:
                top_crops_list = [
                    {"crop": "Tomato", "confidence": 82},
                    {"crop": "Brinjal", "confidence": 78},
                    {"crop": "Drumstick", "confidence": 75}
                ]

            # Final structure (keeps old key so no error)
            crop_prediction = {
                "recommended_crops": top_crops_list[:3],
                "recommended_crop": top_crops_list[0]["crop"],   # ← This key is used by fertilizer, profit etc.
                "main_crop": top_crops_list[0]["crop"],
                "confidence": top_crops_list[0]["confidence"]
            }

            print(f"✅ Recommended for this place: {crop_prediction['recommended_crop']} (Top 3: {[c['crop'] for c in crop_prediction['recommended_crops']]})")

        except Exception as e:
            print("Prediction error:", str(e))

    # ←←← Everything below this line remains the same (fertilizer, irrigation, harvest, profit, etc.)
    # Yield estimation (simple average from agri_yield_df)
    estimated_yield = "Medium"  # default
    yield_value = "N/A"

    if agri_yield_df is not None and crop_prediction and closest_district:
        crop_name = crop_prediction["recommended_crop"].lower()
        district_data = agri_yield_df[
            (agri_yield_df['District_Name'].str.lower() == closest_district.lower()) &
            (agri_yield_df['Crop'].str.lower().str.contains(crop_name))
        ]
        if not district_data.empty:
            avg_prod = district_data['Production'].mean()
            avg_area = district_data['Area'].mean()
            yield_value = round(avg_prod / avg_area, 1) if avg_area > 0 else "N/A"
            estimated_yield = "High" if yield_value > 2 else "Medium" if yield_value > 1 else "Low"

    district_insights["estimated_yield"] = estimated_yield
    district_insights["yield_value_tonnes_ha"] = yield_value
   
    # Crop-specific fertilizer recommendation (amount in kg/ha and timing)
    fertilizer_advice = "Soil NPK levels appear balanced. No major adjustment needed."

    if closest_district and crop_prediction:
        crop_name = crop_prediction["recommended_crop"].lower()
        
        # Crop-specific NPK requirements (approximate kg/ha) and timing
        # Source: TNAU Agritech Portal, ICAR, Tamil Nadu Agriculture Department guidelines
        crop_requirements = {
            "muskmelon": {
                "n_req": 80, "p_req": 60, "k_req": 30,
                "timing": "Basal: NPK 40:60:30 kg/ha + FYM 20 t/ha. Top dress N 40 kg/ha at 30 days after sowing."
            },
            "rice": {
                "n_req": 120, "p_req": 60, "k_req": 60,
                "timing": "Basal: NPK 60:60:60 kg/ha. Top dress N 60 kg/ha in two splits (tillering & panicle initiation)."
            },
            "maize": {
                "n_req": 120, "p_req": 60, "k_req": 60,
                "timing": "Basal: NPK 60:60:60 kg/ha. Top dress N 60 kg/ha at knee-high stage."
            },
            "chickpea": {
                "n_req": 25, "p_req": 50, "k_req": 25,
                "timing": "Basal: NPK 25:50:25 kg/ha. No top dressing needed (legume fixes N)."
            },
            "kidneybeans": {
                "n_req": 20, "p_req": 60, "k_req": 40,
                "timing": "Basal: NPK 20:60:40 kg/ha. No top dressing needed."
            },
            "pigeonpeas": {
                "n_req": 25, "p_req": 50, "k_req": 25,
                "timing": "Basal: NPK 25:50:25 kg/ha. No top dressing needed."
            },
            "mungbean": {
                "n_req": 20, "p_req": 50, "k_req": 20,
                "timing": "Basal: NPK 20:50:20 kg/ha. No top dressing needed."
            },
            "blackgram": {
                "n_req": 25, "p_req": 50, "k_req": 25,
                "timing": "Basal: NPK 25:50:25 kg/ha. No top dressing needed."
            },
            "lentil": {
                "n_req": 20, "p_req": 50, "k_req": 20,
                "timing": "Basal: NPK 20:50:20 kg/ha. No top dressing needed."
            },
            "pomegranate": {
                "n_req": 100, "p_req": 50, "k_req": 100,
                "timing": "Basal: NPK 50:50:50 kg/ha. Top dress N & K in 3 splits at flowering and fruiting."
            },
            "banana": {
                "n_req": 200, "p_req": 60, "k_req": 300,
                "timing": "Basal: NPK 50:60:100 kg/ha. Top dress N & K in 5 splits every 45 days."
            },
            "mango": {
                "n_req": 100, "p_req": 50, "k_req": 100,
                "timing": "Basal: NPK 50:50:50 kg/ha. Top dress N & K after fruit set."
            },
            "grapes": {
                "n_req": 80, "p_req": 40, "k_req": 120,
                "timing": "Basal: NPK 40:40:60 kg/ha. Top dress N & K at flowering and berry development."
            },
            "watermelon": {
                "n_req": 100, "p_req": 50, "k_req": 80,
                "timing": "Basal: NPK 50:50:40 kg/ha. Top dress N 50 kg/ha at vine growth."
            },
            "apple": {
                "n_req": 70, "p_req": 50, "k_req": 100,
                "timing": "Basal: NPK 35:50:50 kg/ha. Top dress N & K at fruit set."
            },
            "orange": {
                "n_req": 120, "p_req": 60, "k_req": 100,
                "timing": "Basal: NPK 60:60:50 kg/ha. Top dress N & K in 3 splits."
            },
            "papaya": {
                "n_req": 150, "p_req": 60, "k_req": 120,
                "timing": "Basal: NPK 75:60:60 kg/ha. Top dress N & K every 2 months."
            },
            "coconut": {
                "n_req": 500, "p_req": 320, "k_req": 1200,
                "timing": "Basal: NPK 500:320:1200 kg/ha per hectare. Apply in 3 splits annually."
            },
            "cotton": {
                "n_req": 120, "p_req": 60, "k_req": 60,
                "timing": "Basal: NPK 60:60:60 kg/ha. Top dress N in 2 splits at squaring and boll formation."
            },
            "jute": {
                "n_req": 80, "p_req": 40, "k_req": 40,
                "timing": "Basal: NPK 40:40:40 kg/ha. Top dress N 40 kg/ha at 30 days."
            },
            "coffee": {
                "n_req": 100, "p_req": 40, "k_req": 100,
                "timing": "Basal: NPK 50:40:50 kg/ha. Top dress N & K at flowering."
            }
        }

        if crop_name in crop_requirements:
            req = crop_requirements[crop_name]
            n_req = req["n_req"]
            p_req = req["p_req"]
            k_req = req["k_req"]
            timing = req["timing"]

            advice_parts = []
            if n < n_req - 20:
                advice_parts.append(f"Low Nitrogen (N = {n}). Increase N by 20-30 kg/ha.")
            elif n > n_req + 20:
                advice_parts.append(f"High Nitrogen (N = {n}). Reduce N by 20 kg/ha to avoid excess growth.")

            if p < p_req - 10:
                advice_parts.append(f"Low Phosphorus (P = {p}). Increase P by 10-20 kg/ha.")
            elif p > p_req + 10:
                advice_parts.append(f"High Phosphorus (P = {p}). No additional P needed.")

            if k < k_req - 20:
                advice_parts.append(f"Low Potassium (K = {k}). Increase K by 20-30 kg/ha.")
            elif k > k_req + 20:
                advice_parts.append(f"High Potassium (K = {k}). No additional K needed.")

            fertilizer_advice = f"For {crop_prediction['recommended_crop'].capitalize()}: {timing} "
            if advice_parts:
                fertilizer_advice += "Adjustments: " + " ".join(advice_parts)
            else:
                fertilizer_advice += "NPK levels are optimal. No adjustments needed."

        else:
            fertilizer_advice = f"For {crop_prediction['recommended_crop'].capitalize()}: Use general NPK 80:40:60 kg/ha. Consult local agriculture officer for exact dose."

    district_insights["fertilizer_advice"] = fertilizer_advice

    
    # Irrigation frequency & amount (farmer-friendly, crop-specific, adjusted for soil & weather)
    irrigation_advice = "Check soil moisture and rainfall before irrigating. Consult local expert if needed."

    if closest_district and crop_prediction:
        crop_name = crop_prediction["recommended_crop"].lower()
        soil_moisture = soil_info.get("soil_moisture", 30.0)  # % from AgroMonitoring
        rainfall_mm = rainfall  # from your earlier calculation
        soil_type = soil_info.get("soil_type", "Unknown").lower()  # e.g., "lo47-2a-3803" → loam

        # Full crop-specific irrigation needs (all 22 crops from your model)
        # Values from TNAU/ICAR/Tamil Nadu Agri Dept guidelines
        crop_irrigation = {
            "rice": {"frequency_days": "Continuous (keep 2-5 cm standing water)", "amount_mm": 50, "note": "Maintain water level during tillering and flowering. Reduce before harvest."},
            "maize": {"frequency_days": "7-10", "amount_mm": 40, "note": "Critical at tasseling and grain filling. Use furrow method."},
            "chickpea": {"frequency_days": "10-15", "amount_mm": 30, "note": "Drought-tolerant. Irrigate at flowering and pod filling only."},
            "kidneybeans": {"frequency_days": "7-10", "amount_mm": 30, "note": "Light irrigation. Avoid waterlogging."},
            "pigeonpeas": {"frequency_days": "10-15", "amount_mm": 30, "note": "Deep but infrequent. Drought-resistant after 30 days."},
            "mothbeans": {"frequency_days": "8-12", "amount_mm": 25, "note": "Very drought-tolerant. Irrigate only if soil is dry."},
            "mungbean": {"frequency_days": "7-10", "amount_mm": 25, "note": "Irrigate at flowering and pod filling."},
            "blackgram": {"frequency_days": "7-10", "amount_mm": 25, "note": "Light irrigation. Avoid excess water."},
            "lentil": {"frequency_days": "8-12", "amount_mm": 25, "note": "Irrigate at flowering and pod development."},
            "pomegranate": {"frequency_days": "7-10", "amount_mm": 30, "note": "Drip irrigation best. Critical during fruit development."},
            "banana": {"frequency_days": "3-5", "amount_mm": 40, "note": "Keep soil moist. Drip system recommended."},
            "mango": {"frequency_days": "10-15", "amount_mm": 35, "note": "Irrigate at flowering and fruit set. Avoid during flowering."},
            "grapes": {"frequency_days": "5-7", "amount_mm": 30, "note": "Drip irrigation. Critical at berry development."},
            "watermelon": {"frequency_days": "4-6", "amount_mm": 30, "note": "Avoid over-watering to prevent cracking."},
            "muskmelon": {"frequency_days": "4-5", "amount_mm": 25, "note": "Drip preferred. Avoid waterlogging."},
            "apple": {"frequency_days": "7-10", "amount_mm": 30, "note": "Regular moisture during fruit growth."},
            "orange": {"frequency_days": "5-8", "amount_mm": 35, "note": "Drip system best. Avoid stress at flowering."},
            "papaya": {"frequency_days": "4-6", "amount_mm": 35, "note": "Keep soil moist but well-drained."},
            "coconut": {"frequency_days": "7-10", "amount_mm": 40, "note": "Drip or basin irrigation. Critical during summer."},
            "cotton": {"frequency_days": "10-12", "amount_mm": 35, "note": "Critical at flowering and boll formation."},
            "jute": {"frequency_days": "5-7", "amount_mm": 30, "note": "Keep moist during vegetative stage."},
            "coffee": {"frequency_days": "7-10", "amount_mm": 30, "note": "Drip irrigation. Blossom irrigation important."},
        }

        if crop_name in crop_irrigation:
            needs = crop_irrigation[crop_name]
            freq = needs["frequency_days"]
            amount = needs["amount_mm"]
            note = needs["note"]

            # Adjust for current conditions and soil type
            adjustment = ""
            if rainfall_mm > 10:
                adjustment += f"Recent rain ({rainfall_mm} mm) — skip irrigation for 2-4 days. "
            elif soil_moisture > 35:
                adjustment += f"High soil moisture ({soil_moisture}%) — no irrigation needed now. "
            elif soil_moisture < 15:
                adjustment += f"Low soil moisture ({soil_moisture}%) — irrigate today. "

            # Soil type adjustment (basic)
            if "lo" in soil_type or "clay" in soil_type:
                adjustment += "Your loamy/clay soil holds water longer — irrigate less often. "
            elif "sa" in soil_type or "sand" in soil_type:
                adjustment += "Your sandy soil drains fast — irrigate more frequently. "

            irrigation_advice = f"For {crop_prediction['recommended_crop'].capitalize()}: Water every {freq} days with {amount} mm (about {amount//25} inch) per session if no rain. {adjustment}{note}"

        else:
            irrigation_advice = f"For {crop_prediction['recommended_crop'].capitalize()}: Water every 5-7 days with 25-40 mm (1-1.5 inch) per session. Adjust based on soil moisture and rain. Use drip if possible."

    district_insights["irrigation_advice"] = irrigation_advice

    # Harvest time / crop duration (more precise, ±5–10 days variation)
    harvest_advice = "Harvest time depends on variety, temperature, and local conditions. Check with local agriculture officer for exact date."

    if crop_prediction:
        crop_name = crop_prediction["recommended_crop"].lower()
        current_temp = temp  # from OpenWeatherMap (in °C)

        # Crop-specific average harvest duration (days from sowing) — most common Tamil Nadu variety
        # Source: TNAU Crop Production Guide, ICAR, Tamil Nadu Agri Dept
        crop_duration = {
            "rice": {"days": 105, "range": 5, "note": "Kar / Kuruvai varieties: 90–110 days; Samba: 120–140 days."},
            "maize": {"days": 100, "range": 10, "note": "Hybrid varieties: 90–110 days."},
            "chickpea": {"days": 100, "range": 10, "note": "Desi varieties: 90–110 days."},
            "kidneybeans": {"days": 100, "range": 10, "note": "Common varieties: 90–110 days."},
            "pigeonpeas": {"days": 150, "range": 15, "note": "Short-duration: 120–140 days; medium: 150–180 days."},
            "mothbeans": {"days": 75, "range": 5, "note": "Very short duration: 70–80 days."},
            "mungbean": {"days": 65, "range": 5, "note": "Summer varieties: 60–70 days."},
            "blackgram": {"days": 70, "range": 5, "note": "Summer varieties: 65–75 days."},
            "lentil": {"days": 95, "range": 10, "note": "Common varieties: 85–105 days."},
            "pomegranate": {"days": 210, "range": 30, "note": "First harvest: 180–240 days after planting. Perennial crop."},
            "banana": {"days": 330, "range": 30, "note": "First harvest: 300–360 days after planting. Perennial."},
            "mango": {"days": 150, "range": 30, "note": "Flowering to harvest: 120–180 days. Perennial tree."},
            "grapes": {"days": 135, "range": 15, "note": "Flowering to harvest: 120–150 days."},
            "watermelon": {"days": 80, "range": 10, "note": "Early varieties: 70–90 days."},
            "muskmelon": {"days": 80, "range": 10, "note": "Common varieties: 75–95 days. Harvest when fruit slips easily."},
            "apple": {"days": 165, "range": 15, "note": "Flowering to harvest: 150–180 days. Perennial."},
            "orange": {"days": 270, "range": 30, "note": "Flowering to harvest: 240–300 days. Perennial."},
            "papaya": {"days": 270, "range": 30, "note": "First harvest: 240–300 days after planting. Perennial."},
            "coconut": {"days": 1275, "range": 180, "note": "First harvest: 3–4 years (1095–1460 days). Perennial palm."},
            "cotton": {"days": 165, "range": 15, "note": "Sowing to harvest: 150–180 days."},
            "jute": {"days": 135, "range": 15, "note": "Sowing to harvest: 120–150 days."},
            "coffee": {"days": 1275, "range": 180, "note": "First harvest: 3–4 years (1095–1460 days). Perennial."},
        }

        if crop_name in crop_duration:
            base_days = crop_duration[crop_name]["days"]
            range_days = crop_duration[crop_name]["range"]
            note = crop_duration[crop_name]["note"]

            # Adjust for current temperature (warmer = faster maturity)
            temp_adjust = 0
            if current_temp > 30:
                temp_adjust = -5  # warmer → harvest 5 days earlier
            elif current_temp < 25:
                temp_adjust = 5   # cooler → harvest 5 days later

            min_days = base_days - range_days + temp_adjust
            max_days = base_days + range_days + temp_adjust

            harvest_advice = f"{crop_prediction['recommended_crop'].capitalize()} is usually ready for harvest in {min_days}–{max_days} days from sowing. {note}"

        else:
            harvest_advice = f"{crop_prediction['recommended_crop'].capitalize()}: Typical harvest in 60–120 days. Confirm with local agriculture officer."

    district_insights["harvest_advice"] = harvest_advice

    # Soil recovery / land rest period + crop rotation (dynamic, location & weather-aware)
    recovery_advice = "Rotate crops to keep soil healthy. Consult local agriculture officer for best plan."

    if crop_prediction:
        crop_name = crop_prediction["recommended_crop"].lower()
        current_month = datetime.now().month
        rainfall_mm = rainfall  # from earlier calculation
        current_temp = temp  # from OpenWeatherMap (°C)
        soil_type = soil_info.get("soil_type", "Unknown").lower()

        # Base rotation for all 22 crops (rest months + default alternatives)
        crop_rotation = {
            "rice": {"rest_months": "no long rest — rotate next season (within 1 month after harvest)",
                    "default_alternatives": "blackgram, greengram, groundnut"},
            "maize": {"rest_months": "no long rest — rotate next season (within 1 month)",
                    "default_alternatives": "blackgram, mungbean, pigeonpea"},
            "chickpea": {"rest_months": "no long rest — rotate next season (within 1 month)",
                    "default_alternatives": "rice, maize, groundnut"},
            "kidneybeans": {"rest_months": "no long rest — rotate next season (within 1 month)",
                    "default_alternatives": "maize, cotton, sesame"},
            "pigeonpeas": {"rest_months": "no long rest — rotate next season (within 1 month)",
                    "default_alternatives": "blackgram, greengram, sorghum"},
            "mothbeans": {"rest_months": "no long rest — rotate next season (within 1 month)",
                    "default_alternatives": "maize, cotton, groundnut"},
            "mungbean": {"rest_months": "no long rest — rotate next season (within 1 month)",
                    "default_alternatives": "rice, maize, groundnut"},
            "blackgram": {"rest_months": "no long rest — rotate next season (within 1 month)",
                    "default_alternatives": "rice, maize, sesame"},
            "lentil": {"rest_months": "no long rest — rotate next season (within 1 month)",
                    "default_alternatives": "wheat, maize, mustard"},
            "pomegranate": {"rest_months": "no long rest (perennial) — maintain orchard",
                    "default_alternatives": "blackgram, greengram, short-duration pulses"},
            "banana": {"rest_months": "3–6 months after harvest",
                    "default_alternatives": "green manure crops, blackgram, greengram"},
            "mango": {"rest_months": "no long rest (perennial tree) — maintain orchard",
                    "default_alternatives": "blackgram, greengram, vegetables"},
            "grapes": {"rest_months": "no long rest (perennial vine) — prune annually",
                    "default_alternatives": "blackgram, greengram, avoid solanaceous crops"},
            "watermelon": {"rest_months": "3–4 months (avoid cucurbits)",
                    "default_alternatives": "blackgram, greengram, pigeonpea"},
            "muskmelon": {"rest_months": "3–4 months (avoid cucurbits)",
                    "default_alternatives": "blackgram, greengram, pigeonpea"},
            "apple": {"rest_months": "no long rest (perennial tree) — maintain orchard",
                    "default_alternatives": "blackgram, greengram, short-duration crops"},
            "orange": {"rest_months": "no long rest (perennial tree) — maintain orchard",
                    "default_alternatives": "blackgram, greengram, pulses"},
            "papaya": {"rest_months": "3–6 months after harvest",
                    "default_alternatives": "green manure, blackgram, greengram"},
            "coconut": {"rest_months": "no long rest (perennial palm) — maintain plantation",
                    "default_alternatives": "blackgram, banana, vegetables"},
            "cotton": {"rest_months": "3–4 months (avoid malvaceae family)",
                    "default_alternatives": "blackgram, greengram, cereals"},
            "jute": {"rest_months": "no long rest — rotate next season (within 1 month)",
                    "default_alternatives": "blackgram, greengram, cereals"},
            "coffee": {"rest_months": "no long rest (perennial) — maintain plantation",
                    "default_alternatives": "blackgram, greengram, shade crops"},
        }

        if crop_name in crop_rotation:
            info = crop_rotation[crop_name]
            base_advice = f"After {crop_prediction['recommended_crop'].capitalize()}: rest land for {info['rest_months']}. Next crop suggestions: {info['default_alternatives']}."

            # Dynamic adjustment based on current weather & location conditions
            adjustment = ""
            if current_month in [4,5,6,7,8,9]:  # Summer/monsoon (hot/wet)
                adjustment = "Current hot/wet season — prefer blackgram or pigeonpea (drought/flood-tolerant)."
            elif current_month in [10,11,12,1,2,3]:  # Winter (cool/dry)
                adjustment = "Current cooler/dry season — prefer chickpea or lentil (cold-tolerant)."

            if rainfall_mm < 10 and current_temp > 32:
                adjustment += " Very low rainfall & high temperature — prioritize drought-resistant crops like mothbeans or sesame."
            elif rainfall_mm > 50:
                adjustment += " High recent rainfall — prioritize flood-tolerant crops like rice or blackgram."

            # Soil type adjustment
            if "sa" in soil_type or "sand" in soil_type:
                adjustment += " Sandy soil — choose deep-rooted crops like pigeonpea or groundnut."
            elif "lo" in soil_type or "clay" in soil_type:
                adjustment += " Loamy/clay soil — good for most crops; avoid water-sensitive ones if rain is high."

            recovery_advice = base_advice + " " + adjustment.strip()
        else:
            recovery_advice = f"After {crop_prediction['recommended_crop'].capitalize()}: rest land for 3–4 months or rotate with legumes/pulses to restore nutrients and prevent pests."

    district_insights["recovery_advice"] = recovery_advice

    # Profit estimation (yield × market price - basic cost)
    profit_advice = "Profit depends on market price, yield, and costs. Check local mandi rates."

    if crop_prediction:
        crop_name = crop_prediction["recommended_crop"].lower()

        # Approximate market price (₹ per tonne) — Tamil Nadu mandi rates 2025–26 approx
        crop_prices_per_tonne = {
            "rice": 25000, "maize": 20000, "chickpea": 55000, "kidneybeans": 80000,
            "pigeonpeas": 70000, "mothbeans": 60000, "mungbean": 75000, "blackgram": 80000,
            "lentil": 65000, "pomegranate": 100000, "banana": 15000, "mango": 40000,
            "grapes": 60000, "watermelon": 10000, "muskmelon": 20000, "apple": 80000,
            "orange": 50000, "papaya": 15000, "coconut": 30000, "cotton": 70000,
            "jute": 50000, "coffee": 150000
        }

        # Approximate cost per hectare (₹/ha) — seed, fertilizer, labor, irrigation
        crop_costs = {
            "rice": 60000, "maize": 50000, "chickpea": 40000, "kidneybeans": 45000,
            "pigeonpeas": 45000, "mothbeans": 35000, "mungbean": 40000, "blackgram": 40000,
            "lentil": 40000, "pomegranate": 80000, "banana": 100000, "mango": 90000,
            "grapes": 120000, "watermelon": 50000, "muskmelon": 60000, "apple": 100000,
            "orange": 90000, "papaya": 70000, "coconut": 80000, "cotton": 70000,
            "jute": 50000, "coffee": 150000
        }

        # Try to get yield from CSV first
        yield_t = "N/A"
        if agri_yield_df is not None and closest_district:
            district_data = agri_yield_df[
                (agri_yield_df['District_Name'].str.lower() == closest_district.lower()) &
                (agri_yield_df['Crop'].str.lower().str.contains(crop_name))
            ]
            if not district_data.empty:
                avg_prod = district_data['Production'].mean()
                avg_area = district_data['Area'].mean()
                yield_t = round(avg_prod / avg_area, 2) if avg_area > 0 else "N/A"

        # Fallback average yield if CSV has no data (common values for Tamil Nadu)
        fallback_yield = {
            "rice": 4.5, "maize": 5.0, "chickpea": 1.2, "kidneybeans": 1.5,
            "pigeonpeas": 1.0, "mothbeans": 0.8, "mungbean": 1.0, "blackgram": 1.0,
            "lentil": 1.2, "pomegranate": 10.0, "banana": 30.0, "mango": 8.0,
            "grapes": 15.0, "watermelon": 20.0, "muskmelon": 15.0, "apple": 10.0,
            "orange": 12.0, "papaya": 25.0, "coconut": 8.0, "cotton": 2.0,
            "jute": 2.5, "coffee": 1.0
        }

        if yield_t == "N/A":
            yield_t = fallback_yield.get(crop_name, 2.0)  # default 2 t/ha if missing

        yield_t = float(yield_t)

        price_per_tonne = crop_prices_per_tonne.get(crop_name, 30000)  # default
        revenue = yield_t * price_per_tonne
        cost = crop_costs.get(crop_name, 60000)
        profit = revenue - cost

        profit_advice = f"Estimated profit for {crop_prediction['recommended_crop'].capitalize()}: ₹ {round(profit):,} per hectare. " \
                        f"Revenue: ₹ {round(revenue):,} | Cost: ₹ {cost:,} | Yield: {yield_t} t/ha | Market price: ₹ {price_per_tonne:,}/tonne"

    district_insights["profit_advice"] = profit_advice


    return JSONResponse({
        "status": "success",
        "message": f"Weather at {city}: {temp}°C, {humidity}% humidity, {description}",
        "weather": weather_info,
        "soil": soil_info,
        "rainfall": round(rainfall, 1),
        "district_insights": district_insights,
        "crop_prediction": crop_prediction or {"recommended_crop": "Unable to predict", "confidence": 0}
    }) 

# ==================== GPS ENDPOINT ====================
@router.post("/save-location")
async def save_location(data: dict):
    lat = data.get("latitude")
    lon = data.get("longitude")
    if lat is None or lon is None:
        return JSONResponse({"status": "error", "message": "Invalid location data"}, status_code=400)
    try:
        lat = float(lat)
        lon = float(lon)
    except:
        return JSONResponse({"status": "error", "message": "Invalid lat/lon"}, status_code=400)
    return await process_location(lat, lon)

# ==================== MANUAL ADDRESS ENDPOINT ====================
@router.post("/save-manual-address")
async def save_manual_address(data: dict):
    address = data.get("address", "").strip()
    if not address:
        return JSONResponse({"status": "error", "message": "Address is required"}, status_code=400)

    print(f"🔍 Manual address received: {address}")   # ← Added for debugging

    geo_url = f"https://api.openweathermap.org/geo/1.0/direct?q={address}&limit=1&appid={os.getenv('OPENWEATHER_API_KEY')}"
    try:
        resp = requests.get(geo_url, timeout=8)
        resp.raise_for_status()
        geo_data = resp.json()
        if not geo_data:
            return JSONResponse({"status": "error", "message": "Address not found. Try adding district name (e.g. Periyakulam, Theni, Tamil Nadu)"}, status_code=400)
        lat = geo_data[0]["lat"]
        lon = geo_data[0]["lon"]
        city = geo_data[0].get("name", address)
        print(f"✅ Converted to lat/lon: {lat}, {lon}")
    except Exception as e:
        print(f"❌ Geocoding error: {str(e)}")
        return JSONResponse({"status": "error", "message": "Could not find location. Please try with district name."}, status_code=500)

    return await process_location(lat, lon, city)