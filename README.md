AI-Based Real-Time Crop Risk Prediction System

🌾 Overview

The AI-Based Real-Time Crop Risk Prediction System is a smart agriculture web application designed to help farmers make informed decisions using Artificial Intelligence and real-time environmental data. The system predicts crop risk levels by analyzing weather conditions, soil parameters, and historical agricultural data to reduce crop loss and improve farming productivity.

This project aims to support sustainable farming practices through an easy-to-use and multilingual platform with real-time insights and guidance.

🚀 Features
✅ Real-time crop risk prediction using Machine Learning
🌦️ Live weather analysis using OpenWeather API
🌱 Soil and environmental parameter evaluation
🌐 Multilingual support (English & Tamil)
📊 Interactive dashboard with charts and notifications
🏛️ Government schemes and agricultural support information
📦 Live stock availability updates
📚 Beginner-friendly cultivation guidance
📱 Responsive and user-friendly interface

🛠️ Tech Stack
Frontend
HTML5
CSS3
JavaScript
Chart.js
Backend
Python
Flask

Machine Learning
Scikit-learn
Pandas
NumPy
APIs & Tools
OpenWeather API

⚙️ System Workflow
Farmer accesses the web application
System fetches real-time weather data
User selects crop and location
Backend processes environmental inputs
Machine Learning model predicts crop risk level
Results are displayed using charts and color indicators
Additional farming guidance and government schemes are shown

📈 Machine Learning Model
The system uses Machine Learning algorithms such as:

Random Forest Classifier
Classification-based crop risk prediction
Risk Levels
🟢 Low Risk
🟡 Medium Risk
🔴 High Risk

🎯 Project Objectives
Reduce crop loss through early risk prediction
Improve agricultural decision-making
Provide real-time farming assistance
Increase awareness of government agricultural schemes
Support beginner and small-scale farmers

📂 Project Structure
AI-Crop-Risk-Prediction/
│
├── static/              # CSS, JS, Images
├── templates/           # HTML templates
├── model/               # ML model files
├── dataset/             # Training datasets
├── app.py               # Flask application
├── requirements.txt     # Dependencies
├── README.md
└── .gitignore

▶️ Installation & Setup
1️⃣ Clone the Repository
git clone https://github.com/your-username/AI-Crop-Risk-Prediction.git
cd AI-Crop-Risk-Prediction
2️⃣ Create Virtual Environment
python -m venv venv
3️⃣ Activate Virtual Environment
Windows
venv\Scripts\activate
Linux / Mac
source venv/bin/activate
4️⃣ Install Dependencies
pip install -r requirements.txt
5️⃣ Run the Application
python app.py

📊 Future Enhancements
Mobile application support
AI-based fertilizer recommendation
Crop disease detection using Deep Learning
IoT sensor integration
SMS alert system for farmers

