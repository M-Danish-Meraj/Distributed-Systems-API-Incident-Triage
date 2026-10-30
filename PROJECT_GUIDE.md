# Project Guide – API Incident Triage Expert System

**Course:** Introduction to AI  **Student:** Muhammad Danish Meraj (CT-24268)  **Instructor:** Sir Wasiq Noor
**Repo:** https://github.com/M-Danish-Meraj/Distributed-Systems-API-Incident-Triage
**Live app:** `<paste your streamlit.app link here>`

This file explains everything: what the project is, how each part works, how to
run it, every rule in the knowledge base, and the questions you may be asked
in the viva (with answers).

---

## 1. What is the project? (one-paragraph answer)

It is a **rule-based expert system** for **Distributed Systems & API Incident
Triage**. When a web app or API breaks, the user describes the problem in plain
English (e.g. *"Users get 504 timeout and the database is slow"*). The system
picks up keywords from the sentence, asks a few yes/no questions, applies
IF–THEN rules and tells the user **the root cause, which layer failed, how
confident it is, how to fix it, and why it reached that conclusion**. It works
like a virtual **Site Reliability Engineer (SRE)**. It uses **symbolic AI only**
– no machine learning.

### Requirements vs. what was built

| Requirement | Status |
|---|---|
| Expert system in Python | ✅ Pure Python |
| Minimum 50 conditions | ✅ **79 rules, 179 conditions** |
| Unique niche | ✅ API / distributed-systems incident triage |
| UI with Streamlit only | ✅ `app.py` uses only Streamlit |
| Live over the internet (WAN) | ✅ Deployed on Streamlit Community Cloud |

> Note: the original proposal said "CLI". It was changed to a Streamlit web UI
> to meet the course requirement. The reasoning part is unchanged.

---

## 2. Project files

| File | Role | Size |
|---|---|---|
| `knowledge_base.py` | **Knowledge base** – questions, keywords, rules, diagnoses + fixes | 50 facts, 159 keywords, 79 rules, 27 diagnoses |
| `engine.py` | **Inference engine** – NLP, forward chaining, conflict resolution, next question, explanation | ~110 lines |
| `app.py` | **User interface** (Streamlit) – input, questions, result | ~190 lines |
| `requirements.txt` | Python packages needed online (`streamlit`) | |
| `README.md` | Short intro + deploy steps | |

The **knowledge is separate from the reasoning**. To add knowledge you only
edit `knowledge_base.py`; the engine does not change. This separation is the
main idea of an expert system.

```
 user sentence ─► NLP (keywords) ─► facts ─► INFERENCE ENGINE ◄── KNOWLEDGE BASE
                                                │    ▲              (rules)
                                    question ◄──┘    └── yes / no
                                                │
                                                ▼
                               diagnosis + fix + confidence + explanation
```

---

## 3. How it works – step by step

### 3.1 Facts
A **fact** is a short yes/no statement, e.g. `http_504` = "requests fail with
HTTP 504". There are 50 facts, and each has a question in `QUESTIONS`.
All known facts are stored in the **working memory**, a dictionary:

```python
answers = {"http_504": True, "db_queries_slow": True, "recent_deploy": False}
```

### 3.2 NLP – keyword matching (`extract_facts`)
1. The sentence is converted to lower case.
2. Each phrase in `KEYWORDS` is searched with a regular expression using `\b`
   (word boundary), so `"401"` doesn't match inside `"14010"`.
3. Each phrase found sets its fact to **True**, so that question is skipped.

```
"Users get 504 timeout and the database is slow"
   "504"              → http_504
   "database is slow" → db_queries_slow
```

### 3.3 Rules
```python
{"id": "R52", "if": ["http_504", "db_queries_slow"], "then": "DB_SLOW_QUERY", "cf": 0.85}
```
= **IF** 504 errors **AND** slow database queries **THEN** slow query / missing
index, with **certainty factor 0.85 (85 %)**.

Each rule is in one of three states (`rule_status`):

| State | Meaning |
|---|---|
| **fired** | all conditions are True |
| **failed** | at least one condition is False, so it can never fire |
| **open** | some conditions are still unknown |

### 3.4 Inference – forward chaining (`find_diagnosis`)
Forward chaining is **data-driven**: start from the known facts and fire every
rule whose conditions are all true.

**Conflict resolution by specificity:** if more than one rule fires, the rule
with the **most conditions** wins, because it is more specific. If a more
specific rule could still fire (it contains all the conditions of the winner
and is still open), the engine **asks more questions first**.
Example: R52 (`504 + slow DB`) has fired, but R27 (`504 + slow DB + recent
deploy`) is still open, so the engine asks "Was there a recent deploy?" before
it decides.

### 3.5 Choosing the next question (`next_question`)
1. Keep only the **open** rules.
2. From those, keep the ones **closest to firing** (most conditions already True).
3. Ask about the unknown fact that appears in **most** of those rules, because
   its answer confirms or removes the most rules at once.

This is why irrelevant questions are never asked: a database question is not
asked when the user is talking about login, and so on.

### 3.6 Result + explanation (`explain`)
The UI shows the diagnosis name, its layer, its confidence (CF), a description,
the fix steps, and **"How did I reach this?"**: the true conditions and the
rule that fired. This is the **explanation facility** of the expert system.

### 3.7 Worked examples (real output of the engine)

