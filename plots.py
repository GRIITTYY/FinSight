import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def plot_main_category_bar(df):
    category_summary = (
        df.groupby("Main Category")["Amount"]
        .sum()
        .reset_index()
        .sort_values("Amount", ascending=True) 
        )

    fig = px.bar(
        category_summary,
        x="Amount",
        y="Main Category",
        text="Amount",
        labels={"Main Category": "Category", "Amount": "Total Amount (₦)"},
        title="Total Amount of Money per Category".upper(),
        color="Main Category",
        orientation='h'
    )

    fig.update_traces(
        texttemplate="₦%{x:,.2f}",
        textposition="outside",
        hovertemplate="<b>%{y}</b><br><b>Total Amont:</b> ₦%{x:,.2f}<extra></extra>"
    )

    fig.update_layout(
        hovermode="y unified",
        height=700,
        showlegend=False,
        title_font_size=30,
        yaxis_title=None,
    )

    return fig



def inflow_outflow_bar_chart(df):
    total_inflow = df["Inflow"].sum()
    total_outflow = df["Outflow"].sum()
    deficit = total_outflow - total_inflow

    data = {
        'Category': ['Inflow', 'Outflow'],
        'Amount': [total_inflow, total_outflow]
    }

    fig = px.bar(
        data, 
        x='Category', 
        y='Amount',
        color='Category',
        text=[f"₦{total_inflow:,.2f}", f"₦{total_outflow:,.2f}"],
        title='INFLOWs VS OUTFLOWS',
        color_discrete_map={
            'Inflow': '#2ecc71',
            'Outflow': '#e74c3c'
        }
    )

    fig.update_traces(
        textposition='auto',
        hovertemplate="<b>%{x}</b><br><b>Amount:</b> ₦%{y:,.2f}<extra></extra>"
    )


    if deficit > 0:
        fig.add_annotation(
            text=f"Deficit: ₦{deficit:,.2f}",
            x='Outflow',
            y=total_outflow + (deficit * 0.1),
            showarrow=True,
            arrowhead=2,
            font=dict(color="red", size=16),
            bgcolor="white",
            bordercolor="red"
        )

    elif deficit < 0:
        surplus = abs(deficit)
        fig.add_annotation(
            text=f"Surplus: ₦{surplus:,.2f}",
            x='Inflow',
            y=total_inflow + (surplus * 0.1),
            showarrow=True,
            arrowhead=2,
            font=dict(color="green", size=16),
            bgcolor="white",
            bordercolor="green"
        )

    else:
        fig.add_annotation(
            text="You broke even: Your Inflow = Your Outflow",
            x='Inflow',
            y=total_inflow * 1.05,
            showarrow=False,
            font=dict(color="blue", size=16),
            bgcolor="white",
            bordercolor="blue"
        )


    fig.update_layout(
        title_font_size=30,
        yaxis_title='Amount (₦)',
        xaxis_title='Category',
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False),
        hoverlabel=dict(
            font_size=16,
            bgcolor="white",
            font_color="black",
            bordercolor="blue",
            align="left"
        )
    )

    return fig

def plot_top_inflow_categories(df, top_n=10):
    df = df.query("Type == 'Credit'")

    grouped = (
        df.groupby("Category")["Amount"]
        .sum()
        .reset_index()
        .sort_values(by="Amount", ascending=False)
    )

    top_categories = grouped.head(top_n)

    fig = px.bar(
        top_categories,
        x="Amount",
        y="Category",
        color="Category",
        orientation="h", 
        title=f"Top {top_n} Inflow Streams".upper(),
        hover_data={"Amount": ":,.2f"},
        text_auto='.2s'
    )
    
    fig.update_traces(
    hovertemplate="<b>Category:</b> %{y}<br><b>Amount:</b> ₦%{x:,.2f}<extra></extra>"
)
    fig.update_layout(
        yaxis={"categoryorder": "total ascending"},
        title_font_size=30,
        yaxis_title=None,
        xaxis_title="Amount (NGN)",
        legend_title_text="Transaction Type",
        hoverlabel=dict(
            font_size=16,
            bgcolor="white",
            font_color="black",
            bordercolor="red",
            align="left"
        ), 
        showlegend=False,
        # hovermode="x"
)
    return fig

def plot_top_inflow_count(df, top_n=10):
    df = df.query("Type == 'Credit'")

    grouped = (
        df.groupby("Category")["Amount"]
        .count()
        .reset_index()
        .rename(columns={"Amount": "Number of Transactions"})
        .sort_values(by="Number of Transactions", ascending=True)
    )

    top_categories = grouped.tail(top_n)

    fig = px.bar(
        top_categories,
        x="Number of Transactions",
        y="Category",
        color="Category",
        orientation="h",
        title=f"Top {top_n} Inflow Streams by Number of Transactions".upper(),
        hover_data={"Number of Transactions": True},
        text_auto=True
    )

    fig.update_traces(
        hovertemplate="<b>Category:</b> %{y}<br><b>Number of Transactions:</b> %{x}<extra></extra>"
    )

    fig.update_layout(
        yaxis={"categoryorder": "total ascending"},
        title_font_size=30,
        yaxis_title=None,
        xaxis_title="Number of Transactions",
        legend_title_text="Transaction Type",
        hoverlabel=dict(
            font_size=16,
            bgcolor="white",
            font_color="black",
            bordercolor="red",
            align="left"
        ),
        showlegend=False,
    )

    return fig

