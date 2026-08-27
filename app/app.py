import streamlit as st
import pandas as pd
from datetime import datetime
import snowflake.connector
from snowflake.snowpark import Session


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Dilytics Supply Chain AI",
    page_icon="📦",
    layout="wide"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* --------------------------------------------------------
       GLOBAL PAGE
       -------------------------------------------------------- */
    html, body, [data-testid="stAppViewContainer"] {
        background: #f4f8ff;
    }

    section[data-testid="stMain"] {
        background: #f4f8ff;
    }

    section[data-testid="stMain"] .block-container {
        max-width: none !important;
        padding-top: 92px !important;
        padding-left: 0 !important;
        padding-right: 0 !important;
        padding-bottom: 110px !important;
    }

    /* --------------------------------------------------------
       FIXED MAIN HEADER
       -------------------------------------------------------- */
    .dilytics-topbar {
        position: fixed;
        top: 0;
        left: 21rem;
        right: 0;
        height: 84px;
        z-index: 999999;
        background: #0759d9;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 0 28px;
        box-sizing: border-box;
        box-shadow: 0 1px 0 rgba(0,0,0,0.04);
    }

    .dilytics-topbar-title {
        position: absolute;
        left: 50%;
        top: 50%;
        transform: translate(-50%, -50%);
        color: white;
        font-size: 30px;
        line-height: 1;
        font-weight: 700;
        letter-spacing: -0.5px;
        margin: 0;
        white-space: nowrap;
    }

    .dilytics-topbar-right {
        position: absolute;
        right: 28px;
        top: 50%;
        transform: translateY(-50%);
        display: flex;
        align-items: center;
        gap: 25px;
        color: white;
        font-size: 24px;
    }

    .topbar-bell {
        font-size: 25px;
    }

    .topbar-help {
        font-size: 22px;
        font-weight: 500;
    }

    .topbar-user {
        font-size: 22px;
    }

    /* --------------------------------------------------------
       SIDEBAR
       -------------------------------------------------------- */
    section[data-testid="stSidebar"] {
        width: 21rem !important;
        min-width: 21rem !important;
        background: #ffffff;
        border-right: 1px solid #dbe4f0;
    }

    section[data-testid="stSidebar"] > div {
        padding-top: 0 !important;
    }

    .sidebar-logo {
        width: 100%;
        height: 84px;
        display: flex;
        align-items: center;
        box-sizing: border-box;
        padding: 0 28px;
        background: #ffffff;
    }

    .sidebar-logo-box {
        width: 170px;
        height: 60px;
        background: #ed0909;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 25px;
        font-weight: 800;
        letter-spacing: 0.4px;
    }

    .sidebar-content {
        padding: 22px 20px 30px 20px;
    }

    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 7px;
        background-color: #ecfdf5;
        color: #087a59;
        border: 1px solid #a7f3d0;
        border-radius: 22px;
        padding: 8px 14px;
        font-size: 0.80rem;
        font-weight: 650;
    }

    .status-dot {
        font-size: 12px;
    }

    /* Sidebar separators */
    section[data-testid="stSidebar"] hr {
        margin: 24px 0 !important;
        border-color: #dce4ee !important;
    }

    /* Sidebar buttons */
    section[data-testid="stSidebar"] div[data-testid="stButton"] > button {
        min-height: 48px;
        border-radius: 8px;
        border: 1px solid #d4deeb;
        background: #ffffff;
        color: #0b315f;
        font-weight: 550;
        font-size: 15px;
    }

    section[data-testid="stSidebar"] div[data-testid="stButton"] > button:hover {
        border-color: #0b5ed7;
        color: #0b5ed7;
    }

    /* --------------------------------------------------------
       HERO
       -------------------------------------------------------- */
    .hero-panel {
        width: 100%;
        min-height: 350px;
        box-sizing: border-box;
        background: linear-gradient(180deg, #edf5ff 0%, #e8f1ff 100%);
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        padding-top: 34px;
        padding-bottom: 28px;
    }

    .bot-circle {
        width: 76px;
        height: 76px;
        border-radius: 50%;
        background: #ffffff;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 29px;
        margin-bottom: 20px;
        box-shadow: 0 8px 25px rgba(40, 83, 135, 0.10);
    }

    .hero-title {
        margin: 0;
        color: #062c63;
        font-size: 42px;
        line-height: 1.15;
        font-weight: 750;
        letter-spacing: -0.8px;
    }

    .hero-line {
        width: 82px;
        height: 4px;
        background: #0b5ed7;
        margin: 18px 0 18px 0;
    }

    .hero-subtitle {
        color: #153e70;
        font-size: 17px;
        line-height: 1.5;
        margin: 0;
    }

    /* --------------------------------------------------------
       MODULE CARDS
       -------------------------------------------------------- */
    .module-section {
        background: #f4f8ff;
        padding: 18px 18px 22px 18px;
        box-sizing: border-box;
    }

    .module-card-title {
        text-align: center;
        color: #062c63;
        font-weight: 700;
        font-size: 16px;
        line-height: 1.25;
    }

    .module-icon {
        font-size: 39px;
        line-height: 1;
        margin-bottom: 10px;
    }

    div[data-testid="stHorizontalBlock"] .module-button-wrap {
        width: 100%;
    }

    /* Module Streamlit buttons are the visible cards */
    .module-row div[data-testid="stButton"] > button {
        height: 126px !important;
        min-height: 126px !important;
        border-radius: 16px !important;
        border: 1px solid #d5e2f3 !important;
        background: #ffffff !important;
        color: #062c63 !important;
        box-shadow: 0 7px 18px rgba(45, 84, 130, 0.06) !important;
        font-size: 16px !important;
        font-weight: 700 !important;
        white-space: pre-line !important;
        line-height: 1.3 !important;
        padding: 12px 8px !important;
    }

    .module-row div[data-testid="stButton"] > button:hover {
        border-color: #0b5ed7 !important;
        color: #0b5ed7 !important;
        transform: translateY(-1px);
    }

    /* --------------------------------------------------------
       CHAT INPUT
       -------------------------------------------------------- */
    div[data-testid="stChatInput"] {
        background: transparent !important;
    }

    div[data-testid="stChatInput"] > div {
        border-radius: 18px !important;
        border: 1px solid #cddbeb !important;
        background: #ffffff !important;
        box-shadow: 0 6px 20px rgba(39, 75, 117, 0.08) !important;
    }

    /* --------------------------------------------------------
       RESPONSIVE
       -------------------------------------------------------- */
    @media (max-width: 900px) {
        .dilytics-topbar {
            left: 0;
        }

        .dilytics-topbar-title {
            font-size: 22px;
        }

        .hero-title {
            font-size: 32px;
        }

        .module-row {
            gap: 8px;
        }
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SNOWFLAKE CONFIGURATION
# ============================================================

def get_snowflake_config():

    return {
        "account": st.secrets["snowflake"]["account"],
        "role": st.secrets["snowflake"]["role"],
        "warehouse": st.secrets["snowflake"]["warehouse"],
        "database": st.secrets["snowflake"]["database"],
        "schema": st.secrets["snowflake"]["schema"]
    }


# ============================================================
# SESSION STATE
# ============================================================

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "username" not in st.session_state:
    st.session_state.username = st.secrets["snowflake"].get(
        "user",
        ""
    )

if "password" not in st.session_state:
    st.session_state.password = ""

if "snowpark_session" not in st.session_state:
    st.session_state.snowpark_session = None


# ============================================================
# LOGIN
# ============================================================

if not st.session_state.authenticated:

    st.title("Welcome to Dilytics Supply Chain AI")

    st.markdown(
        "Please login to connect to your Snowflake Data Warehouse."
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

        if not st.session_state.username:

            st.error("Please enter your Snowflake username.")
            st.stop()

        if not st.session_state.password:

            st.error("Please enter your Snowflake password.")
            st.stop()

        try:

            with st.spinner("Connecting to Snowflake..."):

                config = get_snowflake_config()

                connection_parameters = {
                    "account": config["account"],
                    "user": st.session_state.username,
                    "password": st.session_state.password,
                    "role": config["role"],
                    "warehouse": config["warehouse"],
                    "database": config["database"],
                    "schema": config["schema"]
                }

                # Test connection
                conn = snowflake.connector.connect(
                    **connection_parameters
                )

                conn.close()

                # Create Snowpark session
                st.session_state.snowpark_session = (
                    Session.builder
                    .configs(connection_parameters)
                    .create()
                )

                st.session_state.authenticated = True

                st.rerun()

        except Exception as e:

            st.error(
                f"Authentication failed: {str(e)}"
            )

    st.stop()


# ============================================================
# SNOWPARK SESSION
# ============================================================

session = st.session_state.snowpark_session


# ============================================================
# CHAT SESSIONS
# ============================================================

if "chat_sessions" not in st.session_state:

    st.session_state.chat_sessions = {}


if "current_session_id" not in st.session_state:

    session_id = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    st.session_state.current_session_id = session_id

    st.session_state.chat_sessions[session_id] = {
        "title": "New Conversation",
        "messages": []
    }


current_id = st.session_state.current_session_id

messages = (
    st.session_state
    .chat_sessions[current_id]["messages"]
)

# Selected module is UI state only. It does not change any
# Snowflake logic or query-generation logic.
if "selected_module" not in st.session_state:
    st.session_state.selected_module = "Supply Chain"

# ============================================================
# CHART FUNCTION
# ============================================================

def display_chart_tab(
    df,
    key_prefix=""
):

    if df is None or df.empty:

        st.info(
            "No data available to create a chart."
        )

        return

    if len(df.columns) < 2:

        st.info(
            "At least two columns are required for a chart."
        )

        return

    columns = list(df.columns)

    col1, col2, col3 = st.columns(3)

    x_col = col1.selectbox(
        "Dimension",
        columns,
        key=f"{key_prefix}_x"
    )

    remaining = [
        c for c in columns
        if c != x_col
    ]

    y_col = col2.selectbox(
        "Metric",
        remaining,
        key=f"{key_prefix}_y"
    )

    chart_type = col3.selectbox(
        "Chart Type",
        [
            "Bar Chart",
            "Line Chart",
            "Area Chart",
            "Scatter Plot"
        ],
        key=f"{key_prefix}_type"
    )

    chart_df = df.copy()

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


# ============================================================
# SUPPLY CHAIN SQL GENERATOR
# ============================================================

def generate_sql_from_prompt(prompt):

    p = prompt.lower().strip()


    # ========================================================
    # GREETINGS
    # ========================================================

    if p in [
        "hi",
        "hello",
        "hey",
        "good morning",
        "good afternoon",
        "good evening"
    ]:

        return (
            "Hello! 👋 I am your Supply Chain Intelligence "
            "Assistant. You can ask me about purchase orders, "
            "suppliers, shipments, deliveries, carriers, "
            "shipping modes, warehouses, products, delays, "
            "and delivery performance.",
            None
        )


    # ========================================================
    # HELP
    # ========================================================

    if (
        "what can i ask" in p
        or "what questions" in p
        or "what can you do" in p
        or "examples" in p
        or p == "help"
    ):

        return (
            """
You can ask me questions about **Supply Chain data**.

### 📋 Purchase Orders

- What is the total purchase order count?
- What is the total ordered quantity?
- What is the total ordered value?
- What is the total open commitment?
- What is the total rejected value?
- What is the purchase order status breakdown?
- What is the purchase order value by supplier?
- What is the purchase order value by warehouse?
- What is the ordered quantity by product category?

### 🚚 Shipments & Deliveries

- What is the total number of shipments?
- How many shipments are currently in transit?
- How many shipments have been delivered?
- How many shipments are delayed?
- What is the average delivery delay?
- What is the average delivery delay by supplier?
- What are the top delay reasons?
- What is the shipment count by carrier?
- What is the shipment count by shipping mode?

### 🏭 Suppliers

- Which suppliers have the most purchase orders?
- What is the supplier on-time delivery percentage?
- Which suppliers have the highest delivery delays?
- Which suppliers have the highest rejected value?
- Which suppliers are high risk?
- Which suppliers have active contracts?
- Which suppliers are single source?

### 📦 Products

- What are the top products by ordered value?
- What is the ordered quantity by product category?
- What is the ordered value by product category?
- What is the ordered value by brand?

### 🚢 Logistics

- What is the total freight cost?
- What is the total landed cost?
- What is freight cost by carrier?
- What is freight cost by shipping mode?
- What is the average transit time by shipping mode?
""",
            None
        )


    # ========================================================
    # VERIFIED QUERY 1
    # TOTAL PURCHASE ORDERS
    # ========================================================

    if (
        "total purchase order" in p
        or "total purchase orders" in p
        or "purchase order count" in p
    ):

        explanation = (
            "Calculating the total number of unique purchase orders."
        )

        sql = """
        SELECT
            COUNT(DISTINCT PURCHASE_ORDER_NUMBER)
                AS TOTAL_PURCHASE_ORDERS
        FROM SUPPLY_CHAIN_DW.GOLD.FACT_PURCHASE_ORDER_LINE
        """

        return explanation, sql.strip()


    # ========================================================
    # VERIFIED QUERY 2
    # TOTAL ORDERED QUANTITY
    # ========================================================

    if (
        "total ordered quantity" in p
        or "ordered quantity" in p
        and "by" not in p
    ):

        explanation = (
            "Calculating the total quantity ordered from suppliers."
        )

        sql = """
        SELECT
            SUM(ORDERED_QUANTITY)
                AS TOTAL_ORDERED_QUANTITY
        FROM SUPPLY_CHAIN_DW.GOLD.FACT_PURCHASE_ORDER_LINE
        """

        return explanation, sql.strip()


    # ========================================================
    # VERIFIED QUERY 3
    # SUPPLIER ON-TIME DELIVERY %
    # ========================================================

    if (
        "supplier on-time delivery" in p
        or "supplier on time delivery" in p
        or "on-time delivery %" in p
        or "on time delivery %" in p
    ):

        explanation = (
            "Calculating the overall supplier on-time delivery percentage."
        )

        sql = """
        SELECT
            ROUND(
                100.0 * COUNT_IF(IS_ON_TIME_FLAG = TRUE)
                /
                NULLIF(
                    COUNT_IF(IS_ON_TIME_FLAG IS NOT NULL),
                    0
                ),
                2
            ) AS SUPPLIER_ON_TIME_PCT
        FROM SUPPLY_CHAIN_DW.GOLD.FACT_PURCHASE_ORDER_LINE
        """

        return explanation, sql.strip()


    # ========================================================
    # VERIFIED QUERY 4
    # TOTAL REJECTED VALUE
    # ========================================================

    if (
        "total rejected value" in p
        or "rejected value" in p
    ):

        explanation = (
            "Calculating the total value of goods rejected during inspection."
        )

        sql = """
        SELECT
            SUM(REJECTED_AMT)
                AS TOTAL_REJECTED_VALUE
        FROM SUPPLY_CHAIN_DW.GOLD.FACT_PURCHASE_ORDER_LINE
        """

        return explanation, sql.strip()


    # ========================================================
    # VERIFIED QUERY 5
    # TOTAL SHIPMENTS
    # ========================================================

    if (
        "total shipments" in p
        or "shipment count" in p
        or "number of shipments" in p
    ):

        explanation = (
            "Calculating the total number of shipments."
        )

        sql = """
        SELECT
            COUNT(SHIPMENT_KEY)
                AS TOTAL_SHIPMENTS
        FROM SUPPLY_CHAIN_DW.GOLD.FACT_SHIPMENT_DELIVERY
        """

        return explanation, sql.strip()


    # ========================================================
    # OPEN PURCHASE ORDERS
    # ========================================================

    if (
        "open purchase order" in p
        or "open po" in p
        or "outstanding purchase order" in p
    ):

        explanation = (
            "Calculating purchase orders that are still outstanding."
        )

        sql = """
        SELECT
            COUNT(DISTINCT PURCHASE_ORDER_NUMBER)
                AS OPEN_PURCHASE_ORDERS
        FROM SUPPLY_CHAIN_DW.GOLD.FACT_PURCHASE_ORDER_LINE
        WHERE IS_OPEN_PO_FLAG = TRUE
        """

        return explanation, sql.strip()


    # ========================================================
    # OPEN COMMITMENT
    # ========================================================

    if (
        "open commitment" in p
        or "committed value" in p
        or "outstanding commitment" in p
    ):

        explanation = (
            "Calculating the value of goods ordered but not yet received."
        )

        sql = """
        SELECT
            SUM(OPEN_COMMITMENT_AMT)
                AS TOTAL_OPEN_COMMITMENT
        FROM SUPPLY_CHAIN_DW.GOLD.FACT_PURCHASE_ORDER_LINE
        """

        return explanation, sql.strip()


    # ========================================================
    # ORDERED VALUE
    # ========================================================

    if (
        "total ordered value" in p
        or "total order value" in p
        or "ordered value" in p
    ):

        explanation = (
            "Calculating the total value of goods ordered."
        )

        sql = """
        SELECT
            SUM(ORDERED_AMT)
                AS TOTAL_ORDERED_VALUE
        FROM SUPPLY_CHAIN_DW.GOLD.FACT_PURCHASE_ORDER_LINE
        """

        return explanation, sql.strip()


    # ========================================================
    # RECEIVED VALUE / SPEND
    # ========================================================

    if (
        "received value" in p
        or "supplier spend" in p
        or "total spend" in p
    ):

        explanation = (
            "Calculating the value of goods actually received."
        )

        sql = """
        SELECT
            SUM(RECEIVED_AMT)
                AS TOTAL_RECEIVED_VALUE
        FROM SUPPLY_CHAIN_DW.GOLD.FACT_PURCHASE_ORDER_LINE
        """

        return explanation, sql.strip()


    # ========================================================
    # FREIGHT COST
    # ========================================================

    if (
        "total freight cost" in p
        or "freight cost" in p
        and "by" not in p
    ):

        explanation = (
            "Calculating the total freight cost across shipments."
        )

        sql = """
        SELECT
            SUM(FREIGHT_COST_AMT)
                AS TOTAL_FREIGHT_COST
        FROM SUPPLY_CHAIN_DW.GOLD.FACT_SHIPMENT_DELIVERY
        """

        return explanation, sql.strip()


    # ========================================================
    # LANDED COST
    # ========================================================

    if (
        "landed cost" in p
        and "by" not in p
    ):

        explanation = (
            "Calculating the total landed cost, including freight and customs duty."
        )

        sql = """
        SELECT
            SUM(TOTAL_LANDED_COST_AMT)
                AS TOTAL_LANDED_COST
        FROM SUPPLY_CHAIN_DW.GOLD.FACT_SHIPMENT_DELIVERY
        """

        return explanation, sql.strip()


    # ========================================================
    # IN TRANSIT
    # ========================================================

    if (
        "in transit" in p
        or "in-transit" in p
    ):

        explanation = (
            "Counting shipments that have left the supplier "
            "but have not yet arrived."
        )

        sql = """
        SELECT
            COUNT(SHIPMENT_KEY)
                AS IN_TRANSIT_SHIPMENTS
        FROM SUPPLY_CHAIN_DW.GOLD.FACT_SHIPMENT_DELIVERY
        WHERE IS_IN_TRANSIT_FLAG = TRUE
        """

        return explanation, sql.strip()


    # ========================================================
    # DELIVERED SHIPMENTS
    # ========================================================

    if (
        "delivered shipments" in p
        or "shipments delivered" in p
    ):

        explanation = (
            "Counting shipments that have successfully arrived."
        )

        sql = """
        SELECT
            COUNT(SHIPMENT_KEY)
                AS DELIVERED_SHIPMENTS
        FROM SUPPLY_CHAIN_DW.GOLD.FACT_SHIPMENT_DELIVERY
        WHERE IS_DELIVERED_FLAG = TRUE
        """

        return explanation, sql.strip()


    # ========================================================
    # DELAYED SHIPMENTS
    # ========================================================

    if (
        "delayed shipments" in p
        or "shipments delayed" in p
        or "how many shipments are delayed" in p
    ):

        explanation = (
            "Counting shipments that arrived late and have a recorded delay."
        )

        sql = """
        SELECT
            COUNT(SHIPMENT_KEY)
                AS DELAYED_SHIPMENTS
        FROM SUPPLY_CHAIN_DW.GOLD.FACT_SHIPMENT_DELIVERY
        WHERE IS_DELAYED_FLAG = TRUE
        """

        return explanation, sql.strip()


    # ========================================================
    # AVERAGE DELIVERY DELAY
    # ========================================================

    if (
        "average delivery delay" in p
        and "supplier" not in p
    ):

        explanation = (
            "Calculating the average number of days deliveries "
            "were late against the planned delivery date."
        )

        sql = """
        SELECT
            AVG(DELIVERY_DELAY_DAYS)
                AS AVG_DELIVERY_DELAY_DAYS
        FROM SUPPLY_CHAIN_DW.GOLD.FACT_SHIPMENT_DELIVERY
        WHERE IS_DELIVERED_FLAG = TRUE
          AND DELIVERY_DELAY_DAYS IS NOT NULL
        """

        return explanation, sql.strip()


    # ========================================================
    # VERIFIED: AVERAGE DELIVERY DELAY BY SUPPLIER
    # ========================================================

    if (
        "average delivery delay by supplier" in p
        or "delivery delay by supplier" in p
    ):

        explanation = (
            "Calculating average delivery delay for each supplier."
        )

        sql = """
        SELECT
            s.SUPPLIER_NAME,
            s.SUPPLIER_CODE,
            MIN(d.FULL_DATE) AS START_DATE,
            MAX(d.FULL_DATE) AS END_DATE,
            AVG(f.DELIVERY_DELAY_DAYS)
                AS AVG_DELIVERY_DELAY_DAYS
        FROM SUPPLY_CHAIN_DW.GOLD.FACT_SHIPMENT_DELIVERY f

        INNER JOIN SUPPLY_CHAIN_DW.GOLD.DIM_SUPPLIER s
            ON f.SUPPLIER_KEY = s.SUPPLIER_KEY

        INNER JOIN SUPPLY_CHAIN_DW.GOLD.DIM_DATE d
            ON f.ORDER_DATE_KEY = d.DATE_KEY

        WHERE f.IS_DELIVERED_FLAG = TRUE
          AND f.DELIVERY_DELAY_DAYS IS NOT NULL

        GROUP BY
            s.SUPPLIER_NAME,
            s.SUPPLIER_CODE

        ORDER BY
            AVG_DELIVERY_DELAY_DAYS DESC NULLS LAST
        """

        return explanation, sql.strip()


    # ========================================================
    # DELAY REASONS
    # ========================================================

    if (
        "delay reason" in p
        or "reasons for delay" in p
        or "why are shipments delayed" in p
    ):

        explanation = (
            "Analyzing shipment delays by their recorded reason."
        )

        sql = """
        SELECT
            r.DELAY_REASON_NAME,
            COUNT(f.SHIPMENT_KEY)
                AS DELAYED_SHIPMENT_COUNT
        FROM SUPPLY_CHAIN_DW.GOLD.FACT_SHIPMENT_DELIVERY f

        INNER JOIN SUPPLY_CHAIN_DW.GOLD.DIM_DELAY_REASON r
            ON f.DELAY_REASON_KEY = r.DELAY_REASON_KEY

        WHERE f.IS_DELAYED_FLAG = TRUE

        GROUP BY
            r.DELAY_REASON_NAME

        ORDER BY
            DELAYED_SHIPMENT_COUNT DESC
        """

        return explanation, sql.strip()


    # ========================================================
    # PURCHASE ORDER BY SUPPLIER
    # ========================================================

    if (
        "purchase order" in p
        and "supplier" in p
        and (
            "value" in p
            or "amount" in p
        )
    ):

        explanation = (
            "Calculating purchase order value by supplier."
        )

        sql = """
        SELECT
            s.SUPPLIER_NAME,
            s.SUPPLIER_CODE,
            SUM(f.ORDERED_AMT)
                AS ORDERED_VALUE
        FROM SUPPLY_CHAIN_DW.GOLD.FACT_PURCHASE_ORDER_LINE f

        INNER JOIN SUPPLY_CHAIN_DW.GOLD.DIM_SUPPLIER s
            ON f.SUPPLIER_KEY = s.SUPPLIER_KEY

        GROUP BY
            s.SUPPLIER_NAME,
            s.SUPPLIER_CODE

        ORDER BY
            ORDERED_VALUE DESC
        """

        return explanation, sql.strip()


    # ========================================================
    # PURCHASE ORDER BY WAREHOUSE
    # ========================================================

    if (
        "purchase order" in p
        and "warehouse" in p
        and (
            "value" in p
            or "amount" in p
        )
    ):

        explanation = (
            "Calculating purchase order value by destination warehouse."
        )

        sql = """
        SELECT
            w.WAREHOUSE_NAME,
            SUM(f.ORDERED_AMT)
                AS ORDERED_VALUE
        FROM SUPPLY_CHAIN_DW.GOLD.FACT_PURCHASE_ORDER_LINE f

        INNER JOIN SUPPLY_CHAIN_DW.GOLD.DIM_WAREHOUSE w
            ON f.WAREHOUSE_KEY = w.WAREHOUSE_KEY

        GROUP BY
            w.WAREHOUSE_NAME

        ORDER BY
            ORDERED_VALUE DESC
        """

        return explanation, sql.strip()


    # ========================================================
    # ORDER STATUS
    # ========================================================

    if (
        "purchase order status" in p
        or "po status" in p
        or "order status" in p
    ):

        explanation = (
            "Showing the purchase order count by status."
        )

        sql = """
        SELECT
            s.PO_STATUS_NAME,
            s.STATUS_CATEGORY,
            COUNT(DISTINCT f.PURCHASE_ORDER_NUMBER)
                AS PURCHASE_ORDER_COUNT
        FROM SUPPLY_CHAIN_DW.GOLD.FACT_PURCHASE_ORDER_LINE f

        INNER JOIN SUPPLY_CHAIN_DW.GOLD.DIM_PO_STATUS s
            ON f.PO_STATUS_KEY = s.PO_STATUS_KEY

        GROUP BY
            s.PO_STATUS_NAME,
            s.STATUS_CATEGORY

        ORDER BY
            PURCHASE_ORDER_COUNT DESC
        """

        return explanation, sql.strip()


    # ========================================================
    # SUPPLIER QUALITY
    # ========================================================

    if (
        "supplier quality" in p
        or "quality rating by supplier" in p
        or "supplier quality rating" in p
    ):

        explanation = (
            "Showing supplier quality ratings."
        )

        sql = """
        SELECT
            SUPPLIER_NAME,
            SUPPLIER_CODE,
            QUALITY_RATING,
            QUALITY_BAND
        FROM SUPPLY_CHAIN_DW.GOLD.DIM_SUPPLIER
        ORDER BY
            QUALITY_RATING DESC
        """

        return explanation, sql.strip()


    # ========================================================
    # SUPPLIER RISK
    # ========================================================

    if (
        "supplier risk" in p
        or "risky supplier" in p
        or "high risk supplier" in p
    ):

        explanation = (
            "Showing suppliers according to their risk rating."
        )

        sql = """
        SELECT
            SUPPLIER_NAME,
            SUPPLIER_CODE,
            RISK_RATING,
            SUPPLIER_TIER,
            COUNTRY_CODE,
            REGION_NAME
        FROM SUPPLY_CHAIN_DW.GOLD.DIM_SUPPLIER
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


    # ========================================================
    # SINGLE SOURCE SUPPLIERS
    # ========================================================

    if (
        "single source" in p
        or "single-source" in p
    ):

        explanation = (
            "Identifying suppliers that are the only approved source "
            "for what they provide."
        )

        sql = """
        SELECT
            SUPPLIER_NAME,
            SUPPLIER_CODE,
            SUPPLIER_TYPE,
            SUPPLIER_TIER,
            RISK_RATING
        FROM SUPPLY_CHAIN_DW.GOLD.DIM_SUPPLIER
        WHERE IS_SINGLE_SOURCE_FLAG = TRUE
        ORDER BY
            SUPPLIER_NAME
        """

        return explanation, sql.strip()


    # ========================================================
    # ACTIVE CONTRACTS
    # ========================================================

    if (
        "active contract" in p
        or "active supplier contract" in p
    ):

        explanation = (
            "Showing suppliers with active contracts."
        )

        sql = """
        SELECT
            SUPPLIER_NAME,
            SUPPLIER_CODE,
            CONTRACT_START_DATE,
            CONTRACT_END_DATE,
            SUPPLIER_TIER
        FROM SUPPLY_CHAIN_DW.GOLD.DIM_SUPPLIER
        WHERE IS_CONTRACT_ACTIVE_FLAG = TRUE
        ORDER BY
            CONTRACT_END_DATE
        """

        return explanation, sql.strip()


    # ========================================================
    # SHIPMENT BY CARRIER
    # ========================================================

    if (
        "shipment" in p
        and "carrier" in p
    ):

        explanation = (
            "Showing shipment volumes by freight carrier."
        )

        sql = """
        SELECT
            c.CARRIER_NAME,
            c.CARRIER_CODE,
            c.CARRIER_MODE,
            COUNT(f.SHIPMENT_KEY)
                AS SHIPMENT_COUNT
        FROM SUPPLY_CHAIN_DW.GOLD.FACT_SHIPMENT_DELIVERY f

        INNER JOIN SUPPLY_CHAIN_DW.GOLD.DIM_CARRIER c
            ON f.CARRIER_KEY = c.CARRIER_KEY

        GROUP BY
            c.CARRIER_NAME,
            c.CARRIER_CODE,
            c.CARRIER_MODE

        ORDER BY
            SHIPMENT_COUNT DESC
        """

        return explanation, sql.strip()


    # ========================================================
    # SHIPMENT BY SHIPPING MODE
    # ========================================================

    if (
        "shipping mode" in p
        or "ship mode" in p
        or "shipment by mode" in p
    ):

        explanation = (
            "Showing shipment volumes by shipping mode."
        )

        sql = """
        SELECT
            m.SHIP_MODE_NAME,
            m.TRANSPORT_MODE,
            m.SPEED_CATEGORY,
            COUNT(f.SHIPMENT_KEY)
                AS SHIPMENT_COUNT
        FROM SUPPLY_CHAIN_DW.GOLD.FACT_SHIPMENT_DELIVERY f

        INNER JOIN SUPPLY_CHAIN_DW.GOLD.DIM_SHIP_MODE m
            ON f.SHIP_MODE_KEY = m.SHIP_MODE_KEY

        GROUP BY
            m.SHIP_MODE_NAME,
            m.TRANSPORT_MODE,
            m.SPEED_CATEGORY

        ORDER BY
            SHIPMENT_COUNT DESC
        """

        return explanation, sql.strip()


    # ========================================================
    # FREIGHT BY CARRIER
    # ========================================================

    if (
        "freight" in p
        and "carrier" in p
    ):

        explanation = (
            "Calculating freight cost by carrier."
        )

        sql = """
        SELECT
            c.CARRIER_NAME,
            c.CARRIER_CODE,
            SUM(f.FREIGHT_COST_AMT)
                AS TOTAL_FREIGHT_COST
        FROM SUPPLY_CHAIN_DW.GOLD.FACT_SHIPMENT_DELIVERY f

        INNER JOIN SUPPLY_CHAIN_DW.GOLD.DIM_CARRIER c
            ON f.CARRIER_KEY = c.CARRIER_KEY

        GROUP BY
            c.CARRIER_NAME,
            c.CARRIER_CODE

        ORDER BY
            TOTAL_FREIGHT_COST DESC
        """

        return explanation, sql.strip()


    # ========================================================
    # TOP PRODUCTS BY ORDERED VALUE
    # ========================================================

    if (
        "top" in p
        and "product" in p
        and (
            "ordered value" in p
            or "order value" in p
        )
    ):

        explanation = (
            "Ranking products by total ordered value."
        )

        sql = """
        SELECT
            p.PRODUCT_SKU,
            p.PRODUCT_NAME,
            p.CATEGORY_NAME,
            p.SUBCATEGORY_NAME,
            SUM(f.ORDERED_AMT)
                AS ORDERED_VALUE
        FROM SUPPLY_CHAIN_DW.GOLD.FACT_PURCHASE_ORDER_LINE f

        INNER JOIN SUPPLY_CHAIN_DW.GOLD.DIM_PRODUCT p
            ON f.PRODUCT_KEY = p.PRODUCT_KEY

        GROUP BY
            p.PRODUCT_SKU,
            p.PRODUCT_NAME,
            p.CATEGORY_NAME,
            p.SUBCATEGORY_NAME

        ORDER BY
            ORDERED_VALUE DESC

        LIMIT 10
        """

        return explanation, sql.strip()


    # ========================================================
    # ORDERED VALUE BY CATEGORY
    # ========================================================

    if (
        "ordered value" in p
        and "category" in p
    ):

        explanation = (
            "Calculating ordered value by product category."
        )

        sql = """
        SELECT
            p.CATEGORY_NAME,
            SUM(f.ORDERED_AMT)
                AS ORDERED_VALUE
        FROM SUPPLY_CHAIN_DW.GOLD.FACT_PURCHASE_ORDER_LINE f

        INNER JOIN SUPPLY_CHAIN_DW.GOLD.DIM_PRODUCT p
            ON f.PRODUCT_KEY = p.PRODUCT_KEY

        GROUP BY
            p.CATEGORY_NAME

        ORDER BY
            ORDERED_VALUE DESC
        """

        return explanation, sql.strip()


    # ========================================================
    # ORDERED QUANTITY BY CATEGORY
    # ========================================================

    if (
        "ordered quantity" in p
        and "category" in p
    ):

        explanation = (
            "Calculating ordered quantity by product category."
        )

        sql = """
        SELECT
            p.CATEGORY_NAME,
            SUM(f.ORDERED_QUANTITY)
                AS ORDERED_QUANTITY
        FROM SUPPLY_CHAIN_DW.GOLD.FACT_PURCHASE_ORDER_LINE f

        INNER JOIN SUPPLY_CHAIN_DW.GOLD.DIM_PRODUCT p
            ON f.PRODUCT_KEY = p.PRODUCT_KEY

        GROUP BY
            p.CATEGORY_NAME

        ORDER BY
            ORDERED_QUANTITY DESC
        """

        return explanation, sql.strip()


    # ========================================================
    # ORDERED VALUE BY BRAND
    # ========================================================

    if (
        "ordered value" in p
        and "brand" in p
    ):

        explanation = (
            "Calculating ordered value by product brand."
        )

        sql = """
        SELECT
            p.BRAND_NAME,
            SUM(f.ORDERED_AMT)
                AS ORDERED_VALUE
        FROM SUPPLY_CHAIN_DW.GOLD.FACT_PURCHASE_ORDER_LINE f

        INNER JOIN SUPPLY_CHAIN_DW.GOLD.DIM_PRODUCT p
            ON f.PRODUCT_KEY = p.PRODUCT_KEY

        GROUP BY
            p.BRAND_NAME

        ORDER BY
            ORDERED_VALUE DESC
        """

        return explanation, sql.strip()


    # ========================================================
    # TOP SUPPLIERS BY ORDER VALUE
    # ========================================================

    if (
        "top" in p
        and "supplier" in p
    ):

        explanation = (
            "Ranking suppliers by total ordered value."
        )

        sql = """
        SELECT
            s.SUPPLIER_NAME,
            s.SUPPLIER_CODE,
            SUM(f.ORDERED_AMT)
                AS ORDERED_VALUE
        FROM SUPPLY_CHAIN_DW.GOLD.FACT_PURCHASE_ORDER_LINE f

        INNER JOIN SUPPLY_CHAIN_DW.GOLD.DIM_SUPPLIER s
            ON f.SUPPLIER_KEY = s.SUPPLIER_KEY

        GROUP BY
            s.SUPPLIER_NAME,
            s.SUPPLIER_CODE

        ORDER BY
            ORDERED_VALUE DESC

        LIMIT 10
        """

        return explanation, sql.strip()


    # ========================================================
    # DOMAIN GUARDRAIL
    # ========================================================

    supply_chain_keywords = [

        "supply chain",
        "purchase order",
        "purchase orders",
        "po",
        "supplier",
        "suppliers",
        "shipment",
        "shipments",
        "delivery",
        "deliveries",
        "carrier",
        "carriers",
        "warehouse",
        "warehouses",
        "product",
        "products",
        "material",
        "quantity",
        "ordered",
        "received",
        "rejected",
        "freight",
        "landed cost",
        "transit",
        "delay",
        "delayed",
        "shipping",
        "ship mode",
        "shipping mode",
        "customs",
        "contract",
        "risk",
        "quality"
    ]


    if not any(
        keyword in p
        for keyword in supply_chain_keywords
    ):

        return (
            """
I am specialized in **Supply Chain Intelligence**.

Please ask a question about:

- Purchase Orders
- Suppliers
- Shipments
- Deliveries
- Carriers
- Shipping Modes
- Warehouses
- Products
- Delivery Delays
- Freight
- Customs
- Supplier Performance
- Purchase Order Status
""",
            None
        )


    # ========================================================
    # GENERAL SUPPLY CHAIN FALLBACK
    # ========================================================

    explanation = (
        "Here is a recent Supply Chain overview showing "
        "purchase orders and shipment activity."
    )

    sql = """
    SELECT
        f.PURCHASE_ORDER_NUMBER,
        f.PO_LINE_NUMBER,
        p.PRODUCT_SKU,
        p.PRODUCT_NAME,
        s.SUPPLIER_NAME,
        w.WAREHOUSE_NAME,
        f.ORDERED_QUANTITY,
        f.ORDERED_AMT,
        f.RECEIVED_QUANTITY,
        f.RECEIVED_AMT,
        f.OPEN_QUANTITY,
        f.IS_OPEN_PO_FLAG
    FROM SUPPLY_CHAIN_DW.GOLD.FACT_PURCHASE_ORDER_LINE f

    LEFT JOIN SUPPLY_CHAIN_DW.GOLD.DIM_PRODUCT p
        ON f.PRODUCT_KEY = p.PRODUCT_KEY

    LEFT JOIN SUPPLY_CHAIN_DW.GOLD.DIM_SUPPLIER s
        ON f.SUPPLIER_KEY = s.SUPPLIER_KEY

    LEFT JOIN SUPPLY_CHAIN_DW.GOLD.DIM_WAREHOUSE w
        ON f.WAREHOUSE_KEY = w.WAREHOUSE_KEY

    ORDER BY
        f.ORDERED_AMT DESC

    LIMIT 20
    """

    return explanation, sql.strip()


# ============================================================
# FIXED HEADER + SIDEBAR
# ============================================================

# Main-page fixed blue header.
st.markdown(
    f"""
    <div class="dilytics-topbar">
        <div class="dilytics-topbar-title">{hero_title}</div>
        <div class="dilytics-topbar-right">
            <span class="topbar-bell">🔔</span>
            <span class="topbar-help">?</span>
            <span class="topbar-user">●</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# ------------------------------------------------------------
# SIDEBAR
# ------------------------------------------------------------

with st.sidebar:

    # DILYTICS logo stays at the very top of the sidebar.
    st.markdown(
        """
        <div class="sidebar-logo">
            <div class="sidebar-logo-box">DILYTICS</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)

    st.markdown(
        '<span class="status-pill"><span class="status-dot">●</span> Semantic Mart Live</span>',
        unsafe_allow_html=True
    )

    st.write("")

    # --------------------------------------------------------
    # NEW CHAT
    # --------------------------------------------------------

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
            "title": "New Conversation",
            "messages": []
        }

        st.rerun()

    st.markdown("---")

    st.markdown(
        "##### 🕒 Recent Conversations"
    )

    for s_id, s_data in reversed(
        list(
            st.session_state.chat_sessions.items()
        )
    ):

        is_active = (
            s_id ==
            st.session_state.current_session_id
        )

        label = s_data["title"]

        if len(label) > 20:
            label = label[:18] + "..."

        if st.button(
            f"{'👉 ' if is_active else '🗨️ '}{label}",
            key=f"sess_{s_id}",
            use_container_width=True
        ):

            st.session_state.current_session_id = s_id

            st.rerun()

    st.markdown("---")

    if st.button(
        "🗑️ Clear All Sessions",
        use_container_width=True
    ):

        st.session_state.chat_sessions = {}

        new_id = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        st.session_state.current_session_id = new_id

        st.session_state.chat_sessions[new_id] = {
            "title": "New Conversation",
            "messages": []
        }

        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


# ============================================================
# HERO
# ============================================================

# ============================================================
# CURRENT MODULE TITLE
# ============================================================

module_titles = {
    "Supply Chain": "Dilytics Supply Chain AI",
    "Purchase Orders": "Purchase Orders Chatbot",
    "Shipments & Deliveries": "Shipments & Deliveries Chatbot",
    "Inventory & Warehouses": "Inventory & Warehouses Chatbot",
    "Suppliers": "Suppliers Chatbot",
    "Products": "Products Chatbot",
    "Analytics & Reports": "Analytics & Reports Chatbot",
}

hero_title = module_titles.get(
    st.session_state.selected_module,
    "Dilytics Supply Chain AI"
)


# ============================================================
# MODULE CARDS
# ============================================================

st.markdown('<div class="module-section">', unsafe_allow_html=True)

st.markdown('<div class="module-row">', unsafe_allow_html=True)

m1, m2, m3, m4, m5, m6 = st.columns(
    [1, 1, 1, 1, 1, 1],
    gap="small"
)

with m1:
    if st.button(
        "📋\nPurchase\nOrders",
        key="module_purchase_orders",
        use_container_width=True
    ):
        st.session_state.selected_module = "Purchase Orders"
        st.rerun()

with m2:
    if st.button(
        "🚚\nShipments\n& Deliveries",
        key="module_shipments",
        use_container_width=True
    ):
        st.session_state.selected_module = "Shipments & Deliveries"
        st.rerun()

with m3:
    if st.button(
        "📊\nInventory\n& Warehouses",
        key="module_inventory",
        use_container_width=True
    ):
        st.session_state.selected_module = "Inventory & Warehouses"
        st.rerun()

with m4:
    if st.button(
        "👥\nSuppliers",
        key="module_suppliers",
        use_container_width=True
    ):
        st.session_state.selected_module = "Suppliers"
        st.rerun()

with m5:
    if st.button(
        "📦\nProducts",
        key="module_products",
        use_container_width=True
    ):
        st.session_state.selected_module = "Products"
        st.rerun()

with m6:
    if st.button(
        "📈\nAnalytics\n& Reports",
        key="module_analytics",
        use_container_width=True
    ):
        st.session_state.selected_module = "Analytics & Reports"
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)


# ============================================================
# SUGGESTED QUESTIONS
# ============================================================

with st.expander(
    "💡 What exact questions can I ask this assistant?",
    expanded=False
):

    st.markdown(
        "Here are some Supply Chain questions you can try:"
    )

    col1, col2 = st.columns(2)

    with col1:

        st.markdown(
            """
            ### 📋 Purchase Orders

            * "What is the total purchase order count?"

            * "What is the total ordered quantity?"

            * "What is the total ordered value?"

            * "What is the total open commitment?"

            * "What is the total rejected value?"

            * "What is the purchase order status breakdown?"

            * "What is the purchase order value by supplier?"

            * "What is the purchase order value by warehouse?"
            """
        )

    with col2:

        st.markdown(
            """
            ### 🚚 Shipments & Suppliers

            * "What is the total number of shipments?"

            * "How many shipments are currently in transit?"

            * "How many shipments are delayed?"

            * "What is the average delivery delay?"

            * "What is the average delivery delay by supplier?"

            * "What are the top delay reasons?"

            * "What is the supplier on-time delivery percentage?"

            * "Which suppliers are high risk?"
            """
        )

    st.markdown("---")

    st.markdown(
        """
        ### 🚢 Logistics & Products

        * "What is the total freight cost?"

        * "What is the total landed cost?"

        * "What is freight cost by carrier?"

        * "What is the shipment count by shipping mode?"

        * "What are the top products by ordered value?"

        * "What is the ordered value by product category?"

        * "What is the ordered quantity by product category?"

        * "What is the ordered value by brand?"
        """
    )


# ============================================================
# VERIFIED ONBOARDING QUESTIONS
# ============================================================

st.markdown(
    "##### 💡 Verified Onboarding Questions:"
)


q1, q2, q3, q4, q5 = st.columns(5)

quick_prompt = None


if q1.button(
    "📋 Total Purchase Orders",
    use_container_width=True
):

    quick_prompt = (
        "What is the total purchase order count?"
    )


if q2.button(
    "📦 Total Ordered Quantity",
    use_container_width=True
):

    quick_prompt = (
        "What is the total ordered quantity?"
    )


if q3.button(
    "⏱️ Supplier On-Time %",
    use_container_width=True
):

    quick_prompt = (
        "What is the supplier on-time delivery percentage?"
    )


if q4.button(
    "❌ Total Rejected Value",
    use_container_width=True
):

    quick_prompt = (
        "What is the total rejected value?"
    )


if q5.button(
    "🚚 Total Shipments",
    use_container_width=True
):

    quick_prompt = (
        "What is the total number of shipments?"
    )


# ============================================================
# DISPLAY CHAT HISTORY
# ============================================================

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
            and not msg["data"].empty
        ):

            tab1, tab2 = st.tabs(
                [
                    "Data 📄",
                    "Chart 📈"
                ]
            )


            with tab1:

                st.dataframe(
                    msg["data"],
                    use_container_width=True
                )


            with tab2:

                display_chart_tab(
                    msg["data"],
                    key_prefix=f"history_{current_id}_{idx}"
                )


# ============================================================
# CHAT INPUT
# ============================================================

user_prompt = (
    st.chat_input(
        "Ask about suppliers, purchase orders, "
        "shipments, deliveries, warehouses, "
        "carriers, or products..."
    )
    or quick_prompt
)


# ============================================================
# PROCESS QUESTION
# ============================================================

if user_prompt:

    # --------------------------------------------------------
    # CONVERSATION TITLE
    # --------------------------------------------------------

    if len(messages) == 0:

        st.session_state.chat_sessions[
            current_id
        ]["title"] = (
            user_prompt[:25]
            + (
                "..."
                if len(user_prompt) > 25
                else ""
            )
        )


    # --------------------------------------------------------
    # SAVE USER MESSAGE
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # GENERATE SQL
    # --------------------------------------------------------

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


        # ----------------------------------------------------
        # EXECUTE SQL
        # ----------------------------------------------------

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

                df = (
                    session
                    .sql(sql_query)
                    .to_pandas()
                )


                if df.empty:

                    st.info(
                        "The query executed successfully, "
                        "but no records were returned."
                    )

                else:

                    tab1, tab2 = st.tabs(
                        [
                            "Data 📄",
                            "Chart 📈"
                        ]
                    )


                    with tab1:

                        st.dataframe(
                            df,
                            use_container_width=True
                        )


                    with tab2:

                        display_chart_tab(
                            df,
                            key_prefix=f"live_{current_id}"
                        )


            except Exception as e:

                st.error(
                    f"SQL Execution Error: {str(e)}"
                )


    # --------------------------------------------------------
    # SAVE ASSISTANT MESSAGE
    # --------------------------------------------------------

    messages.append(
        {
            "role": "assistant",
            "content": explanation,
            "sql": sql_query,
            "data": df
        }
    )


    st.rerun()