**Example 1:** *"Users get 504 timeout on checkout and the database is slow"*
| Step | What happens |
|---|---|
| NLP | `http_504 = True`, `db_queries_slow = True` |
| R52 fires, but R27 (more specific) is still open | Q: *Did the errors start right after a new deployment/release?* → **No** |
| R27 failed, so R52 is the most specific fired rule | **Diagnosis: Slow query / missing index**, Database layer, 85 % |

**Example 2:** *"Login fails with 401 unauthorized"*
| Step | What happens |
|---|---|
| NLP | `area_login = True`, `http_401 = True` |
| Most open rules contain `token_expired_msg` | Q: *Does the error say the token/session has expired?* → **Yes** |
| R63 fires, but R60 (clock skew) is still open | Q: *Do server clocks differ, or does the error say the token is 'not yet valid'?* → **No** |
| R63 wins | **Diagnosis: Access token expired**, Authentication layer, 95 % |

### 3.8 The Streamlit UI (`app.py`)
Three stages are stored in `st.session_state.stage`:
1. **describe**: text box + sample incidents + *Analyze* button (runs the NLP)
2. **questions**: Yes / No / Don't know buttons, plus *Undo last answer*
3. **result**: diagnosis, layer, confidence bar, fix steps, reasoning, all answers

The sidebar shows the number of rules, conditions and diagnoses, a *Start over*
button and *Show knowledge base* (a table of all rules).

Streamlit **re-runs the whole script on every click**, so the answers and the
current stage are kept in `st.session_state`, and `st.rerun()` moves the app to
the next stage.

---

## 4. How to run it from the terminal

### First time only (setup)
Open a terminal (PowerShell or Git Bash) in the project folder:

```bash
cd "D:\expert system iai"
```
Create a virtual environment (a private Python just for this project):
```bash
python -m venv .venv
```
Activate it – **PowerShell**:
```bash
.venv\Scripts\Activate.ps1
```
…or **Git Bash**:
```bash
source .venv/Scripts/activate
```
Install Streamlit:
```bash
pip install -r requirements.txt
```

> If PowerShell says "running scripts is disabled", run this once:
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

### Every time (run the app)
```bash
cd "D:\expert system iai"
```
```bash
.venv\Scripts\Activate.ps1
```
```bash
streamlit run app.py
```
The browser opens **http://localhost:8501**. Press **Ctrl + C** in the
terminal to stop the app.

Shortcut without activating:
```bash
.venv\Scripts\streamlit run app.py
```

### Update the live app after a change
```bash
git add .
```
```bash
git commit -m "describe your change"
```
```bash
git push
```
Streamlit Cloud redeploys automatically in about a minute.

---

## 5. Viva questions and answers

### A. Expert system basics
**Q: What is an expert system?**
A program that copies the decision-making of a human expert in one narrow
domain, using knowledge written as rules. Mine copies an SRE diagnosing
outages.

**Q: What are its main components?**
1) **Knowledge base**: the rules and facts (`knowledge_base.py`).
2) **Inference engine**: applies the rules (`engine.py`).
3) **Working memory**: the facts known so far (the `answers` dictionary).
4) **User interface**: `app.py`.
5) **Explanation facility**: the "How did I reach this?" section.

**Q: Is this AI if there's no machine learning?**
Yes. It is **symbolic AI** (classical / GOFAI): knowledge is written as
explicit logic rules and a reasoning algorithm draws conclusions. Machine
learning is a different branch of AI that learns patterns from data.

**Q: Why rules instead of ML?**
- There's no labelled outage dataset.
- Rules are **explainable**: every answer can be justified.
- Rules are easy to check and update.
- The course asked for an expert system.

**Q: Who is the "expert" here?**
The knowledge comes from standard SRE/DevOps practice: the meanings of HTTP
status codes, common database and authentication failures, and standard fixes.

### B. Inference
**Q: Forward or backward chaining?**
**Forward chaining** (data-driven): it starts from the facts the user gives
and fires rules whose conditions are all true. Question selection is goal-guided:
it asks about the rules closest to firing.

**Q: Difference between forward and backward chaining?**
Forward: facts → conclusions (data-driven). Backward: start from a goal or
hypothesis and check whether its conditions are true (goal-driven, e.g. Prolog,
MYCIN).

**Q: What is conflict resolution? Which strategy do you use?**
When several rules can fire, the engine must pick one. I use **specificity**:
the rule with the most conditions wins, and the engine waits if a more specific
rule could still fire. Other strategies are rule order (priority), recency,
and the highest certainty factor.

**Q: What is a certainty factor (CF)?**
A number from 0 to 1 that shows how confident the expert is in a rule's
conclusion. Specific rules have a higher CF (e.g. 0.9) and general rules a
lower one (e.g. 0.65). It is shown as the confidence percentage.

**Q: How do you decide which question to ask next?**
From the rules that can still fire, I take the ones with the most true
conditions and ask the unknown fact that appears in most of them. One answer
then removes or confirms the most rules.

**Q: What happens if no rule matches?**
The app says no rule matched, shows all the answers and asks the user to
give more detail.

**Q: What does "Don't know" do?**
It is treated as **No** (not observed). This keeps the logic simple. A
limitation is that the system can't reason with unknowns.

**Q: How many rules and conditions?**
**79 rules, 179 conditions** (each rule has 2–3), 50 facts, 27 diagnoses,
6 layers.

**Q: How do you add a new rule?**
Add one dictionary to `RULES` in `knowledge_base.py` (and a question and
keyword if it uses a new fact). The engine and UI don't change.

