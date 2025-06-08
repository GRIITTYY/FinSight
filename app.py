import streamlit as st
import fitz
from datetime import datetime
import re
import pandas as pd
import io
from streamlit_option_menu import option_menu
import plotly.express as px
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta, timezone
from plots import (
        plot_main_category_bar,
        plot_top_inflow_categories,
        plot_top_inflow_count,
        plot_monthly_inflow_and_count,
        plot_transfer_inflow_from_sender,
        plot_top_outflow_categories, 
        inflow_outflow_bar_chart, 
        plot_spending_by_channel, 
        plot_monthly_outflow_and_count,
        plot_transfer_to_recipients,
        balance_trend_chart,
        create_sparkline
        )

st.set_page_config(
    page_title="Finsight ",
    page_icon="📈",
    layout="wide"
)


pd.set_option('display.float_format', '{:.2f}'.format)

# Store session state
if 'df' not in st.session_state:
    st.session_state.df = None
if 'full_df' not in st.session_state:
    st.session_state.full_df = None
if 'wallet_df' not in st.session_state:
    st.session_state.wallet_df = None
if 'owealth_df' not in st.session_state:
    st.session_state.owealth_df = None
if 'wallet_info' not in st.session_state:
    st.session_state.wallet_info = None
if 'analyzed' not in st.session_state:
    st.session_state.analyzed = False
if "tab1_df" not in st.session_state:
    st.session_state["tab1_df"] = None
if "df_encoded" not in st.session_state:
    st.session_state["df_encoded"] = None


# Sidebar for navigation
with st.sidebar:
    app_pages = option_menu(
        "FinSight", 
        ["Welcome", "inSight Model", "Inflow Patterns", "Outflow Patterns", "Detected Anomalies", "FinSight AI"], 
        icons=["house-gear", "bar-chart-steps", "cash-coin", "currency-exchange", "exclamation-triangle-fill", "robot"], 
        menu_icon="graph-up-arrow"
    )
    
    st.sidebar.success("Select a Page above")
    st.sidebar.caption("We prioritize your privacy - no data is collected or processed externally")
    
    # Social links in sidebar
    st.sidebar.markdown("### Connect with us")
    st.sidebar.markdown("[Linkedin](https://www.linkedin.com/in/samuel-o-momoh/) | [Twitter](https://twitter.com/griittyy) | [GitHub](https://github.com/GRIITTYY)")
    
    # App Info
    st.sidebar.markdown("---")
    st.sidebar.caption("Version 1.1.0")

category_mappings = {
    "Mobile Data & Airtime": ["Mobile Data", "Airtime"],
    "Card Payments": ["OPay Card Payment"],
    "USSD Deposits": ["Add Money Bank USSD"],
    "Bank Deposits": ["Bank Deposit", "^Transfer from(?! EaseMoni)"],
    "Outgoing Transfers": ["^Transfer to"],
    "TV Subscriptions": ["TV"],
    "Electricity Bills": ["Electricity"],
    "ATM": ["^ATM"],
    "POS Transactions": ["^POS"],
    "Loan Repayment": ["MerchantLoan repayment", "EaseMoni loan repayment"],
    "OWealth Deposits": ["OWealth Deposit", "OWealth Deposit(AutoSave)", "OWealth Deposit(from Fixed)"],
    "Fixed Deposits": ["Fixed Deposit"],
    "OPay Card Rewards": ["Apply OPay Physical Card"],
    "Online Payments": ["^Transfer to Paystack", "Merchant Consumption"],
    "Others": ["Other", "Certpay"],
    "Refunds": ["Refund"],
    "Betting": ["Betting"],
    "USSD Charges": ["USSD Charge"],
    "EaseMoni Loans": ["Transfer from EaseMoni"],
    "OWealth Interest": ["OWealth Interest Earned"],
    "Electronic Money Levy": ["Electronic Money Transfer Levy"]
}

def categorize_description(description):
    if not isinstance(description, str):
        return "Others"
    
    for category, keywords in category_mappings.items():
        for keyword in keywords:
            if keyword.startswith("^"):
                pattern = re.escape(keyword[1:])
                if re.match(rf"^{pattern}", description, re.IGNORECASE):
                    return category
            else:
                if keyword.lower() in description.lower():
                    return category
    return "Others"

# Function to parse data to DataFrame
def parse_data(data):
        # Collect errors
        fix = []

        # Track error row number
        row = 0

        # Store transaction data in dictionary
        x = {
            1: [],
            2: [],
            3: [],
            4: [],
            5: [],
            6: [],
            7: []
        }

        counter = 1

        for val in data:
            if row != 0:
                val = val.strip()
                if (len(val) == 2 and val.isdigit()):
                    fix.append((row, val))
                    continue

                if counter == 2:
                    try:
                        datetime.strptime(val, "%d %b %Y")
                    except ValueError:
                        fix.append((row, val))
                        continue

                if counter == 4 and not re.fullmatch(r"[+-].*\.\d{2}", val):
                        fix.append((row, val))
                        continue

                else:
                    x[counter].append(val)

            counter += 1
            if counter > 7:
                row += 1
                counter = 1

        for keys in x:
            if len(x[keys]) != len(x[1]):
                x[keys] += [None] * (len(x[1]) - len(x[keys]))


        df = pd.DataFrame(x)
        df.columns = [
                'Trans Time',
                'Date',
                'Description',
                'Amount',
                'Balance',
                'Channel',
                'Reference'
        ]

        for err in fix:
            if len(err[1]) == 2:
                df.iloc[err[0]-1, 0] += str(err[1])
            else:
                df.iloc[err[0]-1, 2] += str(err[1])

        del x
        del fix
        del row

        return df

