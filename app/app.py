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

YAML_FILE = "SUPPLY_CHAIN_SEMANTIC.yaml"


# ===================================================================
# 2. LOAD SUPPLY CHAIN YAML
# ===================================================================

def load_semantic_yaml():

    if not os.path.exists(YAML_FILE):
        return {
            "name": "SUPPLY_CHAIN_SEMANTIC",
            "tables": [],
            "relationships": [],
            "verified_queries": []
        }

    try:
        with open(YAML_FILE, "r", encoding="utf-8") as file:
            model = yaml.safe_load(file)

        if model is None:
            model = {}

        return model

    except Exception as e:
        st.error(f"Unable to load semantic YAML: {e}")

        return {
            "name": "SUPPLY_CHAIN_SEMANTIC",
            "tables": [],
            "relationships": [],
            "verified_queries": []
        }


SEMANTIC_MODEL = load_semantic_yaml()


# ===================================================================
# 3. PAGE CONFIGURATION
# ===================================================================

st.set_page_config(
    page_title="Dilytics Supply Chain AI",
    page_icon="🚚",
    layout="wide"
)


# ===================================================================
# 4. CUSTOM UI STYLING
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
# 5. LOGIN / SNOWFLAKE CONNECTION
# ===================================================================

if "authenticated" not in st.session_state:

    st.session_state.authenticated = False
    st.session_state.username = "PBCS"
    st.session_state.password = ""
    st.session_state.snowpark_session = None


if not st.session_state.authenticated:

    st.title("Welcome to Dilytics Supply Chain AI")

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

    if st.button("Login"):

        try:

            with st.spinner("Connecting to Snowflake..."):

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
                    .configs({"connection": conn})
                    .create()
                )

                st.session_state.authenticated = True

                st.rerun()

        except Exception as e:

            st.error(f"Authentication failed: {e}")

    st.stop()


# ===================================================================
# 6. GET SNOWPARK SESSION
# ===================================================================

session = st.session_state.snowpark_session


# ===================================================================
# 7. SESSION STATE - MULTI CHAT
# ===================================================================

if "chat_sessions" not in st.session_state:

    st.session_state.chat_sessions = {}


if "current_session_id" not in st.session_state:

    init_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    st.session_state.current_session_id = init_id

    st.session_state.chat_sessions[init_id] = {
        "title": "New Conversation",
        "messages": []
    }


current_id = st.session_state.current_session_id

messages = st.session_state.chat_sessions[current_id]["messages"]


# ===================================================================
# 8. CHART RENDERER
# ===================================================================

def display_chart_tab(df: pd.DataFrame, key_prefix: str = ""):

    if df is None or df.empty:

        st.info("No data available for chart.")

        return

    if len(df.columns) < 2:

        st.info("Need at least 2 columns to render a chart.")

        return

    all_cols = list(df.columns)

    col1, col2, col3 = st.columns(3)

    x_key = f"{key_prefix}_x"
    y_key = f"{key_prefix}_y"
    t_key = f"{key_prefix}_type"

    x_col = col1.selectbox(
        "Dimension (X-axis)",
        all_cols,
        index=0,
        key=x_key
    )

    remaining_cols = [
        c for c in all_cols
        if c != x_col
    ]

    if not remaining_cols:
        st.info("No metric column available.")
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
        key=t_key
    )

    chart_df = df.copy()

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

        chart_df[x_col] = chart_df[x_col].apply(
            lambda x:
            str(int(x))
            if pd.notnull(x)
            and isinstance(x, (int, float))
            else str(x)
        )

    if chart_type == "Bar Chart":

        st.bar_chart(
            chart_df.set_index(x_col)[y_col]
        )

    elif chart_type == "Line Chart":

        st.line_chart(
            chart_df.set_index(x_col)[y_col]
        )

    elif chart_type == "Area Chart":

        st.area_chart(
            chart_df.set_index(x_col)[y_col]
        )

    elif chart_type == "Scatter Plot":

        st.scatter_chart(
            chart_df,
            x=x_col,
            y=y_col
        )


# ===================================================================
# 9. GET VERIFIED QUESTIONS FROM YAML
# ===================================================================

