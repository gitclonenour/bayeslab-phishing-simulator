from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st


st.set_page_config(
    page_title="BayesLab | Phishing Probability Simulator",
    page_icon="🧮",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Styling ----------
st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
        html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
        .stApp { background: #0b1220; color: #e8eef8; }
        [data-testid="stSidebar"] { background: #111b2d; border-right: 1px solid #23324a; }
        [data-testid="stHeader"] { background: rgba(11,18,32,0.92); }
        h1, h2, h3 { font-family: 'Space Grotesk', sans-serif !important; color: #f4f7fb !important; }
        p, label, li { color: #c8d3e3; }
        .hero { padding: 0.5rem 0 1.2rem 0; }
        .eyebrow { color: #55d6be; font-size: .78rem; font-weight: 700; letter-spacing: .15em; text-transform: uppercase; }
        .hero-title { font-family: 'Space Grotesk', sans-serif; font-size: clamp(2rem, 4vw, 3.1rem); line-height: 1.08; font-weight: 700; color: #f6f8fc; margin: .35rem 0 .55rem; }
        .hero-sub { color: #aab9ce; font-size: 1.02rem; max-width: 850px; }
        .panel { background: #121e31; border: 1px solid #263650; border-radius: 16px; padding: 1rem 1.15rem; }
        .kpi-label { color: #9fb0c8; text-transform: uppercase; font-size: .72rem; font-weight: 700; letter-spacing: .09em; }
        .kpi-value { color: #f6f8fc; font-family: 'Space Grotesk', sans-serif; font-size: 2rem; font-weight: 700; margin-top: .15rem; }
        .kpi-note { color: #91a3bd; font-size: .82rem; margin-top: .15rem; }
        .accent { color: #55d6be; }
        .muted { color: #9fb0c8; }
        .small-note { color: #8fa2bd; font-size: .82rem; }
        .result-good { background: rgba(85,214,190,.10); border: 1px solid rgba(85,214,190,.35); border-radius: 14px; padding: 1rem 1.1rem; }
        .result-warn { background: rgba(255,190,92,.09); border: 1px solid rgba(255,190,92,.32); border-radius: 14px; padding: 1rem 1.1rem; }
        div[data-testid="stMetric"] { background: #121e31; border: 1px solid #263650; border-radius: 14px; padding: 13px 16px; }
        div[data-testid="stMetricLabel"] { color: #9fb0c8; }
        div[data-testid="stMetricValue"] { color: #f6f8fc; }
        .stTabs [data-baseweb="tab-list"] { gap: 8px; }
        .stTabs [data-baseweb="tab"] { background: #121e31; border-radius: 10px 10px 0 0; padding: 10px 18px; }
        .stTabs [aria-selected="true"] { background: #1b2b42; }
        .stButton button { border-radius: 10px; font-weight: 600; }
        hr { border-color: #263650; }
        div[data-testid="stAlert"][data-baseweb="notification-warning"] {
            background-color: rgba(255, 193, 7, 0.12) !important;
            border: 1px solid rgba(255, 193, 7, 0.5) !important;
        }

        div[data-testid="stAlert"][data-baseweb="notification-warning"] p {
            color: #FFD54F !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------- Sidebar controls ----------
st.sidebar.markdown("## BayesLab")
st.sidebar.caption("PHISHING PROBABILITY SIMULATOR")
st.sidebar.caption("By Noureldin, Mazin, and Besan.")
st.sidebar.markdown("---")
st.sidebar.markdown("### Scenario inputs")
st.sidebar.caption("Adjust the assumptions. The result updates automatically.")

prevalence_pct = st.sidebar.slider(
    "Phishing prevalence",
    min_value=0,
    max_value=100,
    value=10,
    step=1,
    help="Among all websites being checked, what percentage are actually phishing?",
)
sensitivity_pct = st.sidebar.slider(
    "Detection rate (sensitivity)",
    min_value=0,
    max_value=100,
    value=80,
    step=1,
    help="Of all phishing websites, what percentage does the security system flag?",
)
false_positive_pct = st.sidebar.slider(
    "False positive rate",
    min_value=0,
    max_value=100,
    value=20,
    step=1,
    help="Of all legitimate websites, what percentage does the system incorrectly flag?",
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Simulation settings")
population = st.sidebar.select_slider(
    "Number of websites to simulate",
    options=[1000, 5000, 10000, 25000, 50000, 100000],
    value=10000,
    format_func=lambda x: f"{x:,}",
)
seed = st.sidebar.number_input("Random seed", min_value=0, max_value=999999, value=42, step=1)
st.sidebar.caption("The random seed makes the simulation reproducible.")


# ---------- Probability calculations ----------
p = prevalence_pct / 100.0
sensitivity = sensitivity_pct / 100.0
fpr = false_positive_pct / 100.0
specificity = 1.0 - fpr

# Events: A = website is phishing; B = security system flags the website.
p_flagged_given_phishing = sensitivity
p_flagged_given_legitimate = fpr
p_flagged = (sensitivity * p) + (fpr * (1.0 - p))
p_not_flagged = 1.0 - p_flagged
p_phishing_and_flagged = sensitivity * p
p_legitimate_and_flagged = fpr * (1.0 - p)
p_phishing_given_flagged = (
    p_phishing_and_flagged / p_flagged if p_flagged > 0 else None
)

# Expected confusion-matrix counts for a hypothetical population.
expected = {
    "True positive": population * p * sensitivity,
    "False negative": population * p * (1.0 - sensitivity),
    "False positive": population * (1.0 - p) * fpr,
    "True negative": population * (1.0 - p) * specificity,
}
expected_flagged = expected["True positive"] + expected["False positive"]
expected_not_flagged = expected["False negative"] + expected["True negative"]


# ---------- Header ----------
st.markdown(
    """
    <div class="hero">
      <div class="eyebrow">Probability • Conditional reasoning • Cybersecurity</div>
      <div class="hero-title">Bayes' Theorem, made interactive.</div>
      <div class="hero-sub">Explore a simple but important question: when a security system flags a website, how likely is it that the website is actually phishing?</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Main answer banner
if p_phishing_given_flagged is not None:
    answer_pct = 100 * p_phishing_given_flagged
    st.markdown(
        f"""
        <div class="result-good">
          <div class="kpi-label">Probability a flagged website is actually phishing • P(A | B)</div>
          <div class="kpi-value">{answer_pct:,.2f}%</div>
          <div class="kpi-note">Based on the prevalence, detection rate and false positive rate selected in the sidebar.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        """
        <div class="result-warn">
          <strong>No websites are flagged under the current assumptions.</strong>
          <div class="kpi-note">Bayes' posterior P(A | B) is undefined because P(B) = 0. Increase the detection rate or false positive rate to produce flagged cases.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.write("")

# KPI row
k1, k2, k3, k4 = st.columns(4)
k1.metric("Phishing prevalence", f"{prevalence_pct}%", help="Prior probability P(A).")
k2.metric("Detection rate", f"{sensitivity_pct}%", help="P(B | A): probability a phishing website is flagged.")
k3.metric("False positive rate", f"{false_positive_pct}%", help="P(B | not A): probability a legitimate website is flagged.")
k4.metric("Chance of being flagged", f"{100*p_flagged:.2f}%", help="Total probability P(B).")

st.markdown("---")

# ---------- Tabs ----------
tab_overview, tab_simulation = st.tabs(
    ["01 · Probability breakdown", "02 · Run simulation"]
)

with tab_overview:
    st.subheader("What happens in a population of websites?")
    st.caption(
        f"Expected counts for {population:,} websites using the selected probabilities."
    )

    c1, c2 = st.columns([1.08, 0.92], gap="large")
    with c1:
        matrix_df = pd.DataFrame(
            [
                [expected["True positive"], expected["False negative"]],
                [expected["False positive"], expected["True negative"]],
            ],
            index=["Actually phishing", "Actually legitimate"],
            columns=["Flagged", "Not flagged"],
        )
        display_df = matrix_df.copy().map(lambda x: f"{x:,.1f}")
        st.markdown("#### Outcome table")
        st.dataframe(display_df, use_container_width=True)


        st.markdown("#### How to read the outcomes")
        outcome_cols = st.columns(2)
        outcome_cols[0].markdown(
            f"**<span class='accent'>True positive</span>**  \n{expected['True positive']:,.1f} phishing sites correctly flagged",
            unsafe_allow_html=True,
        )
        outcome_cols[1].markdown(
            f"**False negative**  \n{expected['False negative']:,.1f} phishing sites missed",
            unsafe_allow_html=True,
        )
        outcome_cols[0].markdown(
            f"**False positive**  \n{expected['False positive']:,.1f} legitimate sites incorrectly flagged"
        )
        outcome_cols[1].markdown(
            f"**True negative**  \n{expected['True negative']:,.1f} legitimate sites correctly left unflagged"
        )

    with c2:
        st.markdown("#### Actual condition vs. system decision")
        fig = go.Figure(
            data=go.Heatmap(
                z=[
                    [expected["True positive"], expected["False negative"]],
                    [expected["False positive"], expected["True negative"]],
                ],
                x=["Flagged", "Not flagged"],
                y=["Actually phishing", "Actually legitimate"],
                text=[
                    [f"{expected['True positive']:,.0f}", f"{expected['False negative']:,.0f}"],
                    [f"{expected['False positive']:,.0f}", f"{expected['True negative']:,.0f}"],
                ],
                texttemplate="%{text}",
                textfont={"size": 17, "color": "#f6f8fc"},
                colorscale=[[0, "#1a2a40"], [0.5, "#176e72"], [1, "#55d6be"]],
                showscale=False,
                hovertemplate="%{y}<br>%{x}: %{z:,.1f}<extra></extra>",
            )
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font={"color": "#dce6f3"},
            height=300,
            margin={"l": 10, "r": 10, "t": 15, "b": 10},
            xaxis={"side": "top", "fixedrange": True},
            yaxis={"autorange": "reversed", "fixedrange": True},
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        st.markdown("#### Of all flagged websites...")
        if p_phishing_given_flagged is not None:
            true_share = 100 * p_phishing_given_flagged
            false_share = 100 - true_share
            donut = go.Figure(
                data=[
                    go.Pie(
                        labels=["Actually phishing", "Actually legitimate"],
                        values=[true_share, false_share],
                        hole=0.68,
                        sort=False,
                        marker={"colors": ["#55d6be", "#f3ad55"]},
                        textinfo="none",
                        hovertemplate="%{label}: %{value:.2f}%<extra></extra>",
                    )
                ]
            )
            donut.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                font={"color": "#dce6f3"},
                height=240,
                margin={"l": 5, "r": 5, "t": 5, "b": 5},
                showlegend=True,
                legend={"orientation": "h", "y": -0.08, "x": 0.5, "xanchor": "center"},
                annotations=[
                    {"text": f"{true_share:.1f}%<br><sup>phishing</sup>", "x": 0.5, "y": 0.5, "showarrow": False, "font": {"size": 18, "color": "#f6f8fc"}}
                ],
            )
            st.plotly_chart(donut, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("No flagged websites are expected with these assumptions.")

with tab_simulation:
    st.subheader("Test the theory with a random simulation")
    st.write(
        "The app will generate a hypothetical population, assign each website a true status, and then simulate whether the security system flags it."
    )

    if st.button("Run simulation", type="primary", use_container_width=False):
        rng = np.random.default_rng(int(seed))
        actual_phishing = rng.random(population) < p
        flag_probability = np.where(actual_phishing, sensitivity, fpr)
        flagged = rng.random(population) < flag_probability

        simulated_tp = int(np.sum(actual_phishing & flagged))
        simulated_fn = int(np.sum(actual_phishing & ~flagged))
        simulated_fp = int(np.sum(~actual_phishing & flagged))
        simulated_tn = int(np.sum(~actual_phishing & ~flagged))
        simulated_flagged = simulated_tp + simulated_fp
        simulated_posterior = simulated_tp / simulated_flagged if simulated_flagged else None

        st.session_state["simulation_result"] = {
            "tp": simulated_tp,
            "fn": simulated_fn,
            "fp": simulated_fp,
            "tn": simulated_tn,
            "flagged": simulated_flagged,
            "posterior": simulated_posterior,
            "population": population,
            "seed": int(seed),
            "p": p,
            "sensitivity": sensitivity,
            "fpr": fpr,
        }

    sim = st.session_state.get("simulation_result")
    if sim is not None:
        settings_match = (
            sim["population"] == population
            and sim["seed"] == int(seed)
            and np.isclose(sim["p"], p)
            and np.isclose(sim["sensitivity"], sensitivity)
            and np.isclose(sim["fpr"], fpr)
        )

        # Always compare a simulation with theory calculated from the exact
        # settings that generated that simulation (not the live sidebar values).
        sim_p = sim["p"]
        sim_sensitivity = sim["sensitivity"]
        sim_fpr = sim["fpr"]
        sim_specificity = 1.0 - sim_fpr
        sim_expected = {
            "True positive": sim["population"] * sim_p * sim_sensitivity,
            "False negative": sim["population"] * sim_p * (1.0 - sim_sensitivity),
            "False positive": sim["population"] * (1.0 - sim_p) * sim_fpr,
            "True negative": sim["population"] * (1.0 - sim_p) * sim_specificity,
        }
        sim_p_flagged = sim_sensitivity * sim_p + sim_fpr * (1.0 - sim_p)
        sim_theoretical_posterior = (
            sim_sensitivity * sim_p / sim_p_flagged if sim_p_flagged > 0 else None
        )

        if not settings_match:
            st.warning(
                "These results are from a previous simulation. "
                f"That run used {sim_p:.0%} phishing prevalence, "
                f"{sim_sensitivity:.0%} detection rate, "
                f"{sim_fpr:.0%} false positive rate, and "
                f"{sim['population']:,} websites. The sidebar currently has different settings. "
                "Click **Run simulation** above to generate a new run using the current settings. "
                "The comparison below remains valid because it uses the saved run's original settings."
            )
        else:
            st.success("Simulation settings match the current sidebar inputs.")

        s1, s2, s3 = st.columns(3)
        s1.metric("Websites simulated", f"{sim['population']:,}")
        s2.metric("Websites flagged", f"{sim['flagged']:,}")
        s3.metric(
            "Simulated P(phishing | flagged)",
            f"{100*sim['posterior']:.2f}%" if sim["posterior"] is not None else "Not defined",
        )

        sim_df = pd.DataFrame(
            {
                "Outcome": ["True positive", "False negative", "False positive", "True negative"],
                "Simulated count": [sim["tp"], sim["fn"], sim["fp"], sim["tn"]],
                "Theoretical expected count": [
                    sim_expected["True positive"], sim_expected["False negative"],
                    sim_expected["False positive"], sim_expected["True negative"]
                ],
            }
        )
        st.markdown("#### Simulated outcomes vs. theoretical expectations")
        comp_fig = go.Figure()
        comp_fig.add_trace(go.Bar(name="Simulation", x=sim_df["Outcome"], y=sim_df["Simulated count"], marker_color="#55d6be"))
        comp_fig.add_trace(go.Bar(name="Theory", x=sim_df["Outcome"], y=sim_df["Theoretical expected count"], marker_color="#7188a8"))
        comp_fig.update_layout(
            barmode="group",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font={"color": "#dce6f3"},
            height=350,
            margin={"l": 10, "r": 10, "t": 20, "b": 10},
            yaxis_title="Number of websites",
            legend={"orientation": "h", "y": 1.12, "x": 0},
        )
        st.plotly_chart(comp_fig, use_container_width=True, config={"displayModeBar": False})
        st.dataframe(sim_df.round(1), use_container_width=True, hide_index=True)

        if sim_theoretical_posterior is not None and sim["posterior"] is not None:
            difference = abs(sim["posterior"] - sim_theoretical_posterior) * 100
            st.info(
                f"For the settings used in this run, Bayes' Theorem gives "
                f"{100*sim_theoretical_posterior:.2f}%. The simulation produced "
                f"{100*sim['posterior']:.2f}%, a difference of {difference:.2f} "
                "percentage points. Some variation is expected because this is a random sample; "
                "larger populations generally produce estimates closer to the theoretical result."
            )
        elif sim_theoretical_posterior is None and sim["posterior"] is None:
            st.info("The simulation and the theoretical calculation both produced no flagged websites.")
        else:
            st.warning("The simulation produced no flagged websites, so its conditional probability cannot be estimated in this run.")
    else:
        st.info("Select **Run simulation** to generate websites and compare the simulated result with Bayes' Theorem.")


# ---------- Footer ----------
st.markdown("---")
st.markdown(
    "<div class='small-note'>Made with ♡ by Noureldin, Mazin, and Besan, for MATH 251.</div>",
    unsafe_allow_html=True,
)
