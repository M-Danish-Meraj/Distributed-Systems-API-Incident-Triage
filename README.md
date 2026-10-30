# API Incident Triage – Expert System

**Course:** Introduction to AI  **Student:** Muhammad Danish Meraj (CT-24268)

A rule-based (symbolic AI) expert system that acts like a virtual
**Site Reliability Engineer**. You describe what is broken in your web app / API,
it asks a few yes/no questions and tells you the **root cause**, **which layer
failed**, **how to fix it** and **why** it reached that conclusion.

No machine learning is used – only IF–THEN rules written by hand.

Live app: `<paste your streamlit.app link here>`

---

## Files

| File | What it contains |
|---|---|
| `knowledge_base.py` | The **knowledge** – questions, keywords, 60+ rules, diagnoses + fixes |
| `engine.py` | The **inference engine** – keyword NLP, forward chaining, next-question choice, explanation |
| `app.py` | The **Streamlit UI** |
| `requirements.txt` | Python packages needed (only `streamlit`) |

## How it works (explain it like this)

1. **Facts** – small statements such as `http_504` ("requests fail with 504")
   that are either *yes* or *no*.
2. **NLP (keyword matching)** – the sentence the user types is lower-cased and
   searched for known phrases (`"timeout" → http_504`, `"forbidden" → http_403`).
   Every match becomes a *yes* fact, so those questions are never asked.
3. **Rules** – `IF http_401 AND token_expired THEN TOKEN_EXPIRED`.
   Each rule has a **certainty factor (CF)**, e.g. 0.9 = 90 % confidence.
4. **Inference (forward chaining)** – the engine checks every rule:
   * all conditions *yes* → rule **fires** → diagnosis found
   * any condition *no* → rule **fails** (ignored from now on)
   * otherwise the rule is still **open**
5. **Choosing the next question** – from the open rules, take the one that has
   the most *yes* conditions already (closest to firing) and ask its first
   unknown condition. That is why irrelevant questions are skipped.
6. **Explanation** – the fired rule and the answers that made it true are
   shown under "How did I reach this?".

```
user text ──► NLP (keywords) ──► facts ──► inference engine ◄── knowledge base
                                              │    ▲
                                    question ◄┘    └── yes / no answer
                                              │
                                              ▼
                                diagnosis + fix + explanation
```

## Run on your laptop

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```
Opens at http://localhost:8501

## Make it live on the internet (Streamlit Community Cloud – free)

1. Create a **public** GitHub repo (e.g. `api-triage-expert-system`) and push
   this folder:
   ```bash
   git add .
   git commit -m "Expert system"
   git branch -M main
   git remote add origin https://github.com/<your-username>/api-triage-expert-system.git
   git push -u origin main
   ```
2. Go to **https://share.streamlit.io** → *Sign in with GitHub*.
3. Click **Create app** → *Deploy a public app from GitHub* → choose the repo,
   branch `main`, main file `app.py` → **Deploy**.
4. After ~2 minutes you get a link like `https://<name>.streamlit.app`
   that works from any network (WAN). Put it at the top of this README.

Note: free apps sleep after a few days without visitors. Open the link before
your demo so it wakes up (~30 seconds).

## Demo sentences to try

* `Users get 504 timeout on checkout and the database is slow`
* `Login fails with 401 unauthorized after some time`
* `Admin page returns 403 forbidden for some users`
* `Browser console shows CORS error and the page is blank`
* `API returns 429 too many requests`
