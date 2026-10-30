# =====================================================================
#  KNOWLEDGE BASE - Distributed Systems & API Incident Triage
#  A simple rule-based "virtual SRE" that diagnoses why a web app/API
#  is broken. Contains 4 parts:
#    1. QUESTIONS  - facts the system can ask about (yes/no)
#    2. KEYWORDS   - phrases in a free-text description -> facts
#    3. RULES      - IF facts THEN diagnosis (with certainty factor)
#    4. DIAGNOSES  - explanation and fixes for each diagnosis
# =====================================================================


# ---------------------------------------------------------------------
# 1. QUESTIONS: fact_id -> yes/no question
# ---------------------------------------------------------------------
QUESTIONS = {
    # --- Frontend / client symptoms ---
    "fe_blank_page": "Does the web page load as a blank/white screen?",
    "fe_js_console_error": "Does the browser console show JavaScript errors (e.g. 'Uncaught TypeError' or 'ChunkLoadError')?",
    "fe_cors_error": "Does the browser console show a CORS error ('blocked by CORS policy')?",
    "fe_old_version": "Do users still see an old version of the site after a release?",
    "fe_works_after_hard_refresh": "Does the problem go away after a hard refresh or clearing the browser cache?",
    "fe_ssl_warning": "Does the browser show a certificate / 'connection is not private' warning?",
    "fe_mixed_content": "Does the console show 'Mixed Content' warnings (HTTP resources on an HTTPS page)?",
    "client_network_error": "Do requests fail with a generic network error (e.g. 'Failed to fetch' or 'ERR_CONNECTION_REFUSED')?",
    "client_dns_error": "Does the browser report a DNS error (e.g. 'DNS_PROBE_FINISHED_NXDOMAIN' or 'server not found')?",
    "single_user_only": "Is the problem limited to a single user, device or network?",
    "intermittent": "Is the problem intermittent (some requests succeed, some fail)?",

    # --- HTTP status codes ---
    "http_400": "Are requests failing with HTTP 400 (Bad Request)?",
    "http_401": "Are requests failing with HTTP 401 (Unauthorized)?",
    "http_403": "Are requests failing with HTTP 403 (Forbidden)?",
    "http_413": "Are requests failing with HTTP 413 (Payload Too Large)?",
    "http_422": "Are requests failing with HTTP 422 (Unprocessable Entity)?",
    "http_429": "Are requests failing with HTTP 429 (Too Many Requests)?",
    "http_500": "Are requests failing with HTTP 500 (Internal Server Error)?",
    "http_502": "Are requests failing with HTTP 502 (Bad Gateway)?",
    "http_503": "Are requests failing with HTTP 503 (Service Unavailable)?",
    "http_504": "Are requests failing with HTTP 504 (Gateway Timeout)?",

    # --- Changes and load ---
    "recent_deploy": "Did the errors start right after a new deployment/release?",
    "recent_config_change": "Did the errors start after a configuration or infrastructure change?",
    "new_endpoint": "Does the problem happen on a newly added endpoint or feature?",
    "high_traffic": "Is traffic much higher than normal (spike, campaign, bot traffic)?",
    "cpu_high": "Is CPU usage on the servers very high (above ~90%)?",
    "memory_rising": "Does memory usage keep rising over time until the service restarts?",
    "pods_restarting": "Are service instances/pods/containers restarting or crash-looping?",

    # --- Backend logs ---
    "stack_trace_in_logs": "Do the server logs show an exception stack trace for the failing requests?",
    "missing_env_var": "Do the logs mention a missing environment variable or config key?",
    "json_parse_error": "Does the error say the JSON body could not be parsed ('Unexpected token' / 'malformed JSON')?",
    "validation_error_msg": "Does the error response list field validation problems (missing or unknown fields)?",
    "large_payload": "Does the failing request upload a large body or file?",
    "api_version_changed": "Was the API version or request/response schema changed recently?",
    "third_party_dependency": "Does the failing request call an external/third-party API or webhook?",
    "third_party_errors": "Is the third-party provider returning errors or reporting an outage?",

    # --- Authentication / authorization ---
    "area_login": "Is the problem related to logging in or user sessions?",
    "token_expired_msg": "Does the error say the token/session has expired?",
    "token_valid": "Is the user's token valid (correct signature and not expired)?",
    "invalid_signature_msg": "Does the error say the token signature is invalid?",
    "secret_rotated": "Were signing keys/secrets (e.g. JWT secret) rotated recently?",
    "clock_skew": "Do server clocks differ, or does the error say the token is 'not yet valid'?",
    "insufficient_scope_msg": "Does the error mention 'insufficient scope' or a missing OAuth scope?",
    "user_role_changed": "Were the user's roles/permissions changed recently?",

    # --- Database ---
    "db_queries_slow": "Are database queries much slower than usual?",
    "db_pool_errors": "Do logs show 'connection pool exhausted' or 'timeout acquiring connection'?",
    "db_deadlock": "Do logs show database deadlocks or lock-wait timeouts?",
    "db_unreachable": "Does the application fail to connect to the database (connection refused/unreachable)?",
    "stale_data_after_write": "Do users see old data right after saving a change?",
    "read_replica_used": "Does the application read from a database read replica?",
}


