# 🏭 Enterprise Manufacturing Digital Twin & Financial Analyzer

A powerful **Discrete Event Simulation (DES)** tool designed for Industrial Engineers and Operations Managers.
Unlike traditional simulations that only focus on "physics" (time, units), this application integrates **Financial Intelligence**, calculating the **Return on Investment (ROI)** and **Net Profit** of production scenarios in real-time.

## 🎯 Business Value
This tool answers critical strategic questions:
- *"If we add a 2nd CNC machine, will the extra revenue cover the operating cost?"*
- *"Where is the bottleneck preventing us from hitting daily targets?"*
- *"What is the exact OEE (Overall Equipment Effectiveness) of our critical resources?"*

## 🚀 Key Features

### 1. ⚙️ Physics-Based Simulation (SimPy)
- Simulates a multi-stage production line: **Prep → Machining → QC**.
- Models real-world variability using stochastic processing times (Exponential Distribution).
- Handles complex queuing logic and resource contention.

### 2. 💰 Financial ROI Dashboard
- Real-time calculation of **Revenue**, **Operating Costs** (Labor/Energy), and **Material Costs**.
- dynamic **Net Profit** and **Profit Margin** analysis based on simulation results.

### 3. 📊 Advanced Analytics
- **Bottleneck Detector:** Automatically flags the constraint resource.
- **Interactive Gantt Chart:** Visualizes the flow of every single part through the system.
- **OEE Gauge:** Live monitoring of equipment efficiency.

## 🛠️ Tech Stack
- **Engine:** Python & `SimPy` (Standard for DES).
- **Interface:** Streamlit (Web App).
- **Visualization:** Plotly (Interactive Charts).
- **Data Processing:** Pandas.

## 📦 Installation & Usage

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/YOUR_USERNAME/factory-digital-twin-simpy.git](https://github.com/YOUR_USERNAME/factory-digital-twin-simpy.git)

DEMO MODE: https://factory-digital-twin-simpy-yckbwzcnydmj8n73iwr7fu.streamlit.app/
   