def clean_dataframes(df):
    df = df.copy()
    df['Trans Time'] = pd.to_datetime(df['Trans Time'])
    df['Date'] = pd.to_datetime(df['Date']).dt.date
    df["Type"] = df["Amount"].apply(lambda x: "Debit" if str(x).startswith("-") else "Credit")
    df['Amount'] = df['Amount'].str.replace(r"[+, -]", "", regex=True).astype(float)
    df['Balance'] = df['Balance'].str.replace(r"[+, -]", "", regex=True)
    df['Balance'] = df['Balance'].fillna("0")
    df['Balance'] = pd.to_numeric(df['Balance'], errors='coerce')
    df["Year"] = df["Trans Time"].dt.year
    df["Month"] = df["Trans Time"].dt.month_name()
    df["MonthYear"] = df["Trans Time"].dt.to_period("M")

    transfer_to_pattern = r"^Transfer to\s+(.*)"
    transfer_from_pattern = r"^Transfer from\s+(.*)"
    df["Category"] = df["Description"]

    outgoing_mask = df["Description"].str.extract(transfer_to_pattern, expand=False).notna()
    df.loc[outgoing_mask, "Category"] = "Outgoing Bank Transfers"

    received_mask = df["Description"].str.extract(transfer_from_pattern, expand=False).notna()
    df.loc[received_mask, "Category"] = "Received Bank Transfers"

    df.loc[df['Channel'] == 'ATM', 'Description'] = 'ATM'
    df.loc[df['Channel'] == 'POS', 'Description'] = 'POS'

    df["Main Category"] = df["Description"].apply(categorize_description)
    
    df["Recipient"] = df["Description"].str.extract(transfer_to_pattern, expand=False)
    df["Sender"] = df["Description"].str.extract(transfer_from_pattern, expand=False)

    df["Inflow"] = df.apply(lambda row: row["Amount"] if row["Type"] == "Credit" else 0.0,axis=1)
    df["Outflow"] = df.apply(lambda row: row["Amount"] if row["Type"] == "Debit" else 0.0,axis=1)

    df = df.query("Description != 'OWealth Withdrawal'")

    df['Hour'] = df['Trans Time'].dt.hour
    df['Day'] = df['Trans Time'].dt.day
    df['Weekday'] = df['Trans Time'].dt.weekday
    df['IsWeekend'] = df['Weekday'].isin([5, 6]).astype(int)

    return df

def rainbow_divider():
    st.markdown("""
                <div style="height: 2px; background: linear-gradient(to right, red, orange, yellow, green, blue, indigo, violet); border-radius: 5px; margin-top: 0.5rem;"></div>
                    """, unsafe_allow_html=True)