### C. NLP
**Q: How does the NLP work?**
It lower-cases the sentence, then matches phrases from the `KEYWORDS`
dictionary using regular expressions with word boundaries. Each match becomes a
True fact. It uses only Python's built-in `re` module, with no external NLP
library.

**Q: Limitations of keyword NLP?**
- It does not understand negation ("**not** a 504" still matches 504).
- It misses spelling mistakes.
- It needs phrases listed in advance.

The follow-up questions make up for missed keywords.

### D. Domain (computer networking / web) questions
| Term | Meaning |
|---|---|
| **400** Bad Request | The server cannot parse the request (e.g. malformed JSON) |
| **401** Unauthorized | Not authenticated: the token is missing, expired or invalid |
| **403** Forbidden | Authenticated but **not allowed**: a missing role or permission (RBAC) |
| **413** Payload Too Large | The request body is bigger than the server limit |
| **422** Unprocessable Entity | Valid JSON but wrong fields or types (schema mismatch) |
| **429** Too Many Requests | Rate limit exceeded |
| **500** Internal Server Error | Unhandled exception / bug in the backend |
| **502** Bad Gateway | The gateway got an invalid response; the upstream service is down or crashing |
| **503** Service Unavailable | The service is overloaded or in maintenance |
| **504** Gateway Timeout | The upstream was too slow (slow DB, slow third party) |
| **CORS** | Browser security that blocks calls to another domain unless the server allows it |
| **Connection pool exhaustion** | All DB connections are in use, so new requests wait or fail |
| **Deadlock** | Two transactions each wait for a lock the other holds |
| **Replica lag** | A read copy of the DB is behind the main copy, so reads return stale data |
| **JWT** | A signed token used for login; expires after some time |
| **Clock skew** | Server clocks differ, so a valid token looks expired or not yet valid |
| **RBAC** | Role-Based Access Control: permissions given by role |
| **SRE** | Site Reliability Engineer: keeps production systems running |
| **Microservices** | An app split into small services that call each other over the network |

**Q: 401 vs 403?** 401 means *who are you?* (bad or missing identity). 403
means *I know you, but you're not allowed* (missing permission).

**Q: 502 vs 503 vs 504?** 502 is a bad or no response from the upstream. 503 is
an overloaded or unavailable service. 504 is an upstream that responded too slowly.

### E. Streamlit / deployment
**Q: Why Streamlit?** It builds a web UI in pure Python with no HTML or JS,
and the course requires it.

**Q: What is `st.session_state`?** Streamlit reruns the whole script on each
click, so normal variables reset. `session_state` keeps data (answers, stage)
between reruns.

**Q: What does `st.rerun()` do?** It restarts the script immediately so the
new stage is drawn.

**Q: How is it live on the internet?** The code is on GitHub. Streamlit
Community Cloud pulls the repo, installs `requirements.txt`, runs `app.py` on
its servers and gives it a public `*.streamlit.app` URL. Anyone on the internet
(WAN) can open it, not only my local network (LAN).

**Q: What is `requirements.txt`?** The list of packages the cloud server
must install.

**Q: What is a virtual environment (`.venv`)?** A separate Python installation
for one project, so its packages don't clash with others.

### F. Testing and evaluation
**Q: How did you test it?**
1. For **every one of the 79 rules**, a simulated user answered "yes" only to
   that rule's conditions. Every rule's diagnosis was reached (no dead rules).
2. Demo sentences were checked to make sure the NLP detects the right facts.
3. Streamlit's `AppTest` clicked through the whole UI automatically.

**Q: Limitations?**
- Keyword NLP (no negation or spelling handling).
- "Don't know" is treated as No.
- Only one diagnosis is shown, even when there are multiple causes.
- The CFs are expert estimates, not measured values.
- The knowledge is fixed: the system does not learn.

**Q: Future improvements?**
- Show the top 3 possible diagnoses with combined CF.
- Read real log files.
- Fuzzy matching for typos.
- Let the admin add rules from the UI.
- Backward chaining mode.

---

## 6. Complete knowledge base

Totals: **79 rules**, **179 conditions**, **50 facts**, **159 keywords**, **27 diagnoses** in **6 layers** (API Gateway, Authentication, Backend Service, Database, Frontend, Infrastructure).

### 6.1 Diagnoses (conclusions)

