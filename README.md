# BayesLab — Phishing Probability Simulator

An educational Streamlit application demonstrating Bayes' Theorem through a hypothetical phishing-detection scenario.

## Deploy on Streamlit Community Cloud

1. Create a GitHub repository (for example, `bayeslab`).
2. Upload `app.py`, `requirements.txt`, and this `README.md` to the **root** of the repository.
3. Open https://share.streamlit.io/ and sign in with GitHub.
4. Select **Create app** → **Yup, I have an app**.
5. Select your repository, branch (`main`), and app file (`app.py`).
6. Optionally choose an available custom app URL, then select **Deploy**.

No secrets or external data files are required by this app.

## Run locally

Requires Python 3.10 or newer.

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

macOS / Linux:

```bash
source .venv/bin/activate
```

Install dependencies and run:

```bash
pip install -r requirements.txt
streamlit run app.py
```

## What it demonstrates

- Bayes' Theorem using prevalence, detection rate (sensitivity), and false-positive rate.
- A theoretical 2×2 outcome table: true positives, false negatives, false positives, and true negatives.
- A Monte Carlo simulation comparing empirical outcomes with theoretical expectations.

The application has two sections: a probability breakdown and a Monte Carlo simulation. Mathematical theory and worked explanations are covered in the accompanying presentation slides.

## Mathematical model

Let:

- `A` = a website is phishing.
- `B` = the security system flags the website.
- `p = P(A)` = phishing prevalence.
- `s = P(B | A)` = detection rate / sensitivity.
- `f = P(B | Aᶜ)` = false-positive rate.

Then:

`P(A | B) = (s × p) / [(s × p) + (f × (1 − p))]`

If `P(B) = 0`, then `P(A | B)` is undefined because no flagged cases occur under the selected assumptions.

## Important note

The default inputs (10% prevalence, 80% detection rate, and 20% false-positive rate) are hypothetical teaching assumptions, not measured statistics. BayesLab is an educational probability simulator, not a trained phishing detector or a real-world security product.