if app_pages == "Welcome":
    st.markdown("""
    <div style="text-align: center; padding: 3rem 1rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%); border-radius: 20px; margin-bottom: 2rem;">
        <h1 style="font-size: 3.5rem; font-weight: bold; color: white; margin: 0 0 1rem 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">
            Analyze Bank Statements Effortlessly 💸
        </h1>
        <p style="font-size: 1.3rem; color: rgba(255,255,255,0.9); max-width: 700px; margin: 0 auto; line-height: 1.6; text-shadow: 1px 1px 2px rgba(0,0,0,0.2);">
            Upload your PDF bank statements and instantly visualize inflow & outflow trends, detect anomalies, and gain financial insights.
        </p>
    </div>
    """, unsafe_allow_html=True)

    bank = st.selectbox("Select Bank", options = ["Choose a Bank", "Opay", "GTBank (Coming Soon)", "Zenith (Coming Soon)", "Kuda (Coming Soon)", "Access Bank (Coming Soon)"])
    uploaded_file = st.file_uploader("Upload PDF Statement")

    if uploaded_file:
        if (uploaded_file.name != st.session_state.get("processed_file_name")):
            keys_to_reset = [
                "file_bytes", "wallet_info", "owealth_info",
                "wallet_df", "owealth_df", "df"
            ]
            for key in keys_to_reset:
                st.session_state.pop(key, None)

            # Read file bytes once and store
            file_bytes = uploaded_file.read()
            st.session_state.file_bytes = file_bytes
            st.session_state.processed_file_name = uploaded_file.name
        else:
            # Use previously stored bytes for processing
            file_bytes = st.session_state.file_bytes

        if bank == "Opay":
            with fitz.open(stream=file_bytes, filetype="pdf") as doc:
                all_text = ""
                for page in doc:
                    all_text += page.get_text()

            data = all_text.split("\n")
            if "Note: Current Balance includes OWealth Balance which is powered by Blue Ridge Microfinance Bank, and OPay Wallet Balance." in data:
                # Extract Wallet Info
                wallet_info = data[:data.index("Note: Current Balance includes OWealth Balance which is powered by Blue Ridge Microfinance Bank, and OPay Wallet Balance.")]
                wallet_info.remove('Account Statement')
                wallet_info = dict(zip(wallet_info[::2], wallet_info[1::2]))

                # Extract Wallet Transactions
                wallet_trans = data[data.index("Trans. Time") : data.index("Summary - OWealth Balance") - 10]

                wallet_df = parse_data(wallet_trans)
                wallet_df = clean_dataframes(wallet_df)
                wallet_df["Label"] = ["Wallet"] * len(wallet_df)
                df = wallet_df


                if "Summary - Wallet Balance" in data:
                    # Extract Owealth Info
                    owealth_info = data[data.index("Summary - OWealth Balance") - 10 : data.index("Summary - OWealth Balance")]
                    # Extract Owealth Transactions
                    owealth_trans = data[data.index("Summary - OWealth Balance")+1:-2]
                    owealth_df = parse_data(owealth_trans)
                    owealth_df = clean_dataframes(owealth_df)
                    owealth_df["Label"] = ["Owealth"] * len(owealth_df)
                    df = pd.concat([wallet_df, owealth_df], ignore_index=True)
                    st.session_state.owealth_info = owealth_info
                    st.session_state.owealth_df = owealth_df

                # Store dataframes info in session state
                st.session_state.wallet_info = wallet_info
                st.session_state.wallet_df = wallet_df
                st.session_state.df = df.sort_values("Trans Time")
                st.session_state.analyzed = True

                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    wallet_df[["Trans Time",
                              "Date",
                              "Description",
                              "Amount",	
                              "Balance",
                              "Channel",
                              "Reference",
                              "Type"]].to_excel(writer, sheet_name='Wallet Transactions', index=False)
                    owealth_df[["Trans Time",
                              "Date",
                              "Description",
                              "Amount",	
                              "Balance",
                              "Channel",
                              "Reference",
                              "Type"]].to_excel(writer, sheet_name='Owealth Transactions', index=False)
                    df[["Trans Time",
                              "Date",
                              "Description",
                              "Amount",	
                              "Balance",
                              "Channel",
                              "Reference",
                              "Type"]].to_excel(writer, sheet_name='All Transactions', index=False)

                buffer.seek(0)

                st.markdown("""
                <div style="background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%); border-left: 6px solid #10b981; border-radius: 12px; padding: 1.5rem; margin: 2rem 0; box-shadow: 0 4px 6px rgba(16, 185, 129, 0.1);">
                    <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                        <span style="font-size: 1.5rem; margin-right: 0.75rem;">🎉</span>
                        <h3 style="margin: 0; color: #065f46; font-size: 1.25rem;">Statement Processed Successfully!</h3>
                    </div>
                    <p style="margin: 0; color: #047857; font-size: 1rem;">
                        Your bank statement has been processed and is ready for insights. Navigate to <strong>inSight Model</strong> to explore your financial patterns.
                    </p>
                </div>
                """, unsafe_allow_html=True)

                st.download_button(
                    label="📥 Download Excel (Wallet + Owealth)",
                    data=buffer,
                    file_name='wallet_owealth_data.xlsx',
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )

                st.markdown("""
                <div style="background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%); border-left: 6px solid #3b82f6; border-radius: 12px; padding: 1.5rem; margin: 1rem 0; box-shadow: 0 4px 6px rgba(59, 130, 246, 0.1);">
                    <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                        <span style="font-size: 1.5rem; margin-right: 0.75rem;">💾</span>
                        <h4 style="margin: 0; color: #1e40af; font-size: 1.1rem;">Download Your Data</h4>
                    </div>
                    <p style="margin: 0; color: #1d4ed8; font-size: 0.95rem;">
                        Below is a preview of your processed Bank Statement. You can use the download button above to download your statement in Excel format now.
                    </p>
                </div>
                """, unsafe_allow_html=True)
                

                st.dataframe(st.session_state.df[["Trans Time",
                              "Date",
                              "Description",
                              "Amount",	
                              "Balance",
                              "Channel",
                              "Reference",
                              "Type"]])
            else:
                st.markdown("""
                <div style="background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%); border-left: 6px solid #dc2626; border-radius: 12px; padding: 1.5rem; margin: 2rem 0; box-shadow: 0 4px 6px rgba(220, 38, 38, 0.1);">
                    <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                        <span style="font-size: 1.5rem; margin-right: 0.75rem;">❌</span>
                        <h3 style="margin: 0; color: #991b1b; font-size: 1.25rem;">Invalid Bank Statement</h3>
                    </div>
                    <p style="margin: 0; color: #b91c1c; font-size: 1rem;">
                        We couldn't identify this as an OPay bank statement. Please check your file and try again with a valid OPay PDF statement.
                    </p>
                </div>
                """, unsafe_allow_html=True)

        elif bank == "Choose a Bank":
            st.markdown("""
            <div style="background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); border-left: 6px solid #f59e0b; border-radius: 12px; padding: 1.5rem; margin: 2rem 0; box-shadow: 0 4px 6px rgba(245, 158, 11, 0.1);">
                <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                    <span style="font-size: 1.5rem; margin-right: 0.75rem;">⚠️</span>
                    <h3 style="margin: 0; color: #92400e; font-size: 1.25rem;">Please Select a Bank</h3>
                </div>
                <p style="margin: 0; color: #a16207; font-size: 1rem;">
                    Choose your bank from the dropdown menu above to proceed with the statement analysis.
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%); border-left: 6px solid #6366f1; border-radius: 12px; padding: 1.5rem; margin: 2rem 0; box-shadow: 0 4px 6px rgba(99, 102, 241, 0.1);">
                <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                    <span style="font-size: 1.5rem; margin-right: 0.75rem;">🚧</span>
                    <h3 style="margin: 0; color: #4338ca; font-size: 1.25rem;">Coming Soon!</h3>
                </div>
                <p style="margin: 0; color: #5b21b6; font-size: 1rem;">
                    Support for other banks is currently in development. Stay tuned for updates!
                </p>
            </div>
            """, unsafe_allow_html=True)