| ID | Name | Layer | Rules leading here |
|---|---|---|---|
| `CORS_BLOCKED` | CORS policy blocking requests | Frontend | R06, R07, R08 |
| `JS_BUNDLE_ERROR` | JavaScript bundle / runtime error | Frontend | R04, R05 |
| `STALE_CACHE_CDN` | Stale browser cache / CDN | Frontend | R01, R02, R03 |
| `CLIENT_NETWORK_DNS` | Client network or DNS failure | Frontend | R12, R13, R14 |
| `SSL_CERT_ISSUE` | SSL certificate expired / mixed content | Frontend | R09, R10, R11 |
| `UPSTREAM_DOWN` | 502 Bad Gateway - upstream service down | API Gateway | R19, R20, R79 |
| `GATEWAY_TIMEOUT` | 504 Gateway Timeout - slow upstream | API Gateway | R28, R29, R30 |
| `RATE_LIMITED` | Rate limited (429) | API Gateway | R37, R38, R39 |
| `PAYLOAD_TOO_LARGE` | Payload too large (413) | API Gateway | R40, R41 |
| `UNHANDLED_EXCEPTION` | Unhandled exception (500) | Backend Service | R35, R36 |
| `MISCONFIGURATION` | Misconfiguration / missing environment variable | Backend Service | R31, R32, R33, R34 |
| `MALFORMED_JSON` | Malformed JSON request (400) | Backend Service | R42, R43 |
| `SCHEMA_MISMATCH` | Schema / API version mismatch (422) | Backend Service | R44, R45, R46 |
| `THIRD_PARTY_FAILURE` | Third-party API / webhook failure | Backend Service | R24, R25, R26 |
| `DB_POOL_EXHAUSTED` | Database connection pool exhausted | Database | R47, R48, R49 |
| `DB_DEADLOCK` | Database deadlock / lock contention | Database | R50, R51 |
| `DB_SLOW_QUERY` | Slow query / missing index | Database | R27, R52, R53 |
| `DB_DOWN` | Database down / unreachable | Database | R54, R55, R56 |
| `REPLICA_LAG` | Read replica lag (stale reads) | Database | R57, R58, R59 |
| `TOKEN_EXPIRED` | Access token expired | Authentication | R63, R64 |
| `INVALID_SIGNATURE` | Invalid token signature / rotated secret | Authentication | R65, R66, R67, R68 |
| `CLOCK_SKEW` | Server clock skew | Authentication | R60, R61, R62 |
| `RBAC_MISSING_ROLE` | Missing role / permission (403) | Authentication | R71, R72, R73, R74 |
| `WRONG_OAUTH_SCOPE` | Wrong or missing OAuth scope | Authentication | R69, R70 |
| `BAD_DEPLOYMENT` | Bad deployment | Infrastructure | R16, R17, R18, R78 |
| `SERVICE_OVERLOADED` | Service overloaded | Infrastructure | R21, R22, R23, R77 |
| `MEMORY_LEAK_OOM` | Memory leak / out-of-memory restarts | Infrastructure | R15, R75, R76 |

### 6.2 Facts (conditions) and their questions

| Fact | Question asked | Example keywords |
|---|---|---|
| `fe_blank_page` | Does the web page load as a blank/white screen? | blank page, page is blank, white screen |
| `fe_js_console_error` | Does the browser console show JavaScript errors (e.g. 'Uncaught TypeError' or 'ChunkLoadError')? | console error, uncaught, typeerror |
| `fe_cors_error` | Does the browser console show a CORS error ('blocked by CORS policy')? | cors, access-control-allow-origin, preflight |
| `fe_old_version` | Do users still see an old version of the site after a release? | old version, outdated version, changes not showing |
| `fe_works_after_hard_refresh` | Does the problem go away after a hard refresh or clearing the browser cache? | hard refresh, clear cache, clearing cache |
| `fe_ssl_warning` | Does the browser show a certificate / 'connection is not private' warning? | certificate, ssl, not secure |
| `fe_mixed_content` | Does the console show 'Mixed Content' warnings (HTTP resources on an HTTPS page)? | mixed content |
| `client_network_error` | Do requests fail with a generic network error (e.g. 'Failed to fetch' or 'ERR_CONNECTION_REFUSED')? | failed to fetch, network error, connection refused |
| `client_dns_error` | Does the browser report a DNS error (e.g. 'DNS_PROBE_FINISHED_NXDOMAIN' or 'server not found')? | dns, nxdomain, server not found |
| `single_user_only` | Is the problem limited to a single user, device or network? | only one user, only me, single user |
| `intermittent` | Is the problem intermittent (some requests succeed, some fail)? | intermittent, sometimes, randomly |
| `http_400` | Are requests failing with HTTP 400 (Bad Request)? | bad request, http 400, error 400 |
| `http_401` | Are requests failing with HTTP 401 (Unauthorized)? | unauthorized, 401 |
| `http_403` | Are requests failing with HTTP 403 (Forbidden)? | forbidden, 403, access denied |
| `http_413` | Are requests failing with HTTP 413 (Payload Too Large)? | payload too large, request entity too large, 413 |
| `http_422` | Are requests failing with HTTP 422 (Unprocessable Entity)? | unprocessable, 422 |
| `http_429` | Are requests failing with HTTP 429 (Too Many Requests)? | too many requests, 429, rate limit |
| `http_500` | Are requests failing with HTTP 500 (Internal Server Error)? | internal server error, http 500, error 500 |
| `http_502` | Are requests failing with HTTP 502 (Bad Gateway)? | bad gateway, 502 |
| `http_503` | Are requests failing with HTTP 503 (Service Unavailable)? | service unavailable, 503 |
| `http_504` | Are requests failing with HTTP 504 (Gateway Timeout)? | gateway timeout, 504, timed out |
| `recent_deploy` | Did the errors start right after a new deployment/release? | deploy, new release, after release |
| `recent_config_change` | Did the errors start after a configuration or infrastructure change? | config change, configuration change, changed the config |
| `new_endpoint` | Does the problem happen on a newly added endpoint or feature? | new endpoint, new feature |
| `high_traffic` | Is traffic much higher than normal (spike, campaign, bot traffic)? | traffic spike, high traffic, lots of users |
| `cpu_high` | Is CPU usage on the servers very high (above ~90%)? | cpu |
| `memory_rising` | Does memory usage keep rising over time until the service restarts? | memory leak, memory keeps, out of memory |
| `pods_restarting` | Are service instances/pods/containers restarting or crash-looping? | crashloop, keeps restarting, pod restart |
| `stack_trace_in_logs` | Do the server logs show an exception stack trace for the failing requests? | stack trace, exception, nullpointer |
| `missing_env_var` | Do the logs mention a missing environment variable or config key? | environment variable, env var, missing config |
| `json_parse_error` | Does the error say the JSON body could not be parsed ('Unexpected token' / 'malformed JSON')? | unexpected token, malformed json, invalid json |
| `validation_error_msg` | Does the error response list field validation problems (missing or unknown fields)? | validation error, required field, missing field |
| `large_payload` | Does the failing request upload a large body or file? | file upload, large file, uploading |
| `api_version_changed` | Was the API version or request/response schema changed recently? | api version, schema change |
| `third_party_dependency` | Does the failing request call an external/third-party API or webhook? | third-party, third party, external api |
| `third_party_errors` | Is the third-party provider returning errors or reporting an outage? | provider outage, provider is down |
| `area_login` | Is the problem related to logging in or user sessions? | login, log in, sign in |
| `token_expired_msg` | Does the error say the token/session has expired? | token expired, jwt expired, session expired |
| `token_valid` | Is the user's token valid (correct signature and not expired)? | – |
| `invalid_signature_msg` | Does the error say the token signature is invalid? | invalid signature, signature verification |
| `secret_rotated` | Were signing keys/secrets (e.g. JWT secret) rotated recently? | rotated, new secret |
| `clock_skew` | Do server clocks differ, or does the error say the token is 'not yet valid'? | clock skew, not yet valid, time drift |
| `insufficient_scope_msg` | Does the error mention 'insufficient scope' or a missing OAuth scope? | insufficient scope, insufficient_scope, oauth scope |
| `user_role_changed` | Were the user's roles/permissions changed recently? | role changed, permissions changed, new role |
| `db_queries_slow` | Are database queries much slower than usual? | database is slow, database seems slow, slow database |
| `db_pool_errors` | Do logs show 'connection pool exhausted' or 'timeout acquiring connection'? | connection pool, pool exhausted, too many connections |
| `db_deadlock` | Do logs show database deadlocks or lock-wait timeouts? | deadlock, lock wait |
| `db_unreachable` | Does the application fail to connect to the database (connection refused/unreachable)? | database is down, database down, cannot connect to database |
| `stale_data_after_write` | Do users see old data right after saving a change? | stale data, old data |
| `read_replica_used` | Does the application read from a database read replica? | replica |

