import streamlit as st
import pandas as pd
from datetime import datetime
import snowflake.connector
from snowflake.snowpark import Session


# ============================================================
# CONFIGURATION
# ============================================================

HOST = "XYUHKAV-XRB12650.snowflakecomputing.com"
ACCOUNT = "XYUHKAV-XRB12650"
DATABASE = "SUPPLY_CHAIN_DW"
SCHEMA = "GOLD"
WAREHOUSE = "COMPUTE_WH"


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Dilytics Supply Chain AI",
    page_icon="📦",
    layout="wide"
)


# ============================================================
# CUSTOM UI STYLING
# ============================================================

st.markdown(
    """
    <style>

    /* ========================================================
       SIDEBAR STATUS
       ======================================================== */

    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;

        background-color: #ecfdf5;
        color: #065f46;

        border: 1px solid #a7f3d0;
        border-radius: 20px;

        padding: 3px 10px;

        font-size: 0.75rem;
        font-weight: 600;
    }


    /* ========================================================
       BUTTONS
       ======================================================== */

    div[data-testid="stButton"] > button {
        border-radius: 8px;
        font-weight: 500;
    }


    /* ========================================================
       MAIN TITLE
       ======================================================== */

    .supply-chain-title {
        width: 100%;

        text-align: center;

        font-size: 42px;

        font-weight: 700;

        line-height: 1.2;

        color: #30313d;

        margin-top: 5px;

        margin-bottom: 35px;

        padding: 0;
    }


    /* ========================================================
       REMOVE EXTRA TOP SPACE
       ======================================================== */

    .block-container {
        padding-top: 2rem;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# 1. LOGIN SCREEN
# ============================================================

if "authenticated" not in st.session_state:

    st.session_state.authenticated = False

    st.session_state.username = "PBCS"

    st.session_state.password = ""

    st.session_state.snowpark_session = None


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

                    role="ACCOUNTADMIN",

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


# ============================================================
# 2. GET SNOWFLAKE SESSION
# ============================================================

session = (
    st.session_state.snowpark_session
)


# ============================================================
# 3. CHAT SESSION MANAGEMENT
# ============================================================

if "chat_sessions" not in st.session_state:

    st.session_state.chat_sessions = {}


if "current_session_id" not in st.session_state:

    init_id = datetime.now().strftime(
        "%Y%m%d_%H%M%S_%f"
    )

    st.session_state.current_session_id = init_id

    st.session_state.chat_sessions[init_id] = {

        "title": "New Conversation",

        "messages": []
    }


current_id = (
    st.session_state.current_session_id
)


messages = (
    st.session_state
    .chat_sessions[current_id]["messages"]
)


# ============================================================
# 4. CHART FUNCTION
# ============================================================

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


    all_cols = list(df.columns)


    col1, col2, col3 = st.columns(3)


    x_col = col1.selectbox(
        "Dimension (X-axis)",
        all_cols,
        index=0,
        key=f"{key_prefix}_x"
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


    if any(
        k in x_col.lower()
        for k in [
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
                and isinstance(
                    x,
                    (int, float)
                )
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


# ============================================================
# 5. QUESTION / SQL ENGINE
# ============================================================

def generate_sql_from_prompt(
    prompt: str
):

    p = prompt.lower().strip()


    # ========================================================
    # GREETINGS
    # ========================================================

    if any(
        greet in p
        for greet in [
            "how are you",
            "how's it going",
            "what's up",
            "whats up"
        ]
    ):

        explanation = (
            "I'm doing well, thank you! "
            "I am ready to help you analyze "
            "your supply chain data. "
            "What would you like to explore?"
        )

        return explanation, None


    elif p in [
        "hi",
        "hello",
        "hey",
        "good morning",
        "good evening"
    ]:

        explanation = (
            "Hello! 👋 I am your "
            "**Supply Chain Intelligence Assistant**. "
            "Ask me about purchase orders, suppliers, "
            "shipments, deliveries, warehouses, "
            "inventory, products, or logistics."
        )

        return explanation, None


    # ========================================================
    # HELP
    # ========================================================

    elif any(
        help_word in p
        for help_word in [
            "what can i ask",
            "what questions",
            "what can you do",
            "examples",
            "help"
        ]
    ):

        explanation = (
            """
You can ask me questions about your
**Supply Chain data**.

### 📋 Purchase Orders

- What is the total purchase order value?
- What is the purchase order value by supplier?
- What are the top 10 purchase orders by value?
- What is the order status by supplier?

### 🚚 Shipments & Deliveries

- How many deliveries are pending?
- Which shipments are delayed?
- What are the top 10 materials by purchase value?

### 🏭 Suppliers

- Which suppliers have the highest number of delayed orders?
- What is the supplier on-time delivery percentage?

### 📦 Inventory

- What is the total available inventory value?
- What is the total quantity of inventory currently on hand?
- What is the inventory value by warehouse?
- What is the inventory value by product category?
- What is the inventory value by brand?
- How many products are out of stock?
"""
        )

        return explanation, None


    # ========================================================
    # TOTAL AVAILABLE INVENTORY VALUE
    # ========================================================

    if (
        "total available inventory" in p
        or "total inventory value" in p
    ):

        explanation = (
            "Calculating total inventory value "
            "across all warehouses as of the "
            "latest snapshot."
        )


        sql = """

        SELECT
            SUM(INVENTORY_VALUE_AMT)
                AS TOTAL_INVENTORY_VALUE

        FROM INVENTORY_DW.GOLD.FACT_INVENTORY_DAILY_SNAPSHOT

        WHERE SNAPSHOT_DATE_KEY = (

            SELECT
                MAX(SNAPSHOT_DATE_KEY)

            FROM INVENTORY_DW.GOLD.FACT_INVENTORY_DAILY_SNAPSHOT

        )

        """


        return explanation, sql.strip()


    # ========================================================
    # TOTAL QUANTITY ON HAND
    # ========================================================

    elif (
        "quantity" in p
        and "on hand" in p
        and "product" not in p
    ):

        explanation = (
            "Calculating the total physical "
            "quantity of inventory currently on hand."
        )


        sql = """

        SELECT
            SUM(ON_HAND_QTY)
                AS TOTAL_ON_HAND_QTY

        FROM INVENTORY_DW.GOLD.FACT_INVENTORY_DAILY_SNAPSHOT

        WHERE SNAPSHOT_DATE_KEY = (

            SELECT
                MAX(SNAPSHOT_DATE_KEY)

            FROM INVENTORY_DW.GOLD.FACT_INVENTORY_DAILY_SNAPSHOT

        )

        """


        return explanation, sql.strip()


    # ========================================================
    # INVENTORY VALUE BY WAREHOUSE
    # ========================================================

    elif (
        "inventory value by warehouse"
        in p
    ):

        explanation = (
            "Aggregating total inventory value "
            "grouped by warehouse location."
        )


        sql = """

        SELECT

            w.WAREHOUSE_NAME,

            SUM(
                f.INVENTORY_VALUE_AMT
            ) AS INVENTORY_VALUE

        FROM INVENTORY_DW.GOLD.FACT_INVENTORY_DAILY_SNAPSHOT f

        JOIN INVENTORY_DW.GOLD.DIM_WAREHOUSE w

            ON f.WAREHOUSE_KEY =
               w.WAREHOUSE_KEY

        WHERE f.SNAPSHOT_DATE_KEY = (

            SELECT
                MAX(SNAPSHOT_DATE_KEY)

            FROM INVENTORY_DW.GOLD.FACT_INVENTORY_DAILY_SNAPSHOT

        )

        GROUP BY
            w.WAREHOUSE_NAME

        ORDER BY
            INVENTORY_VALUE DESC

        """


        return explanation, sql.strip()


    # ========================================================
    # INVENTORY VALUE BY PRODUCT CATEGORY
    # ========================================================

    elif (
        "inventory value by product category"
        in p
        or "by category" in p
    ):

        explanation = (
            "Aggregating inventory value "
            "by product category."
        )


        sql = """

        SELECT

            p.CATEGORY_NAME,

            SUM(
                f.INVENTORY_VALUE_AMT
            ) AS TOTAL_INVENTORY_VALUE

        FROM INVENTORY_DW.GOLD.FACT_INVENTORY_DAILY_SNAPSHOT f

        JOIN INVENTORY_DW.GOLD.DIM_PRODUCT p

            ON f.PRODUCT_KEY =
               p.PRODUCT_KEY

        WHERE f.SNAPSHOT_DATE_KEY = (

            SELECT
                MAX(SNAPSHOT_DATE_KEY)

            FROM INVENTORY_DW.GOLD.FACT_INVENTORY_DAILY_SNAPSHOT

        )

        GROUP BY
            p.CATEGORY_NAME

        ORDER BY
            TOTAL_INVENTORY_VALUE DESC

        """


        return explanation, sql.strip()


    # ========================================================
    # INVENTORY VALUE BY SUBCATEGORY
    # ========================================================

    elif "subcategory" in p:

        explanation = (
            "Aggregating inventory value "
            "by product subcategory."
        )


        sql = """

        SELECT

            p.SUBCATEGORY_NAME,

            SUM(
                f.INVENTORY_VALUE_AMT
            ) AS TOTAL_INVENTORY_VALUE

        FROM INVENTORY_DW.GOLD.FACT_INVENTORY_DAILY_SNAPSHOT f

        JOIN INVENTORY_DW.GOLD.DIM_PRODUCT p

            ON f.PRODUCT_KEY =
               p.PRODUCT_KEY

        WHERE f.SNAPSHOT_DATE_KEY = (

            SELECT
                MAX(SNAPSHOT_DATE_KEY)

            FROM INVENTORY_DW.GOLD.FACT_INVENTORY_DAILY_SNAPSHOT

        )

        GROUP BY
            p.SUBCATEGORY_NAME

        ORDER BY
            TOTAL_INVENTORY_VALUE DESC

        """


        return explanation, sql.strip()


    # ========================================================
    # INVENTORY VALUE BY BRAND
    # ========================================================

    elif (
        "inventory value by brand" in p
        or (
            "inventory value" in p
            and "brand" in p
        )
    ):

        explanation = (
            "Aggregating inventory value "
            "by product brand."
        )


        sql = """

        SELECT

            p.BRAND_NAME,

            SUM(
                f.INVENTORY_VALUE_AMT
            ) AS TOTAL_INVENTORY_VALUE

        FROM INVENTORY_DW.GOLD.FACT_INVENTORY_DAILY_SNAPSHOT f

        JOIN INVENTORY_DW.GOLD.DIM_PRODUCT p

            ON f.PRODUCT_KEY =
               p.PRODUCT_KEY

        WHERE f.SNAPSHOT_DATE_KEY = (

            SELECT
                MAX(SNAPSHOT_DATE_KEY)

            FROM INVENTORY_DW.GOLD.FACT_INVENTORY_DAILY_SNAPSHOT

        )

        GROUP BY
            p.BRAND_NAME

        ORDER BY
            TOTAL_INVENTORY_VALUE DESC

        """


        return explanation, sql.strip()


    # ========================================================
    # STOCKOUT
    # ========================================================

    elif (
        "stockout" in p
        or "out of stock" in p
    ):

        if "warehouse" in p:

            explanation = (
                "Calculating the number of stockouts "
                "organized by warehouse."
            )


            sql = """

            SELECT

                w.WAREHOUSE_NAME,

                COUNT_IF(
                    f.IS_STOCKOUT_FLAG
                ) AS STOCKOUT_COUNT

            FROM INVENTORY_DW.GOLD.FACT_INVENTORY_DAILY_SNAPSHOT f

            JOIN INVENTORY_DW.GOLD.DIM_WAREHOUSE w

                ON f.WAREHOUSE_KEY =
                   w.WAREHOUSE_KEY

            WHERE f.SNAPSHOT_DATE_KEY = (

                SELECT
                    MAX(SNAPSHOT_DATE_KEY)

                FROM INVENTORY_DW.GOLD.FACT_INVENTORY_DAILY_SNAPSHOT

            )

            GROUP BY
                w.WAREHOUSE_NAME

            ORDER BY
                STOCKOUT_COUNT DESC

            """


        else:

            explanation = (
                "Counting how many products "
                "are completely out of stock."
            )


            sql = """

            SELECT

                COUNT(*) AS STOCKOUT_COUNT

            FROM INVENTORY_DW.GOLD.FACT_INVENTORY_DAILY_SNAPSHOT

            WHERE SNAPSHOT_DATE_KEY = (

                SELECT
                    MAX(SNAPSHOT_DATE_KEY)

                FROM INVENTORY_DW.GOLD.FACT_INVENTORY_DAILY_SNAPSHOT

            )

            AND IS_STOCKOUT_FLAG = TRUE

            """


        return explanation, sql.strip()


    # ========================================================
    # EXCESS INVENTORY BY WAREHOUSE
    # ========================================================

    elif (
        "excess" in p
        and "warehouse" in p
    ):

        explanation = (
            "Aggregating the financial value "
            "of excess stock by warehouse."
        )


        sql = """

        SELECT

            w.WAREHOUSE_NAME,

            SUM(
                f.EXCESS_STOCK_VALUE_AMT
            ) AS TOTAL_EXCESS_VALUE

        FROM INVENTORY_DW.GOLD.FACT_INVENTORY_DAILY_SNAPSHOT f

        JOIN INVENTORY_DW.GOLD.DIM_WAREHOUSE w

            ON f.WAREHOUSE_KEY =
               w.WAREHOUSE_KEY

        WHERE f.SNAPSHOT_DATE_KEY = (

            SELECT
                MAX(SNAPSHOT_DATE_KEY)

            FROM INVENTORY_DW.GOLD.FACT_INVENTORY_DAILY_SNAPSHOT

        )

        GROUP BY
            w.WAREHOUSE_NAME

        ORDER BY
            TOTAL_EXCESS_VALUE DESC

        """


        return explanation, sql.strip()


    # ========================================================
    # TOP 10 PRODUCTS BY INVENTORY VALUE
    # ========================================================

    elif (
        "top 10" in p
        and "inventory value" in p
    ):

        explanation = (
            "Ranking the top 10 products "
            "carrying the highest inventory value."
        )


        sql = """

        SELECT

            p.PRODUCT_SKU,

            p.PRODUCT_NAME,

            SUM(
                f.INVENTORY_VALUE_AMT
            ) AS INVENTORY_VALUE

        FROM INVENTORY_DW.GOLD.FACT_INVENTORY_DAILY_SNAPSHOT f

        JOIN INVENTORY_DW.GOLD.DIM_PRODUCT p

            ON f.PRODUCT_KEY =
               p.PRODUCT_KEY

        WHERE f.SNAPSHOT_DATE_KEY = (

            SELECT
                MAX(SNAPSHOT_DATE_KEY)

            FROM INVENTORY_DW.GOLD.FACT_INVENTORY_DAILY_SNAPSHOT

        )

        GROUP BY
            p.PRODUCT_SKU,
            p.PRODUCT_NAME

        ORDER BY
            INVENTORY_VALUE DESC

        LIMIT 10

        """


        return explanation, sql.strip()


    # ========================================================
    # REORDER NEEDED
    # ========================================================

    elif "reorder" in p:

        explanation = (
            "Counting products that have "
            "fallen below their reorder threshold."
        )


        sql = """

        SELECT

            COUNT(*) AS REORDER_NEEDED_COUNT

        FROM INVENTORY_DW.GOLD.FACT_INVENTORY_DAILY_SNAPSHOT

        WHERE SNAPSHOT_DATE_KEY = (

            SELECT
                MAX(SNAPSHOT_DATE_KEY)

            FROM INVENTORY_DW.GOLD.FACT_INVENTORY_DAILY_SNAPSHOT

        )

        AND IS_REORDER_NEEDED_FLAG = TRUE

        """


        return explanation, sql.strip()


    # ========================================================
    # ABC CLASSIFICATION
    # ========================================================

    elif "abc" in p:

        explanation = (
            "Evaluating inventory value "
            "across ABC classification tiers."
        )


        sql = """

        SELECT

            p.ABC_CLASSIFICATION,

            SUM(
                f.INVENTORY_VALUE_AMT
            ) AS TOTAL_INVENTORY_VALUE

        FROM INVENTORY_DW.GOLD.FACT_INVENTORY_DAILY_SNAPSHOT f

        JOIN INVENTORY_DW.GOLD.DIM_PRODUCT p

            ON f.PRODUCT_KEY =
               p.PRODUCT_KEY

        WHERE f.SNAPSHOT_DATE_KEY = (

            SELECT
                MAX(SNAPSHOT_DATE_KEY)

            FROM INVENTORY_DW.GOLD.FACT_INVENTORY_DAILY_SNAPSHOT

        )

        GROUP BY
            p.ABC_CLASSIFICATION

        ORDER BY
            p.ABC_CLASSIFICATION

        """


        return explanation, sql.strip()


    # ========================================================
    # SUPPLY CHAIN DOMAIN
    # ========================================================

    domain_keywords = [

        "supply",

        "purchase order",

        "supplier",

        "shipment",

        "delivery",

        "warehouse",

        "carrier",

        "freight",

        "inventory",

        "product",

        "stock",

        "stockout",

        "category",

        "brand",

        "quantity",

        "reorder",

        "abc",

        "logistics"
    ]


    if not any(
        word in p
        for word in domain_keywords
    ):

        explanation = (
            """
I am specialized in **Supply Chain Intelligence**.

Please ask a question related to:

- Purchase Orders
- Suppliers
- Shipments
- Deliveries
- Warehouses
- Carriers
- Inventory
- Products
- Logistics
"""
        )


        return explanation, None


    # ========================================================
    # FALLBACK
    # ========================================================

    explanation = (
        "Displaying a recent inventory snapshot "
        "by product and warehouse:"
    )


    sql = """

    SELECT

        d.FULL_DATE,

        p.PRODUCT_NAME,

        w.WAREHOUSE_NAME,

        f.ON_HAND_QTY,

        f.INVENTORY_VALUE_AMT,

        f.IS_STOCKOUT_FLAG

    FROM INVENTORY_DW.GOLD.FACT_INVENTORY_DAILY_SNAPSHOT f

    JOIN INVENTORY_DW.GOLD.DIM_DATE d

        ON f.SNAPSHOT_DATE_KEY =
           d.DATE_KEY

    JOIN INVENTORY_DW.GOLD.DIM_PRODUCT p

        ON f.PRODUCT_KEY =
           p.PRODUCT_KEY

    JOIN INVENTORY_DW.GOLD.DIM_WAREHOUSE w

        ON f.WAREHOUSE_KEY =
           w.WAREHOUSE_KEY

    WHERE f.SNAPSHOT_DATE_KEY = (

        SELECT
            MAX(SNAPSHOT_DATE_KEY)

        FROM INVENTORY_DW.GOLD.FACT_INVENTORY_DAILY_SNAPSHOT

    )

    ORDER BY
        f.INVENTORY_VALUE_AMT DESC

    LIMIT 20

    """


    return explanation, sql.strip()


# ============================================================
# 6. SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        "### ⚡ Dilytics AI"
    )


    st.markdown(
        '<span class="status-pill">'
        '● Semantic Mart Live'
        '</span>',
        unsafe_allow_html=True
    )


    st.write("")


    # ========================================================
    # NEW CHAT
    # ========================================================

    if st.button(
        "➕ New Chat",
        use_container_width=True,
        type="primary"
    ):

        new_id = datetime.now().strftime(
            "%Y%m%d_%H%M%S_%f"
        )


        st.session_state.current_session_id = (
            new_id
        )


        st.session_state.chat_sessions[
            new_id
        ] = {

            "title": "New Conversation",

            "messages": []
        }


        st.rerun()


    st.markdown("---")


    st.markdown(
        "##### 🕒 Recent Conversations"
    )


    # ========================================================
    # RECENT CONVERSATIONS
    # ========================================================

    for s_id, s_data in reversed(
        list(
            st.session_state
            .chat_sessions
            .items()
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
            f"{'👉 ' if is_active else '🗨️ '}"
            f"{session_label}",
            key=f"sess_{s_id}",
            use_container_width=True
        ):

            st.session_state.current_session_id = (
                s_id
            )

            st.rerun()


    st.markdown("---")


    # ========================================================
    # CLEAR ALL SESSIONS
    # ========================================================

    if st.button(
        "🗑️ Clear All Sessions",
        use_container_width=True
    ):

        st.session_state.chat_sessions = {}


        init_id = datetime.now().strftime(
            "%Y%m%d_%H%M%S_%f"
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


# ============================================================
# 7. MAIN PAGE TITLE
# ============================================================

st.markdown(
    """
    <div class="supply-chain-title">
        💬 Dilytics Supply Chain AI
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# 8. RESET THREAD
# ============================================================

reset_col1, reset_col2 = st.columns(
    [5, 1.2]
)


with reset_col2:

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


# ============================================================
# 9. QUESTIONS EXPANDER
# ============================================================

with st.expander(
    "💡 What exact questions can I ask this assistant?",
    expanded=False
):

    st.markdown(
        """
This assistant is currently programmed to answer
Supply Chain questions such as:

### 📋 Purchase Orders

* What is the total purchase order value?
* What is the purchase order value by supplier?
* What are the top 10 purchase orders by value?
* What is the order status by supplier?

### 🚚 Shipments & Deliveries

* How many deliveries are pending?
* Which shipments are delayed?
* What are the top 10 materials by purchase value?

### 🏭 Suppliers

* Which suppliers have the highest number of delayed orders?
* What is the supplier on-time delivery percentage?

### 📦 Inventory

* What is the total available inventory value?
* What is the total quantity of inventory currently on hand?
* What is the inventory value by warehouse?
* What is the inventory value by product category?
* What is the inventory value by brand?
* How many products are out of stock?
"""
    )


    st.info(
        "💡 **Pro-Tip:** "
        "You can copy and paste any of these questions "
        "directly into the chat bar below!"
    )


# ============================================================
# 10. VERIFIED ONBOARDING QUESTIONS
# ============================================================

st.markdown(
    "##### 💡 Verified Onboarding Questions:"
)


q_col1, q_col2, q_col3, q_col4, q_col5 = (
    st.columns(5)
)


quick_prompt = None


if q_col1.button(
    "💰 Total Inv. Value",
    use_container_width=True
):

    quick_prompt = (
        "What is the total available inventory value?"
    )


if q_col2.button(
    "🏭 Value by Warehouse",
    use_container_width=True
):

    quick_prompt = (
        "What is the inventory value by warehouse?"
    )


if q_col3.button(
    "📦 Value by Category",
    use_container_width=True
):

    quick_prompt = (
        "What is the inventory value by product category?"
    )


if q_col4.button(
    "📉 Stockout Count",
    use_container_width=True
):

    quick_prompt = (
        "How many products are out of stock?"
    )


if q_col5.button(
    "⚠️ Excess Stock",
    use_container_width=True
):

    quick_prompt = (
        "What is the total excess inventory value by warehouse?"
    )


# ============================================================
# 11. DISPLAY CHAT HISTORY
# ============================================================

for idx, msg in enumerate(messages):

    with st.chat_message(
        msg["role"]
    ):

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
                    key_prefix=(
                        f"hist_{current_id}_{idx}"
                    )
                )


# ============================================================
# 12. CHAT INPUT
# ============================================================

user_prompt = (
    st.chat_input(
        "Ask a question about suppliers, "
        "purchase orders, shipments, deliveries, "
        "warehouses, carriers, products, or inventory..."
    )
    or quick_prompt
)


# ============================================================
# 13. PROCESS USER QUESTION
# ============================================================

if user_prompt:


    # ========================================================
    # SET CHAT TITLE
    # ========================================================

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


    # ========================================================
    # SAVE USER MESSAGE
    # ========================================================

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


    # ========================================================
    # ASSISTANT RESPONSE
    # ========================================================

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


        # ====================================================
        # SQL EXECUTION
        # ====================================================

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


            except Exception as e:

                st.error(
                    f"SQL Execution Error: {str(e)}"
                )


        # ====================================================
        # SAVE ASSISTANT MESSAGE
        # ====================================================

        messages.append(
            {
                "role": "assistant",

                "content": explanation,

                "sql": sql_query,

                "data": df
            }
        )


    st.rerun()