elif app_pages == "inSight Model":
    if not st.session_state.analyzed:
        st.warning("Please upload a bank statement first.")
    else:
        wallet_df = st.session_state.wallet_df
        owealth_df = st.session_state.owealth_df
        df = st.session_state.df

        st.title("💱 Welcome to your inSight Model ")
        st.subheader("Here's a quick insighful glance at your financial health.")
        st.write("Be sure to use the date filters below to get more insights into your wallet patterns.")
        min_date = st.session_state.df['Date'].min()
        max_date = st.session_state.df['Date'].max()
        start_date = st.date_input("Enter Start Date", value=min_date, min_value=min_date, max_value=max_date)
        end_date = st.date_input("Enter End Date", value=max_date, min_value=min_date, max_value=max_date)

        tab1_df = st.session_state.df[
                            (st.session_state.df["Date"] >= start_date) 
                            & (st.session_state.df["Date"] <= end_date)]
    

        if start_date >= end_date:
            st.error("Error: Start date must be before end date.")

        total_inflow = tab1_df["Inflow"].sum()
        total_outflow = tab1_df["Outflow"].sum()
    
        col1, col2, col3 = st.columns(3)

        # Net Income Card
        with col1:
            net_flow = total_inflow - total_outflow
            color = "#2ca02c" if net_flow >= 0 else "#d62728"
            arrow = "▲" if net_flow >= 0 else "▼"

            net_balance_html = f"""
            <div style="margin-bottom: 10px; background:#f0f4f8; padding:20px; border-radius:10px; text-align:center; box-shadow: 2px 4px 6px #ccc;,">
                <h4>Net Flow</h4>
                <h2 style="margin:5px 0; color:{color};">₦{net_flow:,.2f} {arrow}</h2>
            </div>
            """
            st.markdown(net_balance_html, unsafe_allow_html=True)
            if net_flow > 0:
                st.caption(
                    f"⭐ Awesome! You've got ₦{net_flow:,.2f} extra cash this period because your income was higher than your spending! \n🥳 Great job! This is perfect for growing your savings. Want to see what led to this win? Check your 'Outflow Patterns' for smart choices or your 'Inflow Patterns' to see your earnings shine!"
                )
            elif net_flow < 0:
                st.caption(
                    f"⚠️ Your Expenses were ₦{abs(net_flow):,.2f} more than your income this time.\n"
                    "\nDon't worry, there is a chance to adjust! 🧐 The best first step is to visit your 'Outflow Patterns' page. It'll clearly show where your money went and help you spot areas to tweak for next period. Also, take a quick look at your 'Inflow Patterns' page."
                )
            else:
                st.caption(
                    f"⚖️ You broke even! Your Money in = Your Money out. Good job on balancing! 🥳 \nWant to save more? Take a look at your 'Outflow Patterns' page to see where you might trim a little for next period."
                )
                    

        # Total Inflow Card
        with col2:
            income_html = f"""
            <div style="margin-bottom: 10px; background:#e6f7e6; padding:20px; border-radius:10px; text-align:center; box-shadow: 2px 4px 6px #c1e2c1;">
                <h4>Total Inflow</h4>
                <h2 style="margin:5px 0; color:#2ca02c;">₦{total_inflow:,.2f}</h2>
            </div>
            """
            st.markdown(income_html, unsafe_allow_html=True)
            st.plotly_chart(create_sparkline(tab1_df, 'Inflow', '#2ca02c'), use_container_width=True)

        # Total Outflow Card
        with col3:
            expense_html = f"""
            <div style="margin-bottom: 10px; background:#fdecea; padding:20px; border-radius:10px; text-align:center; box-shadow: 2px 4px 6px #f5c6c6;">
                <h4>Total Outflow</h4>
                <h2 style="margin:5px 0; color:#d62728;">₦{total_outflow:,.2f}</h2>
            </div>
            """
            st.markdown(expense_html, unsafe_allow_html=True)
            st.plotly_chart(create_sparkline(tab1_df, 'Outflow', '#d62728'), use_container_width=True)

        rainbow_divider()

        cols = st.columns([1, 2, 2]) 
        cols[0].metric("Current Wallet Balance", f"{st.session_state.wallet_info.get('Current Balance', 'N/A')}")
        cols[1].metric("Overall Number of Credit Transactions", st.session_state.wallet_info.get('Credit Count', 'N/A'))
        cols[2].metric("Overall Number of Debit Transactions", st.session_state.wallet_info.get('Debit Count', 'N/A'))
        

        rainbow_divider()
        
        fig = inflow_outflow_bar_chart(tab1_df)
        st.plotly_chart(fig, use_container_width=True)

        rainbow_divider()


        # 1. Most Active Spending Day (highest number of debit transactions)
        debit_df = tab1_df[tab1_df['Outflow'] > 0]
        debit_df["Date"] = pd.to_datetime(debit_df["Date"])
        most_active = debit_df['Date'].dt.date.value_counts().idxmax()
        active_count = debit_df['Date'].dt.date.value_counts().max()

        # 2. Highest Single Transaction
        max_trans = debit_df.loc[debit_df['Outflow'].idxmax()]
        max_amount = max_trans['Outflow']
        max_date = pd.to_datetime(max_trans['Date']).strftime("%b %d, %Y")

        # 3. Lowest Transaction
        min_trans = debit_df.loc[debit_df['Outflow'].idxmin()]
        min_amount = min_trans['Outflow']
        min_date = pd.to_datetime(min_trans['Date']).strftime("%b %d, %Y")

        # 4. Most Frequent Spending Channel
        top_channel = debit_df['Channel'].value_counts().idxmax()
        channel_count = debit_df['Channel'].value_counts().max()


        st.markdown("### 🔍 Quick Facts About Your Spending")

        col1, col2 = st.columns(2)

        with col1:
            # Most Active Spending Day
            st.markdown(f"""
            <div style="background:white; padding:1rem; border-radius:1rem; text-align:center; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border: 1px solid #e5e7eb;">
                <h4 style="font-size: 1rem; color:#374151;">🗓️ Most Active Spending Day</h4>
                <p style="font-size: 1.5rem; font-weight:bold; color:#2563eb;">{most_active.strftime('%B %d %Y')}</p>
                <p style="color:#6b7280;">You made a total of {active_count} transactions.</p>
                <p style="font-size:0.875rem; color:#6b7280;">Your wallet really worked overtime on this day!</p>
            </div>
            """, unsafe_allow_html=True)

            # Highest Single Transaction
            st.markdown(f"""
            <div style="background:white; margin-top:1rem; padding:1rem; border-radius:1rem; text-align:center; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border: 1px solid #e5e7eb;">
                <h4 style="font-size: 1rem; color:#374151;">💸 Highest Single Transaction</h4>
                <p style="font-size: 1.5rem; font-weight:bold; color:#dc2626;">₦{max_amount:,.2f}</p>
                <p style="color:#6b7280;">on {max_date}</p>
                <p style="font-size:0.875rem; color:#6b7280;">That was a real power move, we hope it was worth every naira!</p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            # Lowest Transaction
            st.markdown(f"""
            <div style="background:white; padding:1rem; border-radius:1rem; text-align:center; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border: 1px solid #e5e7eb;">
                <h4 style="font-size: 1rem; color:#374151;">🪙 Lowest Transaction</h4>
                <p style="font-size: 1.5rem; font-weight:bold; color:#16a34a;">₦{min_amount:,.2f}</p>
                <p style="color:#6b7280;">on {min_date}</p>
                <p style="font-size:0.875rem; color:#6b7280;">Small nyash dey shake oh! 😅😅😅. Well this is him! 😉</p>
            </div>
            """, unsafe_allow_html=True)

            # Most Frequent Spending Channel
            st.markdown(f"""
            <div style="background:white; margin-top:1rem; padding:1rem; border-radius:1rem; text-align:center; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border: 1px solid #e5e7eb;">
                <h4 style="font-size: 1rem; color:#374151;">🏦 Most Frequent Channel</h4>
                <p style="font-size: 1.5rem; font-weight:bold; color:#7c3aed;">{top_channel}</p>
                <p style="color:#6b7280;">{channel_count} transactions made in total</p>
                <p style="font-size:0.875rem; color:#6b7280;">Run or stay Mate! This is where most of your magic happens. 💱.</p>
            </div>
            """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)


        with col1:
            fixed_deposits = df.query("Description == 'Fixed Deposit'")
            fixed_deposit_total = fixed_deposits["Amount"].sum()
            fixed_deposit_count = fixed_deposits.shape[0]
            latest_amount = (fixed_deposits.sort_values(by="Trans Time", ascending=False).iloc[0]["Amount"] if not df.query("Description == 'Fixed Deposit'").empty else 0)
            max_date = fixed_deposits["Trans Time"].max() if fixed_deposit_count > 0 else None
            max_date_str = max_date.strftime('%B %d, %Y') if max_date else "N/A"
            # max_date_str = max_date.strftime('%B %d, %Y') if pd.notna(max_date) else "N/A"
    

            st.markdown(f"""
            <div style="background:white; margin-top:1rem; padding:1rem; border-radius:1rem; text-align:center; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border: 1px solid #e5e7eb;">
                <h4 style="font-size: 1rem; color:#374151;">🏦 Total Fixed Deposit</h4>
                <p style="font-size: 1.5rem; font-weight:bold; color:#2563eb;">₦{fixed_deposit_total:,.2f}</p>
                <p style="color:#6b7280;">You saved this across {fixed_deposit_count} transaction{'s.' if fixed_deposit_count != 1 else 'No Fixed Deposit savings made at all.'}</p>
                <p style="font-size:0.875rem; color:#6b7280;">With your recent save being ₦{latest_amount:,.2f} on {max_date_str}</p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            owealth_deposit = df.query("Description == 'OWealth Deposit(from Fixed)'")

            if not owealth_deposit.empty:
                total_owealth = owealth_deposit["Amount"].sum()
                profit_count = owealth_deposit.shape[0]
            else:
                profit = 0
                profit_count = 0
            profit = total_owealth - fixed_deposit_total

        
            st.markdown(f"""
            <div style="background:white; margin-top:1rem; padding:1rem; border-radius:1rem; text-align:center; 
                        box-shadow: 0 4px 6px rgba(0,0,0,0.1); border: 1px solid #e5e7eb;">
                <h4 style="font-size: 1rem; color:#374151;">💰 Profit from Fixed Deposits Savings</h4>
                <p style="font-size: 1.5rem; font-weight:bold; color:#16a34a;">₦{profit:,.2f}</p>
                <p style="font-size: 0.875rem; color:#6b7280; margin-top: -10px;">
                    You made profits totalling ₦{profit:,.2f} from your Fixed Deposits.
                </p>
                <p style="font-size:0.875rem; color:#6b7280;">The sum of your Fixed Deposits and the Profits are ₦{total_owealth:,.2f}</p>
            </div>
            """, unsafe_allow_html=True)

        rainbow_divider()
        rainbow_divider()
        
        fig = plot_main_category_bar(st.session_state.df)
        st.plotly_chart(fig, use_container_width=True)





elif app_pages == "Inflow Patterns":
    if not st.session_state.analyzed:
        st.warning("Please upload a bank statement first.")
    else: 
        if not st.session_state.analyzed:
            st.warning("Please upload a bank statement first.")
        else:
            wallet_df = st.session_state.wallet_df
            owealth_df = st.session_state.owealth_df
            df = st.session_state.full_df


            st.markdown("""
                <div style="margin-bottom: 3px; padding: 1rem 1.5rem; background-color: #ecfdf5; border-left: 4px solid #10b981; border-radius: 8px;">
                    <h2 style="margin-bottom: 0.5rem;">Inflow Patterns 💴💵💷💶</h2>
                    <p style="margin: 0;">
                        This section gives you a clear view of your <strong>money sources</strong> – 
                        <strong>where</strong> your money comes from, <strong>how often</strong> it comes in, and <strong>when</strong> you tend to receive it the most. 
                        Understanding your inflow patterns can help you plan, save, and grow your finances better.
                    </p>
                </div>
            """, unsafe_allow_html=True)
            rainbow_divider()

            top_inflow_amount = st.selectbox("Showing Top Inflow categories:", [5, 10, 20, 30, 50], index=1)
            fig = plot_top_inflow_categories(st.session_state.df, top_n=top_inflow_amount)
            st.plotly_chart(fig, use_container_width=True)

            rainbow_divider()

            top_inflow_count = st.selectbox("Showing Top Inflow based on Number of Trasactions:", [5, 10, 20, 30, 50, 70], index=1)
            fig = plot_top_inflow_count(st.session_state.df, top_n=top_inflow_count)
            st.plotly_chart(fig, use_container_width=True)

            rainbow_divider()

            top_sender_inflow = st.selectbox("Select Top Senders", [5, 10, 20, 30, 50, 100], index=1)
            fig = plot_transfer_inflow_from_sender(st.session_state.df, top_n=top_sender_inflow)
            st.plotly_chart(fig, use_container_width=True)

            rainbow_divider()

            fig = plot_monthly_inflow_and_count(st.session_state.df)
            st.plotly_chart(fig, use_container_width=True)

        
            avg_inflow_per_month = (st.session_state.df[st.session_state.df["Type"] == "Credit"].groupby("MonthYear")["Amount"].sum()).mean()
            st.markdown(f"""
                <div style="background:white; margin-top:1rem; padding:1.5rem; border-radius:1rem; text-align:center;
                            box-shadow: 0 4px 6px rgba(0,0,0,0.1); border: 1px solid #e5e7eb;">
                    <h4 style="font-size: 1rem; color:#374151;">📈 Average Monthly Inflow</h4>
                    <p style="font-size: 1.8rem; font-weight:bold; color:#2563eb;">₦{avg_inflow_per_month:,.2f}</p>
                    <p style="font-size:0.875rem; color:#6b7280;">On average, you receive the above amount of money each month based on your records.</p>
                </div>
            """, unsafe_allow_html=True)




elif app_pages == "Outflow Patterns":
        if not st.session_state.analyzed:
            st.warning("Please upload a bank statement first.")
        else: 
            st.markdown("""
                <div style="margin-bottom: 3px; padding: 1rem 1.5rem; background-color: #fef2f2; border-left: 4px solid #dc2626; border-radius: 8px;">
                    <h2 style="margin-bottom: 0.5rem;">Outflow Patterns 💸</h2>
                    <p style="margin: 0;">
                        This section reveals your <strong>spending habits</strong> – 
                        <strong>where</strong> your money goes, <strong>how frequently</strong> you spend, and <strong>when</strong> your expenses peak. 
                        Recognizing your outflow patterns helps you manage costs, reduce waste, and make smarter financial decisions.
                    </p>
                </div>
            """, unsafe_allow_html=True)

            rainbow_divider()


            top_cat_n = st.selectbox("Showing Top Outflow streams:", [5, 10, 20, 30, 50], index=1)
            fig = plot_top_outflow_categories(st.session_state.df, top_n=top_cat_n)
            st.plotly_chart(fig, use_container_width=True)

            rainbow_divider()

            rep_top_n = st.selectbox("View Top Outgoing Bank Transfer Recipients", [3, 5, 10, 20, 25], index=1)
            st.plotly_chart(plot_transfer_to_recipients(st.session_state.df, top_n=rep_top_n))

            rainbow_divider()

            st.plotly_chart(plot_spending_by_channel(st.session_state.df))

            rainbow_divider()

            st.plotly_chart(plot_monthly_outflow_and_count(st.session_state.df))

            avg_outflow_per_month = (
                st.session_state.df[st.session_state.df["Type"] == "Debit"]
                .groupby("MonthYear")["Amount"]
                .sum()
            ).mean()

            st.markdown(f"""
                <div style="background:white; margin-top:1rem; padding:1.5rem; border-radius:1rem; text-align:center;
                            box-shadow: 0 4px 6px rgba(0,0,0,0.1); border: 1px solid #e5e7eb;">
                    <h4 style="font-size: 1rem; color:#374151;">📉 Average Monthly Outflow</h4>
                    <p style="font-size: 1.8rem; font-weight:bold; color:#dc2626;">₦{avg_outflow_per_month:,.2f}</p>
                    <p style="font-size:0.875rem; color:#6b7280;">On average, you spend the above amount of money each month based on your records.</p>
                </div>
            """, unsafe_allow_html=True)

    
            st.info("Below is a review of your Maximum Held Balance for each day in the statement's period")
            st.plotly_chart(balance_trend_chart(st.session_state.df))
            st.caption("Feel free to zoom in to any of our interactive charts above")
        
            rainbow_divider()

  
elif app_pages == "Detected Anomalies":
    if not st.session_state.analyzed:
        st.warning("Please upload a bank statement first.")
    else:
        st.markdown("""
        <div style="margin-bottom: 2rem; padding: 1.5rem; background: linear-gradient(135deg, #fee2e2 0%, #fef3c7 100%); border-radius: 12px; border-left: 6px solid #dc2626;">
            <h1 style="margin: 0; color: #dc2626; font-size: 1.8rem;">🚨Detected Anomalies 🚨</h1>
            <p style="margin: 0.5rem 0 0 0; color: #666; font-size: 1rem;">
                This section highlights <strong>unusual financial activities</strong> across your transactions.<br> 
                It uses machine learning to detect patterns that differ significantly from your usual behavior — including rare amounts, abnormal channels, or unexpected timing.
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Enhanced CSS
        st.markdown("""
        <style>
            .risk-high {
                background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
                border-left: 5px solid #dc2626;
                border-radius: 12px;
                padding: 1.5rem;
                margin: 1rem 0;
                box-shadow: 0 4px 6px rgba(220, 38, 38, 0.1);
            }
            .risk-medium {
                background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
                border-left: 5px solid #f59e0b;
                border-radius: 12px;
                padding: 1.5rem;
                margin: 1rem 0;
                box-shadow: 0 4px 6px rgba(245, 158, 11, 0.1);
            }
            .summary-card {
                background: white;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                padding: 1rem;
                text-align: center;
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            }
            .tag {
                background-color: #dc2626;
                color: white;
                padding: 0.25rem 0.5rem;
                border-radius: 4px;
                font-size: 0.8rem;
                margin: 0.25rem;
                display: inline-block;
            }
            .transaction-details {
                margin-bottom: 1rem;
            }
            .transaction-flags {
                margin-bottom: 1rem;
            }
            .transaction-reasons {
                margin-bottom: 1.5rem;
            }
            .transaction-actions {
                border-top: 1px solid #e5e7eb;
                padding-top: 1rem;
            }
        </style>
        """, unsafe_allow_html=True)

        @st.cache_data
        def analyze_transactions(df):
            """Focused anomaly detection - only genuine security concerns"""
            # Filter out OWealth transactions
            excluded_categories = ['OWealth Deposits', 'OWealth Interest']
            df_clean = df[~df['Main Category'].isin(excluded_categories)].copy()
            
            # Calculate dynamic thresholds based on actual data
            amounts = df_clean['Amount']
            
            # Statistical thresholds based on the data itself
            q95 = amounts.quantile(0.95)  # Top 5%
            q99 = amounts.quantile(0.99)  # Top 1%
            q999 = amounts.quantile(0.999)  # Top 0.1%
            
            user_patterns = {
                'total_transactions': len(df_clean),
                'max_single_transaction': amounts.max(),
                'data_span_days': (df_clean['Trans Time'].max() - df_clean['Trans Time'].min()).days,
                'median_amount': amounts.median(),
                'q95_threshold': q95,
                'q99_threshold': q99,
                'q999_threshold': q999
            }
            
            # Store suspicious transactions
            suspicious = []
            
            for idx, row in df_clean.iterrows():
                flags = []
                reasons = []
                risk_level = "🟢 NORMAL"
                
                amount = row['Amount']
                is_credit = row['Type'] == 'Credit'
                
                # 1. EXTREMELY large amounts (top 0.1%)
                if amount >= q999:
                    if is_credit:
                        flags.append("🚨 Massive Deposit")
                        reasons.append(f"Extremely large deposit of ₦{amount:,.2f} - this is in the top 0.1% of all your transactions")
                    else:
                        flags.append("🚨 Massive Payment")
                        reasons.append(f"Extremely large payment of ₦{amount:,.2f} - this is in the top 0.1% of all your transactions")
                    risk_level = "🔴 HIGH RISK"
                
                elif amount >= q99:  # Top 1%
                    if is_credit:
                        flags.append("💰 Very Large Deposit")
                        reasons.append(f"Very large deposit of ₦{amount:,.2f} - this is in the top 1% of your transactions")
                    else:
                        flags.append("💰 Very Large Payment")
                        reasons.append(f"Very large payment of ₦{amount:,.2f} - this is in the top 1% of your transactions")
                    risk_level = "🟡 UNUSUAL ACTIVITY"
                
                # 2. Very late night large transactions (11 PM - 6 AM)
                is_late_night = (row['Hour'] >= 23) or (row['Hour'] <= 6)
                if is_late_night and amount >= q95:
                    flags.append("🌙 Late Night Large Transaction")
                    reasons.append(f"Large transaction (₦{amount:,.2f}) at {row['Hour']:02d}:00 - unusual time for significant financial activity")
                    if risk_level == "🟢 NORMAL":
                        risk_level = "🟡 UNUSUAL ACTIVITY"
                
                # 3. Extremely high daily activity
                same_day = df_clean[df_clean['Date'] == row['Date']]
                daily_counts = df_clean.groupby('Date').size()
                q95_daily = daily_counts.quantile(0.95)
                
                if len(same_day) >= q95_daily * 2:
                    flags.append("🔄 Extremely High Activity")
                    reasons.append(f"{len(same_day)} transactions on this day - much higher than your typical busy day")
                    if risk_level == "🟢 NORMAL":
                        risk_level = "🟡 UNUSUAL ACTIVITY"
                
                # 4. Rapid sequential large transactions
                transaction_time = row['Trans Time']
                nearby_transactions = df_clean[
                    (df_clean['Trans Time'] >= transaction_time - pd.Timedelta(minutes=5)) &
                    (df_clean['Trans Time'] <= transaction_time + pd.Timedelta(minutes=5)) &
                    (df_clean['Amount'] >= q95)
                ]
                if len(nearby_transactions) > 2:
                    flags.append("⚡ Rapid Large Transactions")
                    reasons.append(f"Multiple large transactions within 5 minutes")
                    if risk_level == "🟢 NORMAL":
                        risk_level = "🟡 UNUSUAL ACTIVITY"
                
                if flags:
                    suspicious.append({
                        'index': idx,
                        'transaction': row,
                        'risk_level': risk_level,
                        'flags': flags,
                        'reasons': reasons,
                        'risk_score': len(flags) + (2 if "🔴" in risk_level else 1 if "🟡" in risk_level else 0)
                    })
            
            return suspicious, user_patterns, len(df) - len(df_clean)

      
        with st.spinner("🔍 Analyzing your transactions for unusual activity..."):
            suspicious_transactions, patterns, excluded_count = analyze_transactions(st.session_state.df)

        # Summary Statistics
        total_analyzed = len(st.session_state.df) - excluded_count
        high_risk = len([t for t in suspicious_transactions if "🔴" in t['risk_level']])
        medium_risk = len([t for t in suspicious_transactions if "🟡" in t['risk_level']])
        original_count = len(suspicious_transactions)

        
        # Filter control
        st.markdown("### 🔍 Filter the Results below")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            risk_filter = st.selectbox("Risk Level", 
                ["All", "🔴 High Risk Only", "🟡 Medium Risk Only"],
                key="risk_filter")
        
        with col2:
            amount_min = st.number_input("Minimum Amount (₦)", 
                min_value=0, 
                value=0, 
                step=1000,
                key="amount_filter")
        
        with col3:
            max_display = st.slider("Max Transactions to Show", 
                min_value=5, 
                max_value=100, 
                value=20,
                key="max_display")
        
        # Apply filters
        filtered_transactions = suspicious_transactions.copy()
        
        # Risk level filter
        if risk_filter == "🔴 High Risk Only":
            filtered_transactions = [t for t in filtered_transactions if "🔴" in t['risk_level']]
        elif risk_filter == "🟡 Medium Risk Only":
            filtered_transactions = [t for t in filtered_transactions if "🟡" in t['risk_level']]
        
        # Amount filter
        if amount_min > 0:
            filtered_transactions = [t for t in filtered_transactions if t['transaction']['Amount'] >= amount_min]
        
        # Limit display
        suspicious_transactions = filtered_transactions[:max_display]
        
    
        if len(suspicious_transactions) != len(filtered_transactions):
            st.info(f"📊 Showing {len(suspicious_transactions)} of {len(filtered_transactions):,} total flagged transactions (filtered)")
        
        # Summary Cards
        st.markdown("### 📊 Summary")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="summary-card">
                <h3 style="margin: 0; color: #3b82f6;">{total_analyzed:,}</h3>
                <p style="margin: 0.5rem 0 0 0; color: #666;">Transactions Reviewed</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="summary-card">
                <h3 style="margin: 0; color: #dc2626;">{len(suspicious_transactions)}</h3>
                <p style="margin: 0.5rem 0 0 0; color: #666;">Showing Below</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="summary-card">
                <h3 style="margin: 0; color: #dc2626;">{high_risk}</h3>
                <p style="margin: 0.5rem 0 0 0; color: #666;">High Risk</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="summary-card">
                <h3 style="margin: 0; color: #f59e0b;">{medium_risk}</h3>
                <p style="margin: 0.5rem 0 0 0; color: #666;">Unusual Activity</p>
            </div>
            """, unsafe_allow_html=True)

        
        if suspicious_transactions:
            st.markdown(f"### 🚨 {len(suspicious_transactions)} transactions need your attention")
            st.markdown("**Review these transactions...**")
            
            # Sort by risk score
            suspicious_transactions.sort(key=lambda x: x['risk_score'], reverse=True)
            
            for i, item in enumerate(suspicious_transactions):
                row = item['transaction']
                risk_level = item['risk_level']
                flags = item['flags']
                reasons = item['reasons']
                
                # Card style
                if "🔴" in risk_level:
                    card_class = "risk-high"
                elif "🟡" in risk_level:
                    card_class = "risk-medium"
                else:
                    card_class = "risk-low"
                
                
                with st.container():
                    # Card headers
                    st.markdown(f"""
                    <div class="{card_class}">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                            <div>
                                <h3 style="margin: 0; color: {'#dc2626' if '🔴' in risk_level else '#f59e0b' if '🟡' in risk_level else '#16a34a'};">
                                    {risk_level}
                                </h3>
                                <p style="margin: 0.25rem 0 0 0; font-size: 0.9rem; color: #666;">
                                    Transaction #{i+1}
                                </p>
                            </div>
                            <div style="text-align: right;">
                                <h2 style="margin: 0; color: #1f2937;">₦{row['Amount']:,.2f}</h2>
                                <p style="margin: 0.25rem 0 0 0; font-size: 0.9rem; color: #666;">
                                    {row['Trans Time'].strftime('%b %d, %Y %I:%M %p')}
                                </p>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Transaction details
                    st.markdown(f"""
                    <div class="transaction-details">
                        <p style="margin: 0; font-size: 1rem;"><strong>📝 Description:</strong> {row.get('Description', 'N/A')}</p>
                        <p style="margin: 0.5rem 0; font-size: 1rem;"><strong>🏷️ Category:</strong> {row['Main Category']} • <strong>🏪 Channel:</strong> {row.get('Channel', 'N/A')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Tags
                    tags_html = ''.join([f'<span class="tag">{flag}</span>' for flag in flags])
                    st.markdown(f"""
                    <div class="transaction-flags">
                        {tags_html}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Reasons
                    reasons_html = '<br>'.join([f'• {reason}' for reason in reasons])
                    st.markdown(f"""
                    <div class="transaction-reasons">
                        <p style="margin: 0 0 0.5rem 0; font-weight: bold; color: #374151;">🚩 Why this was flagged:</p>
                        {reasons_html}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    rainbow_divider()
        
        else:
            # In absence of suspicious transactions
            st.markdown("""
            <div style="text-align: center; padding: 3rem 2rem; background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%); border-radius: 12px; border: 1px solid #bbf7d0;">
                <h2 style="color: #16a34a; margin-bottom: 1rem;">🎉 All Clear!</h2>
                <p style="font-size: 1.2rem; color: #374151; margin-bottom: 1rem;">
                    Great news! We didn't find any unusual activity in your transactions.
                </p>
                <p style="color: #6b7280; margin: 0;">
                    Your spending patterns look normal and consistent. We'll keep monitoring for you.
                </p>
            </div>
            """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 🛡️ Your Security Profile")
        
            st.markdown(f"""
            <div style="background: white; padding: 1.5rem; border-radius: 8px; border: 1px solid #e5e7eb;">
                <h4 style="margin: 0 0 1rem 0; color: #374151;">📊 Account Overview</h4>
                <p style="margin: 0.5rem 0;">📊 <strong>Total transactions:</strong> {patterns['total_transactions']:,}</p>
                <p style="margin: 0.5rem 0;">📅 <strong>Transaction period:</strong> {patterns['data_span_days']} days</p>
                <p style="margin: 0.5rem 0;">💰 <strong>Typical amount:</strong> ₦{patterns['median_amount']:,.0f}</p>
                <p style="margin: 0.5rem 0;">📈 <strong>Largest transaction:</strong> ₦{patterns['max_single_transaction']:,.0f}</p>
            </div>
            """, unsafe_allow_html=True)

            with st.expander("📊 Detection Thresholds (Based on Your Transaction data)"):
                st.write(f"**High Risk:** Transactions ≥ ₦{patterns['q999_threshold']:,.0f} (top 0.1%)")
                st.write(f"**Medium Risk:** Transactions ≥ ₦{patterns['q99_threshold']:,.0f} (top 1%)")
                st.write(f"**Large Amount:** Transactions ≥ ₦{patterns['q95_threshold']:,.0f} (top 5%)")
        

        with col2:
            # Recommendations
            st.header("")
            st.markdown("### 💡 Recommendations")
            
            recommendations = []
            
            if high_risk > 0:
                recommendations.append("🚨 **Immediate Action:** Review high-risk transactions above and confirm if they were made by you.")
            
    
            recommendations.append("📱 **Stay Protected:** Enable push notifications for instant alerts on suspicious activity.")
            
            for rec in recommendations:
                st.markdown(f"- {rec}")

    


elif app_pages == "FinSight AI":
    # Center everything
    st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
    
    # Main emoji and title
    st.markdown("# 🤖✨")
    st.markdown("# FinSight AI")
    st.markdown("## Your Intelligent Financial Assistant")
    
    # Coming Soon badge
    st.markdown("""
    <h2 style="background: linear-gradient(135deg, #ff6b6b, #ee5a24); 
               color: white; 
               padding: 1rem 2rem; 
               border-radius: 30px; 
               display: inline-block; 
               font-weight: bold;
               text-align: center;">
        🚀 COMING SOON
    </h2>
    """, unsafe_allow_html=True)
    
    # Description
    st.markdown("""
    ### Get ready for the most advanced AI-powered financial insights! 
    Chat with your data, discover hidden patterns, and receive personalized financial advice.
    """)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Feature cards using columns
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("## 💬")
        st.markdown("**Smart Chat**")
        st.caption("Ask questions about your finances in natural language")
    
    with col2:
        st.markdown("## 📊") 
        st.markdown("**Deep Analysis**")
        st.caption("Uncover hidden patterns in your spending")
    
    with col3:
        st.markdown("## 💡")
        st.markdown("**Personalized Tips**") 
        st.caption("Get tailored financial advice and recommendations")
    
    # Progress bar
    st.markdown("---")
    st.markdown("### 85% Complete • Expected Launch: Soon!")
    st.progress(0.85)