def get_verified_queries():

    verified = SEMANTIC_MODEL.get(
        "verified_queries",
        []
    )

    result = []

    if not isinstance(verified, list):
        return result

    for item in verified:

        if not isinstance(item, dict):
            continue

        question = item.get("question")
        sql = item.get("sql")

        if question and sql:

            result.append(
                {
                    "question": str(question).strip(),
                    "sql": str(sql).strip(),
                    "onboarding": item.get(
                        "use_as_onboarding_question",
                        False
                    )
                }
            )

    return result


VERIFIED_QUERIES = get_verified_queries()


# ===================================================================
# 10. NORMALIZE TEXT
# ===================================================================

def normalize_text(text):

    text = text.lower().strip()

    text = re.sub(
        r"[^a-z0-9% ]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text


# ===================================================================
# 11. MATCH VERIFIED YAML QUERY
# ===================================================================

def match_verified_query(prompt):

    p = normalize_text(prompt)

    if not VERIFIED_QUERIES:
        return None

    # Exact / near exact matching first

    for item in VERIFIED_QUERIES:

        q = normalize_text(
            item["question"]
        )

        if p == q:
            return item["sql"]

    # Keyword based matching

    keyword_rules = [

        (
            [
                "total purchase order",
                "total purchase orders",
                "how many purchase orders"
            ],
            "purchase order"
        ),

        (
            [
                "total ordered quantity",
                "ordered quantity"
            ],
            "ordered quantity"
        ),

        (
            [
                "supplier on time",
                "supplier on-time",
                "on time delivery",
                "on-time delivery"
            ],
            "supplier on time"
        ),

        (
            [
                "rejected value",
                "total rejected value"
            ],
            "rejected value"
        ),

        (
            [
                "total shipment",
                "total shipments",
                "how many shipments"
            ],
            "total shipments"
        ),

        (
            [
                "average delivery delay by supplier",
                "average delivery delay supplier",
                "delivery delay by supplier"
            ],
            "average delivery delay by supplier"
        ),

        (
            [
                "city wise supplier",
                "suppliers by city",
                "supplier count by city",
                "supplier city"
            ],
            "city wise suppliers count"
        ),

        (
            [
                "products in each category",
                "products by category",
                "how many products are there in each category"
            ],
            "products are there in each category"
        ),

        (
            [
                "total received quantity",
                "received quantity"
            ],
            "total received quantity"
        ),

        (
            [
                "warehouses by city",
                "warehouses are there by city",
                "warehouse count by city"
            ],
            "warehouses are there by city"
        )
    ]

    for keywords, query_identifier in keyword_rules:

        if any(
            keyword in p
            for keyword in keywords
        ):

            for item in VERIFIED_QUERIES:

                q = normalize_text(
                    item["question"]
                )

                if query_identifier in q:

                    return item["sql"]

    return None


# ===================================================================
# 12. SUPPLY CHAIN RULE-BASED SQL ENGINE
# ===================================================================

def generate_sql_from_prompt(prompt):

    p = normalize_text(prompt)

    # ---------------------------------------------------------------
    # Greetings
    # ---------------------------------------------------------------

    if any(
        greet in p
        for greet in [
            "how are you",
            "how is it going",
            "what is up",
            "whats up"
        ]
    ):

        explanation = (
            "I'm doing well, thank you! "
            "I am ready to help you analyze "
            "purchase orders, suppliers, shipments, "
            "delivery performance, logistics, products, "
            "warehouses, carriers, and supply chain costs."
        )

        return explanation, None


    if p in [
        "hi",
        "hello",
        "hey",
        "good morning",
        "good evening"
    ]:

        explanation = (
            "Hello! I am your Supply Chain Intelligence "
            "Assistant powered by the Supply Chain semantic model. "
            "Ask me about purchase orders, suppliers, shipments, "
            "delivery performance, warehouses, products, carriers, "
            "or logistics."
        )

        return explanation, None


    # ---------------------------------------------------------------
    # Help
    # ---------------------------------------------------------------

    if any(
        word in p
        for word in [
            "what can i ask",
            "what questions",
            "what can you do",
            "examples",
            "help"
        ]
    ):

        explanation = (
            "You can ask me questions about your Supply Chain data.\n\n"

            "**Purchase Orders:**\n"
            "- How many purchase orders do we have?\n"
            "- What is the total ordered quantity?\n"
            "- What is the total received quantity?\n"
            "- What is the total rejected value?\n\n"

            "**Supplier Performance:**\n"
            "- What is the supplier on-time delivery percentage?\n"
            "- What is the average delivery delay by supplier?\n"
            "- How many suppliers are there by city?\n\n"

            "**Shipments & Logistics:**\n"
            "- How many shipments do we have?\n"
            "- What is the average delivery delay by supplier?\n"
            "- What are the shipment delays by reason?\n\n"

            "**Products & Locations:**\n"
            "- How many products are there in each category?\n"
            "- What are the top 10 products by weight?\n"
            "- How many warehouses are there by city?\n"
        )

        return explanation, None


    # ---------------------------------------------------------------
    # Try YAML verified queries FIRST
    # ---------------------------------------------------------------

    verified_sql = match_verified_query(prompt)

    if verified_sql:

        explanation = (
            "I found a verified Supply Chain query "
            "from the semantic YAML and am executing it."
        )

        return explanation, verified_sql


    # =================================================================
    # ADDITIONAL SUPPLY CHAIN QUESTIONS
    # =================================================================


    # ---------------------------------------------------------------
    # Open Purchase Orders
    # ---------------------------------------------------------------

    if (
        "open purchase order" in p
        or "open po" in p
        or "outstanding purchase order" in p
    ):

        explanation = (
            "Calculating the number of purchase orders "
            "that are still open and awaiting fulfillment."
        )

        sql = """
        SELECT
            COUNT(DISTINCT PURCHASE_ORDER_NUMBER) AS OPEN_PURCHASE_ORDERS
        FROM SUPPLY_CHAIN_DW.GOLD.FACT_PURCHASE_ORDER_LINE
        WHERE IS_OPEN_PO_FLAG = TRUE
        """

        return explanation, sql.strip()


    # ---------------------------------------------------------------
    # Open Quantity
    # ---------------------------------------------------------------

    if (
        "open quantity" in p
        or "quantity still not arrived" in p
        or "outstanding quantity" in p
    ):

        explanation = (
            "Calculating the quantity that has been ordered "
            "but has not yet been received."
        )

        sql = """
        SELECT
            SUM(OPEN_QUANTITY) AS TOTAL_OPEN_QUANTITY
        FROM SUPPLY_CHAIN_DW.GOLD.FACT_PURCHASE_ORDER_LINE
        """

        return explanation, sql.strip()


    # ---------------------------------------------------------------
    # Ordered Amount
    # ---------------------------------------------------------------

    if (
        "ordered amount" in p
        or "value ordered" in p
        or "total order value" in p
    ):

        explanation = (
            "Calculating the total monetary value of "
            "purchase orders placed with suppliers."
        )

        sql = """
        SELECT
            SUM(ORDERED_AMT) AS TOTAL_ORDERED_AMOUNT
        FROM SUPPLY_CHAIN_DW.GOLD.FACT_PURCHASE_ORDER_LINE
        """

        return explanation, sql.strip()


    # ---------------------------------------------------------------
    # Received Amount / Spend
    # ---------------------------------------------------------------

    if (
        "received amount" in p
        or "received value" in p
        or "supplier spend" in p
        or "spend by supplier" in p
    ):

        if "supplier" in p:

            explanation = (
                "Calculating received spend by supplier."
            )

            sql = """
            SELECT
                s.SUPPLIER_NAME,
                s.SUPPLIER_CODE,
                SUM(f.RECEIVED_AMT) AS RECEIVED_AMOUNT
            FROM SUPPLY_CHAIN_DW.GOLD.FACT_PURCHASE_ORDER_LINE f
            JOIN SUPPLY_CHAIN_DW.GOLD.DIM_SUPPLIER s
                ON f.SUPPLIER_KEY = s.SUPPLIER_KEY
            GROUP BY
                s.SUPPLIER_NAME,
                s.SUPPLIER_CODE
            ORDER BY RECEIVED_AMOUNT DESC
            """

        else:

            explanation = (
                "Calculating the total value of goods "
                "received from suppliers."
            )

            sql = """
            SELECT
                SUM(RECEIVED_AMT) AS TOTAL_RECEIVED_AMOUNT
            FROM SUPPLY_CHAIN_DW.GOLD.FACT_PURCHASE_ORDER_LINE
            """

        return explanation, sql.strip()


    # ---------------------------------------------------------------
    # OTIF
    # ---------------------------------------------------------------

    if (
        "otif" in p
        or "on time in full" in p
    ):

        explanation = (
            "Calculating the percentage of purchase order lines "
            "that were delivered both on time and in full."
        )

        sql = """
        SELECT
            ROUND(
                100.0 * COUNT_IF(IS_OTIF_FLAG = TRUE)
                /
                NULLIF(
                    COUNT_IF(IS_OTIF_FLAG IS NOT NULL),
                    0
                ),
                2
            ) AS OTIF_PERCENTAGE
        FROM SUPPLY_CHAIN_DW.GOLD.FACT_PURCHASE_ORDER_LINE
        """

        return explanation, sql.strip()


    # ---------------------------------------------------------------
    # Quality Issues
    # ---------------------------------------------------------------

    if (
        "quality issue" in p
        or "quality issues" in p
        or "rejected quantity" in p
        or "rejection rate" in p
    ):

        explanation = (
            "Analyzing supplier delivery quality and rejected quantities."
        )

        sql = """
        SELECT
            s.SUPPLIER_NAME,
            s.SUPPLIER_CODE,
            SUM(f.REJECTED_QUANTITY) AS REJECTED_QUANTITY,
            ROUND(
                AVG(f.REJECT_RATE_PCT),
                2
            ) AS AVG_REJECT_RATE_PCT
        FROM SUPPLY_CHAIN_DW.GOLD.FACT_PURCHASE_ORDER_LINE f
        JOIN SUPPLY_CHAIN_DW.GOLD.DIM_SUPPLIER s
            ON f.SUPPLIER_KEY = s.SUPPLIER_KEY
        GROUP BY
            s.SUPPLIER_NAME,
            s.SUPPLIER_CODE
        ORDER BY REJECTED_QUANTITY DESC
        """

        return explanation, sql.strip()


    # ---------------------------------------------------------------
    # Supplier Risk
    # ---------------------------------------------------------------

    if (
        "supplier risk" in p
        or "risky supplier" in p
        or "high risk supplier" in p
        or "critical supplier" in p
    ):

        explanation = (
            "Showing suppliers grouped by their supply chain risk rating."
        )

        sql = """
        SELECT
            RISK_RATING,
            COUNT(DISTINCT SUPPLIER_KEY) AS SUPPLIER_COUNT
        FROM SUPPLY_CHAIN_DW.GOLD.DIM_SUPPLIER
        GROUP BY RISK_RATING
        ORDER BY
            CASE RISK_RATING
                WHEN 'Critical' THEN 1
                WHEN 'High' THEN 2
                WHEN 'Medium' THEN 3
                WHEN 'Low' THEN 4
                ELSE 5
            END
        """

        return explanation, sql.strip()


    # ---------------------------------------------------------------
    # Supplier Quality
    # ---------------------------------------------------------------

    if (
        "supplier quality" in p
        or "quality by supplier" in p
        or "supplier quality rating" in p
    ):

        explanation = (
            "Comparing supplier quality ratings."
        )

        sql = """
        SELECT
            SUPPLIER_NAME,
            SUPPLIER_CODE,
            QUALITY_RATING,
            QUALITY_BAND
        FROM SUPPLY_CHAIN_DW.GOLD.DIM_SUPPLIER
        ORDER BY QUALITY_RATING DESC
        """

        return explanation, sql.strip()


    # ---------------------------------------------------------------
    # Supplier Lead Time
    # ---------------------------------------------------------------

    if (
        "supplier lead time" in p
        or "lead time by supplier" in p
        or "supplier delivery time" in p
    ):

        explanation = (
            "Comparing supplier standard lead times."
        )

        sql = """
        SELECT
            SUPPLIER_NAME,
            SUPPLIER_CODE,
            STANDARD_LEAD_TIME_DAYS,
            LEAD_TIME_BAND
        FROM SUPPLY_CHAIN_DW.GOLD.DIM_SUPPLIER
        ORDER BY STANDARD_LEAD_TIME_DAYS DESC
        """

        return explanation, sql.strip()


    # ---------------------------------------------------------------
    # Shipments by Carrier
    # ---------------------------------------------------------------

    if (
        "shipment by carrier" in p
        or "shipments by carrier" in p
        or "carrier shipments" in p
    ):

        explanation = (
            "Counting shipments handled by each carrier."
        )

        sql = """
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
        """

        return explanation, sql.strip()


    # ---------------------------------------------------------------
    # Carrier On-Time Performance
    # ---------------------------------------------------------------

    if (
        "carrier on time" in p
        or "carrier performance" in p
        or "carrier on-time" in p
    ):

        explanation = (
            "Calculating shipment on-time delivery performance by carrier."
        )

        sql = """
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
        """

        return explanation, sql.strip()


    # ---------------------------------------------------------------
    # Shipments by Mode
    # ---------------------------------------------------------------

    if (
        "shipment by mode" in p
        or "shipments by mode" in p
        or "shipping mode" in p
    ):

        explanation = (
            "Analyzing shipment volume by transportation mode."
        )

        sql = """
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
        """

        return explanation, sql.strip()


    # ---------------------------------------------------------------
    # Shipment Delay Reasons
    # ---------------------------------------------------------------

    if (
        "delay reason" in p
        or "delays by reason" in p
        or "shipment delay reasons" in p
    ):

        explanation = (
            "Analyzing shipment delays by their recorded delay reason."
        )

        sql = """
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
        """

        return explanation, sql.strip()


    # ---------------------------------------------------------------
    # Shipment Stage
    # ---------------------------------------------------------------

    if (
        "shipment stage" in p
        or "shipment status" in p
        or "shipments in transit" in p
        or "in transit shipments" in p
    ):

        explanation = (
            "Showing the current shipment distribution by lifecycle stage."
        )

        sql = """
        SELECT
            SHIPMENT_STAGE,
            COUNT(SHIPMENT_KEY) AS SHIPMENT_COUNT
        FROM SUPPLY_CHAIN_DW.GOLD.FACT_SHIPMENT_DELIVERY
        GROUP BY SHIPMENT_STAGE
        ORDER BY SHIPMENT_COUNT DESC
        """

        return explanation, sql.strip()


    # ---------------------------------------------------------------
    # Freight Cost by Carrier
    # ---------------------------------------------------------------

    if (
        "freight cost by carrier" in p
        or "carrier freight cost" in p
        or "freight cost carrier" in p
    ):

        explanation = (
            "Calculating total freight cost by carrier."
        )

        sql = """
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
        """

        return explanation, sql.strip()


    # ---------------------------------------------------------------
    # Landed Cost by Supplier
    # ---------------------------------------------------------------

    if (
        "landed cost by supplier" in p
        or "supplier landed cost" in p
        or "landed cost supplier" in p
    ):

        explanation = (
            "Calculating total landed cost by supplier."
        )

        sql = """
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
        """

        return explanation, sql.strip()


    # ---------------------------------------------------------------
    # International Shipments
    # ---------------------------------------------------------------

    if (
        "international shipment" in p
        or "international shipments" in p
        or "international" in p and "shipment" in p
    ):

        explanation = (
            "Analyzing shipments that require international customs processing."
        )

        sql = """
        SELECT
            COUNT(SHIPMENT_KEY) AS INTERNATIONAL_SHIPMENTS
        FROM SUPPLY_CHAIN_DW.GOLD.FACT_SHIPMENT_DELIVERY
        WHERE IS_INTERNATIONAL_FLAG = TRUE
        """

        return explanation, sql.strip()


    # ---------------------------------------------------------------
    # Damaged Shipments
    # ---------------------------------------------------------------

    if (
        "damaged shipment" in p
        or "damaged shipments" in p
        or "damage" in p
    ):

        explanation = (
            "Analyzing shipments containing damaged goods."
        )

        sql = """
        SELECT
            COUNT(SHIPMENT_KEY) AS DAMAGED_SHIPMENTS,
            SUM(DAMAGED_QUANTITY) AS DAMAGED_QUANTITY
        FROM SUPPLY_CHAIN_DW.GOLD.FACT_SHIPMENT_DELIVERY
        WHERE IS_DAMAGED_FLAG = TRUE
        """

        return explanation, sql.strip()


    # ---------------------------------------------------------------
    # Products by Category
    # ---------------------------------------------------------------

    if (
        "product category" in p
        or "products by category" in p
        or "products in each category" in p
    ):

        explanation = (
            "Counting products within each product category."
        )

        sql = """
        SELECT
            CATEGORY_NAME,
            COUNT(PRODUCT_KEY) AS PRODUCT_COUNT
        FROM SUPPLY_CHAIN_DW.GOLD.DIM_PRODUCT
        GROUP BY CATEGORY_NAME
        ORDER BY PRODUCT_COUNT DESC
        """

        return explanation, sql.strip()


    # ---------------------------------------------------------------
    # Products by Subcategory
    # ---------------------------------------------------------------

    if (
        "product subcategory" in p
        or "products by subcategory" in p
        or "subcategory" in p
    ):

        explanation = (
            "Counting products within each product subcategory."
        )

        sql = """
        SELECT
            SUBCATEGORY_NAME,
            COUNT(PRODUCT_KEY) AS PRODUCT_COUNT
        FROM SUPPLY_CHAIN_DW.GOLD.DIM_PRODUCT
        GROUP BY SUBCATEGORY_NAME
        ORDER BY PRODUCT_COUNT DESC
        """

        return explanation, sql.strip()


    # ---------------------------------------------------------------
    # Products by Brand
    # ---------------------------------------------------------------

    if (
        "products by brand" in p
        or "product brand" in p
        or "brand count" in p
    ):

        explanation = (
            "Counting products by brand."
        )

        sql = """
        SELECT
            BRAND_NAME,
            COUNT(PRODUCT_KEY) AS PRODUCT_COUNT
        FROM SUPPLY_CHAIN_DW.GOLD.DIM_PRODUCT
        GROUP BY BRAND_NAME
        ORDER BY PRODUCT_COUNT DESC
        """

        return explanation, sql.strip()


    # ---------------------------------------------------------------
    # Top Products by Weight
    # ---------------------------------------------------------------

    if (
        "top 10 products by weight" in p
        or "heaviest products" in p
        or "top products by weight" in p
    ):

        explanation = (
            "Showing the 10 products with the highest unit weight."
        )

        sql = """
        SELECT
            PRODUCT_KEY,
            PRODUCT_NAME,
            PRODUCT_SKU,
            CATEGORY_NAME,
            SUBCATEGORY_NAME,
            WEIGHT_KG
        FROM SUPPLY_CHAIN_DW.GOLD.DIM_PRODUCT
        ORDER BY WEIGHT_KG DESC NULLS LAST
        LIMIT 10
        """

        return explanation, sql.strip()


    # ---------------------------------------------------------------
    # Preferred Suppliers
    # ---------------------------------------------------------------

    if (
        "approved supplier" in p
        or "approved suppliers" in p
        or "preferred supplier" in p
        or "preferred suppliers" in p
    ):

        explanation = (
            "Showing approved and preferred supplier information."
        )

        sql = """
        SELECT
            SUPPLIER_NAME,
            SUPPLIER_CODE,
            SUPPLIER_TIER,
            SUPPLIER_TYPE,
            COUNTRY_CODE,
            CITY_NAME,
            IS_APPROVED_FLAG,
            IS_CONTRACT_ACTIVE_FLAG
        FROM SUPPLY_CHAIN_DW.GOLD.DIM_SUPPLIER
        WHERE IS_APPROVED_FLAG = TRUE
        ORDER BY SUPPLIER_NAME
        """

        return explanation, sql.strip()


    # ---------------------------------------------------------------
    # Warehouse by City
    # ---------------------------------------------------------------

    if (
        "warehouse by city" in p
        or "warehouses by city" in p
        or "warehouse count by city" in p
    ):

        explanation = (
            "Counting warehouses by city."
        )

        sql = """
        SELECT
            CITY_NAME,
            COUNT(WAREHOUSE_KEY) AS WAREHOUSE_COUNT
        FROM SUPPLY_CHAIN_DW.GOLD.DIM_WAREHOUSE
        GROUP BY CITY_NAME
        ORDER BY WAREHOUSE_COUNT DESC
        """

        return explanation, sql.strip()


    # =================================================================
    # DOMAIN GUARDRAIL
    # =================================================================

    domain_keywords = [

        "supply",
        "supply chain",
        "purchase",
        "purchase order",
        "po",
        "supplier",
        "vendor",
        "shipment",
        "shipping",
        "delivery",
        "carrier",
        "freight",
        "logistics",
        "warehouse",
        "product",
        "category",
        "subcategory",
        "brand",
        "quantity",
        "ordered",
        "received",
        "rejected",
        "delay",
        "late",
        "on time",
        "otif",
        "lead time",
        "risk",
        "quality",
        "customs",
        "transit",
        "landed cost",
        "transport",
        "ship mode"
    ]


    if not any(
        word in p
        for word in domain_keywords
    ):

        explanation = (
            "I am specialized strictly as a "
            "**Supply Chain Domain Intelligence Assistant**.\n\n"

            "I can answer questions about purchase orders, "
            "suppliers, shipments, delivery performance, "
            "carriers, logistics, products, warehouses, "
            "shipping modes, delays, quality, and supply chain costs."
        )

        return explanation, None


    # =================================================================
    # FALLBACK OVERVIEW
    # =================================================================

    explanation = (
        "Here is a recent Supply Chain overview showing "
        "purchase order and shipment activity."
    )

    sql = """
    SELECT
        'PURCHASE_ORDERS' AS METRIC,
        COUNT(DISTINCT PURCHASE_ORDER_NUMBER) AS VALUE
    FROM SUPPLY_CHAIN_DW.GOLD.FACT_PURCHASE_ORDER_LINE

    UNION ALL

    SELECT
        'SHIPMENTS' AS METRIC,
        COUNT(SHIPMENT_KEY) AS VALUE
    FROM SUPPLY_CHAIN_DW.GOLD.FACT_SHIPMENT_DELIVERY

    UNION ALL

    SELECT
        'ORDERED_QUANTITY' AS METRIC,
        SUM(ORDERED_QUANTITY) AS VALUE
    FROM SUPPLY_CHAIN_DW.GOLD.FACT_PURCHASE_ORDER_LINE

    UNION ALL

    SELECT
        'RECEIVED_QUANTITY' AS METRIC,
        SUM(RECEIVED_QUANTITY) AS VALUE
    FROM SUPPLY_CHAIN_DW.GOLD.FACT_PURCHASE_ORDER_LINE
    """

    return explanation, sql.strip()


# ===================================================================
# 13. SIDEBAR
# ===================================================================

with st.sidebar:

    st.markdown("### ⚡ Dilytics AI")

    st.markdown(
        '<span class="status-pill">● Supply Chain Semantic Mart Live</span>',
        unsafe_allow_html=True
    )

    st.write("")


    # New Chat

    if st.button(
        "➕ New Chat",
        use_container_width=True,
        type="primary"
    ):

        new_id = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        st.session_state.current_session_id = new_id

        st.session_state.chat_sessions[new_id] = {
            "title": f"Chat {len(st.session_state.chat_sessions) + 1}",
            "messages": []
        }

        st.rerun()


    st.markdown("---")


    # Recent conversations

    st.markdown("##### 🕒 Recent Conversations")


    for s_id, s_data in reversed(
        list(
            st.session_state.chat_sessions.items()
        )
    ):

        is_active = (
            s_id ==
            st.session_state.current_session_id
        )

        session_label = s_data["title"]

        if len(session_label) > 20:

            session_label = (
                session_label[:18] +
                "..."
            )


        if st.button(
            f"{'👉 ' if is_active else '🗨️ '}{session_label}",
            key=f"sess_{s_id}",
            use_container_width=True
        ):

            st.session_state.current_session_id = s_id

            st.rerun()


    st.markdown("---")


    # Clear all sessions

    if st.button(
        "🗑️ Clear All Sessions",
        use_container_width=True
    ):

        st.session_state.chat_sessions = {}

        init_id = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        st.session_state.current_session_id = init_id

        st.session_state.chat_sessions[init_id] = {
            "title": "New Conversation",
            "messages": []
        }

        st.rerun()


# ===================================================================
# 14. MAIN HEADER
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
        "performance, logistics, products, and warehouses."
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
# 15. WHAT CAN I ASK?
# ===================================================================

with st.expander(
    "💡 What exact questions can I ask this assistant?",
    expanded=False
):

    st.markdown(
        "This assistant is connected to the Supply Chain semantic model "
        "and is programmed to answer the following questions."
    )


    col_a, col_b = st.columns(2)


    with col_a:

        st.markdown(
            """
            **📋 Purchase Orders**

            * "How many purchase orders do we have?"
            * "What is the total ordered quantity?"
            * "What is the total received quantity?"
            * "How many purchase orders are open?"
            * "What is the total order value?"
            * "What is the total rejected value?"
            * "What is the open quantity?"

            **🏭 Suppliers**

            * "What is the supplier on-time delivery percentage?"
            * "What is the average delivery delay by supplier?"
            * "How many suppliers are there by city?"
            * "What are the high risk suppliers?"
            * "What is the supplier quality?"
            * "What is the supplier lead time?"
            * "Show approved suppliers."
            """
        )


    with col_b:

        st.markdown(
            """
            **🚚 Shipments & Logistics**

            * "How many shipments do we have?"
            * "What is the shipment stage distribution?"
            * "What are the shipment delays by reason?"
            * "What is carrier performance?"
            * "What are shipments by carrier?"
            * "What are shipments by shipping mode?"
            * "What is the freight cost by carrier?"
            * "What is the landed cost by supplier?"
            * "How many international shipments are there?"
            * "How many damaged shipments are there?"

            **📦 Products & Warehouses**

            * "How many products are there in each category?"
            * "How many products are there by subcategory?"
            * "What are the top 10 products by weight?"
            * "How many warehouses are there by city?"
            """
        )


    st.info(
        "💡 Pro-Tip: You can copy and paste any of these "
        "questions directly into the chat bar."
    )


# ===================================================================
# 16. VERIFIED ONBOARDING QUESTIONS
# ===================================================================

st.markdown(
    "##### 💡 Verified Onboarding Questions:"
)


q_col1, q_col2, q_col3, q_col4, q_col5 = st.columns(5)


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
# 17. DISPLAY CHAT HISTORY
# ===================================================================

for idx, msg in enumerate(messages):

    with st.chat_message(msg["role"]):

        st.markdown(
            msg["content"]
        )


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


        if (
            "data" in msg
            and msg["data"] is not None
        ):

            tab_data, tab_chart = st.tabs(
                [
                    "Data 📄",
                    "Chart 📈"
                ]
            )


            with tab_data:

                st.dataframe(
                    msg["data"],
                    use_container_width=True
                )


            with tab_chart:

                display_chart_tab(
                    msg["data"],
                    key_prefix=f"hist_{current_id}_{idx}"
                )


# ===================================================================
# 18. USER INPUT
# ===================================================================

user_prompt = (
    st.chat_input(
        "Ask a question about purchase orders, suppliers, shipments, carriers, logistics, or products..."
    )
    or quick_prompt
)


# ===================================================================
# 19. PROCESS USER QUESTION
# ===================================================================

if user_prompt:

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
    # User message
    # ---------------------------------------------------------------

    messages.append(
        {
            "role": "user",
            "content": user_prompt
        }
    )


    with st.chat_message("user"):

        st.markdown(
            user_prompt
        )


    # ---------------------------------------------------------------
    # Assistant
    # ---------------------------------------------------------------

    with st.chat_message("assistant"):

        explanation, sql_query = (
            generate_sql_from_prompt(
                user_prompt
            )
        )


        st.markdown(
            explanation
        )


        df = None


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


                if df is not None and not df.empty:

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
                            key_prefix=f"live_{current_id}"
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
        # Save assistant message
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