### 6.3 All rules

Read each row as **IF** all conditions are true **THEN** diagnosis (with CF confidence).


**Frontend**

| Rule | IF (all must be true) | THEN | CF |
|---|---|---|---|
| R01 | `fe_blank_page` **AND** `fe_works_after_hard_refresh` **AND** `recent_deploy` | Stale browser cache / CDN | 0.9 |
| R02 | `fe_old_version` **AND** `fe_works_after_hard_refresh` | Stale browser cache / CDN | 0.85 |
| R03 | `fe_old_version` **AND** `recent_deploy` | Stale browser cache / CDN | 0.75 |
| R04 | `fe_blank_page` **AND** `fe_js_console_error` **AND** `recent_deploy` | JavaScript bundle / runtime error | 0.9 |
| R05 | `fe_blank_page` **AND** `fe_js_console_error` | JavaScript bundle / runtime error | 0.8 |
| R06 | `fe_cors_error` **AND** `new_endpoint` **AND** `recent_config_change` | CORS policy blocking requests | 0.9 |
| R07 | `fe_cors_error` **AND** `recent_deploy` | CORS policy blocking requests | 0.8 |
| R08 | `fe_cors_error` **AND** `client_network_error` | CORS policy blocking requests | 0.75 |
| R09 | `fe_ssl_warning` **AND** `client_network_error` | SSL certificate expired / mixed content | 0.85 |
| R10 | `fe_ssl_warning` **AND** `recent_config_change` | SSL certificate expired / mixed content | 0.8 |
| R11 | `fe_mixed_content` **AND** `fe_js_console_error` | SSL certificate expired / mixed content | 0.75 |
| R12 | `client_dns_error` **AND** `single_user_only` | Client network or DNS failure | 0.85 |
| R13 | `client_dns_error` **AND** `client_network_error` | Client network or DNS failure | 0.8 |
| R14 | `client_network_error` **AND** `single_user_only` | Client network or DNS failure | 0.7 |

**Infrastructure**

| Rule | IF (all must be true) | THEN | CF |
|---|---|---|---|
| R15 | `http_502` **AND** `pods_restarting` **AND** `memory_rising` | Memory leak / out-of-memory restarts | 0.9 |
| R16 | `http_502` **AND** `recent_deploy` **AND** `pods_restarting` | Bad deployment | 0.9 |
| R17 | `http_500` **AND** `recent_deploy` **AND** `stack_trace_in_logs` | Bad deployment | 0.85 |
| R18 | `http_502` **AND** `recent_deploy` | Bad deployment | 0.8 |

**API Gateway**

| Rule | IF (all must be true) | THEN | CF |
|---|---|---|---|
| R19 | `http_502` **AND** `pods_restarting` | 502 Bad Gateway - upstream service down | 0.8 |
| R20 | `http_502` **AND** `intermittent` | 502 Bad Gateway - upstream service down | 0.65 |

**Infrastructure**

