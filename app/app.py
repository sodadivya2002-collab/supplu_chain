# ============================================================
# WHAT TO ADD / CHANGE IN YOUR APP
# ============================================================

# ------------------------------------------------------------
# 1) Add these imports at the top
# ------------------------------------------------------------
import requests


# ------------------------------------------------------------
# 2) Set your semantic view's fully-qualified name.
#    Format: DATABASE.SCHEMA.SEMANTIC_VIEW_NAME
#    (You can also pull this from st.secrets instead of hardcoding.)
# ------------------------------------------------------------
SEMANTIC_VIEW = "SUPPLY_CHAIN_DW.GOLD.SUPPLY_CHAIN_SEMANTIC_VIEW"  # <-- change to yours


# ------------------------------------------------------------
# 3) In the LOGIN block, DO NOT close the raw connector connection.
#    Cortex Analyst auth relies on that connection's session token.
#
#    Replace:
#        conn = snowflake.connector.connect(**connection_parameters)
#        conn.close()
#    With:
#        conn = snowflake.connector.connect(**connection_parameters)
#        st.session_state.raw_conn = conn   # keep it alive
#
#    (Keep creating the Snowpark session exactly as you do now —
#     you still need it to run the generated SQL and show results.)
# ------------------------------------------------------------


# ------------------------------------------------------------
# 4) New function: calls Cortex Analyst and parses its response.
#    Put this near your other helper functions.
# ------------------------------------------------------------
def call_cortex_analyst(prompt: str, conn, account: str):
    """
    Sends the user's natural-language question to Cortex Analyst,
    which uses your semantic view to generate SQL.
    Returns: (explanation_text, sql_statement_or_None, suggestions_list)
    """

    # Build the account host. If your account identifier has
    # underscores, Snowflake's URL form usually wants dashes instead
    # e.g. "myorg_myaccount" -> "myorg-myaccount"
    host = f"{account.replace('_', '-')}.snowflakecomputing.com"

    url = f"https://{host}/api/v2/cortex/analyst/message"

    request_body = {
        "messages": [
            {"role": "user", "content": [{"type": "text", "text": prompt}]}
        ],
        "semantic_view": SEMANTIC_VIEW,
    }

    resp = requests.post(
        url,
        json=request_body,
        headers={
            "Authorization": f'Snowflake Token="{conn.rest.token}"',
            "Content-Type": "application/json",
        },
        timeout=60,
    )

    if resp.status_code >= 400:
        raise Exception(
            f"Cortex Analyst error ({resp.status_code}): {resp.text}"
        )

    data = resp.json()

    explanation_text = ""
    sql_statement = None
    suggestions = []

    for item in data.get("message", {}).get("content", []):

        if item["type"] == "text":
            explanation_text += item["text"]

        elif item["type"] == "sql":
            sql_statement = item["statement"]

        elif item["type"] == "suggestions":
            suggestions = item.get("suggestions", [])

    return explanation_text.strip(), sql_statement, suggestions


# ------------------------------------------------------------
# 5) In the "GENERATE SQL" section of your chat handler, replace:
#
#       explanation, sql_query = generate_sql_from_prompt(user_prompt)
#
#    With something like:
#
#       is_greeting_prompt = user_prompt.strip().lower() in GREETING_PHRASES
#
#       if is_greeting_prompt:
#           explanation, sql_query = generate_sql_from_prompt(user_prompt)  # keep your greeting/help logic
#           suggestions = GREETING_SUGGESTIONS
#       else:
#           try:
#               explanation, sql_query, suggestions = call_cortex_analyst(
#                   user_prompt,
#                   st.session_state.raw_conn,
#                   get_snowflake_config()["account"],
#               )
#           except Exception as e:
#               explanation, sql_query, suggestions = (
#                   f"Sorry, I couldn't reach Cortex Analyst: {e}", None, None
#               )
#
#    Everything below that (st.markdown(explanation), showing the SQL
#    expander, session.sql(sql_query).to_pandas(), the Data/Chart tabs)
#    stays exactly the same — Cortex Analyst just supplies real SQL
#    instead of your keyword matcher.
# ------------------------------------------------------------
