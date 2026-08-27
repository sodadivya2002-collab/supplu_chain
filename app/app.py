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

    /* ========================================================
       GENERAL
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

    div[data-testid="stButton"] > button {
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.2s ease-in-out;
    }


    /* ========================================================
       FIXED MAIN HEADER
       ======================================================== */

    .fixed-main-header {
        position: fixed !important;

        top: 0 !important;

        /*
        IMPORTANT:
        Streamlit sidebar is approximately 343px wide.
        This prevents the title from going underneath
        the sidebar.
        */

        left: 343px !important;

        right: 20px !important;

        z-index: 99999 !important;

        background-color: white !important;

        padding: 20px 20px 15px 20px !important;

        margin: 0 !important;

        border-bottom: 1px solid #eeeeee !important;

        box-sizing: border-box !important;
    }


    .fixed-main-title {
        font-size: 2.4rem !important;

        font-weight: 700 !important;

        line-height: 1.2 !important;

        color: #30313d !important;

        margin: 0 !important;
    }


    .fixed-main-subtitle {
        margin-top: 8px !important;

        font-size: 1rem !important;

        color: #8b8d98 !important;
    }


    /*
    Reserve space for fixed header.
    */

    .header-space {
        height: 125px !important;
    }


    /* ========================================================
       CHAT
       ======================================================== */

    [data-testid="stChatMessage"] {
        margin-bottom: 10px;
    }


    /* ========================================================
       EXPANDER
       ======================================================== */

    div[data-testid="stExpander"] {
        border-radius: 10px;
    }


    /* ========================================================
       DATAFRAME
       ======================================================== */

    [data-testid="stDataFrame"] {
        width: 100%;
    }


    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SNOWFLAKE CONNECTION
# ============================================================

@st.cache_resource
def get_snowflake_session():

    connection_parameters = {

        "account": st.secrets["snowflake"]["account"],

        "user": st.secrets["snowflake"]["user"],

        "password": st.secrets["snowflake"]["password"],

        "role": st.secrets["snowflake"].get(
            "role",
            "ACCOUNTADMIN"
        ),

        "warehouse": st.secrets["snowflake"].get(
            "warehouse",
            "COMPUTE_WH"
        ),

        "database": st.secrets["snowflake"].get(
            "database",
            "SUPPLY_CHAIN_DW"
        ),

        "schema": st.secrets["snowflake"].get(
            "schema",
            "GOLD"
        )
    }

    return (
        Session
        .builder
        .configs(connection_parameters)
        .create()
    )


# ============================================================
# CREATE SNOWFLAKE SESSION
# ============================================================

try:

    session = get_snowflake_session()

    st.sidebar.success(
        "✅ Connected to Snowflake"
    )

except Exception as e:

    st.sidebar.error(
        f"❌ Snowflake connection failed: {e}"
    )

    st.stop()


# ============================================================
# CHAT SESSION MANAGEMENT
# ============================================================

if "chat_sessions" not in st.session_state:

    st.session_state.chat_sessions = {}