| Rule | IF (all must be true) | THEN | CF |
|---|---|---|---|
| R21 | `http_503` **AND** `high_traffic` **AND** `cpu_high` | Service overloaded | 0.9 |
| R22 | `http_504` **AND** `high_traffic` **AND** `cpu_high` | Service overloaded | 0.8 |
| R23 | `http_503` **AND** `high_traffic` | Service overloaded | 0.75 |

**Backend Service**

| Rule | IF (all must be true) | THEN | CF |
|---|---|---|---|
| R24 | `http_504` **AND** `third_party_dependency` **AND** `third_party_errors` | Third-party API / webhook failure | 0.9 |
| R25 | `http_502` **AND** `third_party_dependency` | Third-party API / webhook failure | 0.7 |
| R26 | `third_party_dependency` **AND** `third_party_errors` | Third-party API / webhook failure | 0.8 |

**Database**

| Rule | IF (all must be true) | THEN | CF |
|---|---|---|---|
| R27 | `http_504` **AND** `db_queries_slow` **AND** `recent_deploy` | Slow query / missing index | 0.85 |

**API Gateway**

| Rule | IF (all must be true) | THEN | CF |
|---|---|---|---|
| R28 | `http_504` **AND** `intermittent` | 504 Gateway Timeout - slow upstream | 0.7 |
| R29 | `http_504` **AND** `cpu_high` | 504 Gateway Timeout - slow upstream | 0.7 |
| R30 | `http_504` **AND** `third_party_dependency` | 504 Gateway Timeout - slow upstream | 0.65 |

**Backend Service**

| Rule | IF (all must be true) | THEN | CF |
|---|---|---|---|
| R31 | `http_500` **AND** `recent_config_change` **AND** `missing_env_var` | Misconfiguration / missing environment variable | 0.95 |
| R32 | `missing_env_var` **AND** `pods_restarting` | Misconfiguration / missing environment variable | 0.85 |
| R33 | `missing_env_var` **AND** `recent_deploy` | Misconfiguration / missing environment variable | 0.8 |
| R34 | `http_500` **AND** `recent_config_change` | Misconfiguration / missing environment variable | 0.75 |
| R35 | `http_500` **AND** `stack_trace_in_logs` **AND** `new_endpoint` | Unhandled exception (500) | 0.85 |
| R36 | `http_500` **AND** `stack_trace_in_logs` | Unhandled exception (500) | 0.8 |

**API Gateway**

| Rule | IF (all must be true) | THEN | CF |
|---|---|---|---|
| R37 | `http_429` **AND** `high_traffic` | Rate limited (429) | 0.85 |
| R38 | `http_429` **AND** `single_user_only` | Rate limited (429) | 0.85 |
| R39 | `http_429` **AND** `intermittent` | Rate limited (429) | 0.75 |
| R40 | `http_413` **AND** `large_payload` | Payload too large (413) | 0.95 |
| R41 | `large_payload` **AND** `client_network_error` | Payload too large (413) | 0.65 |

**Backend Service**

| Rule | IF (all must be true) | THEN | CF |
|---|---|---|---|
| R42 | `http_400` **AND** `json_parse_error` **AND** `recent_deploy` | Malformed JSON request (400) | 0.9 |
| R43 | `http_400` **AND** `json_parse_error` | Malformed JSON request (400) | 0.85 |
| R44 | `http_422` **AND** `validation_error_msg` **AND** `api_version_changed` | Schema / API version mismatch (422) | 0.95 |
| R45 | `http_422` **AND** `api_version_changed` | Schema / API version mismatch (422) | 0.85 |
| R46 | `http_400` **AND** `api_version_changed` | Schema / API version mismatch (422) | 0.75 |

**Database**

| Rule | IF (all must be true) | THEN | CF |
|---|---|---|---|
| R47 | `http_500` **AND** `db_pool_errors` **AND** `high_traffic` | Database connection pool exhausted | 0.9 |
| R48 | `http_504` **AND** `db_pool_errors` | Database connection pool exhausted | 0.8 |
| R49 | `db_pool_errors` **AND** `intermittent` | Database connection pool exhausted | 0.75 |
| R50 | `http_500` **AND** `db_deadlock` | Database deadlock / lock contention | 0.9 |
| R51 | `db_deadlock` **AND** `intermittent` | Database deadlock / lock contention | 0.8 |
| R52 | `http_504` **AND** `db_queries_slow` | Slow query / missing index | 0.85 |
| R53 | `db_queries_slow` **AND** `cpu_high` | Slow query / missing index | 0.7 |
| R54 | `db_unreachable` **AND** `http_500` | Database down / unreachable | 0.9 |
| R55 | `db_unreachable` **AND** `http_503` | Database down / unreachable | 0.9 |
| R56 | `db_unreachable` **AND** `recent_config_change` | Database down / unreachable | 0.8 |
| R57 | `stale_data_after_write` **AND** `read_replica_used` **AND** `high_traffic` | Read replica lag (stale reads) | 0.9 |
| R58 | `stale_data_after_write` **AND** `read_replica_used` | Read replica lag (stale reads) | 0.85 |
| R59 | `stale_data_after_write` **AND** `intermittent` | Read replica lag (stale reads) | 0.65 |

**Authentication**