def plot_monthly_inflow_and_count(df):
    df = df[df["Type"] == "Credit"]

    grouped = (
        df.groupby("MonthYear")
        .agg(Total_Inflow=("Amount", "sum"), Transaction_Count=("Amount", "count"))
        .reset_index()
        .sort_values("MonthYear")
    )

    grouped["Date_Str"] = grouped["MonthYear"].dt.strftime("%b %Y")

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=grouped["Date_Str"],
        y=grouped["Total_Inflow"],
        name="Total Inflow (₦)",
        marker_color="#2ca02c",
        hovertemplate="<b>Month:</b> %{x}<br><b>Total Inflow:</b> ₦%{y:,.2f}<extra></extra>"
    ))

    # Line for Transaction Count
    fig.add_trace(go.Scatter(
        x=grouped["Date_Str"],
        y=grouped["Transaction_Count"],
        mode="lines+markers",
        name="Number of Inflow Transactions",
        line=dict(color="#d62728", width=3, dash="dash"),
        hovertemplate="<b>Month:</b> %{x}<br><b>Number of Transactions:</b> %{y}<extra></extra>"
    ))

    fig.update_layout(
        title="Monthly Inflow and Number of Transactions".upper(),
        title_font_size=28,
        xaxis_title="Month",
        yaxis_title="Total Inflow (₦)",
        hovermode="x unified",
        barmode="overlay",
        legend=dict(title="Metrics"),
        margin=dict(l=60, r=40, t=60, b=60),
        font=dict(size=14),
        xaxis_tickangle=-45
    )

    return fig

def plot_transfer_inflow_from_sender(df, top_n=20):

    transfer_df = df[df["Description"].str.startswith("Transfer from", na=False)].copy()
    transfer_df["Sender"] = transfer_df["Description"].str.replace(r"^Transfer from\s+", "", regex=True)

    grouped = (
        transfer_df.groupby("Sender")["Amount"]
        .agg(["sum", "count"])
        .reset_index()
        .rename(columns={"sum": "Total Sent", "count": "Transaction Count"})
        .sort_values(by="Total Sent", ascending=False)
        .head(top_n)
    )

    fig = px.bar(
        grouped,
        x="Total Sent",
        y="Sender",
        orientation="h",
        title=f"Top {top_n} People Sending You Bank Transfers".upper(),
        hover_data={"Transaction Count": True, "Total Sent": ":,.2f"},
        color="Sender",
        text_auto='.2s'
    )

    fig.update_layout(
        title_font_size=26,
        xaxis_title="Total Sent (₦)",
        yaxis_title="Sender",
        showlegend=False,
        hoverlabel=dict(bordercolor="green"),
        margin=dict(l=100, r=40, t=60, b=60)
        # hovermode="x"
    )

    fig.update_traces(
        hovertemplate="<b>%{y}</b><br><b>Amount Received:</b> ₦%{x:,.2f}<br><b>Number of Transactions:</b> %{customdata[0]}",
        textfont_size=12, textangle=0, textposition="outside", cliponaxis=False
    )

    return fig






def plot_top_outflow_categories(df, top_n=10):
    df = df.query("Type == 'Debit'")
    
    grouped = (
        df.groupby("Category")["Amount"]
        .sum()
        .reset_index()
        .sort_values(by="Amount", ascending=False)
    )

    top_categories = grouped.head(top_n)

    fig = px.bar(
        top_categories,
        x="Amount",
        y="Category",
        color="Category",
        orientation="h", 
        title=f"Top {top_n} Outflow Streams".upper(),
        hover_data={"Amount": ":,.2f"},
        text_auto='.2s'
    )
    
    fig.update_traces(
    hovertemplate="<b>Category:</b> %{y}<br><b>Amount:</b> ₦%{x:,.2f}<extra></extra>"
)
    fig.update_layout(
        yaxis={"categoryorder": "total ascending"},
        title_font_size=30,
        yaxis_title=None,
        xaxis_title="Amount (NGN)",
        legend_title_text="Transaction Type",
        hoverlabel=dict(
            font_size=16,
            bgcolor="white",
            font_color="black",
            bordercolor="red",
            align="left"
        ), 
        showlegend=False,
        # hovermode="x"
)
    return fig