# ---------------------------------------------------------------------
# 2. KEYWORDS: phrase found in user's description -> fact_id
# ---------------------------------------------------------------------
KEYWORDS = {
    # Frontend
    "blank page": "fe_blank_page",
    "page is blank": "fe_blank_page",
    "white screen": "fe_blank_page",
    "white screen": "fe_blank_page",
    "blank screen": "fe_blank_page",
    "page is empty": "fe_blank_page",
    "console error": "fe_js_console_error",
    "uncaught": "fe_js_console_error",
    "typeerror": "fe_js_console_error",
    "chunkloaderror": "fe_js_console_error",
    "javascript error": "fe_js_console_error",
    "cors": "fe_cors_error",
    "access-control-allow-origin": "fe_cors_error",
    "preflight": "fe_cors_error",
    "old version": "fe_old_version",
    "outdated version": "fe_old_version",
    "changes not showing": "fe_old_version",
    "hard refresh": "fe_works_after_hard_refresh",
    "clear cache": "fe_works_after_hard_refresh",
    "clearing cache": "fe_works_after_hard_refresh",
    "incognito": "fe_works_after_hard_refresh",
    "certificate": "fe_ssl_warning",
    "ssl": "fe_ssl_warning",
    "not secure": "fe_ssl_warning",
    "not private": "fe_ssl_warning",
    "cert expired": "fe_ssl_warning",
    "mixed content": "fe_mixed_content",
    "failed to fetch": "client_network_error",
    "network error": "client_network_error",
    "connection refused": "client_network_error",
    "err_connection": "client_network_error",
    "dns": "client_dns_error",
    "nxdomain": "client_dns_error",
    "server not found": "client_dns_error",
    "only one user": "single_user_only",
    "only me": "single_user_only",
    "single user": "single_user_only",
    "one customer": "single_user_only",
    "intermittent": "intermittent",
    "sometimes": "intermittent",
    "randomly": "intermittent",
    "on and off": "intermittent",
    "flaky": "intermittent",

    # Status codes
    "bad request": "http_400",
    "http 400": "http_400",
    "error 400": "http_400",
    "unauthorized": "http_401",
    "401": "http_401",
    "forbidden": "http_403",
    "403": "http_403",
    "access denied": "http_403",
    "payload too large": "http_413",
    "request entity too large": "http_413",
    "413": "http_413",
    "unprocessable": "http_422",
    "422": "http_422",
    "too many requests": "http_429",
    "429": "http_429",
    "rate limit": "http_429",
    "throttled": "http_429",
    "internal server error": "http_500",
    "http 500": "http_500",
    "error 500": "http_500",
    "500 error": "http_500",
    "bad gateway": "http_502",
    "502": "http_502",
    "service unavailable": "http_503",
    "503": "http_503",
    "gateway timeout": "http_504",
    "504": "http_504",
    "timed out": "http_504",
    "timeout": "http_504",

    # Changes and load
    "deploy": "recent_deploy",
    "new release": "recent_deploy",
    "after release": "recent_deploy",
    "rollout": "recent_deploy",
    "config change": "recent_config_change",
    "configuration change": "recent_config_change",
    "changed the config": "recent_config_change",
    "new endpoint": "new_endpoint",
    "new feature": "new_endpoint",
    "traffic spike": "high_traffic",
    "high traffic": "high_traffic",
    "lots of users": "high_traffic",
    "black friday": "high_traffic",
    "cpu": "cpu_high",
    "memory leak": "memory_rising",
    "memory keeps": "memory_rising",
    "out of memory": "memory_rising",
    "oomkilled": "memory_rising",
    "crashloop": "pods_restarting",
    "keeps restarting": "pods_restarting",
    "pod restart": "pods_restarting",
    "container restart": "pods_restarting",

    # Backend logs
    "stack trace": "stack_trace_in_logs",
    "exception": "stack_trace_in_logs",
    "nullpointer": "stack_trace_in_logs",
    "environment variable": "missing_env_var",
    "env var": "missing_env_var",
    "missing config": "missing_env_var",
    "unexpected token": "json_parse_error",
    "malformed json": "json_parse_error",
    "invalid json": "json_parse_error",
    "json parse": "json_parse_error",
    "validation error": "validation_error_msg",
    "required field": "validation_error_msg",
    "missing field": "validation_error_msg",
    "file upload": "large_payload",
    "large file": "large_payload",
    "uploading": "large_payload",
    "api version": "api_version_changed",
    "schema change": "api_version_changed",
    "third-party": "third_party_dependency",
    "third party": "third_party_dependency",
    "external api": "third_party_dependency",
    "webhook": "third_party_dependency",
    "payment provider": "third_party_dependency",
    "provider outage": "third_party_errors",
    "provider is down": "third_party_errors",

    # Authentication
    "login": "area_login",
    "log in": "area_login",
    "sign in": "area_login",
    "session": "area_login",
    "token expired": "token_expired_msg",
    "jwt expired": "token_expired_msg",
    "session expired": "token_expired_msg",
    "after some time": "token_expired_msg",
    "logged out": "token_expired_msg",
    "invalid signature": "invalid_signature_msg",
    "signature verification": "invalid_signature_msg",
    "rotated": "secret_rotated",
    "new secret": "secret_rotated",
    "clock skew": "clock_skew",
    "not yet valid": "clock_skew",
    "time drift": "clock_skew",
    "insufficient scope": "insufficient_scope_msg",
    "insufficient_scope": "insufficient_scope_msg",
    "oauth scope": "insufficient_scope_msg",
    "role changed": "user_role_changed",
    "permissions changed": "user_role_changed",
    "new role": "user_role_changed",

    # Database
    "database is slow": "db_queries_slow",
    "database seems slow": "db_queries_slow",
    "slow database": "db_queries_slow",
    "slow query": "db_queries_slow",
    "slow queries": "db_queries_slow",
    "full table scan": "db_queries_slow",
    "missing index": "db_queries_slow",
    "connection pool": "db_pool_errors",
    "pool exhausted": "db_pool_errors",
    "too many connections": "db_pool_errors",
    "deadlock": "db_deadlock",
    "lock wait": "db_deadlock",
    "database is down": "db_unreachable",
    "database down": "db_unreachable",
    "cannot connect to database": "db_unreachable",
    "can't connect to database": "db_unreachable",
    "stale data": "stale_data_after_write",
    "old data": "stale_data_after_write",
    "replica": "read_replica_used",
}