| Rule | IF (all must be true) | THEN | CF |
|---|---|---|---|
| R60 | `http_401` **AND** `token_expired_msg` **AND** `clock_skew` | Server clock skew | 0.9 |
| R61 | `http_401` **AND** `clock_skew` | Server clock skew | 0.85 |
| R62 | `clock_skew` **AND** `intermittent` | Server clock skew | 0.7 |
| R63 | `http_401` **AND** `token_expired_msg` | Access token expired | 0.95 |
| R64 | `area_login` **AND** `token_expired_msg` | Access token expired | 0.8 |
| R65 | `http_401` **AND** `invalid_signature_msg` **AND** `secret_rotated` | Invalid token signature / rotated secret | 0.95 |
| R66 | `http_401` **AND** `invalid_signature_msg` | Invalid token signature / rotated secret | 0.85 |
| R67 | `http_401` **AND** `secret_rotated` | Invalid token signature / rotated secret | 0.8 |
| R68 | `area_login` **AND** `invalid_signature_msg` | Invalid token signature / rotated secret | 0.8 |
| R69 | `http_403` **AND** `insufficient_scope_msg` | Wrong or missing OAuth scope | 0.9 |
| R70 | `insufficient_scope_msg` **AND** `new_endpoint` | Wrong or missing OAuth scope | 0.8 |
| R71 | `http_403` **AND** `token_valid` **AND** `new_endpoint` | Missing role / permission (403) | 0.9 |
| R72 | `http_403` **AND** `token_valid` **AND** `user_role_changed` | Missing role / permission (403) | 0.9 |
| R73 | `http_403` **AND** `user_role_changed` | Missing role / permission (403) | 0.8 |
| R74 | `http_403` **AND** `single_user_only` | Missing role / permission (403) | 0.7 |

**Infrastructure**

| Rule | IF (all must be true) | THEN | CF |
|---|---|---|---|
| R75 | `memory_rising` **AND** `pods_restarting` | Memory leak / out-of-memory restarts | 0.85 |
| R76 | `memory_rising` **AND** `http_503` | Memory leak / out-of-memory restarts | 0.7 |
| R77 | `high_traffic` **AND** `cpu_high` **AND** `pods_restarting` | Service overloaded | 0.85 |
| R78 | `recent_deploy` **AND** `pods_restarting` | Bad deployment | 0.8 |

**API Gateway**

| Rule | IF (all must be true) | THEN | CF |
|---|---|---|---|
| R79 | `http_503` **AND** `pods_restarting` | 502 Bad Gateway - upstream service down | 0.7 |

### 6.4 Fix steps for each diagnosis

**CORS policy blocking requests** (Frontend): The browser blocks the API response because the server does not send the right Access-Control-Allow-Origin headers for the website's origin.

1. Add the frontend's origin to the API/gateway CORS allow-list
2. Make sure OPTIONS preflight requests return 200 with CORS headers
3. Check allowed methods and headers (e.g. Authorization, Content-Type)
4. Never use '*' together with credentials (cookies)

**JavaScript bundle / runtime error** (Frontend): A JavaScript error stops the app from rendering, so the user only sees a blank page. Often caused by a broken build or a missing chunk file.

1. Open the browser console and read the first error
2. Roll back to the previous frontend build
3. Check that all bundle/chunk files were uploaded to the server or CDN
4. Add an error boundary so one error does not blank the whole page

**Stale browser cache / CDN** (Frontend): Browsers or the CDN are still serving old files after a release, so users get an old version or an old page pointing to deleted files.

1. Purge/invalidate the CDN cache
2. Use content-hashed file names for JS and CSS
3. Serve index.html with 'Cache-Control: no-cache'
4. Ask affected users to hard refresh

**Client network or DNS failure** (Frontend): The user's device cannot reach the server because of their network, firewall/VPN, or a DNS problem resolving the domain.

1. Check that the domain resolves (nslookup / dig)
2. Try another network or disable VPN/proxy
3. Flush the local DNS cache
4. Verify DNS records were not recently changed or expired

**SSL certificate expired / mixed content** (Frontend): The HTTPS certificate is expired or invalid, or the HTTPS page loads resources over plain HTTP, so the browser blocks the requests.

