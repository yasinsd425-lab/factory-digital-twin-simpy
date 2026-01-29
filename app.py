import streamlit as st
import simpy
import random
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go # Added for Gauge Chart
import datetime

# --- PAGE CONFIG ---
st.set_page_config(page_title="Factory Digital Twin V3.0 (Enterprise)", page_icon="🏭", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6; border-left: 5px solid #28a745; padding: 15px; border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

st.title("🏭 Manufacturing Digital Twin & Financial Analyzer")
st.markdown("**System:** Discrete Event Simulation (DES) + **Financial ROI Model**")

# --- SIDEBAR: CONFIGURATION ---
st.sidebar.header("⚙️ 1. Production Settings")

st.sidebar.subheader("Resources (Machines)")
c_prep = st.sidebar.slider("🛠️ Prep Station", 1, 5, 2)
c_machining = st.sidebar.slider("⚙️ Machining Center", 1, 5, 1)
c_qc = st.sidebar.slider("✅ QC Inspectors", 1, 5, 2)

st.sidebar.subheader("Cycle Times (min)")
t_prep = st.sidebar.number_input("Prep Time", value=10)
t_machining = st.sidebar.number_input("Machining Time", value=15)
t_qc = st.sidebar.number_input("QC Time", value=8)

st.sidebar.markdown("---")
st.sidebar.header("💰 2. Financial Config")
price_per_unit = st.sidebar.number_input("Selling Price per Unit (€)", value=150)
cost_per_hour = st.sidebar.number_input("Op. Cost per Machine/Hour (€)", value=20, help="Labor + Energy cost per machine")
raw_material_cost = st.sidebar.number_input("Raw Material Cost (€)", value=40)

st.sidebar.markdown("---")
st.sidebar.header("⏳ 3. Simulation Time")
sim_duration = st.sidebar.number_input("Shift Duration (min)", value=480, help="8 Hours = 480 min")
arrival_rate = st.sidebar.number_input("Arrival Interval (min)", value=5.0)

# --- SIMULATION ENGINE ---
class ProductionLine:
    def __init__(self, env, c_prep, c_machining, c_qc, t_prep, t_machining, t_qc):
        self.env = env
        self.prep = simpy.Resource(env, capacity=c_prep)
        self.machining = simpy.Resource(env, capacity=c_machining)
        self.qc = simpy.Resource(env, capacity=c_qc)
        
        self.t_prep = t_prep
        self.t_machining = t_machining
        self.t_qc = t_qc
        
        self.logs = []

    def process_part(self, name):
        # STAGE 1
        with self.prep.request() as req:
            yield req
            start = self.env.now
            yield self.env.timeout(random.expovariate(1.0/self.t_prep))
            self.log_data(name, "1. Prep", start, self.env.now)

        # STAGE 2
        with self.machining.request() as req:
            yield req
            start = self.env.now
            yield self.env.timeout(random.expovariate(1.0/self.t_machining))
            self.log_data(name, "2. Machining", start, self.env.now)

        # STAGE 3
        with self.qc.request() as req:
            yield req
            start = self.env.now
            yield self.env.timeout(random.expovariate(1.0/self.t_qc))
            self.log_data(name, "3. QC", start, self.env.now)

    def log_data(self, name, stage, start, finish):
        self.logs.append({
            'Part': name,
            'Stage': stage,
            'Start': start,
            'Finish': finish,
            'Duration': finish - start
        })

def part_generator(env, factory, interval):
    i = 0
    while True:
        yield env.timeout(random.expovariate(1.0 / interval))
        i += 1
        env.process(factory.process_part(f"Part-{i:03d}"))

# --- MAIN LOGIC ---
if st.button("🚀 Run Enterprise Simulation"):
    env = simpy.Environment()
    factory = ProductionLine(env, c_prep, c_machining, c_qc, t_prep, t_machining, t_qc)
    env.process(part_generator(env, factory, arrival_rate))
    
    with st.spinner("Calculating Physics & Financials..."):
        env.run(until=sim_duration)
    
    df = pd.DataFrame(factory.logs)
    
    if not df.empty:
        # --- 1. DATA PROCESSING ---
        base_time = pd.Timestamp.now().replace(hour=8, minute=0, second=0, microsecond=0)
        df['Start_Time'] = base_time + pd.to_timedelta(df['Start'], unit='m')
        df['Finish_Time'] = base_time + pd.to_timedelta(df['Finish'], unit='m')

        # Throughput
        finished_parts = len(df[df['Stage']=='3. QC'])
        
        # --- 2. FINANCIAL CALCULATIONS (NEW!) ---
        total_revenue = finished_parts * price_per_unit
        
        # Operating Cost = (Total Machines * Cost per hour * Hours)
        total_machines = c_prep + c_machining + c_qc
        shift_hours = sim_duration / 60
        total_op_cost = total_machines * cost_per_hour * shift_hours
        
        # Material Cost
        total_mat_cost = finished_parts * raw_material_cost
        
        # Net Profit
        net_profit = total_revenue - (total_op_cost + total_mat_cost)
        roi_margin = (net_profit / total_revenue * 100) if total_revenue > 0 else 0

        # --- 3. UTILIZATION & BOTTLENECK ---
        total_time = sim_duration
        util_prep = df[df['Stage']=="1. Prep"]['Duration'].sum() / (c_prep * total_time) * 100
        util_mach = df[df['Stage']=="2. Machining"]['Duration'].sum() / (c_machining * total_time) * 100
        util_qc = df[df['Stage']=="3. QC"]['Duration'].sum() / (c_qc * total_time) * 100
        
        utils = {"Prep": util_prep, "Machining": util_mach, "QC": util_qc}
        bottleneck_stage = max(utils, key=utils.get)
        
        st.success("Simulation & Financial Analysis Complete!")

        # --- DASHBOARD ROW 1: FINANCIALS 💰 ---
        st.markdown("### 💰 Financial Performance (8hr Shift)")
        f1, f2, f3, f4 = st.columns(4)
        f1.metric("Total Revenue", f"€ {total_revenue:,.0f}")
        f2.metric("Total Cost (Op + Mat)", f"€ {(total_op_cost + total_mat_cost):,.0f}", delta="Expenses", delta_color="inverse")
        f3.metric("Net Profit", f"€ {net_profit:,.0f}", delta=f"{roi_margin:.1f}% Margin")
        
        # Gauge Chart for OEE/Efficiency
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = utils[bottleneck_stage],
            title = {'text': f"Bottleneck OEE ({bottleneck_stage})"},
            gauge = {'axis': {'range': [0, 100]},
                     'bar': {'color': "darkblue"},
                     'steps' : [
                         {'range': [0, 50], 'color': "#ffcccb"},
                         {'range': [50, 85], 'color': "lightyellow"},
                         {'range': [85, 100], 'color': "lightgreen"}],
                     'threshold' : {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 90}}))
        fig_gauge.update_layout(height=200, margin=dict(l=20,r=20,t=50,b=20))
        
        with f4:
            st.plotly_chart(fig_gauge, use_container_width=True)

        # --- DASHBOARD ROW 2: OPERATIONS ⚙️ ---
        st.markdown("### ⚙️ Operational KPIs")
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Production Output", f"{finished_parts} Units")
        k2.metric("Avg Lead Time", f"{(df['Finish'] - df['Start']).mean():.1f} min")
        k3.metric("Bottleneck Station", f"🚩 {bottleneck_stage}")
        k4.metric("Throughput Rate", f"{finished_parts/shift_hours:.1f} units/hr")

        # --- VISUALIZATION TABS ---
        tab1, tab2 = st.tabs(["🗓️ Gantt Schedule", "📊 Machine Utilization"])
        
        with tab1:
            st.markdown("#### Production Schedule (First 20 Parts)")
            unique_parts = sorted(df['Part'].unique())[:20]
            gantt_df = df[df['Part'].isin(unique_parts)].copy()
            
            fig_gantt = px.timeline(
                gantt_df, x_start="Start_Time", x_end="Finish_Time", y="Part", color="Stage",
                title="Digital Twin Timeline", color_discrete_sequence=px.colors.qualitative.Bold
            )
            fig_gantt.update_yaxes(autorange="reversed") 
            st.plotly_chart(fig_gantt, use_container_width=True)
            
        with tab2:
            util_df = pd.DataFrame({'Stage': list(utils.keys()), 'Utilization (%)': list(utils.values())})
            fig_util = px.bar(util_df, x='Stage', y='Utilization (%)', color='Utilization (%)', 
                              color_continuous_scale='RdYlGn_r', range_y=[0, 100])
            st.plotly_chart(fig_util, use_container_width=True)

        with st.expander("📂 View Detailed Production Logs"):
            st.dataframe(df)
            
    else:
        st.warning("No production. Increase time or arrival rate.")