# ---------------------------------------------------------------------
# 3. RULES: IF all conditions are true THEN diagnosis (cf = certainty)
#    Specific rules (3 conditions) come before general ones, because
#    the engine fires the first rule whose conditions are all true.
# ---------------------------------------------------------------------
RULES = [
    # ----- Frontend layer -----
    {"id": "R01", "if": ["fe_blank_page", "fe_works_after_hard_refresh", "recent_deploy"], "then": "STALE_CACHE_CDN", "cf": 0.9},
    {"id": "R02", "if": ["fe_old_version", "fe_works_after_hard_refresh"], "then": "STALE_CACHE_CDN", "cf": 0.85},
    {"id": "R03", "if": ["fe_old_version", "recent_deploy"], "then": "STALE_CACHE_CDN", "cf": 0.75},
    {"id": "R04", "if": ["fe_blank_page", "fe_js_console_error", "recent_deploy"], "then": "JS_BUNDLE_ERROR", "cf": 0.9},
    {"id": "R05", "if": ["fe_blank_page", "fe_js_console_error"], "then": "JS_BUNDLE_ERROR", "cf": 0.8},
    {"id": "R06", "if": ["fe_cors_error", "new_endpoint", "recent_config_change"], "then": "CORS_BLOCKED", "cf": 0.9},
    {"id": "R07", "if": ["fe_cors_error", "recent_deploy"], "then": "CORS_BLOCKED", "cf": 0.8},
    {"id": "R08", "if": ["fe_cors_error", "client_network_error"], "then": "CORS_BLOCKED", "cf": 0.75},
    {"id": "R09", "if": ["fe_ssl_warning", "client_network_error"], "then": "SSL_CERT_ISSUE", "cf": 0.85},
    {"id": "R10", "if": ["fe_ssl_warning", "recent_config_change"], "then": "SSL_CERT_ISSUE", "cf": 0.8},
    {"id": "R11", "if": ["fe_mixed_content", "fe_js_console_error"], "then": "SSL_CERT_ISSUE", "cf": 0.75},
    {"id": "R12", "if": ["client_dns_error", "single_user_only"], "then": "CLIENT_NETWORK_DNS", "cf": 0.85},
    {"id": "R13", "if": ["client_dns_error", "client_network_error"], "then": "CLIENT_NETWORK_DNS", "cf": 0.8},
    {"id": "R14", "if": ["client_network_error", "single_user_only"], "then": "CLIENT_NETWORK_DNS", "cf": 0.7},

    # ----- API Gateway / 5xx errors -----
    {"id": "R15", "if": ["http_502", "pods_restarting", "memory_rising"], "then": "MEMORY_LEAK_OOM", "cf": 0.9},
    {"id": "R16", "if": ["http_502", "recent_deploy", "pods_restarting"], "then": "BAD_DEPLOYMENT", "cf": 0.9},
    {"id": "R17", "if": ["http_500", "recent_deploy", "stack_trace_in_logs"], "then": "BAD_DEPLOYMENT", "cf": 0.85},
    {"id": "R18", "if": ["http_502", "recent_deploy"], "then": "BAD_DEPLOYMENT", "cf": 0.8},
    {"id": "R19", "if": ["http_502", "pods_restarting"], "then": "UPSTREAM_DOWN", "cf": 0.8},
    {"id": "R20", "if": ["http_502", "intermittent"], "then": "UPSTREAM_DOWN", "cf": 0.65},
    {"id": "R21", "if": ["http_503", "high_traffic", "cpu_high"], "then": "SERVICE_OVERLOADED", "cf": 0.9},
    {"id": "R22", "if": ["http_504", "high_traffic", "cpu_high"], "then": "SERVICE_OVERLOADED", "cf": 0.8},
    {"id": "R23", "if": ["http_503", "high_traffic"], "then": "SERVICE_OVERLOADED", "cf": 0.75},
    {"id": "R24", "if": ["http_504", "third_party_dependency", "third_party_errors"], "then": "THIRD_PARTY_FAILURE", "cf": 0.9},
    {"id": "R25", "if": ["http_502", "third_party_dependency"], "then": "THIRD_PARTY_FAILURE", "cf": 0.7},
    {"id": "R26", "if": ["third_party_dependency", "third_party_errors"], "then": "THIRD_PARTY_FAILURE", "cf": 0.8},
    {"id": "R27", "if": ["http_504", "db_queries_slow", "recent_deploy"], "then": "DB_SLOW_QUERY", "cf": 0.85},
    {"id": "R28", "if": ["http_504", "intermittent"], "then": "GATEWAY_TIMEOUT", "cf": 0.7},
    {"id": "R29", "if": ["http_504", "cpu_high"], "then": "GATEWAY_TIMEOUT", "cf": 0.7},
    {"id": "R30", "if": ["http_504", "third_party_dependency"], "then": "GATEWAY_TIMEOUT", "cf": 0.65},
    {"id": "R31", "if": ["http_500", "recent_config_change", "missing_env_var"], "then": "MISCONFIGURATION", "cf": 0.95},
    {"id": "R32", "if": ["missing_env_var", "pods_restarting"], "then": "MISCONFIGURATION", "cf": 0.85},
    {"id": "R33", "if": ["missing_env_var", "recent_deploy"], "then": "MISCONFIGURATION", "cf": 0.8},
    {"id": "R34", "if": ["http_500", "recent_config_change"], "then": "MISCONFIGURATION", "cf": 0.75},
    {"id": "R35", "if": ["http_500", "stack_trace_in_logs", "new_endpoint"], "then": "UNHANDLED_EXCEPTION", "cf": 0.85},
    {"id": "R36", "if": ["http_500", "stack_trace_in_logs"], "then": "UNHANDLED_EXCEPTION", "cf": 0.8},

    # ----- Rate limiting & payload -----
    {"id": "R37", "if": ["http_429", "high_traffic"], "then": "RATE_LIMITED", "cf": 0.85},
    {"id": "R38", "if": ["http_429", "single_user_only"], "then": "RATE_LIMITED", "cf": 0.85},
    {"id": "R39", "if": ["http_429", "intermittent"], "then": "RATE_LIMITED", "cf": 0.75},
    {"id": "R40", "if": ["http_413", "large_payload"], "then": "PAYLOAD_TOO_LARGE", "cf": 0.95},
    {"id": "R41", "if": ["large_payload", "client_network_error"], "then": "PAYLOAD_TOO_LARGE", "cf": 0.65},
    {"id": "R42", "if": ["http_400", "json_parse_error", "recent_deploy"], "then": "MALFORMED_JSON", "cf": 0.9},
    {"id": "R43", "if": ["http_400", "json_parse_error"], "then": "MALFORMED_JSON", "cf": 0.85},
    {"id": "R44", "if": ["http_422", "validation_error_msg", "api_version_changed"], "then": "SCHEMA_MISMATCH", "cf": 0.95},
    {"id": "R45", "if": ["http_422", "api_version_changed"], "then": "SCHEMA_MISMATCH", "cf": 0.85},
    {"id": "R46", "if": ["http_400", "api_version_changed"], "then": "SCHEMA_MISMATCH", "cf": 0.75},

    # ----- Database layer -----
    {"id": "R47", "if": ["http_500", "db_pool_errors", "high_traffic"], "then": "DB_POOL_EXHAUSTED", "cf": 0.9},
    {"id": "R48", "if": ["http_504", "db_pool_errors"], "then": "DB_POOL_EXHAUSTED", "cf": 0.8},
    {"id": "R49", "if": ["db_pool_errors", "intermittent"], "then": "DB_POOL_EXHAUSTED", "cf": 0.75},
    {"id": "R50", "if": ["http_500", "db_deadlock"], "then": "DB_DEADLOCK", "cf": 0.9},
    {"id": "R51", "if": ["db_deadlock", "intermittent"], "then": "DB_DEADLOCK", "cf": 0.8},
    {"id": "R52", "if": ["http_504", "db_queries_slow"], "then": "DB_SLOW_QUERY", "cf": 0.85},
    {"id": "R53", "if": ["db_queries_slow", "cpu_high"], "then": "DB_SLOW_QUERY", "cf": 0.7},
    {"id": "R54", "if": ["db_unreachable", "http_500"], "then": "DB_DOWN", "cf": 0.9},
    {"id": "R55", "if": ["db_unreachable", "http_503"], "then": "DB_DOWN", "cf": 0.9},
    {"id": "R56", "if": ["db_unreachable", "recent_config_change"], "then": "DB_DOWN", "cf": 0.8},
    {"id": "R57", "if": ["stale_data_after_write", "read_replica_used", "high_traffic"], "then": "REPLICA_LAG", "cf": 0.9},
    {"id": "R58", "if": ["stale_data_after_write", "read_replica_used"], "then": "REPLICA_LAG", "cf": 0.85},
    {"id": "R59", "if": ["stale_data_after_write", "intermittent"], "then": "REPLICA_LAG", "cf": 0.65},

    # ----- Authentication / RBAC -----
    {"id": "R60", "if": ["http_401", "token_expired_msg", "clock_skew"], "then": "CLOCK_SKEW", "cf": 0.9},
    {"id": "R61", "if": ["http_401", "clock_skew"], "then": "CLOCK_SKEW", "cf": 0.85},
    {"id": "R62", "if": ["clock_skew", "intermittent"], "then": "CLOCK_SKEW", "cf": 0.7},
    {"id": "R63", "if": ["http_401", "token_expired_msg"], "then": "TOKEN_EXPIRED", "cf": 0.95},
    {"id": "R64", "if": ["area_login", "token_expired_msg"], "then": "TOKEN_EXPIRED", "cf": 0.8},
    {"id": "R65", "if": ["http_401", "invalid_signature_msg", "secret_rotated"], "then": "INVALID_SIGNATURE", "cf": 0.95},
    {"id": "R66", "if": ["http_401", "invalid_signature_msg"], "then": "INVALID_SIGNATURE", "cf": 0.85},
    {"id": "R67", "if": ["http_401", "secret_rotated"], "then": "INVALID_SIGNATURE", "cf": 0.8},
    {"id": "R68", "if": ["area_login", "invalid_signature_msg"], "then": "INVALID_SIGNATURE", "cf": 0.8},
    {"id": "R69", "if": ["http_403", "insufficient_scope_msg"], "then": "WRONG_OAUTH_SCOPE", "cf": 0.9},
    {"id": "R70", "if": ["insufficient_scope_msg", "new_endpoint"], "then": "WRONG_OAUTH_SCOPE", "cf": 0.8},
    {"id": "R71", "if": ["http_403", "token_valid", "new_endpoint"], "then": "RBAC_MISSING_ROLE", "cf": 0.9},
    {"id": "R72", "if": ["http_403", "token_valid", "user_role_changed"], "then": "RBAC_MISSING_ROLE", "cf": 0.9},
    {"id": "R73", "if": ["http_403", "user_role_changed"], "then": "RBAC_MISSING_ROLE", "cf": 0.8},
    {"id": "R74", "if": ["http_403", "single_user_only"], "then": "RBAC_MISSING_ROLE", "cf": 0.7},

    # ----- Infrastructure / Deployment -----
    {"id": "R75", "if": ["memory_rising", "pods_restarting"], "then": "MEMORY_LEAK_OOM", "cf": 0.85},
    {"id": "R76", "if": ["memory_rising", "http_503"], "then": "MEMORY_LEAK_OOM", "cf": 0.7},
    {"id": "R77", "if": ["high_traffic", "cpu_high", "pods_restarting"], "then": "SERVICE_OVERLOADED", "cf": 0.85},
    {"id": "R78", "if": ["recent_deploy", "pods_restarting"], "then": "BAD_DEPLOYMENT", "cf": 0.8},
    {"id": "R79", "if": ["http_503", "pods_restarting"], "then": "UPSTREAM_DOWN", "cf": 0.7},
]