System Demo Representation
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>CropSense AI — Real-Time Crop Risk Prediction</title>
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<style>
  :root {
    --green-deep: #0d3b1e;
    --green-mid: #1a6b38;
    --green-bright: #2eb85c;
    --green-light: #a8f0c6;
    --amber: #f5a623;
    --red: #e03e3e;
    --cream: #f9f5eb;
    --text-dark: #0d1a10;
    --text-muted: #4a6754;
    --card-bg: #ffffff;
    --border: #ddeee4;
    --shadow: 0 4px 24px rgba(14,60,30,0.10);
    --radius: 16px;
    --font-head: 'Syne', sans-serif;
    --font-body: 'DM Sans', sans-serif;
  }
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: var(--font-body);
    background: var(--cream);
    color: var(--text-dark);
    min-height: 100vh;
    font-size: 15px;
    line-height: 1.6;
  }

  /* ──── NAV ──── */
  nav {
    background: var(--green-deep);
    padding: 0 32px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 64px;
    position: sticky;
    top: 0;
    z-index: 100;
    box-shadow: 0 2px 12px rgba(0,0,0,0.25);
  }
  .nav-logo {
    font-family: var(--font-head);
    font-size: 22px;
    font-weight: 800;
    color: var(--green-light);
    display: flex;
    align-items: center;
    gap: 10px;
  }
  .nav-logo span { color: var(--green-bright); }
  .nav-tabs {
    display: flex;
    gap: 4px;
  }
  .nav-tab {
    background: none;
    border: none;
    color: rgba(168,240,198,0.65);
    font-family: var(--font-body);
    font-size: 14px;
    font-weight: 500;
    padding: 8px 16px;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s;
  }
  .nav-tab.active, .nav-tab:hover {
    background: rgba(46,184,92,0.18);
    color: var(--green-light);
  }
  .lang-toggle {
    background: rgba(46,184,92,0.15);
    border: 1px solid rgba(46,184,92,0.3);
    color: var(--green-light);
    font-family: var(--font-body);
    font-size: 13px;
    padding: 6px 14px;
    border-radius: 20px;
    cursor: pointer;
    transition: all 0.2s;
  }
  .lang-toggle:hover { background: rgba(46,184,92,0.3); }

  /* ──── HERO ──── */
  .hero {
    background: linear-gradient(135deg, var(--green-deep) 0%, #0e4a25 60%, #1a6b38 100%);
    color: white;
    padding: 52px 32px 44px;
    text-align: center;
    position: relative;
    overflow: hidden;
  }
  .hero::before {
    content: '';
    position: absolute;
    inset: 0;
    background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%2346d47a' fill-opacity='0.06'%3E%3Ccircle cx='30' cy='30' r='4'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
    pointer-events: none;
  }
  .hero h1 {
    font-family: var(--font-head);
    font-size: clamp(28px, 4vw, 44px);
    font-weight: 800;
    letter-spacing: -0.5px;
    line-height: 1.15;
    margin-bottom: 10px;
  }
  .hero h1 span { color: var(--green-light); }
  .hero p {
    color: rgba(168,240,198,0.8);
    font-size: 16px;
    max-width: 520px;
    margin: 0 auto;
  }
  .weather-strip {
    display: flex;
    justify-content: center;
    gap: 32px;
    margin-top: 28px;
    flex-wrap: wrap;
  }
  .weather-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2px;
  }
  .weather-icon { font-size: 26px; }
  .weather-label { font-size: 11px; color: rgba(168,240,198,0.6); text-transform: uppercase; letter-spacing: 0.05em; }
  .weather-val { font-family: var(--font-head); font-size: 18px; font-weight: 700; color: white; }

  /* ──── MAIN LAYOUT ──── */
  .main {
    max-width: 1100px;
    margin: 0 auto;
    padding: 36px 24px;
  }
  .page { display: none; }
  .page.active { display: block; }

  /* ──── CARDS ──── */
  .card {
    background: var(--card-bg);
    border-radius: var(--radius);
    box-shadow: var(--shadow);
    border: 1px solid var(--border);
    padding: 28px;
  }
  .section-title {
    font-family: var(--font-head);
    font-size: 20px;
    font-weight: 700;
    color: var(--green-deep);
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    gap: 10px;
  }
  .section-title::after {
    content: '';
    flex: 1;
    height: 2px;
    background: linear-gradient(to right, var(--green-bright), transparent);
    border-radius: 2px;
  }

  /* ──── FORM ──── */
  .form-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 18px;
    margin-bottom: 24px;
  }
  .form-group { display: flex; flex-direction: column; gap: 6px; }
  .form-group label {
    font-size: 12px;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--text-muted);
  }
  .form-group input, .form-group select {
    border: 1.5px solid var(--border);
    border-radius: 10px;
    padding: 10px 14px;
    font-family: var(--font-body);
    font-size: 15px;
    color: var(--text-dark);
    background: var(--cream);
    transition: border-color 0.2s, box-shadow 0.2s;
    outline: none;
    -webkit-appearance: none;
  }
  .form-group input:focus, .form-group select:focus {
    border-color: var(--green-bright);
    box-shadow: 0 0 0 3px rgba(46,184,92,0.15);
    background: white;
  }
  .predict-btn {
    display: block;
    width: 100%;
    padding: 16px;
    background: linear-gradient(135deg, var(--green-mid), var(--green-bright));
    color: white;
    font-family: var(--font-head);
    font-size: 17px;
    font-weight: 700;
    border: none;
    border-radius: 12px;
    cursor: pointer;
    transition: all 0.2s;
    letter-spacing: 0.02em;
    box-shadow: 0 4px 16px rgba(46,184,92,0.3);
  }
  .predict-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(46,184,92,0.4);
  }
  .predict-btn:active { transform: translateY(0); }

  /* ──── RESULTS ──── */
  .result-section {
    margin-top: 28px;
    display: none;
  }
  .result-section.visible { display: block; }
  .risk-banner {
    border-radius: var(--radius);
    padding: 24px 28px;
    display: flex;
    align-items: center;
    gap: 20px;
    margin-bottom: 24px;
    animation: fadeSlideIn 0.4s ease;
  }
  @keyframes fadeSlideIn {
    from { opacity: 0; transform: translateY(16px); }
    to   { opacity: 1; transform: translateY(0); }
  }
  .risk-low    { background: linear-gradient(135deg, #d4f7e4, #b0edcc); border: 1.5px solid #6dd9a4; }
  .risk-medium { background: linear-gradient(135deg, #fff3d4, #ffe8a0); border: 1.5px solid #f5c842; }
  .risk-high   { background: linear-gradient(135deg, #fce4e4, #f9c5c5); border: 1.5px solid #e87070; }
  .risk-icon { font-size: 52px; flex-shrink: 0; }
  .risk-label {
    font-family: var(--font-head);
    font-size: 28px;
    font-weight: 800;
  }
  .risk-low .risk-label    { color: #0e6b38; }
  .risk-medium .risk-label { color: #8a5c00; }
  .risk-high .risk-label   { color: #9b1b1b; }
  .risk-desc { font-size: 14px; color: var(--text-muted); margin-top: 4px; }
  .risk-confidence {
    margin-left: auto;
    text-align: center;
    flex-shrink: 0;
  }
  .conf-val {
    font-family: var(--font-head);
    font-size: 36px;
    font-weight: 800;
    color: var(--green-mid);
  }
  .conf-lbl { font-size: 11px; text-transform: uppercase; letter-spacing: 0.06em; color: var(--text-muted); }

  /* ──── CHARTS ROW ──── */
  .charts-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
    margin-bottom: 24px;
  }
  @media (max-width: 640px) { .charts-row { grid-template-columns: 1fr; } }
  .chart-card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 20px;
    box-shadow: var(--shadow);
  }
  .chart-title {
    font-family: var(--font-head);
    font-size: 14px;
    font-weight: 700;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 14px;
  }

  /* ──── FACTORS ──── */
  .factors-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 14px;
    margin-bottom: 24px;
  }
  .factor-card {
    background: var(--cream);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 16px;
    text-align: center;
  }
  .factor-icon { font-size: 28px; margin-bottom: 6px; }
  .factor-name { font-size: 11px; text-transform: uppercase; letter-spacing: 0.06em; color: var(--text-muted); }
  .factor-val { font-family: var(--font-head); font-size: 20px; font-weight: 700; color: var(--green-deep); }
  .factor-status {
    display: inline-block;
    margin-top: 6px;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 500;
  }
  .status-ok   { background: #d4f7e4; color: #0e6b38; }
  .status-warn { background: #fff3d4; color: #8a5c00; }
  .status-bad  { background: #fce4e4; color: #9b1b1b; }

  /* ──── TIPS ──── */
  .tips-list { list-style: none; }
  .tips-list li {
    display: flex;
    gap: 12px;
    padding: 12px 0;
    border-bottom: 1px solid var(--border);
    font-size: 14px;
  }
  .tips-list li:last-child { border-bottom: none; }
  .tip-num {
    width: 26px;
    height: 26px;
    background: var(--green-deep);
    color: white;
    border-radius: 50%;
    font-family: var(--font-head);
    font-size: 12px;
    font-weight: 700;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    margin-top: 2px;
  }

  /* ──── SCHEMES PAGE ──── */
  .schemes-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 20px;
  }
  .scheme-card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 22px;
    box-shadow: var(--shadow);
    border-top: 4px solid var(--green-bright);
    transition: transform 0.2s, box-shadow 0.2s;
  }
  .scheme-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 28px rgba(14,60,30,0.14);
  }
  .scheme-tag {
    display: inline-block;
    background: var(--green-light);
    color: var(--green-deep);
    font-size: 11px;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 20px;
    margin-bottom: 10px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }
  .scheme-name {
    font-family: var(--font-head);
    font-size: 17px;
    font-weight: 700;
    color: var(--green-deep);
    margin-bottom: 8px;
    line-height: 1.3;
  }
  .scheme-desc { font-size: 13px; color: var(--text-muted); line-height: 1.6; }
  .scheme-benefit {
    margin-top: 12px;
    background: #edf9f1;
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 13px;
    font-weight: 500;
    color: var(--green-mid);
  }

  /* ──── STOCK PAGE ──── */
  .stock-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 14px;
  }
  .stock-table th {
    text-align: left;
    padding: 10px 14px;
    background: var(--green-deep);
    color: var(--green-light);
    font-family: var(--font-head);
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }
  .stock-table th:first-child { border-radius: 10px 0 0 0; }
  .stock-table th:last-child  { border-radius: 0 10px 0 0; }
  .stock-table td {
    padding: 12px 14px;
    border-bottom: 1px solid var(--border);
    color: var(--text-dark);
  }
  .stock-table tr:hover td { background: #f5fcf7; }
  .stock-badge {
    display: inline-block;
    padding: 3px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
  }
  .badge-high   { background: #d4f7e4; color: #0e6b38; }
  .badge-medium { background: #fff3d4; color: #8a5c00; }
  .badge-low    { background: #fce4e4; color: #9b1b1b; }

  /* ──── GUIDE PAGE ──── */
  .guide-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 20px;
  }
  .guide-card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    overflow: hidden;
    box-shadow: var(--shadow);
  }
  .guide-header {
    background: linear-gradient(135deg, var(--green-deep), var(--green-mid));
    padding: 18px 20px;
    display: flex;
    align-items: center;
    gap: 12px;
  }
  .guide-emoji { font-size: 30px; }
  .guide-crop {
    font-family: var(--font-head);
    font-size: 18px;
    font-weight: 700;
    color: white;
  }
  .guide-season { font-size: 12px; color: var(--green-light); }
  .guide-body { padding: 18px 20px; }
  .guide-step {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    margin-bottom: 10px;
    font-size: 13px;
  }
  .guide-step-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--green-bright);
    flex-shrink: 0;
    margin-top: 5px;
  }
  .guide-detail { color: var(--text-muted); }
  .guide-ideal {
    margin-top: 14px;
    background: #edf9f1;
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 12px;
    color: var(--green-mid);
  }

  /* ──── LOADING ──── */
  .loading-overlay {
    display: none;
    position: fixed;
    inset: 0;
    background: rgba(13,59,30,0.55);
    z-index: 200;
    align-items: center;
    justify-content: center;
    flex-direction: column;
    gap: 16px;
  }
  .loading-overlay.show { display: flex; }
  .spinner {
    width: 52px;
    height: 52px;
    border: 4px solid rgba(168,240,198,0.3);
    border-top-color: var(--green-light);
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }
  @keyframes spin { to { transform: rotate(360deg); } }
  .loading-text {
    font-family: var(--font-head);
    color: var(--green-light);
    font-size: 16px;
    font-weight: 600;
  }

  /* ──── NOTIFICATION ──── */
  .notif {
    position: fixed;
    top: 80px;
    right: 24px;
    background: var(--green-deep);
    color: var(--green-light);
    padding: 14px 20px;
    border-radius: 12px;
    font-size: 14px;
    font-weight: 500;
    box-shadow: 0 8px 28px rgba(0,0,0,0.25);
    transform: translateX(120%);
    transition: transform 0.3s;
    z-index: 300;
    max-width: 280px;
    border-left: 4px solid var(--green-bright);
  }
  .notif.show { transform: translateX(0); }

  /* ──── MOBILE ──── */
  @media (max-width: 600px) {
    nav { padding: 0 16px; }
    .nav-tabs { display: none; }
    .hero { padding: 32px 16px 28px; }
    .main { padding: 20px 14px; }
    .card { padding: 18px; }
  }
</style>
</head>
<body>

<!-- LOADING -->
<div class="loading-overlay" id="loader">
  <div class="spinner"></div>
  <div class="loading-text" id="loaderText">Analysing crop risk…</div>
</div>

<!-- NOTIFICATION -->
<div class="notif" id="notif"></div>

<!-- NAV -->
<nav>
  <div class="nav-logo">🌾 <span>CropSense</span> AI</div>
  <div class="nav-tabs">
    <button class="nav-tab active" onclick="showPage('predict',this)" data-en="Predict Risk" data-ta="ஆபத்து கணிப்பு">Predict Risk</button>
    <button class="nav-tab" onclick="showPage('schemes',this)" data-en="Gov. Schemes" data-ta="அரசு திட்டங்கள்">Gov. Schemes</button>
    <button class="nav-tab" onclick="showPage('stock',this)" data-en="Stock Updates" data-ta="பங்கு புதுப்பிப்பு">Stock Updates</button>
    <button class="nav-tab" onclick="showPage('guide',this)" data-en="Crop Guide" data-ta="பயிர் வழிகாட்டி">Crop Guide</button>
  </div>
  <button class="lang-toggle" onclick="toggleLang()" id="langBtn">தமிழ்</button>
</nav>

<!-- HERO -->
<div class="hero">
  <h1 data-en="Real-Time <span>Crop Risk</span> Prediction" data-ta="நிகழ்நேர <span>பயிர் ஆபத்து</span> கணிப்பு">Real-Time <span>Crop Risk</span> Prediction</h1>
  <p data-en="AI-powered insights to protect your harvest using live weather, soil data, and machine learning" data-ta="நேரடி வானிலை, மண் தரவு மற்றும் AI மூலம் உங்கள் அறுவடையைப் பாதுகாக்கவும்">AI-powered insights to protect your harvest using live weather, soil data, and machine learning</p>
  <div class="weather-strip" id="weatherStrip">
    <div class="weather-item">
      <div class="weather-icon">🌡️</div>
      <div class="weather-label">Temperature</div>
      <div class="weather-val" id="wTemp">--</div>
    </div>
    <div class="weather-item">
      <div class="weather-icon">💧</div>
      <div class="weather-label">Humidity</div>
      <div class="weather-val" id="wHumidity">--</div>
    </div>
    <div class="weather-item">
      <div class="weather-icon">🌬️</div>
      <div class="weather-label">Wind</div>
      <div class="weather-val" id="wWind">--</div>
    </div>
    <div class="weather-item">
      <div class="weather-icon">🌧️</div>
      <div class="weather-label">Rainfall</div>
      <div class="weather-val" id="wRain">--</div>
    </div>
    <div class="weather-item">
      <div class="weather-icon">📍</div>
      <div class="weather-label">Location</div>
      <div class="weather-val" id="wLoc">--</div>
    </div>
  </div>
</div>

<div class="main">

  <!-- ════ PAGE: PREDICT ════ -->
  <div class="page active" id="page-predict">
    <div class="card">
      <div class="section-title">🔬 <span data-en="Enter Crop & Soil Parameters" data-ta="பயிர் & மண் அளவுகளை உள்ளிடவும்">Enter Crop & Soil Parameters</span></div>
      <div class="form-grid">
        <div class="form-group">
          <label data-en="Crop Type" data-ta="பயிர் வகை">Crop Type</label>
          <select id="cropType">
            <option value="rice">Rice (Paddy)</option>
            <option value="wheat">Wheat</option>
            <option value="sugarcane">Sugarcane</option>
            <option value="tomato">Tomato</option>
            <option value="groundnut">Groundnut</option>
            <option value="maize">Maize</option>
            <option value="cotton">Cotton</option>
            <option value="banana">Banana</option>
          </select>
        </div>
        <div class="form-group">
          <label data-en="Location / District" data-ta="இடம் / மாவட்டம்">Location / District</label>
          <select id="location">
            <option value="Chennai">Chennai</option>
            <option value="Coimbatore">Coimbatore</option>
            <option value="Madurai">Madurai</option>
            <option value="Trichy">Trichy</option>
            <option value="Salem">Salem</option>
            <option value="Thanjavur">Thanjavur</option>
            <option value="Vellore">Vellore</option>
            <option value="Tirunelveli">Tirunelveli</option>
          </select>
        </div>
        <div class="form-group">
          <label data-en="Soil pH (4.0 – 9.0)" data-ta="மண் pH (4.0 – 9.0)">Soil pH (4.0 – 9.0)</label>
          <input type="number" id="pH" min="4" max="9" step="0.1" value="6.5" placeholder="6.5">
        </div>
        <div class="form-group">
          <label data-en="Soil Moisture (%)" data-ta="மண் ஈரப்பதம் (%)">Soil Moisture (%)</label>
          <input type="number" id="moisture" min="0" max="100" value="45" placeholder="45">
        </div>
        <div class="form-group">
          <label data-en="Nitrogen (kg/ha)" data-ta="நைட்ரஜன் (kg/ha)">Nitrogen (kg/ha)</label>
          <input type="number" id="nitrogen" min="0" max="300" value="120" placeholder="120">
        </div>
        <div class="form-group">
          <label data-en="Phosphorus (kg/ha)" data-ta="பாஸ்பரஸ் (kg/ha)">Phosphorus (kg/ha)</label>
          <input type="number" id="phosphorus" min="0" max="200" value="60" placeholder="60">
        </div>
        <div class="form-group">
          <label data-en="Potassium (kg/ha)" data-ta="பொட்டாசியம் (kg/ha)">Potassium (kg/ha)</label>
          <input type="number" id="potassium" min="0" max="300" value="80" placeholder="80">
        </div>
        <div class="form-group">
          <label data-en="Farm Area (acres)" data-ta="பண்ணை பரப்பளவு (ஏக்கர்)">Farm Area (acres)</label>
          <input type="number" id="area" min="0.5" max="100" value="5" placeholder="5">
        </div>
      </div>
      <button class="predict-btn" onclick="predictRisk()">
        🤖 <span data-en="Predict Crop Risk with AI" data-ta="AI மூலம் பயிர் ஆபத்தை கணிக்கவும்">Predict Crop Risk with AI</span>
      </button>
    </div>

    <!-- RESULTS -->
    <div class="result-section" id="resultSection">
      <!-- Risk banner -->
      <div class="risk-banner" id="riskBanner">
        <div class="risk-icon" id="riskIcon">🟢</div>
        <div>
          <div class="risk-label" id="riskLabel">Low Risk</div>
          <div class="risk-desc" id="riskDesc">Your crop conditions look favourable.</div>
        </div>
        <div class="risk-confidence">
          <div class="conf-val" id="confVal">87%</div>
          <div class="conf-lbl" data-en="Confidence" data-ta="நம்பகத்தன்மை">Confidence</div>
        </div>
      </div>

      <!-- Factor cards -->
      <div class="factors-grid" id="factorsGrid"></div>

      <!-- Charts -->
      <div class="charts-row">
        <div class="chart-card">
          <div class="chart-title" data-en="Risk Factor Analysis" data-ta="ஆபத்து காரணி பகுப்பாய்வு">Risk Factor Analysis</div>
          <canvas id="radarChart" height="220"></canvas>
        </div>
        <div class="chart-card">
          <div class="chart-title" data-en="7-Day Risk Forecast" data-ta="7-நாள் ஆபத்து முன்னறிவிப்பு">7-Day Risk Forecast</div>
          <canvas id="lineChart" height="220"></canvas>
        </div>
      </div>

      <!-- Tips -->
      <div class="card" style="margin-top:0">
        <div class="section-title">💡 <span data-en="Recommendations" data-ta="பரிந்துரைகள்">Recommendations</span></div>
        <ul class="tips-list" id="tipsList"></ul>
      </div>
    </div>
  </div>

  <!-- ════ PAGE: SCHEMES ════ -->
  <div class="page" id="page-schemes">
    <div class="section-title" style="margin-bottom:20px">🏛️ <span data-en="Government Agricultural Schemes" data-ta="அரசு விவசாயத் திட்டங்கள்">Government Agricultural Schemes</span></div>
    <div class="schemes-grid" id="schemesGrid"></div>
  </div>

  <!-- ════ PAGE: STOCK ════ -->
  <div class="page" id="page-stock">
    <div class="section-title" style="margin-bottom:20px">📦 <span data-en="Live Stock Availability" data-ta="நேரடி பங்கு கிடைக்கும் தன்மை">Live Stock Availability</span></div>
    <div class="card">
      <table class="stock-table" id="stockTable">
        <thead>
          <tr>
            <th data-en="Crop / Input" data-ta="பயிர் / உள்ளீடு">Crop / Input</th>
            <th data-en="Category" data-ta="வகை">Category</th>
            <th data-en="Price/kg (₹)" data-ta="விலை/கி.கி (₹)">Price/kg (₹)</th>
            <th data-en="Stock Level" data-ta="பங்கு அளவு">Stock Level</th>
            <th data-en="Last Updated" data-ta="கடைசியாக புதுப்பிக்கப்பட்டது">Last Updated</th>
          </tr>
        </thead>
        <tbody id="stockBody"></tbody>
      </table>
    </div>
  </div>

  <!-- ════ PAGE: GUIDE ════ -->
  <div class="page" id="page-guide">
    <div class="section-title" style="margin-bottom:20px">📚 <span data-en="Beginner Cultivation Guide" data-ta="தொடக்கநிலை பயிர் வழிகாட்டி">Beginner Cultivation Guide</span></div>
    <div class="guide-grid" id="guideGrid"></div>
  </div>

</div><!-- end .main -->

<script>
// ══════════════════════════════════════
//  LANGUAGE
// ══════════════════════════════════════
let lang = 'en';
function toggleLang() {
  lang = lang === 'en' ? 'ta' : 'en';
  document.getElementById('langBtn').textContent = lang === 'en' ? 'தமிழ்' : 'English';
  document.querySelectorAll('[data-en]').forEach(el => {
    el.innerHTML = el.dataset[lang] || el.dataset.en;
  });
  showNotif(lang === 'ta' ? '🌐 தமிழ் மொழி செயல்படுத்தப்பட்டது' : '🌐 Switched to English');
}

// ══════════════════════════════════════
//  NAV
// ══════════════════════════════════════
function showPage(id, btn) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
  document.getElementById('page-' + id).classList.add('active');
  btn.classList.add('active');
}

// ══════════════════════════════════════
//  NOTIFICATIONS
// ══════════════════════════════════════
function showNotif(msg) {
  const n = document.getElementById('notif');
  n.textContent = msg;
  n.classList.add('show');
  setTimeout(() => n.classList.remove('show'), 3200);
}

// ══════════════════════════════════════
//  SIMULATED WEATHER (replace API key below)
// ══════════════════════════════════════
const weatherByLocation = {
  Chennai:     { temp:'34°C', humidity:'78%', wind:'14 km/h', rain:'8 mm', emoji:'⛅' },
  Coimbatore:  { temp:'30°C', humidity:'65%', wind:'10 km/h', rain:'2 mm', emoji:'☀️' },
  Madurai:     { temp:'36°C', humidity:'70%', wind:'12 km/h', rain:'0 mm', emoji:'🌤️' },
  Trichy:      { temp:'35°C', humidity:'68%', wind:'11 km/h', rain:'3 mm', emoji:'☀️' },
  Salem:       { temp:'32°C', humidity:'60%', wind:'9 km/h',  rain:'0 mm', emoji:'🌤️' },
  Thanjavur:   { temp:'33°C', humidity:'75%', wind:'13 km/h', rain:'12 mm', emoji:'🌧️' },
  Vellore:     { temp:'33°C', humidity:'64%', wind:'8 km/h',  rain:'1 mm', emoji:'☀️' },
  Tirunelveli: { temp:'35°C', humidity:'72%', wind:'16 km/h', rain:'6 mm', emoji:'⛅' }
};

function updateWeather(loc) {
  const w = weatherByLocation[loc] || weatherByLocation['Chennai'];
  document.getElementById('wTemp').textContent = w.temp;
  document.getElementById('wHumidity').textContent = w.humidity;
  document.getElementById('wWind').textContent = w.wind;
  document.getElementById('wRain').textContent = w.rain;
  document.getElementById('wLoc').textContent = loc;
}
document.getElementById('location').addEventListener('change', e => updateWeather(e.target.value));
updateWeather('Chennai');

// ══════════════════════════════════════
//  ML PREDICTION (Random Forest simulation)
// ══════════════════════════════════════
const cropIdeal = {
  rice:      { pH:[5.5,7.0], moisture:[55,80], N:[100,180], P:[40,80],  K:[60,120] },
  wheat:     { pH:[6.0,7.5], moisture:[40,60], N:[80,150],  P:[50,90],  K:[60,100] },
  sugarcane: { pH:[6.0,8.0], moisture:[50,75], N:[100,200], P:[40,80],  K:[80,160] },
  tomato:    { pH:[5.5,7.0], moisture:[40,65], N:[80,160],  P:[50,100], K:[80,140] },
  groundnut: { pH:[5.5,7.0], moisture:[35,55], N:[20,60],   P:[40,80],  K:[40,80]  },
  maize:     { pH:[5.5,7.0], moisture:[45,70], N:[100,200], P:[50,100], K:[80,140] },
  cotton:    { pH:[5.8,8.0], moisture:[40,65], N:[80,160],  P:[40,80],  K:[60,120] },
  banana:    { pH:[5.5,7.0], moisture:[55,80], N:[150,250], P:[50,100], K:[150,250] }
};

function scoreParam(val, [low, high]) {
  if (val >= low && val <= high) return 100;
  const dist = val < low ? (low - val) / low : (val - high) / high;
  return Math.max(0, Math.round(100 - dist * 160));
}

function predictRisk() {
  const crop     = document.getElementById('cropType').value;
  const loc      = document.getElementById('location').value;
  const pH       = parseFloat(document.getElementById('pH').value);
  const moisture = parseFloat(document.getElementById('moisture').value);
  const N        = parseFloat(document.getElementById('nitrogen').value);
  const P        = parseFloat(document.getElementById('phosphorus').value);
  const K        = parseFloat(document.getElementById('potassium').value);

  if ([pH,moisture,N,P,K].some(isNaN)) { showNotif('⚠️ Please fill all fields'); return; }

  const loader = document.getElementById('loader');
  const msgs = ['Fetching weather data…','Processing soil parameters…','Running Random Forest model…','Generating risk report…'];
  let mi = 0;
  loader.classList.add('show');
  document.getElementById('loaderText').textContent = msgs[0];
  const iv = setInterval(() => { mi = Math.min(mi+1,3); document.getElementById('loaderText').textContent = msgs[mi]; }, 600);

  setTimeout(() => {
    clearInterval(iv);
    loader.classList.remove('show');

    const ideal = cropIdeal[crop];
    const scores = {
      pH:       scoreParam(pH, ideal.pH),
      moisture: scoreParam(moisture, ideal.moisture),
      nitrogen: scoreParam(N, ideal.N),
      phosphorus: scoreParam(P, ideal.P),
      potassium:  scoreParam(K, ideal.K)
    };
    // Weather penalty
    const w = weatherByLocation[loc];
    const tempNum = parseInt(w.temp);
    const weatherScore = tempNum > 38 ? 55 : tempNum > 35 ? 75 : 95;
    scores.weather = weatherScore;

    const avg = Object.values(scores).reduce((a,b)=>a+b,0) / Object.values(scores).length;
    const conf = Math.round(75 + Math.random()*15);

    let risk, icon, cls, desc;
    if (avg >= 72)      { risk='Low Risk';    icon='🟢'; cls='risk-low';    desc='Your crop conditions look favourable. Continue regular monitoring.'; }
    else if (avg >= 48) { risk='Medium Risk'; icon='🟡'; cls='risk-medium'; desc='Some parameters need attention. Take preventive action.'; }
    else                { risk='High Risk';   icon='🔴'; cls='risk-high';   desc='Critical risk detected! Immediate intervention required.'; }

    // Banner
    const banner = document.getElementById('riskBanner');
    banner.className = 'risk-banner ' + cls;
    document.getElementById('riskIcon').textContent  = icon;
    document.getElementById('riskLabel').textContent = risk;
    document.getElementById('riskDesc').textContent  = desc;
    document.getElementById('confVal').textContent   = conf + '%';

    // Factor cards
    const factorDefs = [
      { key:'pH',         icon:'🧪', name:'Soil pH',    val: pH+'',          unit:'' },
      { key:'moisture',   icon:'💧', name:'Moisture',   val: moisture+'',    unit:'%' },
      { key:'nitrogen',   icon:'🌿', name:'Nitrogen',   val: N+'',           unit:' kg/ha' },
      { key:'phosphorus', icon:'🟤', name:'Phosphorus', val: P+'',           unit:' kg/ha' },
      { key:'potassium',  icon:'🟡', name:'Potassium',  val: K+'',           unit:' kg/ha' },
      { key:'weather',    icon:'🌤️', name:'Weather',    val: w.temp,         unit:'' }
    ];
    const fg = document.getElementById('factorsGrid');
    fg.innerHTML = factorDefs.map(f => {
      const s = scores[f.key];
      const sc = s >= 70 ? 'status-ok' : s >= 45 ? 'status-warn' : 'status-bad';
      const sl = s >= 70 ? '✓ Good' : s >= 45 ? '⚠ Fair' : '✗ Poor';
      return `<div class="factor-card">
        <div class="factor-icon">${f.icon}</div>
        <div class="factor-name">${f.name}</div>
        <div class="factor-val">${f.val}${f.unit}</div>
        <span class="factor-status ${sc}">${sl}</span>
      </div>`;
    }).join('');

    // Charts
    renderCharts(scores, risk);

    // Tips
    const tips = generateTips(crop, scores, risk);
    document.getElementById('tipsList').innerHTML = tips.map((t,i)=>
      `<li><div class="tip-num">${i+1}</div><span>${t}</span></li>`).join('');

    document.getElementById('resultSection').classList.add('visible');
    document.getElementById('resultSection').scrollIntoView({ behavior:'smooth', block:'start' });
    showNotif(icon + ' ' + risk + ' detected for ' + crop);
  }, 2600);
}

// ══════════════════════════════════════
//  CHARTS
// ══════════════════════════════════════
let radarInst, lineInst;
function renderCharts(scores, risk) {
  const labels = ['pH','Moisture','Nitrogen','Phosphorus','Potassium','Weather'];
  const vals   = [scores.pH, scores.moisture, scores.nitrogen, scores.phosphorus, scores.potassium, scores.weather];

  if (radarInst) radarInst.destroy();
  radarInst = new Chart(document.getElementById('radarChart'), {
    type: 'radar',
    data: {
      labels,
      datasets: [{
        label: 'Score',
        data: vals,
        backgroundColor: 'rgba(46,184,92,0.15)',
        borderColor: '#2eb85c',
        borderWidth: 2,
        pointBackgroundColor: '#2eb85c',
        pointRadius: 4
      }]
    },
    options: {
      scales: { r: { min:0, max:100, ticks:{ display:false }, grid:{ color:'rgba(0,0,0,0.06)' } } },
      plugins: { legend:{ display:false } },
      responsive: true
    }
  });

  // 7-day forecast (simulated)
  const days = ['Today','Day 2','Day 3','Day 4','Day 5','Day 6','Day 7'];
  const base = risk === 'Low Risk' ? 78 : risk === 'Medium Risk' ? 52 : 32;
  const forecast = days.map((_,i) => Math.max(20,Math.min(98, base + (Math.random()-0.5)*18 + i*2)));

  if (lineInst) lineInst.destroy();
  lineInst = new Chart(document.getElementById('lineChart'), {
    type: 'line',
    data: {
      labels: days,
      datasets: [{
        label: 'Safety Score',
        data: forecast,
        borderColor: '#2eb85c',
        backgroundColor: 'rgba(46,184,92,0.08)',
        fill: true,
        tension: 0.4,
        borderWidth: 2.5,
        pointRadius: 4,
        pointBackgroundColor: '#2eb85c'
      }]
    },
    options: {
      scales: {
        y: { min:0, max:100, grid:{ color:'rgba(0,0,0,0.05)' }, ticks:{ color:'#4a6754' } },
        x: { grid:{ display:false }, ticks:{ color:'#4a6754' } }
      },
      plugins: { legend:{ display:false } },
      responsive: true
    }
  });
}

// ══════════════════════════════════════
//  TIPS ENGINE
// ══════════════════════════════════════
const tipBank = {
  pH:         { bad:'Add lime to raise soil pH or sulphur to lower it to the optimal range.', warn:'Monitor pH weekly and adjust with organic amendments.' },
  moisture:   { bad:'Install drip irrigation or improve drainage depending on whether soil is too dry or waterlogged.', warn:'Irrigate in early morning to reduce evaporation losses.' },
  nitrogen:   { bad:'Apply urea or compost to boost nitrogen; avoid over-application which causes burning.', warn:'Top-dress with nitrogen at 30-day intervals during vegetative stage.' },
  phosphorus: { bad:'Incorporate super-phosphate fertiliser before sowing for better root development.', warn:'Apply phosphorus fertiliser at planting for better uptake.' },
  potassium:  { bad:'Apply muriate of potash (MOP) to replenish potassium and improve drought resistance.', warn:'Use potassium-rich compost to maintain balanced nutrition.' },
  weather:    { bad:'Provide shade nets and increase irrigation during extreme heat; monitor for heat-stress symptoms.', warn:'Harvest rainwater during heavy rain spells for dry-period use.' }
};
const generalTips = [
  'Conduct soil testing every season for accurate nutrient planning.',
  'Use integrated pest management (IPM) to reduce chemical dependency.',
  'Register on the PM-KISAN portal to receive direct income support.',
  'Consult your nearest Krishi Vigyan Kendra (KVK) for localised advice.'
];

function generateTips(crop, scores, risk) {
  const tips = [];
  Object.entries(scores).forEach(([k, v]) => {
    if (v < 50 && tipBank[k]) tips.push(tipBank[k].bad);
    else if (v < 72 && tipBank[k]) tips.push(tipBank[k].warn);
  });
  if (risk === 'High Risk') tips.unshift('🚨 Contact your district agricultural officer immediately for emergency support.');
  tips.push(...generalTips.slice(0, 4 - tips.length));
  return tips.slice(0,5);
}

// ══════════════════════════════════════
//  GOVERNMENT SCHEMES
// ══════════════════════════════════════
const schemes = [
  { tag:'Central', name:'PM-KISAN Samman Nidhi', desc:'Direct income support of ₹6,000/year to small and marginal farmers in three equal instalments.', benefit:'₹6,000/year direct benefit transfer' },
  { tag:'Insurance', name:'PM Fasal Bima Yojana', desc:'Crop insurance scheme covering losses due to natural calamities, pests, and diseases with low premium rates.', benefit:'Up to ₹2 lakh crop loss coverage' },
  { tag:'Tamil Nadu', name:'Chief Minister Drought Relief', desc:'Emergency assistance to farmers in drought-declared areas including free inputs, water supply, and wage support.', benefit:'Free seeds, fertilisers & ₹500/day wage' },
  { tag:'Soil Health', name:'Soil Health Card Scheme', desc:'Free soil testing and personalised nutrient management recommendations issued every 2 years to all farmers.', benefit:'Free soil test + expert advisory' },
  { tag:'Credit', name:'Kisan Credit Card (KCC)', desc:'Flexible credit for agricultural operations, post-harvest expenses, and allied activities at 4% interest rate.', benefit:'Up to ₹3 lakh at 4% interest' },
  { tag:'Market', name:'eNAM – National Agri Market', desc:'Online trading platform connecting farmers directly to buyers across states, eliminating middlemen.', benefit:'Better prices via online auction' },
  { tag:'Tamil Nadu', name:'Uzhavar Sandhai', desc:'State-run farmers\' markets enabling direct sale of fresh produce to consumers at fair prices without middlemen.', benefit:'Direct-to-consumer retail access' },
  { tag:'Technology', name:'Digital Agriculture Mission', desc:'AI, IoT, and remote sensing tools for crop monitoring, advisory services, and precision farming support.', benefit:'Free precision farming advisory' }
];
document.getElementById('schemesGrid').innerHTML = schemes.map(s => `
  <div class="scheme-card">
    <span class="scheme-tag">${s.tag}</span>
    <div class="scheme-name">${s.name}</div>
    <div class="scheme-desc">${s.desc}</div>
    <div class="scheme-benefit">✅ ${s.benefit}</div>
  </div>`).join('');

// ══════════════════════════════════════
//  STOCK TABLE
// ══════════════════════════════════════
const stocks = [
  { name:'Rice (Raw)', cat:'Cereal', price:28, level:'High', time:'2 min ago' },
  { name:'Wheat', cat:'Cereal', price:24, level:'Medium', time:'5 min ago' },
  { name:'Tomato', cat:'Vegetable', price:18, level:'Low', time:'1 min ago' },
  { name:'Sugarcane', cat:'Cash Crop', price:3.5, level:'High', time:'8 min ago' },
  { name:'Groundnut', cat:'Oilseed', price:65, level:'Medium', time:'3 min ago' },
  { name:'Urea Fertiliser', cat:'Input', price:5.4, level:'High', time:'12 min ago' },
  { name:'DAP Fertiliser', cat:'Input', price:27, level:'Low', time:'6 min ago' },
  { name:'Maize', cat:'Cereal', price:20, level:'High', time:'4 min ago' },
  { name:'Cotton (Lint)', cat:'Cash Crop', price:62, level:'Medium', time:'9 min ago' },
  { name:'Banana', cat:'Fruit', price:15, level:'High', time:'2 min ago' }
];
function badgeClass(l) { return l==='High'?'badge-high':l==='Medium'?'badge-medium':'badge-low'; }
document.getElementById('stockBody').innerHTML = stocks.map(s => `
  <tr>
    <td><strong>${s.name}</strong></td>
    <td>${s.cat}</td>
    <td>₹${s.price}</td>
    <td><span class="stock-badge ${badgeClass(s.level)}">${s.level}</span></td>
    <td style="color:var(--text-muted);font-size:13px">${s.time}</td>
  </tr>`).join('');

// Live price jitter
setInterval(() => {
  document.querySelectorAll('#stockBody tr').forEach((row,i) => {
    const td = row.children[2];
    const cur = parseFloat(td.textContent.replace('₹',''));
    const adj = +(cur + (Math.random()-0.5)*0.4).toFixed(1);
    td.textContent = '₹' + adj;
    td.style.color = adj > cur ? '#0e6b38' : '#9b1b1b';
    setTimeout(() => td.style.color = '', 800);
  });
}, 5000);

// ══════════════════════════════════════
//  CROP GUIDE
// ══════════════════════════════════════
const guides = [
  { emoji:'🌾', name:'Rice (Paddy)', season:'Kharif & Rabi', steps:['Prepare puddled field with 5–8 cm standing water','Transplant 21-day-old seedlings, 20×15 cm spacing','Apply Nitrogen in 3 splits (basal, tillering, panicle)','Drain field 10 days before harvest'], ideal:'pH 5.5–7.0 | Temp 22–32°C | Moisture 60–80%' },
  { emoji:'🌽', name:'Maize', season:'Kharif (June–Oct)', steps:['Deep plough to 25 cm and add FYM 10 t/ha','Sow seeds 3–4 cm deep, 60×20 cm spacing','Irrigate at knee-high, tasseling & grain fill stages','Harvest when husk turns brown and grain is hard'], ideal:'pH 5.5–7.0 | Temp 18–32°C | Moisture 45–70%' },
  { emoji:'🍅', name:'Tomato', season:'Sept – Dec (Tamil Nadu)', steps:['Raise nursery in pro-trays; transplant at 4-leaf stage','Provide stakes or trellis for indeterminate varieties','Irrigate via drip every alternate day','Spray copper fungicide fortnightly to prevent blight'], ideal:'pH 5.5–7.0 | Temp 18–27°C | Moisture 40–65%' },
  { emoji:'🥜', name:'Groundnut', season:'Kharif & Rabi', steps:['Plough and ridge field; apply gypsum at 400 kg/ha','Sow seeds 4–5 cm deep at 30×10 cm spacing','Earth up at 45 days for peg development','Harvest when inner shell shows orange/brown markings'], ideal:'pH 5.5–7.0 | Temp 25–35°C | Moisture 35–55%' },
  { emoji:'🌿', name:'Sugarcane', season:'Oct – Mar planting', steps:['Prepare trenches 30 cm deep, 90 cm apart','Place setts with 2–3 buds; cover with 5 cm soil','Ratoon management: retain 2 ratoon crops max','Harvest at 10–12 months when °Brix ≥ 18'], ideal:'pH 6.0–8.0 | Temp 20–35°C | Moisture 50–75%' },
  { emoji:'🍌', name:'Banana', season:'Year-round (irrigated)', steps:['Plant tissue-culture suckers in 45×45×45 cm pits','Apply 200 g urea/plant in 3 splits over 6 months','Prop up bunches after emergence to prevent toppling','Harvest at 75–80% maturity; handle carefully to avoid bruising'], ideal:'pH 5.5–7.0 | Temp 15–35°C | Moisture 55–80%' }
];
document.getElementById('guideGrid').innerHTML = guides.map(g => `
  <div class="guide-card">
    <div class="guide-header">
      <div class="guide-emoji">${g.emoji}</div>
      <div>
        <div class="guide-crop">${g.name}</div>
        <div class="guide-season">📅 ${g.season}</div>
      </div>
    </div>
    <div class="guide-body">
      ${g.steps.map(s=>`<div class="guide-step"><div class="guide-step-dot"></div><span class="guide-detail">${s}</span></div>`).join('')}
      <div class="guide-ideal">🎯 Ideal: ${g.ideal}</div>
    </div>
  </div>`).join('');

// ══════════════════════════════════════
//  WELCOME NOTIF
// ══════════════════════════════════════
setTimeout(() => showNotif('🌾 Welcome! Select your crop and fill soil data to predict risk.'), 800);
</script>
</body>
</html>

🤝 Contribution

Contributions and suggestions are welcome. Feel free to fork the repository and submit pull requests.

📜 License

This project is developed for educational and research purposes.(MIT License)

👨‍💻 Author

Vishal P
AI & Web Development Enthusiast | Smart Agriculture Projects | Machine Learning Developer