if "current_session_id" not in st.session_state:

    new_id = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    st.session_state.current_session_id = new_id

    st.session_state.chat_sessions[new_id] = {

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
# CHART FUNCTION
# ============================================================

def display_chart_tab(
    df,
    key_prefix=""
):

    if df is None or df.empty:

        st.info(
            "No data available for chart."
        )

        return


    if len(df.columns) < 2:

        st.info(
            "At least two columns are required "
            "to create a chart."
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
        c
        for c in columns
        if c != x_col
    ]


    if not remaining:

        st.info(
            "No metric column available."
        )

        return


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
# SQL GENERATOR
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
            """
Hello! 👋 I'm your **Supply Chain Assistant**.

I can help you analyze purchase orders,
suppliers, shipments, deliveries, warehouses,
products, inventory and logistics.
""",
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
You can ask me questions about your
**Supply Chain data**.

### 📋 Purchase Orders

* What is the total purchase order count?
* What is the total ordered quantity?
* What is the total ordered value?
* What is the total open commitment?
* What is the total rejected value?
* What is the purchase order value by supplier?
* What is the purchase order value by warehouse?

### 🚚 Shipments & Deliveries

* What is the total number of shipments?
* How many shipments are currently in transit?
* How many shipments have been delivered?
* How many shipments are delayed?
* What is the average delivery delay?
* What are the top delay reasons?

### 🏭 Suppliers

* What is the supplier on-time delivery percentage?
* Which suppliers have the highest purchase order value?
* Which suppliers are high risk?
* Which suppliers are single source?
* Which suppliers have active contracts?

### 🚢 Logistics

* What is the total freight cost?
* What is the total landed cost?
* What is freight cost by carrier?
* What is the shipment count by shipping mode?

### 📦 Products

* What are the top products by ordered value?
* What is the ordered value by product category?
* What is the ordered quantity by product category?
* What is the ordered value by brand?
""",
            None
        )


    # ========================================================
    # TOTAL INVENTORY VALUE
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
            SELECT MAX(SNAPSHOT_DATE_KEY)
            FROM INVENTORY_DW.GOLD.FACT_INVENTORY_DAILY_SNAPSHOT
        )
        """

        return explanation, sql.strip()


    # ========================================================
    # TOTAL ON HAND QUANTITY
    # ========================================================

    if (
        "quantity" in p
        and "on hand" in p
    ):

        explanation = (
            "Calculating the total quantity "
            "currently on hand."
        )

        sql = """
        SELECT
            SUM(ON_HAND_QTY)
                AS TOTAL_ON_HAND_QTY
        FROM INVENTORY_DW.GOLD.FACT_INVENTORY_DAILY_SNAPSHOT
        WHERE SNAPSHOT_DATE_KEY = (
            SELECT MAX(SNAPSHOT_DATE_KEY)
            FROM INVENTORY_DW.GOLD.FACT_INVENTORY_DAILY_SNAPSHOT
        )
        """

        return explanation, sql.strip()


    # ========================================================
    # INVENTORY VALUE BY WAREHOUSE
    # ========================================================

    if "inventory value by warehouse" in p:

        explanation = (
            "Aggregating inventory value by warehouse."
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
            SELECT MAX(SNAPSHOT_DATE_KEY)
            FROM INVENTORY_DW.GOLD.FACT_INVENTORY_DAILY_SNAPSHOT
        )
        GROUP BY
            w.WAREHOUSE_NAME
        ORDER BY
            INVENTORY_VALUE DESC
        """

        return explanation, sql.strip()


    # ========================================================
    # INVENTORY VALUE BY CATEGORY
    # ========================================================

    if (
        "inventory value by product category" in p
        or "inventory value by category" in p
    ):

        explanation = (
            "Aggregating inventory value by "
            "product category."
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
            SELECT MAX(SNAPSHOT_DATE_KEY)
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

    if "subcategory" in p:

        explanation = (
            "Aggregating inventory value by "
            "product subcategory."
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
            SELECT MAX(SNAPSHOT_DATE_KEY)
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

    if (
        "inventory value by brand" in p
        or (
            "inventory value" in p
            and "brand" in p
        )
    ):

        explanation = (
            "Aggregating inventory value by brand."
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
            SELECT MAX(SNAPSHOT_DATE_KEY)
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

    if (
        "stockout" in p
        or "out of stock" in p
    ):

        explanation = (
            "Calculating products that are "
            "currently out of stock."
        )

        sql = """
        SELECT
            COUNT(*) AS STOCKOUT_COUNT
        FROM INVENTORY_DW.GOLD.FACT_INVENTORY_DAILY_SNAPSHOT
        WHERE SNAPSHOT_DATE_KEY = (
            SELECT MAX(SNAPSHOT_DATE_KEY)
            FROM INVENTORY_DW.GOLD.FACT_INVENTORY_DAILY_SNAPSHOT
        )
        AND IS_STOCKOUT_FLAG = TRUE
        """

        return explanation, sql.strip()


    # ========================================================
    # EXCESS INVENTORY
    # ========================================================

    if (
        "excess" in p
        and "warehouse" in p
    ):

        explanation = (
            "Calculating excess inventory value "
            "by warehouse."
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
            SELECT MAX(SNAPSHOT_DATE_KEY)
            FROM INVENTORY_DW.GOLD.FACT_INVENTORY_DAILY_SNAPSHOT
        )
        GROUP BY
            w.WAREHOUSE_NAME
        ORDER BY
            TOTAL_EXCESS_VALUE DESC
        """

        return explanation, sql.strip()


    # ========================================================
    # TOP 10 PRODUCTS
    # ========================================================

    if (
        "top 10" in p
        and "inventory value" in p
    ):

        explanation = (
            "Ranking the top 10 products "
            "by inventory value."
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
            SELECT MAX(SNAPSHOT_DATE_KEY)
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
    # REORDER
    # ========================================================

    if "reorder" in p:

        explanation = (
            "Calculating the number of products "
            "that need to be reordered."
        )

        sql = """
        SELECT
            COUNT(*) AS REORDER_NEEDED_COUNT
        FROM INVENTORY_DW.GOLD.FACT_INVENTORY_DAILY_SNAPSHOT
        WHERE SNAPSHOT_DATE_KEY = (
            SELECT MAX(SNAPSHOT_DATE_KEY)
            FROM INVENTORY_DW.GOLD.FACT_INVENTORY_DAILY_SNAPSHOT
        )
        AND IS_REORDER_NEEDED_FLAG = TRUE
        """

        return explanation, sql.strip()


    # ========================================================
    # ABC CLASSIFICATION
    # ========================================================

    if "abc" in p:

        explanation = (
            "Calculating inventory value "
            "by ABC classification."
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
            SELECT MAX(SNAPSHOT_DATE_KEY)
            FROM INVENTORY_DW.GOLD.FACT_INVENTORY_DAILY_SNAPSHOT
        )
        GROUP BY
            p.ABC_CLASSIFICATION
        ORDER BY
            p.ABC_CLASSIFICATION
        """

        return explanation, sql.strip()


    # ========================================================
    # SUPPLY CHAIN GENERAL QUESTIONS
    # ========================================================

    if (
        "purchase order" in p
        or "supplier" in p
        or "shipment" in p
        or "delivery" in p
        or "carrier" in p
        or "warehouse" in p
        or "freight" in p
    ):

        return (
            """
I can help with Supply Chain questions about:

- Purchase Orders
- Suppliers
- Shipments
- Deliveries
- Warehouses
- Carriers
- Freight
- Products
- Inventory

Please ask a specific Supply Chain question.
""",
            None
        )


    # ========================================================
    # OUT OF DOMAIN
    # ========================================================

    return (
        """
I am specialized in **Supply Chain Intelligence**.

Please ask a question related to:

- Purchase Orders
- Suppliers
- Shipments
- Deliveries
- Warehouses
- Carriers
- Products
- Inventory
- Logistics
""",
        None
    )


# ============================================================
# SIDEBAR
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
            st.session_state
            .chat_sessions
            .items()
        )
    ):

        is_active = (
            s_id ==
            st.session_state.current_session_id
        )


        session_title = s_data["title"]


        if len(session_title) > 22:

            session_title = (
                session_title[:20]
                + "..."
            )


        if st.button(
            f"{'👉 ' if is_active else '🗨️ '}"
            f"{session_title}",
            key=f"session_{s_id}",
            use_container_width=True
        ):

            st.session_state.current_session_id = s_id

            st.rerun()


    st.markdown("---")


    # ========================================================
    # CLEAR ALL
    # ========================================================

    if st.button(
        "🗑️ Clear All Sessions",
        use_container_width=True
    ):

        st.session_state.chat_sessions = {}


        new_id = datetime.now().strftime(
            "%Y%m%d_%H%M%S_%f"
        )


        st.session_state.current_session_id = new_id


        st.session_state.chat_sessions[new_id] = {

            "title": "New Conversation",

            "messages": []

        }


        st.rerun()


# ============================================================
# MAIN FIXED HEADER
# ============================================================

st.markdown(
    """
    <div class="fixed-main-header">

        <div class="fixed-main-title">
            💬 Dilytics Supply Chain AI
        </div>

        <div class="fixed-main-subtitle">
            Ask questions in natural language to explore
            suppliers, purchase orders, shipments,
            deliveries, warehouses, carriers, and products.
        </div>

    </div>

    <div class="header-space"></div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# RESET THREAD
# ============================================================

reset_col1, reset_col2 = st.columns(
    [5, 1.2]
)


with reset_col2:

    if st.button(
        "🔄 Reset Thread",
        use_container_width=True
    ):

        st.session_state.chat_sessions[
            current_id
        ]["messages"] = []


        st.session_state.chat_sessions[
            current_id
        ]["title"] = "New Conversation"


        st.rerun()


# ============================================================
# SUGGESTED QUESTIONS
# ============================================================

with st.expander(
    "💡 What exact questions can I ask this assistant?",
    expanded=False
):

    st.markdown(
        """
### 💰 Inventory Value & Quantity

* What is the total available inventory value?

* What is the total quantity of inventory currently on hand?

* What is the inventory value by warehouse?


### 📦 Products & Categories

* What is the inventory value by product category?

* What is the inventory value by product subcategory?

* What is the inventory value by brand?

* What are the top 10 products by inventory value?

* What is the inventory value by ABC classification?


### 📋 Purchase Orders

* What is the total purchase order value?

* What is the purchase order value by supplier?

* What is the purchase order value by warehouse?


### 🚚 Supply Chain

* How many shipments are currently in transit?

* How many shipments are delayed?

* What is the average delivery delay?

* What is the supplier on-time delivery percentage?

* What is the total freight cost?
"""
    )


# ============================================================
# VERIFIED ONBOARDING QUESTIONS
# ============================================================

st.markdown(
    "### 💡 Verified Onboarding Questions:"
)


q1, q2, q3, q4, q5 = st.columns(5)


quick_prompt = None


if q1.button(
    "💰 Total Inv. Value",
    use_container_width=True
):

    quick_prompt = (
        "What is the total available inventory value?"
    )


if q2.button(
    "🏭 Value by Warehouse",
    use_container_width=True
):

    quick_prompt = (
        "What is the inventory value by warehouse?"
    )


if q3.button(
    "📦 Value by Category",
    use_container_width=True
):

    quick_prompt = (
        "What is the inventory value by product category?"
    )


if q4.button(
    "📉 Stockout Count",
    use_container_width=True
):

    quick_prompt = (
        "How many products are out of stock?"
    )


if q5.button(
    "⚠️ Excess Stock",
    use_container_width=True
):

    quick_prompt = (
        "What is the total excess inventory value by warehouse?"
    )


# ============================================================
# DISPLAY CHAT HISTORY
# ============================================================

for idx, message in enumerate(messages):

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )


        if (
            "sql" in message
            and message["sql"]
        ):

            with st.expander(
                "Generated SQL",
                expanded=False
            ):

                st.code(
                    message["sql"],
                    language="sql"
                )


        if (
            "data" in message
            and message["data"] is not None
            and not message["data"].empty
        ):

            tab1, tab2 = st.tabs(
                [
                    "Data 📄",
                    "Chart 📈"
                ]
            )


            with tab1:

                st.dataframe(
                    message["data"],
                    use_container_width=True
                )


            with tab2:

                display_chart_tab(
                    message["data"],
                    key_prefix=(
                        f"history_{current_id}_{idx}"
                    )
                )


# ============================================================
# CHAT INPUT
# ============================================================

user_prompt = st.chat_input(
    "Ask a question about suppliers, purchase orders, "
    "shipments, deliveries, warehouses, carriers, "
    "products, or inventory..."
)


# ============================================================
# QUICK QUESTION
# ============================================================

if quick_prompt:

    user_prompt = quick_prompt


# ============================================================
# PROCESS USER QUESTION
# ============================================================

if user_prompt:


    # ========================================================
    # UPDATE CONVERSATION TITLE
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
    # GENERATE SQL
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
        # EXECUTE SQL
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
                            key_prefix=(
                                f"live_{current_id}"
                            )
                        )


            except Exception as e:

                st.error(
                    f"SQL Execution Error: {str(e)}"
                )


        # ====================================================
        # SAVE ASSISTANT RESPONSE
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
