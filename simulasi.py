import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import math
import pandas as pd

st.set_page_config(
    page_title="Terminal Performance Simulator",
    page_icon="🚢",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
    .metric-card {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        border: 1px solid #e9ecef;
    }
    .metric-label { font-size: 12px; color: #6c757d; margin-bottom: 4px; }
    .metric-value { font-size: 22px; font-weight: 600; color: #212529; }
    .metric-unit  { font-size: 11px; color: #adb5bd; margin-top: 2px; }
    .badge-ok   { background:#d1f5e3; color:#0a5c36; padding:2px 10px; border-radius:12px; font-size:11px; font-weight:600; }
    .badge-warn { background:#fff3cd; color:#664d03; padding:2px 10px; border-radius:12px; font-size:11px; font-weight:600; }
    .badge-bad  { background:#f8d7da; color:#842029; padding:2px 10px; border-radius:12px; font-size:11px; font-weight:600; }
    .section-hd { font-size:15px; font-weight:600; border-bottom:1px solid #dee2e6; padding-bottom:6px; margin-bottom:12px; margin-top:8px; }
    .tips-box { background:#f0f4f8; border-radius:8px; padding:12px 16px; font-size:13px; color:#495057; }
    .stTabs [data-baseweb="tab"] { font-size: 13px; }
</style>
""", unsafe_allow_html=True)

st.title("🚢 Terminal Performance Simulator")
st.caption("Simulasi performa pelabuhan peti kemas — standar internasional IAPH · PIANC · UNCTAD")

# ─── TABS ───────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "1. Dermaga & QC",
    "2. Yard & RTG",
    "3. TRT & Truck",
    "4. Kapal & Traffic",
    "5. Output KPI"
])

# ════════════════════════════════════════════════════════════════════════════
# TAB 1 — DERMAGA & QC
# ════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown('<div class="section-hd">Infrastruktur dermaga</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        quay_len = st.number_input("Panjang dermaga (m)", 100, 3000, 600, help="Total panjang quay line")
    with c2:
        draft = st.number_input("Kedalaman air / draft (m)", 8, 20, 14)
    with c3:
        ops_hr = st.number_input("Jam operasi / hari", 8, 24, 20)

    st.markdown('<div class="section-hd">Quay Crane (QC / STS)</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        qc_total = st.number_input("Jumlah QC tersedia", 1, 30, 6,
                                    help="Saran: floor(panjang dermaga / 50)")
        qc_avail = st.number_input("QC availability (%)", 50, 100, 90)
        moor_time = st.number_input("Mooring time (menit)", 15, 120, 45)
    with c2:
        bch_input = st.number_input("BCH — Gross (moves/hr/crane)", 10, 45, 22,
                                     help="Termasuk idle & shift change")
        qc_util = st.number_input("QC utilization (%)", 30, 100, 70)
        unmoor_time = st.number_input("Unmooring time (menit)", 10, 90, 30)
    with c3:
        nch_input = st.number_input("NCH — Net (moves/hr/crane)", 15, 50, 28,
                                     help="Saat crane aktif bergerak")
        twin_lift = st.selectbox("Twin-lift capable?", ["Tidak", "Ya (+25% BCH)"])
        hoist_spd = st.number_input("Hoist speed laden (m/min)", 40, 120, 80)

    if st.button("Auto-hitung QC dari panjang dermaga"):
        loa_preview = 220
        slots = math.floor(quay_len / (loa_preview + 25))
        qc_sug = max(2, slots * 2)
        st.info(f"Saran: {slots} berth tersedia → {qc_sug} QC (2 per berth, asumsi LOA avg 220 m). "
                f"Atur LOA di tab Kapal lalu hitung ulang.")

# ════════════════════════════════════════════════════════════════════════════
# TAB 2 — YARD & RTG
# ════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-hd">Layout & Kapasitas Yard</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        yard_ha     = st.number_input("Luas yard (ha)", 1, 200, 25)
        dwell_imp   = st.number_input("Dwell time import (hari)", 1, 20, 4)
        ratio_imp   = st.number_input("Rasio import (%)", 0, 100, 50)
    with c2:
        stack_h     = st.number_input("Stack height (tier)", 2, 8, 4)
        dwell_exp   = st.number_input("Dwell time ekspor (hari)", 1, 10, 2)
        ratio_exp   = st.number_input("Rasio ekspor (%)", 0, 100, 40)
    with c3:
        yard_occ_t  = st.number_input("Yard target occupancy (%)", 30, 95, 70)
        dwell_ts    = st.number_input("Dwell time transship (hari)", 1, 14, 4)
        rehandle    = st.number_input("Rehandle rate (%)", 0, 40, 15)

    st.markdown('<div class="section-hd">RTG (Rubber Tyre Gantry)</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        rtg_count = st.number_input("Jumlah RTG", 1, 60, 12)
        rtg_cycle = st.number_input("RTG cycle time (menit)", 1.0, 8.0, 3.0, step=0.5)
    with c2:
        rtg_mph   = st.number_input("RTG moves/hr (gross)", 6, 28, 15)
        yard_equip = st.selectbox("Alat yard utama", ["RTG", "RMG (Auto)", "Straddle Carrier", "Reach Stacker"])
    with c3:
        rtg_avail = st.number_input("RTG availability (%)", 50, 100, 88)
        teu_dens  = st.number_input("TEU density (TEU/ha)", 200, 1500, 700,
                                     help="RTG~700, RMG~1100, SC~300")

# ════════════════════════════════════════════════════════════════════════════
# TAB 3 — TRT & TRUCK
# ════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-hd">Komponen TRT (Truck Round Trip)</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        gate_in    = st.number_input("Gate-in processing (menit)", 1, 30, 6)
        trav_in    = st.number_input("Travel gate ke yard (menit)", 2, 30, 8)
    with c2:
        stack_time = st.number_input("Stacking/de-stacking RTG (menit)", 3, 45, 12)
        trav_out   = st.number_input("Travel yard ke gate (menit)", 2, 30, 7)
    with c3:
        gate_out   = st.number_input("Gate-out processing (menit)", 1, 20, 4)
        gate_q     = st.number_input("Antrian di gate (menit, avg)", 0, 60, 5)

    st.markdown('<div class="section-hd">Internal Truck (Prime Mover)</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        pm_count   = st.number_input("Jumlah internal truck", 1, 100, 18)
        int_spd    = st.number_input("Kecepatan dalam terminal (km/h)", 10, 40, 20)
    with c2:
        apron_dist = st.number_input("Jarak apron ke yard avg (m)", 50, 1500, 350)
        mob_time   = st.number_input("Waktu mobilisasi truck (menit)", 1, 20, 5)
    with c3:
        headway    = st.number_input("Headway QC-truck target (detik)", 60, 300, 110)
        truck_per_qc = st.number_input("Truck per QC aktif (rasio)", 1.0, 10.0, 4.0, step=0.5)

    st.markdown('<div class="section-hd">Truck Eksternal (Haulier)</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        ext_truck    = st.number_input("Truck eksternal / hari (avg)", 10, 5000, 300)
        phf          = st.number_input("Peak hour factor", 1.0, 4.0, 2.0, step=0.1)
    with c2:
        gate_lanes   = st.number_input("Gate lanes aktif", 1, 20, 4)
        gate_cap_lane = st.number_input("Kapasitas gate/lane (truck/hr)", 10, 60, 28)
    with c3:
        road_spd    = st.number_input("Kecepatan jalan raya (km/h)", 20, 100, 50)
        depot_dist  = st.number_input("Jarak depot rata-rata (km)", 1, 200, 20)

# ════════════════════════════════════════════════════════════════════════════
# TAB 4 — KAPAL & TRAFFIC
# ════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-hd">Karakteristik Kapal</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        loa_avg     = st.number_input("LOA rata-rata (m)", 80, 420, 220)
        ves_cap_teu = st.number_input("Kapasitas rata-rata (TEU)", 200, 24000, 4500)
    with c2:
        call_vol    = st.number_input("Volume per call (% kapasitas)", 10, 100, 55)
        dis_ratio   = st.selectbox("Rasio discharge : load", ["50:50","60:40","70:30","40:60"])
    with c3:
        deep_sea    = st.number_input("% Deep sea vessel", 0, 100, 40)
        eta_var     = st.number_input("Variasi jadwal ETA (±jam)", 0, 24, 6)

    st.markdown('<div class="section-hd">Volume & Traffic</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        calls_yr    = st.number_input("Vessel calls / tahun", 50, 5000, 650)
        teu_target  = st.number_input("Throughput target (TEU/tahun)", 10000, 20000000, 900000, step=50000)
    with c2:
        ts_ratio    = st.number_input("Rasio transshipment (%)", 0, 100, 20)
        pilot_time  = st.number_input("Pilot boarding time (jam)", 0.5, 6.0, 2.0, step=0.5)
    with c3:
        berth_clr   = st.number_input("Clearance antar berth (m)", 10, 60, 25)
        bor_target  = st.number_input("Berth occupancy target (%)", 30, 90, 65)

    st.divider()
    run_btn = st.button("▶  Jalankan Simulasi & Hitung KPI", type="primary", use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# TAB 5 — OUTPUT KPI  (calculated on button press)
# ════════════════════════════════════════════════════════════════════════════
with tab5:
    if not run_btn:
        st.info("Isi parameter di tab 1–4, lalu klik **Jalankan Simulasi** untuk melihat hasil.")
    else:
        # ── Derived inputs ──────────────────────────────────────────────
        bch = bch_input * 1.25 if twin_lift == "Ya (+25% BCH)" else bch_input
        ratio_ts_pct = max(0, 100 - ratio_imp - ratio_exp)
        dis_pct = int(dis_ratio.split(":")[0]) / 100

        # ── DERMAGA ─────────────────────────────────────────────────────
        berth_slots  = math.floor(quay_len / (loa_avg + berth_clr))
        qc_per_vessel = max(2, min(5, math.floor(loa_avg / 50)))
        qc_active    = min(qc_total, berth_slots * qc_per_vessel)
        bsh          = bch * qc_per_vessel
        moves_per_call = round(ves_cap_teu * call_vol / 100)
        svc_time_hr  = (moves_per_call / bsh) + (moor_time + unmoor_time) / 60
        total_berth_hr_yr = calls_yr * svc_time_hr
        berth_cap_hr_yr   = berth_slots * ops_hr * 365
        bor           = total_berth_hr_yr / berth_cap_hr_yr if berth_cap_hr_yr > 0 else 0
        qc_eff_bch    = bch * (qc_avail / 100) * (qc_util / 100)
        term_cap_qc_yr = qc_total * qc_eff_bch * ops_hr * 365

        # Waiting time (simplified Erlang-C approximation)
        if   bor < 0.70: wait_factor = 0.05
        elif bor < 0.80: wait_factor = 0.15
        elif bor < 0.90: wait_factor = 0.40
        else:            wait_factor = 0.80
        avg_wait_hr  = svc_time_hr * wait_factor
        port_time    = avg_wait_hr + pilot_time + svc_time_hr
        vtt          = svc_time_hr + (moor_time + unmoor_time) / 60 + avg_wait_hr

        # ── YARD ────────────────────────────────────────────────────────
        yard_cap_teu = round(yard_ha * teu_dens * (yard_occ_t / 100))
        avg_dwell = (
            dwell_imp * (ratio_imp / 100) +
            dwell_exp * (ratio_exp / 100) +
            dwell_ts  * (ratio_ts_pct / 100)
        )
        yard_thru_yr       = round(yard_cap_teu / avg_dwell * 365) if avg_dwell > 0 else 0
        yard_move_per_teu  = (
            (ratio_imp / 100) * 3 +
            (ratio_exp / 100) * 3 +
            (ratio_ts_pct / 100) * 1
        ) * (1 + rehandle / 100)
        total_yard_moves_yr = round(teu_target * yard_move_per_teu)
        rtg_cap_yr          = rtg_count * rtg_mph * (rtg_avail / 100) * ops_hr * 365
        rtg_util            = total_yard_moves_yr / rtg_cap_yr if rtg_cap_yr > 0 else 0
        rtg_needed          = math.ceil(
            total_yard_moves_yr / (rtg_mph * (rtg_avail / 100) * ops_hr * 365)
        ) if rtg_mph > 0 else rtg_count

        # ── TRT ─────────────────────────────────────────────────────────
        trt_loaded      = gate_in + trav_in + stack_time + trav_out + gate_out + gate_q
        trt_empty       = gate_in + trav_in*0.8 + stack_time*0.7 + trav_out*0.8 + gate_out + gate_q*0.5
        int_travel_time = (apron_dist / 1000) / (int_spd / 60)
        int_truck_cycle = int_travel_time * 2 + stack_time + mob_time
        int_truck_needed = math.ceil(qc_active * truck_per_qc)
        gate_peak_cap   = gate_lanes * gate_cap_lane
        peak_trucks     = round(ext_truck * phf / 8)
        gate_util       = peak_trucks / gate_peak_cap if gate_peak_cap > 0 else 0
        ext_trip_time   = round((depot_dist / road_spd) * 60 * 2 + trt_loaded)

        # ── THROUGHPUT ─────────────────────────────────────────────────
        teu_per_meter = teu_target / quay_len if quay_len > 0 else 0
        teu_per_ha    = teu_target / yard_ha  if yard_ha  > 0 else 0
        teu_per_qc    = teu_target / qc_total if qc_total > 0 else 0
        teu_per_rtg   = teu_target / rtg_count if rtg_count > 0 else 0
        bottleneck    = "Quayside (QC)" if term_cap_qc_yr < yard_thru_yr else "Yard (RTG)"

        # ─────────────────────────────────────────────────────────────────
        # RENDER OUTPUT
        # ─────────────────────────────────────────────────────────────────

        # Headline KPI cards
        st.markdown("### Ringkasan KPI Utama")
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Kapasitas Throughput", f"{round(term_cap_qc_yr/1000):,}K TEU/thn")
        k2.metric("Vessel Turnaround", f"{vtt:.1f} jam")
        k3.metric("TRT Truck Loaded", f"{round(trt_loaded)} menit")
        k4.metric("BOR Aktual", f"{bor*100:.1f}%")

        st.divider()

        # ── Section 1: Dermaga ──────────────────────────────────────────
        col_l, col_r = st.columns(2)

        with col_l:
            st.markdown('<div class="section-hd">Kinerja Dermaga & Quay Crane</div>', unsafe_allow_html=True)
            def badge(val, good, warn, invert=False):
                if not invert:
                    if val >= good: return "🟢 Baik"
                    if val >= warn: return "🟡 Perhatian"
                    return "🔴 Kritis"
                else:
                    if val <= good: return "🟢 Baik"
                    if val <= warn: return "🟡 Perhatian"
                    return "🔴 Kritis"

            df_quay = pd.DataFrame({
                "Parameter": [
                    "Berth tersedia","QC per kapal","BCH gross","BSH per kapal",
                    "Service time/call","Berth Occupancy (BOR)","Vessel Turnaround","Avg Vessel Waiting","Total Port Time","QC Eff. BCH"
                ],
                "Nilai": [
                    f"{berth_slots}", f"{qc_per_vessel}", f"{bch:.0f} moves/hr/crane",
                    f"{bsh:.0f} moves/hr", f"{svc_time_hr:.1f} jam", f"{bor*100:.1f}%",
                    f"{vtt:.1f} jam", f"{avg_wait_hr:.1f} jam", f"{port_time:.1f} jam",
                    f"{qc_eff_bch:.1f} moves/hr"
                ],
                "Status": [
                    "—", "—",
                    badge(bch, 22, 18), badge(bsh, 80, 60),
                    "—", badge(bor*100, 70, 80, invert=True),
                    badge(vtt, 24, 36, invert=True), badge(avg_wait_hr, 4, 12, invert=True),
                    "—", "—"
                ]
            })
            st.dataframe(df_quay, use_container_width=True, hide_index=True)

        with col_r:
            st.markdown('<div class="section-hd">Kinerja Yard & RTG</div>', unsafe_allow_html=True)
            rtg_status = "🟢 Cukup" if rtg_count >= rtg_needed else f"🔴 Kurang {rtg_needed - rtg_count}"
            df_yard = pd.DataFrame({
                "Parameter": [
                    "Kapasitas yard","Avg dwell time (blended)","Yard thru. kapasitas",
                    "Total yard moves/thn","Yard moves per TEU","RTG utilization",
                    "RTG dibutuhkan","TEU per hektar"
                ],
                "Nilai": [
                    f"{yard_cap_teu:,} TEU", f"{avg_dwell:.1f} hari",
                    f"{yard_thru_yr:,} TEU/thn", f"{total_yard_moves_yr:,} moves",
                    f"{yard_move_per_teu:.2f}", f"{rtg_util*100:.1f}%",
                    f"{rtg_needed} unit", f"{round(teu_per_ha):,} TEU/ha/thn"
                ],
                "Status": [
                    "—","—","—","—","—",
                    badge(rtg_util*100, 80, 90, invert=True),
                    rtg_status, "—"
                ]
            })
            st.dataframe(df_yard, use_container_width=True, hide_index=True)

        # ── Section 2: TRT & Throughput ────────────────────────────────
        col_l2, col_r2 = st.columns(2)

        with col_l2:
            st.markdown('<div class="section-hd">TRT & Pergerakan Truck</div>', unsafe_allow_html=True)
            pm_status = "🟢 Cukup" if pm_count >= int_truck_needed else f"🔴 Kurang {int_truck_needed - pm_count}"
            df_trt = pd.DataFrame({
                "Parameter": [
                    "TRT truck loaded","TRT truck empty",
                    "Internal truck dibutuhkan","Int. truck cycle time",
                    "Gate kapasitas peak","Truck peak/jam (est.)",
                    "Gate utilization peak","Trip waktu total (ext.)"
                ],
                "Nilai": [
                    f"{round(trt_loaded)} menit", f"{round(trt_empty)} menit",
                    f"{int_truck_needed} unit", f"{int_truck_cycle:.1f} menit",
                    f"{round(gate_peak_cap)} truck/jam", f"{peak_trucks} truck/jam",
                    f"{gate_util*100:.1f}%", f"{ext_trip_time} menit"
                ],
                "Status": [
                    badge(trt_loaded, 45, 65, invert=True),
                    "—", pm_status, "—", "—",
                    badge(peak_trucks/gate_peak_cap*100 if gate_peak_cap>0 else 0, 80, 95, invert=True),
                    badge(gate_util*100, 80, 95, invert=True), "—"
                ]
            })
            st.dataframe(df_trt, use_container_width=True, hide_index=True)

        with col_r2:
            st.markdown('<div class="section-hd">Kapasitas & Throughput Terminal</div>', unsafe_allow_html=True)
            df_thru = pd.DataFrame({
                "Parameter": [
                    "Target throughput","Kapasitas QC (max)","Kapasitas yard",
                    "Bottleneck","TEU per meter dermaga",
                    "TEU per hektar","TEU per QC","TEU per RTG"
                ],
                "Nilai": [
                    f"{teu_target:,} TEU/thn", f"{round(term_cap_qc_yr):,} TEU/thn",
                    f"{yard_thru_yr:,} TEU/thn", bottleneck,
                    f"{round(teu_per_meter):,} TEU/m/thn",
                    f"{round(teu_per_ha):,} TEU/ha/thn",
                    f"{round(teu_per_qc):,} TEU/QC/thn",
                    f"{round(teu_per_rtg):,} TEU/RTG/thn"
                ],
                "Status": ["—","—","—",
                    "🔴 QC" if bottleneck=="Quayside (QC)" else "🟡 Yard",
                    "—","—","—","—"]
            })
            st.dataframe(df_thru, use_container_width=True, hide_index=True)

        # ── Scorecard ─────────────────────────────────────────────────
        st.markdown('<div class="section-hd">Scorecard Performa — Benchmark Internasional (IAPH · PIANC)</div>',
                    unsafe_allow_html=True)

        scores = [
            ("BCH gross",          bch,           "moves/hr",  22,  18, False, "#185FA5"),
            ("BSH per kapal",      bsh,           "moves/hr",  80,  60, False, "#185FA5"),
            ("Berth Occupancy",    bor*100,       "%",         70,  80, True,  None),
            ("Vessel Turnaround",  vtt,           "jam",       24,  36, True,  None),
            ("Avg Wait Time",      avg_wait_hr,   "jam",       4,   12, True,  None),
            ("RTG Utilization",    rtg_util*100,  "%",         75,  60, False, "#7F77DD"),
            ("TRT Loaded",         trt_loaded,    "menit",     45,  65, True,  None),
            ("Gate Peak Util.",    gate_util*100, "%",         80,  90, True,  None),
        ]

        sc_names, sc_vals, sc_colors, sc_targets = [], [], [], []
        for name, val, unit, good, warn, invert, col in scores:
            sc_names.append(f"{name} ({unit})")
            sc_vals.append(round(val, 1))
            if invert:
                color = "#1D9E75" if val<=good else "#BA7517" if val<=warn else "#E24B4A"
            else:
                color = "#1D9E75" if val>=good else "#BA7517" if val>=warn else "#E24B4A"
            sc_colors.append(color)
            sc_targets.append(good)

        fig_score = go.Figure()
        fig_score.add_trace(go.Bar(
            x=sc_vals, y=sc_names,
            orientation='h',
            marker_color=sc_colors,
            text=[str(v) for v in sc_vals],
            textposition='outside',
        ))
        fig_score.update_layout(
            height=320, margin=dict(l=10,r=60,t=10,b=10),
            xaxis_title=None, yaxis_title=None,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=True, gridcolor='#f0f0f0'),
        )
        st.plotly_chart(fig_score, use_container_width=True)

        # ── Chart 1: Utilisasi komponen ───────────────────────────────
        st.markdown('<div class="section-hd">Utilisasi komponen vs target</div>', unsafe_allow_html=True)
        labels = ["QC Availability", "QC Utilization", "RTG Utilization", "Berth Occupancy", "Gate Peak"]
        aktual = [qc_avail, qc_util, rtg_util*100, bor*100, gate_util*100]
        target = [95, 80, 80, 70, 90]

        fig1 = go.Figure()
        fig1.add_trace(go.Bar(name="Aktual", x=labels, y=[round(v,1) for v in aktual],
                               marker_color=["#B5D4F4","#B5D4F4","#AFA9EC","#F0997B","#9FE1CB"],
                               marker_line_color=["#185FA5","#185FA5","#534AB7","#D85A30","#1D9E75"],
                               marker_line_width=1.5))
        fig1.add_trace(go.Scatter(name="Target max", x=labels, y=target, mode="lines+markers",
                                   line=dict(color="#888780", dash="dot", width=2),
                                   marker=dict(symbol="triangle-up", size=8)))
        fig1.update_layout(
            height=280, margin=dict(l=10,r=10,t=10,b=10),
            yaxis=dict(title="%", range=[0, 115]),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=False), yaxis_gridcolor='#f0f0f0'
        )
        st.plotly_chart(fig1, use_container_width=True)

        # ── Chart 2: Dekomposisi waktu kapal ─────────────────────────
        st.markdown('<div class="section-hd">Dekomposisi waktu kapal di pelabuhan</div>', unsafe_allow_html=True)
        fig2 = go.Figure()
        moor_total = (moor_time + unmoor_time) / 60
        fig2.add_trace(go.Bar(name="Waiting (jam)", y=["Waktu kapal"], x=[round(avg_wait_hr,2)],
                               orientation='h', marker_color="#9FE1CB", marker_line_color="#1D9E75", marker_line_width=1))
        fig2.add_trace(go.Bar(name="Pilot+Moor (jam)", y=["Waktu kapal"], x=[round(pilot_time+moor_total,2)],
                               orientation='h', marker_color="#B5D4F4", marker_line_color="#185FA5", marker_line_width=1))
        fig2.add_trace(go.Bar(name="Service time (jam)", y=["Waktu kapal"], x=[round(svc_time_hr,2)],
                               orientation='h', marker_color="#AFA9EC", marker_line_color="#534AB7", marker_line_width=1))
        fig2.update_layout(
            barmode='stack', height=160, margin=dict(l=10,r=10,t=10,b=10),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            xaxis=dict(title="Jam"),
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        )
        st.plotly_chart(fig2, use_container_width=True)

        # ── Chart 3: Dekomposisi TRT ──────────────────────────────────
        st.markdown('<div class="section-hd">Dekomposisi TRT truck</div>', unsafe_allow_html=True)
        trt_components = {
            "Gate-in":  [gate_in,           gate_in],
            "Travel":   [trav_in+trav_out,  round((trav_in+trav_out)*0.8)],
            "Stacking": [stack_time,         round(stack_time*0.7)],
            "Gate-out": [gate_out,           gate_out],
            "Queue":    [gate_q,             round(gate_q*0.5)],
        }
        trt_colors = {"Gate-in":"#F5C4B3","Travel":"#B5D4F4","Stacking":"#AFA9EC","Gate-out":"#9FE1CB","Queue":"#FAC775"}
        fig3 = go.Figure()
        for comp, vals in trt_components.items():
            fig3.add_trace(go.Bar(
                name=comp, x=["TRT Loaded","TRT Empty"], y=vals,
                marker_color=trt_colors[comp]
            ))
        fig3.update_layout(
            barmode='stack', height=280, margin=dict(l=10,r=10,t=10,b=10),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            yaxis=dict(title="Menit"),
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=False), yaxis_gridcolor='#f0f0f0'
        )
        st.plotly_chart(fig3, use_container_width=True)

        # ── Rekomendasi ───────────────────────────────────────────────
        st.markdown('<div class="section-hd">Rekomendasi Operasional</div>', unsafe_allow_html=True)
        tips = []
        if bor > 0.75:
            tips.append(f"BOR {bor*100:.1f}% melebihi target 70% → antrian kapal akan meningkat tajam. "
                        "Pertimbangkan penambahan berth atau pembatasan vessel calls.")
        if bch < 20:
            tips.append(f"BCH {bch:.0f} di bawah rata-rata internasional (22–28). "
                        "Evaluasi kecepatan hoist/trolley, cycle time, dan operator performance.")
        if rtg_util > 0.85:
            tips.append(f"Utilisasi RTG {rtg_util*100:.1f}% sudah tinggi. "
                        f"Disarankan tambah {max(1, rtg_needed - rtg_count)} RTG untuk buffer.")
        if trt_loaded > 55:
            tips.append(f"TRT loaded {round(trt_loaded)} menit di atas benchmark (25–55 menit). "
                        "Evaluasi gate processing dan yard stacking time.")
        if gate_util > 0.9:
            tips.append(f"Gate peak utilization {gate_util*100:.1f}% kritis. "
                        "Aktifkan truck appointment system (TAS) atau tambah gate lane.")
        if pm_count < int_truck_needed:
            tips.append(f"Internal truck ({pm_count}) kurang dari kebutuhan ({int_truck_needed}). "
                        "QC berpotensi idle menunggu truck.")
        if not tips:
            tips.append("Semua parameter dalam batas normal. Terminal beroperasi dengan performa baik "
                        "sesuai benchmark internasional (IAPH/PIANC).")

        for t in tips:
            st.markdown(f"• {t}")

        st.divider()
        st.caption("Sumber benchmark: IAPH Study on Productivity 2016 · PIANC Rec. 1992 & Report 2023 · "
                   "Portwise TRAFALQUAR · TBA Group Simulation Whitepaper · UNCTAD Port Performance Indicators")