1. Check the certificate expiry date and renew it
2. Enable automatic renewal (e.g. Let's Encrypt / cert-manager)
3. Change all http:// resource URLs to https://
4. Make sure the full certificate chain is installed

**502 Bad Gateway - upstream service down** (API Gateway): The gateway/load balancer is running but the backend service behind it is down or not responding with a valid answer.

1. Check that backend instances are running and healthy
2. Verify the gateway points to the correct host and port
3. Check load balancer health checks
4. Restart or scale up the failing service

**504 Gateway Timeout - slow upstream** (API Gateway): The backend takes longer to respond than the gateway's timeout, so the gateway gives up and returns 504.

1. Find the slow endpoint using logs/tracing
2. Optimize the slow code path or move long work to a background job
3. Add timeouts and retries with backoff to downstream calls
4. Raise the gateway timeout only if the slowness is expected

**Rate limited (429)** (API Gateway): The client sends more requests than the allowed limit, so the gateway or API rejects extra requests with 429.

1. Respect the Retry-After header and add exponential backoff
2. Reduce request volume with caching or batching
3. Check for a retry loop or bot sending too many requests
4. Request a higher limit if traffic is legitimate

**Payload too large (413)** (API Gateway): The request body is bigger than the maximum size allowed by the gateway, proxy, or server.

1. Increase the body size limit (e.g. nginx client_max_body_size)
2. Compress or split the upload into chunks
3. Upload large files directly to object storage with a signed URL
4. Show a clear file-size limit in the UI

**Unhandled exception (500)** (Backend Service): A bug in the backend code throws an exception that is not caught, so the server returns 500 Internal Server Error.

1. Read the stack trace in the logs to find the failing line
2. Fix the bug (e.g. null check, wrong type) and add a test
3. Add proper error handling that returns clear error codes
4. Set up error tracking (e.g. Sentry) for alerts

**Misconfiguration / missing environment variable** (Backend Service): The service is missing a required setting or has a wrong config value, so it fails at startup or when handling requests.

1. Compare the config/env vars with the last working version
2. Add the missing variable or secret and redeploy
3. Validate required config at startup (fail fast)
4. Revert the recent config change if unsure

**Malformed JSON request (400)** (Backend Service): The client sends a request body that is not valid JSON or uses the wrong Content-Type, so the server cannot parse it.

1. Log and inspect the exact request body sent
2. Use JSON.stringify / a JSON library instead of building strings
3. Set 'Content-Type: application/json'
4. Return a clear parse error message to the client

**Schema / API version mismatch (422)** (Backend Service): Client and server disagree on the request format, usually after an API version or schema change, so fields fail validation.

1. Compare the client request with the current API schema
2. Update the client or pin it to the old API version
3. Keep old versions working (versioning) during migration
4. Document breaking changes and add contract tests

**Third-party API / webhook failure** (Backend Service): An external service the app depends on (payments, email, webhook) is failing or slow, and the error spreads to our API.

1. Check the provider's status page
2. Add timeouts, retries with backoff and a circuit breaker
3. Queue the work and process it later when the provider recovers
4. Show a friendly fallback message to users

**Database connection pool exhausted** (Database): All database connections in the pool are in use, so new requests wait and time out. Often caused by connection leaks or too much load.

1. Make sure connections are always closed/returned (fix leaks)
2. Increase the pool size within database limits
3. Shorten long transactions and slow queries
4. Add a connection proxy/pooler (e.g. PgBouncer)

**Database deadlock / lock contention** (Database): Two or more transactions wait for locks held by each other, so the database aborts one of them or requests wait too long.

1. Find the conflicting queries in the deadlock log
2. Access tables and rows in the same order in all transactions
3. Keep transactions short
4. Retry the transaction automatically on deadlock errors

**Slow query / missing index** (Database): Some queries scan whole tables because an index is missing or the query is inefficient, making requests slow and causing timeouts.

1. Find slow queries using the slow query log
2. Run EXPLAIN to check for full table scans
3. Add the missing index
4. Add pagination or caching for heavy queries

**Database down / unreachable** (Database): The application cannot connect to the database because it is down, out of disk, or blocked by a network/credentials change.

1. Check the database server status and disk space
2. Verify host, port, credentials and firewall rules
3. Fail over to a standby/replica if available
4. Restore service and then review recent infra changes

**Read replica lag (stale reads)** (Database): Writes go to the primary but reads come from a replica that is behind, so users briefly see old data after saving.

1. Monitor replica lag
2. Read from the primary right after a write (read-your-writes)
3. Reduce heavy write load or upgrade the replica
4. Show the saved data from the write response in the UI

**Access token expired** (Authentication): The user's access token or session has passed its expiry time, so the API rejects it with 401.

1. Use the refresh token to get a new access token automatically
2. Redirect the user to log in again if refresh fails
3. Check that the token lifetime is configured sensibly
4. Handle 401 globally in the frontend

**Invalid token signature / rotated secret** (Authentication): The token was signed with a key the API no longer trusts, usually because the signing secret was rotated or services use different keys.

1. Make sure all services use the same signing key / JWKS
2. Support old and new keys during rotation (key id 'kid')
3. Force users to log in again to get new tokens
4. Store secrets in one central secret manager

**Server clock skew** (Authentication): Server clocks are out of sync, so fresh tokens look expired or 'not yet valid' to some servers.

1. Enable NTP time sync on all servers
2. Allow a small clock tolerance (e.g. 30-60 seconds) when checking tokens
3. Find which server has the wrong time
4. Monitor clock drift

**Missing role / permission (403)** (Authentication): The user is logged in with a valid token but does not have the role or permission required for this endpoint.

1. Check which role the endpoint requires
2. Grant the role/permission to the user or group
3. Update the permission mapping for new endpoints
4. Ask the user to log in again so the token gets new roles

**Wrong or missing OAuth scope** (Authentication): The access token was issued without the OAuth scope the API requires, so the request is forbidden.

1. Check which scope the endpoint requires
2. Request the missing scope in the authorization request
3. Allow the scope for this client in the identity provider
4. Have the user re-consent and get a new token

**Bad deployment** (Infrastructure): The newest release contains a bug or broken build, so the new version crashes or fails right after it is deployed.

1. Roll back to the last working version
2. Check deployment and startup logs
3. Fix the issue and test it in staging
4. Use canary or blue-green deployments next time

**Service overloaded** (Infrastructure): There is more traffic than the servers can handle, so CPU is maxed out and the service starts rejecting or delaying requests.

1. Scale out (add more instances) or enable autoscaling
2. Add caching for heavy or repeated requests
3. Enable rate limiting to protect the service
4. Block abusive or bot traffic

**Memory leak / out-of-memory restarts** (Infrastructure): The service keeps using more memory until it is killed for running out of memory (OOM) and restarts, causing errors during restarts.

1. Check memory graphs and OOMKilled events
2. Take a heap dump/profile to find the leak
3. Fix unbounded caches or unreleased objects
4. Temporarily raise memory limits or restart on a schedule

