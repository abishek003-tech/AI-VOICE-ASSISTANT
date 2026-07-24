import streamlit as st

st.set_page_config(
    page_title="Smart Savings",
    page_icon="💰",
    layout="wide"
)

# Session state for login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ---------------- LOGIN PAGE ----------------
if not st.session_state.logged_in:
    st.markdown(
        """
        <h1 style='text-align:center;color:#2E8B57;'>
        💰 Smart Savings Login
        </h1>
        <h4 style='text-align:center;color:gray;'>
        Track Spending • Improve Savings • Build Wealth
        </h4>
        """,
        unsafe_allow_html=True
    )

    username = st.text_input("👤 Username")
    password = st.text_input("🔒 Password", type="password")

    if st.button("Login"):
        if username == "admin" and password == "1234":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Invalid Username or Password")

# ---------------- DASHBOARD ----------------
else:
    st.title("💰 Smart Savings Dashboard")
    st.write("Welcome! Manage your spending and improve your savings.")

    income = st.number_input(
        "💵 Monthly Income",
        min_value=0,
        value=50000
    )

    spending = st.number_input(
        "🛒 Monthly Spending",
        min_value=0,
        value=30000
    )

    savings = income - spending

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Income", f"₹{income}")

    with col2:
        st.metric("Spending", f"₹{spending}")

    with col3:
        st.metric("Savings", f"₹{savings}")

    st.divider()

    if savings >= income * 0.30:
        st.success("🎉 Excellent! Your savings are more than 30% of income.")
    elif savings >= income * 0.20:
        st.info("👍 Good job! Try reducing unnecessary expenses.")
    else:
        st.warning(
            "⚠️ Your savings are low. Reduce spending on non-essential items."
        )

    st.subheader("📈 Savings Tips")

    tips = [
        "Avoid unnecessary online shopping.",
        "Set a monthly savings goal.",
        "Track daily expenses.",
        "Invest a part of your savings.",
        "Use a budget plan every month."
    ]

    for tip in tips:
        st.write("✅", tip)

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()