# Outgoing Transfer Recipients Plot
def plot_transfer_to_recipients(df, top_n=20):
    transfer_df = df[df["Description"].str.startswith("Transfer to", na=False)].copy()
    transfer_df["Recipient"] = transfer_df["Description"].str.replace(r"^Transfer to\s+", "", regex=True)

    grouped = (
        transfer_df.groupby("Recipient")["Amount"]
        .agg(["sum", "count"])
        .reset_index()
        .rename(columns={"sum": "Total Sent", "count": "Transaction Count"})
        .sort_values(by="Total Sent", ascending=False)
        .head(top_n)
    )

    fig = px.bar(
        grouped,
        x="Total Sent",
        y="Recipient",
        orientation="h",
        title=f"Top {top_n} Outgoing Bank Transfer Recipients".upper(),
        hover_data={"Transaction Count": True, "Total Sent": ":,.2f"},
        color="Recipient",
        text_auto='.2s'
    )

    fig.update_layout(
        title_font_size=29,
        xaxis_title="Total Sent (₦)",
        yaxis_title="Recipient",
        showlegend=False,
        hoverlabel=dict(bordercolor="red"),
        margin=dict(l=100, r=40, t=60, b=60),
        # hovermode="x"
    )

    fig.update_traces(
        hovertemplate="<b>%{y}</b><br><b>Amount Sent:</b> ₦%{x:,.2f}<br><b>Number of Transactions:</b> %{customdata[0]}",
        textfont_size=12, textangle=0, textposition="outside", cliponaxis=False
    )

    return fig

# Spending By Channel
def plot_spending_by_channel(df):

    debit_df = df[df["Type"] == "Debit"]
    
    grouped = (
        debit_df.groupby("Channel")["Amount"]
        .agg(["sum", "count"])
        .reset_index()
        .rename(columns={"sum": "Total Amount", "count": "Number of Transactions"})
        .sort_values(by="Total Amount", ascending=False)
    )
    
    fig = px.bar(
        grouped,
        x="Channel",
        y="Total Amount",
        title="Total Outflow by available Channels".upper(),
        color="Channel",
        text_auto='.2s',
        hover_data={"Number of Transactions": True, "Total Amount": ":,.2f"},
        labels={"Total Amount": "Total Spending (₦)", "Channel": "Transaction Channel"},
    )

    fig.update_layout(
        title_font_size=28,
        xaxis_title=None,
        yaxis_title="Total Spending (₦)",
        hoverlabel=dict(font_size=14, bgcolor="white", font_color="black"),
        hovermode="x"
    )
    
    fig.update_traces(hovertemplate="<b>%{x}</b><br><b>Amount:</b> ₦%{y:,.2f}<br><b>Number of Transactions:</b> %{customdata[0]}", 
                      textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)

    
    return fig


# Monthly Spending and Transaction Count
def plot_monthly_outflow_and_count(df):
    df = df[df["Type"] == "Debit"]

    grouped = (
        df.groupby("MonthYear")
        .agg(Total_Outflow=("Amount", "sum"), Transaction_Count=("Amount", "count"))
        .reset_index()
        .sort_values("MonthYear")
    )

    grouped["Date_Str"] = grouped["MonthYear"].dt.strftime("%b %Y")

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=grouped["Date_Str"],
        y=grouped["Total_Outflow"],
        name="Total Outflow (₦)",
        marker_color="#ef4444",  # Red shade for outflow
        hovertemplate="<b>Month:</b> %{x}<br><b>Total Outflow:</b> ₦%{y:,.2f}<extra></extra>"
    ))

    fig.add_trace(go.Scatter(
        x=grouped["Date_Str"],
        y=grouped["Transaction_Count"],
        mode="lines+markers",
        name="Number of Outflow Transactions",
        line=dict(color="#1d4ed8", width=3, dash="dash"),  # Blue line for count
        hovertemplate="<b>Month:</b> %{x}<br><b>Number of Transactions:</b> %{y}<extra></extra>"
    ))

    fig.update_layout(
        title="Monthly Outflow and Number of Transactions".upper(),
        title_font_size=28,
        xaxis_title="Month",
        yaxis_title="Total Outflow (₦)",
        hovermode="x unified",
        barmode="overlay",
        legend=dict(title="Metrics"),
        margin=dict(l=60, r=40, t=60, b=60),
        font=dict(size=14),
        xaxis_tickangle=-45
    )

    return fig



# Balanace Trend
def balance_trend_chart(df):
    daily_balance = (
        df.groupby("Date")["Balance"]
        .max()
        .reset_index()
        .sort_values("Date")
    )

    fig = px.bar(
        daily_balance,
        x="Date",
        y="Balance",
        title="Balance Trend".upper(),
        labels={"Date": "Date", "Balance": "Balance (₦)"},
    )

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Balance (₦)",
        title_font_size=25
    )

    fig.update_traces(
        hovertemplate="<b>Date: </b>%{x}<br><b>Maximun Balance Held: </b> ₦%{y:,.2f}"
    )

    return fig


# Sparkline under cards in Overview
def create_sparkline(df, y_col, line_color):
    fig = go.Figure(go.Scatter(
        x=df['Date'],
        y=df[y_col],
        mode='lines',
        line=dict(color=line_color, width=2),
        hovertemplate=f"<b>Date:</b> %{{x|%b %d, %Y}}<br><b>{y_col}:</b> ₦%{{y:,.2f}}<extra></extra>"
    ))
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        height=50,
        xaxis=dict(showgrid=False, visible=False),
        yaxis=dict(showgrid=False, visible=False),
    )
    return fig





