import streamlit as st
import pandas as pd
from datetime import datetime
import snowflake.connector
from snowflake.snowpark import Session
import yaml
import os
import re


# ===================================================================
# 1. CONFIGURATION
# ===================================================================

HOST = "XYUHKAV-XRB12650.snowflakecomputing.com"
ACCOUNT = "XYUHKAV-XRB12650"

DATABASE = "SUPPLY_CHAIN_DW"
SCHEMA = "GOLD"
WAREHOUSE = "COMPUTE_WH"
ROLE = "ACCOUNTADMIN"

# YAML file should be in the same folder as this Python file
YAML_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "SUPPLY_CHAIN_SEMANTIC.yaml"
)


# ===================================================================
# 2. PAGE CONFIGURATION
# ===================================================================

st.set_page_config(
    page_title="Dilytics Supply Chain AI",
    page_icon="🚚",
    layout="wide"
)


# ===================================================================
# 3. CUSTOM UI STYLING
# ===================================================================

st.markdown(
    """
    <style>

    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background-color: #ecfdf5;
        color: #065f46;
        border: 1px solid #a7f3d0;
        border-radius: 20px;
        padding: 2px 10px;
        font-size: 0.75rem;
        font-weight: 600;
    }

    div[data-testid="stButton"] > button {
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.2s ease-in-out;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ===================================================================
# 4. LOAD SUPPLY CHAIN YAML
# ===================================================================

def load_semantic_yaml():

    if not os.path.exists(YAML_FILE):

        st.error(
            f"Supply Chain YAML file not found:\n\n{YAML_FILE}"
        )

        return {}


    try:

        with open(
            YAML_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            model = yaml.safe_load(file)

        if model is None:
            return {}

        return model

    except Exception as e:

        st.error(
            f"Unable to load SUPPLY_CHAIN_SEMANTIC.yaml: {e}"
        )

        return {}


SEMANTIC_MODEL = load_semantic_yaml()


# ===================================================================
# 5. EXTRACT VERIFIED QUERIES FROM YAML
# ===================================================================

def get_verified_queries():

    verified_queries = (
        SEMANTIC_MODEL.get(
            "verified_queries",
            []
        )
    )

    if not isinstance(
        verified_queries,
        list
    ):

        return []


    results = []


    for item in verified_queries:

        if not isinstance(
            item,
            dict
        ):

            continue


        question = item.get(
            "question"
        )

        sql = item.get(
            "sql"
        )


        if question and sql:

            results.append(
                {
                    "question": str(
                        question
                    ).strip(),

                    "sql": str(
                        sql
                    ).strip(),

                    "onboarding": bool(
                        item.get(
                            "use_as_onboarding_question",
                            False
                        )
                    )
                }
            )


    return results


VERIFIED_QUERIES = get_verified_queries()


# ===================================================================
# 6. NORMALIZE USER QUESTION
# ===================================================================

def normalize_text(text):

    if text is None:
        return ""

    text = str(text).lower().strip()

    # Remove punctuation
    text = re.sub(
        r"[^a-z0-9% ]",
        " ",
        text
    )

    # Remove extra spaces
    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ===================================================================
# 7. MATCH QUESTION TO YAML
# ===================================================================

def match_verified_query(prompt):

    normalized_prompt = normalize_text(
        prompt
    )


    # ===============================================================
    # FIRST: EXACT MATCH
    # ===============================================================

    for item in VERIFIED_QUERIES:

        normalized_question = normalize_text(
            item["question"]
        )

        if normalized_prompt == normalized_question:

            return item


    # ===============================================================
    # SPECIFIC SUPPLY CHAIN MATCHING
    #
    # These are aliases / natural language variations.
    # The SQL ALWAYS comes from YAML.
    # ===============================================================

    question_aliases = {

        "warehouse_city": [
            "how many warehouses are there by city",
            "how many warehouses by city",
            "warehouse count by city",
            "warehouse counts by city",
            "number of warehouses by city",
            "warehouses by city",
            "warehouse by city",
            "city wise warehouse count",
            "city wise warehouses count"
        ],

        "supplier_city": [
            "how many suppliers are there by city",
            "how many suppliers by city",
            "supplier count by city",
            "supplier counts by city",
            "number of suppliers by city",
            "suppliers by city",
            "supplier by city",
            "city wise supplier count",
            "city wise suppliers count"
        ],

        "products_category": [
            "how many products are there in each category",
            "how many products in each category",
            "products by category",
            "product count by category",
            "product counts by category",
            "number of products by category"
        ],

        "top_products_weight": [
            "what are the top 10 products by weight",
            "top 10 products by weight",
            "top products by weight",
            "heaviest products"
        ],

        "received_quantity": [
            "what is the total received quantity",
            "total received quantity",
            "received quantity"
        ],

        "total_shipments": [
            "what is the total shipments",
            "total shipments",
            "how many shipments do we have",
            "how many shipments",
            "shipment count",
            "total shipment count"
        ],

        "total_purchase_orders": [
            "how many purchase orders do we have",
            "how many purchase orders",
            "total purchase orders",
            "purchase order count",
            "total po",
            "how many po"
        ],

        "ordered_quantity": [
            "what is the total ordered quantity",
            "total ordered quantity",
            "ordered quantity"
        ],

        "supplier_on_time": [
            "what is the supplier on time delivery percentage",
            "what is the supplier on-time delivery percentage",
            "supplier on time delivery",
            "supplier on-time delivery",
            "supplier on time delivery percentage",
            "supplier on-time delivery percentage"
        ],

        "rejected_value": [
            "what is the total rejected value",
            "total rejected value",
            "rejected value",
            "total rejected amount"
        ],

        "delivery_delay_supplier": [
            "what is our average delivery delay by supplier",
            "average delivery delay by supplier",
            "delivery delay by supplier",
            "average supplier delivery delay"
        ]
    }


    # ===============================================================
    # FIND ALIAS
    # ===============================================================

    matched_category = None


    for category, aliases in question_aliases.items():

        for alias in aliases:

            if normalized_prompt == normalize_text(alias):

                matched_category = category
                break

            # Allow small variations such as:
            # "can you tell me how many warehouses are there by city"

            if normalize_text(alias) in normalized_prompt:

                matched_category = category
                break

        if matched_category:
            break


    if matched_category is None:

        return None


    # ===============================================================
    # MAP ALIAS TO THE ACTUAL YAML QUESTION
    # ===============================================================

    yaml_question_keywords = {

        "warehouse_city": [
            "warehouse",
            "city"
        ],

        "supplier_city": [
            "supplier",
            "city"
        ],

        "products_category": [
            "product",
            "category"
        ],

        "top_products_weight": [
            "product",
            "weight"
        ],

        "received_quantity": [
            "received",
            "quantity"
        ],

        "total_shipments": [
            "shipment"
        ],

        "total_purchase_orders": [
            "purchase",
            "order"
        ],

        "ordered_quantity": [
            "ordered",
            "quantity"
        ],

        "supplier_on_time": [
            "supplier",
            "on",
            "time",
            "delivery"
        ],

        "rejected_value": [
            "reject"
        ],

        "delivery_delay_supplier": [
            "delivery",
            "delay",
            "supplier"
        ]
    }


    keywords = yaml_question_keywords[
        matched_category
    ]


    best_match = None
    best_score = 0


    for item in VERIFIED_QUERIES:

        q = normalize_text(
            item["question"]
        )

        score = 0


        for keyword in keywords:

            if keyword in q:

                score += 1


        if score > best_score:

            best_score = score
            best_match = item


    if best_match:

        return best_match


    return None


# ===================================================================
# 8. GET VERIFIED SQL ONLY
# ===================================================================

def get_verified_sql(prompt):

    matched = match_verified_query(
        prompt
    )

    if matched:

        return (
            matched["sql"],
            matched["question"]
        )


    return None, None


# ===================================================================
# 9. SUPPLY CHAIN RULE-BASED SQL
#
# Only used for questions that are NOT already in YAML.
# YAML verified queries always take priority.
# ===================================================================

def generate_rule_based_sql(prompt):

    p = normalize_text(
        prompt
    )


    # ===============================================================
    # GREETINGS
    # ===============================================================

    if p in [
        "hi",
        "hello",
        "hey",
        "good morning",
        "good afternoon",
        "good evening"
    ]:

        return (
            "Hello! I am your **Supply Chain Intelligence Assistant**. "
            "You can ask me about purchase orders, suppliers, "
            "shipments, delivery performance, carriers, products, "
            "warehouses, logistics, delays, and supply chain costs.",
            None
        )


    if any(
        phrase in p
        for phrase in [
            "how are you",
            "how is it going",
            "whats up",
            "what is up"
        ]
    ):

        return (
            "I'm doing well! I am ready to help you analyze "
            "your Supply Chain data.",
            None
        )


    # ===============================================================
    # HELP
    # ===============================================================

    if any(
        phrase in p
        for phrase in [
            "what can i ask",
            "what questions",
            "what can you do",
            "examples",
            "help"
        ]
    ):

        return (
            """
You can ask me questions about your **Supply Chain data**.

**Purchase Orders**
- How many purchase orders do we have?
- What is the total ordered quantity?
- What is the total received quantity?
- What is the total rejected value?

**Suppliers**
- What is the supplier on-time delivery percentage?
- What is the average delivery delay by supplier?
- How many suppliers are there by city?

**Shipments**
- How many shipments do we have?
- What are the shipment delays by reason?
- What are the top carriers?
- What is the freight cost by carrier?

**Products**
- How many products are there in each category?
- What are the top 10 products by weight?

**Warehouses**
- How many warehouses are there by city?
""",
            None
        )


    # ===============================================================
    # OPEN PURCHASE ORDERS
    # ===============================================================

    if (
        "open purchase order" in p
        or "open po" in p
        or "outstanding purchase order" in p
    ):

        return (
            "Calculating the number of open purchase orders.",
            """
SELECT
    COUNT(DISTINCT PURCHASE_ORDER_NUMBER) AS OPEN_PURCHASE_ORDERS
FROM SUPPLY_CHAIN_DW.GOLD.FACT_PURCHASE_ORDER_LINE
WHERE IS_OPEN_PO_FLAG = TRUE
            """.strip()
        )


    # ===============================================================
    # OPEN QUANTITY
    # ===============================================================

    if (
        "open quantity" in p
        or "outstanding quantity" in p
        or "quantity not received" in p
    ):

        return (
            "Calculating the quantity that is still open.",
            """
SELECT
    SUM(OPEN_QUANTITY) AS TOTAL_OPEN_QUANTITY
FROM SUPPLY_CHAIN_DW.GOLD.FACT_PURCHASE_ORDER_LINE
            """.strip()
        )


    # ===============================================================
    # ORDERED AMOUNT
    # ===============================================================

    if (
        "ordered amount" in p
        or "total order value" in p
        or "value ordered" in p
    ):

        return (
            "Calculating the total value of purchase orders.",
            """
SELECT
    SUM(ORDERED_AMT) AS TOTAL_ORDERED_AMOUNT
FROM SUPPLY_CHAIN_DW.GOLD.FACT_PURCHASE_ORDER_LINE
            """.strip()
        )


    # ===============================================================
    # SUPPLIER RISK
    # ===============================================================

    if (
        "supplier risk" in p
        or "supplier risks" in p
        or "risky suppliers" in p
        or "high risk suppliers" in p
    ):

        return (
            "Showing suppliers by their supply chain risk rating.",
            """
SELECT
    RISK_RATING,
    COUNT(SUPPLIER_KEY) AS SUPPLIER_COUNT
FROM SUPPLY_CHAIN_DW.GOLD.DIM_SUPPLIER
GROUP BY RISK_RATING
ORDER BY SUPPLIER_COUNT DESC
            """.strip()
        )


    # ===============================================================
    # SUPPLIER QUALITY
    # ===============================================================

    if (
        "supplier quality" in p
        or "quality by supplier" in p
        or "supplier quality rating" in p
    ):

        return (
            "Showing supplier quality ratings.",
            """
SELECT
    SUPPLIER_NAME,
    SUPPLIER_CODE,
    QUALITY_RATING,
    QUALITY_BAND
FROM SUPPLY_CHAIN_DW.GOLD.DIM_SUPPLIER
ORDER BY QUALITY_RATING DESC
            """.strip()
        )


    # ===============================================================
    # SUPPLIER LEAD TIME
    # ===============================================================

    if (
        "supplier lead time" in p
        or "lead time by supplier" in p
        or "supplier delivery time" in p
    ):

        return (
            "Showing standard supplier lead times.",
            """
SELECT
    SUPPLIER_NAME,
    SUPPLIER_CODE,
    STANDARD_LEAD_TIME_DAYS,
    LEAD_TIME_BAND
FROM SUPPLY_CHAIN_DW.GOLD.DIM_SUPPLIER
ORDER BY STANDARD_LEAD_TIME_DAYS DESC
            """.strip()
        )


    # ===============================================================
    # SHIPMENTS BY CARRIER
    # ===============================================================

    if (
        "shipments by carrier" in p
        or "shipment by carrier" in p
        or "carrier shipment count" in p
    ):

        return (
            "Counting shipments handled by each carrier.",
            """
SELECT
    c.CARRIER_NAME,
    c.CARRIER_CODE,
    COUNT(f.SHIPMENT_KEY) AS SHIPMENT_COUNT
FROM SUPPLY_CHAIN_DW.GOLD.FACT_SHIPMENT_DELIVERY f
JOIN SUPPLY_CHAIN_DW.GOLD.DIM_CARRIER c
    ON f.CARRIER_KEY = c.CARRIER_KEY
GROUP BY
    c.CARRIER_NAME,
    c.CARRIER_CODE
ORDER BY SHIPMENT_COUNT DESC
            """.strip()
        )


    # ===============================================================
    # SHIPMENTS BY MODE
    # ===============================================================

    if (
        "shipments by mode" in p
        or "shipment by mode" in p
        or "shipping mode" in p
    ):

        return (
            "Analyzing shipment volume by transportation mode.",
            """
SELECT
    sm.SHIP_MODE_NAME,
    sm.TRANSPORT_MODE,
    COUNT(f.SHIPMENT_KEY) AS SHIPMENT_COUNT
FROM SUPPLY_CHAIN_DW.GOLD.FACT_SHIPMENT_DELIVERY f
JOIN SUPPLY_CHAIN_DW.GOLD.DIM_SHIP_MODE sm
    ON f.SHIP_MODE_KEY = sm.SHIP_MODE_KEY
GROUP BY
    sm.SHIP_MODE_NAME,
    sm.TRANSPORT_MODE
ORDER BY SHIPMENT_COUNT DESC
            """.strip()
        )


    # ===============================================================
    # DELAY REASONS
    # ===============================================================

    if (
        "delay reason" in p
        or "delay reasons" in p
        or "delays by reason" in p
    ):

        return (
            "Analyzing shipment delays by reason.",
            """
SELECT
    dr.DELAY_REASON_NAME,
    dr.RESPONSIBLE_PARTY,
    COUNT(f.SHIPMENT_KEY) AS DELAYED_SHIPMENTS,
    AVG(f.DELIVERY_DELAY_DAYS) AS AVG_DELAY_DAYS
FROM SUPPLY_CHAIN_DW.GOLD.FACT_SHIPMENT_DELIVERY f
JOIN SUPPLY_CHAIN_DW.GOLD.DIM_DELAY_REASON dr
    ON f.DELAY_REASON_KEY = dr.DELAY_REASON_KEY
WHERE f.IS_DELAYED_FLAG = TRUE
GROUP BY
    dr.DELAY_REASON_NAME,
    dr.RESPONSIBLE_PARTY
ORDER BY DELAYED_SHIPMENTS DESC
            """.strip()
        )


    # ===============================================================
    # CARRIER PERFORMANCE
    # ===============================================================

    if (
        "carrier performance" in p
        or "carrier on time" in p
        or "carrier on-time" in p
    ):

        return (
            "Calculating shipment on-time performance by carrier.",
            """
SELECT
    c.CARRIER_NAME,
    c.CARRIER_CODE,
    ROUND(
        100.0 *
        COUNT_IF(
            f.IS_ON_TIME_DELIVERY_FLAG = TRUE
        )
        /
        NULLIF(
            COUNT_IF(
                f.IS_ON_TIME_DELIVERY_FLAG IS NOT NULL
            ),
            0
        ),
        2
    ) AS ON_TIME_DELIVERY_PCT
FROM SUPPLY_CHAIN_DW.GOLD.FACT_SHIPMENT_DELIVERY f
JOIN SUPPLY_CHAIN_DW.GOLD.DIM_CARRIER c
    ON f.CARRIER_KEY = c.CARRIER_KEY
GROUP BY
    c.CARRIER_NAME,
    c.CARRIER_CODE
ORDER BY ON_TIME_DELIVERY_PCT DESC
            """.strip()
        )


    # ===============================================================
    # FREIGHT COST BY CARRIER
    # ===============================================================

    if (
        "freight cost by carrier" in p
        or "carrier freight cost" in p
    ):

        return (
            "Calculating freight cost by carrier.",
            """
SELECT
    c.CARRIER_NAME,
    c.CARRIER_CODE,
    SUM(f.FREIGHT_COST_AMT) AS TOTAL_FREIGHT_COST
FROM SUPPLY_CHAIN_DW.GOLD.FACT_SHIPMENT_DELIVERY f
JOIN SUPPLY_CHAIN_DW.GOLD.DIM_CARRIER c
    ON f.CARRIER_KEY = c.CARRIER_KEY
GROUP BY
    c.CARRIER_NAME,
    c.CARRIER_CODE
ORDER BY TOTAL_FREIGHT_COST DESC
            """.strip()
        )


    # ===============================================================
    # LANDED COST BY SUPPLIER
    # ===============================================================

    if (
        "landed cost by supplier" in p
        or "supplier landed cost" in p
    ):

        return (
            "Calculating total landed cost by supplier.",
            """
SELECT
    s.SUPPLIER_NAME,
    s.SUPPLIER_CODE,
    SUM(f.TOTAL_LANDED_COST_AMT) AS TOTAL_LANDED_COST
FROM SUPPLY_CHAIN_DW.GOLD.FACT_SHIPMENT_DELIVERY f
JOIN SUPPLY_CHAIN_DW.GOLD.DIM_SUPPLIER s
    ON f.SUPPLIER_KEY = s.SUPPLIER_KEY
GROUP BY
    s.SUPPLIER_NAME,
    s.SUPPLIER_CODE
ORDER BY TOTAL_LANDED_COST DESC
            """.strip()
        )


    # ===============================================================
    # INTERNATIONAL SHIPMENTS
    # ===============================================================

    if (
        "international shipment" in p
        or "international shipments" in p
    ):

        return (
            "Counting international shipments.",
            """
SELECT
    COUNT(SHIPMENT_KEY) AS INTERNATIONAL_SHIPMENTS
FROM SUPPLY_CHAIN_DW.GOLD.FACT_SHIPMENT_DELIVERY
WHERE IS_INTERNATIONAL_FLAG = TRUE
            """.strip()
        )


    # ===============================================================
    # DAMAGED SHIPMENTS
    # ===============================================================

    if (
        "damaged shipment" in p
        or "damaged shipments" in p
    ):

        return (
            "Analyzing damaged shipments.",
            """
SELECT
    COUNT(SHIPMENT_KEY) AS DAMAGED_SHIPMENTS,
    SUM(DAMAGED_QUANTITY) AS DAMAGED_QUANTITY
FROM SUPPLY_CHAIN_DW.GOLD.FACT_SHIPMENT_DELIVERY
WHERE IS_DAMAGED_FLAG = TRUE
            """.strip()
        )


    # ===============================================================
    # PRODUCT BRAND
    # ===============================================================

    if (
        "products by brand" in p
        or "product brand" in p
        or "brand count" in p
    ):

        return (
            "Counting products by brand.",
            """
SELECT
    BRAND_NAME,
    COUNT(PRODUCT_KEY) AS PRODUCT_COUNT
FROM SUPPLY_CHAIN_DW.GOLD.DIM_PRODUCT
GROUP BY BRAND_NAME
ORDER BY PRODUCT_COUNT DESC
            """.strip()
        )


    # ===============================================================
    # PRODUCT SUBCATEGORY
    # ===============================================================

    if (
        "products by subcategory" in p
        or "product subcategory" in p
    ):

        return (
            "Counting products by subcategory.",
            """
SELECT
    SUBCATEGORY_NAME,
    COUNT(PRODUCT_KEY) AS PRODUCT_COUNT
FROM SUPPLY_CHAIN_DW.GOLD.DIM_PRODUCT
GROUP BY SUBCATEGORY_NAME
ORDER BY PRODUCT_COUNT DESC
            """.strip()
        )


    # ===============================================================
    # WAREHOUSE / CITY
    #
    # This is deliberately included as a safety net.
    # However, YAML is checked BEFORE this function.
    # ===============================================================

    if (
        "warehouse" in p
        and "city" in p
    ):

        return (
            "Counting warehouses by city.",
            """
SELECT
    w.CITY_NAME,
    COUNT(w.WAREHOUSE_KEY) AS WAREHOUSE_COUNT
FROM SUPPLY_CHAIN_DW.GOLD.DIM_WAREHOUSE w
GROUP BY
    w.CITY_NAME
ORDER BY
    WAREHOUSE_COUNT DESC NULLS LAST
            """.strip()
        )


    # ===============================================================
    # SUPPLIER / CITY
    # ===============================================================

    if (
        "supplier" in p
        and "city" in p
    ):

        return (
            "Counting suppliers by city.",
            """
SELECT
    s.CITY_NAME,
    COUNT(DISTINCT s.SUPPLIER_KEY) AS SUPPLIER_COUNT
FROM SUPPLY_CHAIN_DW.GOLD.DIM_SUPPLIER s
GROUP BY
    s.CITY_NAME
ORDER BY
    SUPPLIER_COUNT DESC NULLS LAST
            """.strip()
        )


    return (
        """
I couldn't find a verified Supply Chain query for that question.

Please ask about purchase orders, suppliers, shipments, 
delivery performance, carriers, products, warehouses, 
logistics, delays, or supply chain costs.
        """.strip(),
        None
    )


# ===================================================================
# 10. MAIN QUESTION PROCESSOR
#
# IMPORTANT:
# YAML VERIFIED QUERY ALWAYS HAS PRIORITY.
# ===================================================================

def generate_sql_from_prompt(prompt):

    # ---------------------------------------------------------------
    # Greetings / Help
    # ---------------------------------------------------------------

    p = normalize_text(
        prompt
    )


    if p in [
        "hi",
        "hello",
        "hey",
        "good morning",
        "good afternoon",
        "good evening"
    ]:

        return (
            "Hello! I am your **Supply Chain Intelligence Assistant**. "
            "Ask me about purchase orders, suppliers, shipments, "
            "delivery performance, products, warehouses, carriers, "
            "or logistics.",
            None
        )


    if any(
        phrase in p
        for phrase in [
            "how are you",
            "how is it going",
            "whats up",
            "what is up"
        ]
    ):

        return (
            "I'm doing well! I am ready to help you analyze "
            "your Supply Chain data.",
            None
        )


    if any(
        phrase in p
        for phrase in [
            "what can i ask",
            "what questions",
            "what can you do",
            "examples",
            "help"
        ]
    ):

        return (
            """
You can ask me about:

**Purchase Orders**
- How many purchase orders do we have?
- What is the total ordered quantity?
- What is the total received quantity?
- What is the total rejected value?

**Suppliers**
- What is the supplier on-time delivery percentage?
- What is the average delivery delay by supplier?
- How many suppliers are there by city?

**Shipments**
- How many shipments do we have?
- What are the shipment delays by reason?
- What are shipments by carrier?
- What are shipments by shipping mode?

**Products**
- How many products are there in each category?
- What are the top 10 products by weight?

**Warehouses**
- How many warehouses are there by city?
            """.strip(),
            None
        )


    # ===============================================================
    # VERY IMPORTANT:
    # CHECK YAML FIRST
    # ===============================================================

    yaml_sql, yaml_question = get_verified_sql(
        prompt
    )


    if yaml_sql:

        return (
            f"Using the verified Supply Chain semantic query for "
            f"**{yaml_question}**.",
            yaml_sql
        )


    # ===============================================================
    # IF NOT IN YAML, USE RULE-BASED SUPPLY CHAIN LOGIC
    # ===============================================================

    return generate_rule_based_sql(
        prompt
    )


# ===================================================================
# 11. CHART RENDERER
# ===================================================================

def display_chart_tab(
    df: pd.DataFrame,
    key_prefix: str = ""
):

    if df is None or df.empty:

        st.info(
            "No data available for chart."
        )

        return


    if len(df.columns) < 2:

        st.info(
            "Need at least 2 columns to render a chart."
        )

        return


    all_cols = list(
        df.columns
    )


    col1, col2, col3 = st.columns(3)


    x_key = (
        f"{key_prefix}_x"
        if key_prefix
        else "x_axis"
    )

    y_key = (
        f"{key_prefix}_y"
        if key_prefix
        else "y_axis"
    )

    type_key = (
        f"{key_prefix}_type"
        if key_prefix
        else "chart_type"
    )


    x_col = col1.selectbox(
        "Dimension (X-axis)",
        all_cols,
        index=0,
        key=x_key
    )


    remaining_cols = [
        c
        for c in all_cols
        if c != x_col
    ]


    if not remaining_cols:

        st.info(
            "No metric column available."
        )

        return


    y_col = col2.selectbox(
        "Metric (Y-axis)",
        remaining_cols,
        index=0,
        key=y_key
    )


    chart_type = col3.selectbox(
        "Chart Type",
        [
            "Bar Chart",
            "Line Chart",
            "Area Chart",
            "Scatter Plot"
        ],
        key=type_key
    )


    chart_df = df.copy()


    # Convert dates / numeric time dimensions
    if any(
        keyword in x_col.lower()
        for keyword in [
            "year",
            "quarter",
            "month",
            "day",
            "date"
        ]
    ):

        chart_df[x_col] = chart_df[
            x_col
        ].apply(
            lambda x:
            str(int(x))
            if pd.notnull(x)
            and isinstance(
                x,
                (int, float)
            )
            else str(x)
        )


    if chart_type == "Bar Chart":

        st.bar_chart(
            chart_df.set_index(
                x_col
            )[y_col]
        )


    elif chart_type == "Line Chart":

        st.line_chart(
            chart_df.set_index(
                x_col
            )[y_col]
        )


    elif chart_type == "Area Chart":

        st.area_chart(
            chart_df.set_index(
                x_col
            )[y_col]
        )


    elif chart_type == "Scatter Plot":

        st.scatter_chart(
            chart_df,
            x=x_col,
            y=y_col
        )


# ===================================================================
# 12. LOGIN / SNOWFLAKE CONNECTION
# ===================================================================

if "authenticated" not in st.session_state:

    st.session_state.authenticated = False

    st.session_state.username = "PBCS"

    st.session_state.password = ""

    st.session_state.snowpark_session = None


if not st.session_state.authenticated:

    st.title(
        "Welcome to Dilytics Supply Chain AI"
    )


    st.markdown(
        "Please login to connect to your Supply Chain Snowflake Data Warehouse."
    )


    st.session_state.username = st.text_input(
        "Enter Snowflake Username:",
        value=st.session_state.username
    )


    st.session_state.password = st.text_input(
        "Enter Password:",
        type="password"
    )


    if st.button(
        "Login"
    ):

        try:

            with st.spinner(
                "Connecting to Snowflake..."
            ):

                conn = snowflake.connector.connect(

                    user=st.session_state.username,

                    password=st.session_state.password,

                    account=ACCOUNT,

                    host=HOST,

                    port=443,

                    warehouse=WAREHOUSE,

                    role=ROLE,

                    database=DATABASE,

                    schema=SCHEMA
                )


                st.session_state.snowpark_session = (
                    Session
                    .builder
                    .configs(
                        {
                            "connection": conn
                        }
                    )
                    .create()
                )


                st.session_state.authenticated = True

                st.rerun()


        except Exception as e:

            st.error(
                f"Authentication failed: {e}"
            )


    st.stop()


# ===================================================================
# 13. GET SNOWPARK SESSION
# ===================================================================

session = (
    st.session_state.snowpark_session
)


# ===================================================================
# 14. MULTI-CHAT SESSION STATE
# ===================================================================

if "chat_sessions" not in st.session_state:

    st.session_state.chat_sessions = {}


if "current_session_id" not in st.session_state:

    init_id = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )


    st.session_state.current_session_id = (
        init_id
    )


    st.session_state.chat_sessions[
        init_id
    ] = {

        "title": "New Conversation",

        "messages": []
    }


current_id = (
    st.session_state.current_session_id
)


messages = (
    st.session_state.chat_sessions[
        current_id
    ]["messages"]
)


# ===================================================================
# 15. SIDEBAR
# ===================================================================

with st.sidebar:

    st.markdown(
        "### ⚡ Dilytics AI"
    )


    st.markdown(
        '<span class="status-pill">● Supply Chain Semantic Mart Live</span>',
        unsafe_allow_html=True
    )


    st.write("")


    # ---------------------------------------------------------------
    # NEW CHAT
    # ---------------------------------------------------------------

    if st.button(
        "➕ New Chat",
        use_container_width=True,
        type="primary"
    ):

        new_id = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )


        st.session_state.current_session_id = (
            new_id
        )


        st.session_state.chat_sessions[
            new_id
        ] = {

            "title":
                f"Chat {len(st.session_state.chat_sessions) + 1}",

            "messages": []
        }


        st.rerun()


    st.markdown("---")


    # ---------------------------------------------------------------
    # RECENT CONVERSATIONS
    # ---------------------------------------------------------------

    st.markdown(
        "##### 🕒 Recent Conversations"
    )


    for (
        s_id,
        s_data
    ) in reversed(
        list(
            st.session_state.chat_sessions.items()
        )
    ):

        is_active = (
            s_id ==
            st.session_state.current_session_id
        )


        session_label = (
            s_data["title"]
        )


        if len(session_label) > 20:

            session_label = (
                session_label[:18]
                + "..."
            )


        if st.button(
            f"{'👉 ' if is_active else '🗨️ '}{session_label}",
            key=f"sess_{s_id}",
            use_container_width=True
        ):

            st.session_state.current_session_id = (
                s_id
            )

            st.rerun()


    st.markdown("---")


    # ---------------------------------------------------------------
    # CLEAR ALL SESSIONS
    # ---------------------------------------------------------------

    if st.button(
        "🗑️ Clear All Sessions",
        use_container_width=True
    ):

        st.session_state.chat_sessions = {}


        init_id = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )


        st.session_state.current_session_id = (
            init_id
        )


        st.session_state.chat_sessions[
            init_id
        ] = {

            "title": "New Conversation",

            "messages": []
        }


        st.rerun()


# ===================================================================
# 16. MAIN HEADER
# ===================================================================

head_col1, head_col2 = st.columns(
    [4.5, 1.2]
)


with head_col1:

    st.title(
        "💬 Dilytics Supply Chain AI"
    )


    st.caption(
        "Ask questions in natural language to explore "
        "purchase orders, suppliers, shipments, delivery "
        "performance, logistics, products, carriers, and warehouses."
    )


with head_col2:

    st.write("")


    if st.button(
        "🔄 Reset Thread",
        use_container_width=True,
        help="Clear message history in this specific thread"
    ):

        st.session_state.chat_sessions[
            current_id
        ]["messages"] = []


        st.session_state.chat_sessions[
            current_id
        ]["title"] = "New Conversation"


        st.rerun()


# ===================================================================
# 17. WHAT CAN I ASK?
# ===================================================================

with st.expander(
    "💡 What exact questions can I ask this assistant?",
    expanded=False
):

    st.markdown(
        "This assistant uses the Supply Chain semantic model and verified YAML queries."
    )


    col_a, col_b = st.columns(2)


    with col_a:

        st.markdown(
            """
### 📋 Purchase Orders

- "How many purchase orders do we have?"
- "What is the total ordered quantity?"
- "What is the total received quantity?"
- "What is the total rejected value?"

### 🏭 Suppliers

- "What is the supplier on-time delivery percentage?"
- "What is the average delivery delay by supplier?"
- "How many suppliers are there by city?"
- "What are the supplier risks?"
- "What is the supplier quality?"
            """
        )


    with col_b:

        st.markdown(
            """
### 🚚 Shipments & Logistics

- "How many shipments do we have?"
- "What are the shipment delays by reason?"
- "What are shipments by carrier?"
- "What are shipments by shipping mode?"
- "What is the freight cost by carrier?"

### 📦 Products & Warehouses

- "How many products are there in each category?"
- "What are the top 10 products by weight?"
- "How many warehouses are there by city?"
            """
        )


    st.info(
        "💡 Pro-Tip: You can copy and paste any of these questions directly into the chat."
    )


# ===================================================================
# 18. VERIFIED ONBOARDING QUESTIONS
# ===================================================================

st.markdown(
    "##### 💡 Verified Onboarding Questions:"
)


q_col1, q_col2, q_col3, q_col4, q_col5 = st.columns(
    5
)


quick_prompt = None


if q_col1.button(
    "📋 Purchase Orders",
    use_container_width=True
):

    quick_prompt = (
        "How many purchase orders do we have?"
    )


if q_col2.button(
    "📦 Ordered Quantity",
    use_container_width=True
):

    quick_prompt = (
        "What is the total ordered quantity?"
    )


if q_col3.button(
    "⏱️ Supplier On-Time",
    use_container_width=True
):

    quick_prompt = (
        "What is the supplier on-time delivery percentage?"
    )


if q_col4.button(
    "🚚 Total Shipments",
    use_container_width=True
):

    quick_prompt = (
        "How many shipments do we have?"
    )


if q_col5.button(
    "❌ Rejected Value",
    use_container_width=True
):

    quick_prompt = (
        "What is the total rejected value?"
    )


# ===================================================================
# 19. DISPLAY CHAT HISTORY
# ===================================================================

for idx, msg in enumerate(
    messages
):

    with st.chat_message(
        msg["role"]
    ):

        st.markdown(
            msg["content"]
        )


        # -----------------------------------------------------------
        # SQL
        # -----------------------------------------------------------

        if (
            "sql" in msg
            and msg["sql"]
        ):

            with st.expander(
                "Generated SQL",
                expanded=False
            ):

                st.code(
                    msg["sql"],
                    language="sql"
                )


        # -----------------------------------------------------------
        # DATA
        # -----------------------------------------------------------

        if (
            "data" in msg
            and msg["data"] is not None
        ):

            data_df = msg["data"]


            if (
                isinstance(
                    data_df,
                    pd.DataFrame
                )
                and not data_df.empty
            ):

                tab_data, tab_chart = st.tabs(
                    [
                        "Data 📄",
                        "Chart 📈"
                    ]
                )


                with tab_data:

                    st.dataframe(
                        data_df,
                        use_container_width=True
                    )


                with tab_chart:

                    display_chart_tab(
                        data_df,
                        key_prefix=(
                            f"hist_{current_id}_{idx}"
                        )
                    )


# ===================================================================
# 20. USER INPUT
# ===================================================================

user_prompt = (
    st.chat_input(
        "Ask a question about purchase orders, suppliers, shipments, carriers, logistics, products, or warehouses..."
    )
    or quick_prompt
)


# ===================================================================
# 21. PROCESS USER QUESTION
# ===================================================================

if user_prompt:

    # ---------------------------------------------------------------
    # Set conversation title
    # ---------------------------------------------------------------

    if len(messages) == 0:

        st.session_state.chat_sessions[
            current_id
        ]["title"] = (
            user_prompt[:25]
            +
            (
                "..."
                if len(user_prompt) > 25
                else ""
            )
        )


    # ---------------------------------------------------------------
    # Save USER message
    # ---------------------------------------------------------------

    messages.append(
        {
            "role": "user",
            "content": user_prompt
        }
    )


    with st.chat_message(
        "user"
    ):

        st.markdown(
            user_prompt
        )


    # ---------------------------------------------------------------
    # ASSISTANT
    # ---------------------------------------------------------------

    with st.chat_message(
        "assistant"
    ):

        explanation, sql_query = (
            generate_sql_from_prompt(
                user_prompt
            )
        )


        st.markdown(
            explanation
        )


        df = None


        # -----------------------------------------------------------
        # Execute SQL
        # -----------------------------------------------------------

        if sql_query:

            with st.expander(
                "Generated SQL",
                expanded=False
            ):

                st.code(
                    sql_query,
                    language="sql"
                )


            try:

                with st.spinner(
                    "Running Supply Chain analysis..."
                ):

                    df = (
                        session
                        .sql(sql_query)
                        .to_pandas()
                    )


                # ---------------------------------------------------
                # DISPLAY DATA
                # ---------------------------------------------------

                if (
                    df is not None
                    and not df.empty
                ):

                    tab_data, tab_chart = st.tabs(
                        [
                            "Data 📄",
                            "Chart 📈"
                        ]
                    )


                    with tab_data:

                        st.dataframe(
                            df,
                            use_container_width=True
                        )


                    with tab_chart:

                        display_chart_tab(
                            df,
                            key_prefix=(
                                f"live_{current_id}"
                            )
                        )


                else:

                    st.info(
                        "The query executed successfully "
                        "but returned no rows."
                    )


            except Exception as e:

                st.error(
                    f"SQL Execution Error: {str(e)}"
                )


        # -----------------------------------------------------------
        # SAVE ASSISTANT MESSAGE
        # -----------------------------------------------------------

        messages.append(
            {
                "role": "assistant",

                "content": explanation,

                "sql": sql_query,

                "data": df
            }
        )


    st.rerun()