# ---------------------------------------------------------------------
# 4. DIAGNOSES: what is wrong, which layer, and how to fix it
# ---------------------------------------------------------------------
DIAGNOSES = {
    # ----- Frontend -----
    "CORS_BLOCKED": {
        "name": "CORS policy blocking requests",
        "layer": "Frontend",
        "description": "The browser blocks the API response because the server does not send the right Access-Control-Allow-Origin headers for the website's origin.",
        "fix": [
            "Add the frontend's origin to the API/gateway CORS allow-list",
            "Make sure OPTIONS preflight requests return 200 with CORS headers",
            "Check allowed methods and headers (e.g. Authorization, Content-Type)",
            "Never use '*' together with credentials (cookies)",
        ],
    },
    "JS_BUNDLE_ERROR": {
        "name": "JavaScript bundle / runtime error",
        "layer": "Frontend",
        "description": "A JavaScript error stops the app from rendering, so the user only sees a blank page. Often caused by a broken build or a missing chunk file.",
        "fix": [
            "Open the browser console and read the first error",
            "Roll back to the previous frontend build",
            "Check that all bundle/chunk files were uploaded to the server or CDN",
            "Add an error boundary so one error does not blank the whole page",
        ],
    },
    "STALE_CACHE_CDN": {
        "name": "Stale browser cache / CDN",
        "layer": "Frontend",
        "description": "Browsers or the CDN are still serving old files after a release, so users get an old version or an old page pointing to deleted files.",
        "fix": [
            "Purge/invalidate the CDN cache",
            "Use content-hashed file names for JS and CSS",
            "Serve index.html with 'Cache-Control: no-cache'",
            "Ask affected users to hard refresh",
        ],
    },
    "CLIENT_NETWORK_DNS": {
        "name": "Client network or DNS failure",
        "layer": "Frontend",
        "description": "The user's device cannot reach the server because of their network, firewall/VPN, or a DNS problem resolving the domain.",
        "fix": [
            "Check that the domain resolves (nslookup / dig)",
            "Try another network or disable VPN/proxy",
            "Flush the local DNS cache",
            "Verify DNS records were not recently changed or expired",
        ],
    },
    "SSL_CERT_ISSUE": {
        "name": "SSL certificate expired / mixed content",
        "layer": "Frontend",
        "description": "The HTTPS certificate is expired or invalid, or the HTTPS page loads resources over plain HTTP, so the browser blocks the requests.",
        "fix": [
            "Check the certificate expiry date and renew it",
            "Enable automatic renewal (e.g. Let's Encrypt / cert-manager)",
            "Change all http:// resource URLs to https://",
            "Make sure the full certificate chain is installed",
        ],
    },

    # ----- API Gateway -----
    "UPSTREAM_DOWN": {
        "name": "502 Bad Gateway - upstream service down",
        "layer": "API Gateway",
        "description": "The gateway/load balancer is running but the backend service behind it is down or not responding with a valid answer.",
        "fix": [
            "Check that backend instances are running and healthy",
            "Verify the gateway points to the correct host and port",
            "Check load balancer health checks",
            "Restart or scale up the failing service",
        ],
    },
    "GATEWAY_TIMEOUT": {
        "name": "504 Gateway Timeout - slow upstream",
        "layer": "API Gateway",
        "description": "The backend takes longer to respond than the gateway's timeout, so the gateway gives up and returns 504.",
        "fix": [
            "Find the slow endpoint using logs/tracing",
            "Optimize the slow code path or move long work to a background job",
            "Add timeouts and retries with backoff to downstream calls",
            "Raise the gateway timeout only if the slowness is expected",
        ],
    },
    "RATE_LIMITED": {
        "name": "Rate limited (429)",
        "layer": "API Gateway",
        "description": "The client sends more requests than the allowed limit, so the gateway or API rejects extra requests with 429.",
        "fix": [
            "Respect the Retry-After header and add exponential backoff",
            "Reduce request volume with caching or batching",
            "Check for a retry loop or bot sending too many requests",
            "Request a higher limit if traffic is legitimate",
        ],
    },
    "PAYLOAD_TOO_LARGE": {
        "name": "Payload too large (413)",
        "layer": "API Gateway",
        "description": "The request body is bigger than the maximum size allowed by the gateway, proxy, or server.",
        "fix": [
            "Increase the body size limit (e.g. nginx client_max_body_size)",
            "Compress or split the upload into chunks",
            "Upload large files directly to object storage with a signed URL",
            "Show a clear file-size limit in the UI",
        ],
    },

    # ----- Backend Service -----
    "UNHANDLED_EXCEPTION": {
        "name": "Unhandled exception (500)",
        "layer": "Backend Service",
        "description": "A bug in the backend code throws an exception that is not caught, so the server returns 500 Internal Server Error.",
        "fix": [
            "Read the stack trace in the logs to find the failing line",
            "Fix the bug (e.g. null check, wrong type) and add a test",
            "Add proper error handling that returns clear error codes",
            "Set up error tracking (e.g. Sentry) for alerts",
        ],
    },
    "MISCONFIGURATION": {
        "name": "Misconfiguration / missing environment variable",
        "layer": "Backend Service",
        "description": "The service is missing a required setting or has a wrong config value, so it fails at startup or when handling requests.",
        "fix": [
            "Compare the config/env vars with the last working version",
            "Add the missing variable or secret and redeploy",
            "Validate required config at startup (fail fast)",
            "Revert the recent config change if unsure",
        ],
    },
    "MALFORMED_JSON": {
        "name": "Malformed JSON request (400)",
        "layer": "Backend Service",
        "description": "The client sends a request body that is not valid JSON or uses the wrong Content-Type, so the server cannot parse it.",
        "fix": [
            "Log and inspect the exact request body sent",
            "Use JSON.stringify / a JSON library instead of building strings",
            "Set 'Content-Type: application/json'",
            "Return a clear parse error message to the client",
        ],
    },
    "SCHEMA_MISMATCH": {
        "name": "Schema / API version mismatch (422)",
        "layer": "Backend Service",
        "description": "Client and server disagree on the request format, usually after an API version or schema change, so fields fail validation.",
        "fix": [
            "Compare the client request with the current API schema",
            "Update the client or pin it to the old API version",
            "Keep old versions working (versioning) during migration",
            "Document breaking changes and add contract tests",
        ],
    },
    "THIRD_PARTY_FAILURE": {
        "name": "Third-party API / webhook failure",
        "layer": "Backend Service",
        "description": "An external service the app depends on (payments, email, webhook) is failing or slow, and the error spreads to our API.",
        "fix": [
            "Check the provider's status page",
            "Add timeouts, retries with backoff and a circuit breaker",
            "Queue the work and process it later when the provider recovers",
            "Show a friendly fallback message to users",
        ],
    },

    # ----- Database -----
    "DB_POOL_EXHAUSTED": {
        "name": "Database connection pool exhausted",
        "layer": "Database",
        "description": "All database connections in the pool are in use, so new requests wait and time out. Often caused by connection leaks or too much load.",
        "fix": [
            "Make sure connections are always closed/returned (fix leaks)",
            "Increase the pool size within database limits",
            "Shorten long transactions and slow queries",
            "Add a connection proxy/pooler (e.g. PgBouncer)",
        ],
    },
    "DB_DEADLOCK": {
        "name": "Database deadlock / lock contention",
        "layer": "Database",
        "description": "Two or more transactions wait for locks held by each other, so the database aborts one of them or requests wait too long.",
        "fix": [
            "Find the conflicting queries in the deadlock log",
            "Access tables and rows in the same order in all transactions",
            "Keep transactions short",
            "Retry the transaction automatically on deadlock errors",
        ],
    },
    "DB_SLOW_QUERY": {
        "name": "Slow query / missing index",
        "layer": "Database",
        "description": "Some queries scan whole tables because an index is missing or the query is inefficient, making requests slow and causing timeouts.",
        "fix": [
            "Find slow queries using the slow query log",
            "Run EXPLAIN to check for full table scans",
            "Add the missing index",
            "Add pagination or caching for heavy queries",
        ],
    },
    "DB_DOWN": {
        "name": "Database down / unreachable",
        "layer": "Database",
        "description": "The application cannot connect to the database because it is down, out of disk, or blocked by a network/credentials change.",
        "fix": [
            "Check the database server status and disk space",
            "Verify host, port, credentials and firewall rules",
            "Fail over to a standby/replica if available",
            "Restore service and then review recent infra changes",
        ],
    },
    "REPLICA_LAG": {
        "name": "Read replica lag (stale reads)",
        "layer": "Database",
        "description": "Writes go to the primary but reads come from a replica that is behind, so users briefly see old data after saving.",
        "fix": [
            "Monitor replica lag",
            "Read from the primary right after a write (read-your-writes)",
            "Reduce heavy write load or upgrade the replica",
            "Show the saved data from the write response in the UI",
        ],
    },

    # ----- Authentication -----
    "TOKEN_EXPIRED": {
        "name": "Access token expired",
        "layer": "Authentication",
        "description": "The user's access token or session has passed its expiry time, so the API rejects it with 401.",
        "fix": [
            "Use the refresh token to get a new access token automatically",
            "Redirect the user to log in again if refresh fails",
            "Check that the token lifetime is configured sensibly",
            "Handle 401 globally in the frontend",
        ],
    },
    "INVALID_SIGNATURE": {
        "name": "Invalid token signature / rotated secret",
        "layer": "Authentication",
        "description": "The token was signed with a key the API no longer trusts, usually because the signing secret was rotated or services use different keys.",
        "fix": [
            "Make sure all services use the same signing key / JWKS",
            "Support old and new keys during rotation (key id 'kid')",
            "Force users to log in again to get new tokens",
            "Store secrets in one central secret manager",
        ],
    },
    "CLOCK_SKEW": {
        "name": "Server clock skew",
        "layer": "Authentication",
        "description": "Server clocks are out of sync, so fresh tokens look expired or 'not yet valid' to some servers.",
        "fix": [
            "Enable NTP time sync on all servers",
            "Allow a small clock tolerance (e.g. 30-60 seconds) when checking tokens",
            "Find which server has the wrong time",
            "Monitor clock drift",
        ],
    },
    "RBAC_MISSING_ROLE": {
        "name": "Missing role / permission (403)",
        "layer": "Authentication",
        "description": "The user is logged in with a valid token but does not have the role or permission required for this endpoint.",
        "fix": [
            "Check which role the endpoint requires",
            "Grant the role/permission to the user or group",
            "Update the permission mapping for new endpoints",
            "Ask the user to log in again so the token gets new roles",
        ],
    },
    "WRONG_OAUTH_SCOPE": {
        "name": "Wrong or missing OAuth scope",
        "layer": "Authentication",
        "description": "The access token was issued without the OAuth scope the API requires, so the request is forbidden.",
        "fix": [
            "Check which scope the endpoint requires",
            "Request the missing scope in the authorization request",
            "Allow the scope for this client in the identity provider",
            "Have the user re-consent and get a new token",
        ],
    },

    # ----- Infrastructure -----
    "BAD_DEPLOYMENT": {
        "name": "Bad deployment",
        "layer": "Infrastructure",
        "description": "The newest release contains a bug or broken build, so the new version crashes or fails right after it is deployed.",
        "fix": [
            "Roll back to the last working version",
            "Check deployment and startup logs",
            "Fix the issue and test it in staging",
            "Use canary or blue-green deployments next time",
        ],
    },
    "SERVICE_OVERLOADED": {
        "name": "Service overloaded",
        "layer": "Infrastructure",
        "description": "There is more traffic than the servers can handle, so CPU is maxed out and the service starts rejecting or delaying requests.",
        "fix": [
            "Scale out (add more instances) or enable autoscaling",
            "Add caching for heavy or repeated requests",
            "Enable rate limiting to protect the service",
            "Block abusive or bot traffic",
        ],
    },
    "MEMORY_LEAK_OOM": {
        "name": "Memory leak / out-of-memory restarts",
        "layer": "Infrastructure",
        "description": "The service keeps using more memory until it is killed for running out of memory (OOM) and restarts, causing errors during restarts.",
        "fix": [
            "Check memory graphs and OOMKilled events",
            "Take a heap dump/profile to find the leak",
            "Fix unbounded caches or unreleased objects",
            "Temporarily raise memory limits or restart on a schedule",
        ],
    },
}
