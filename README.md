# FinSight - Bank Statement Analyzer 📈

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org/)
[![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)](https://plotly.com/)

> **Analyze Bank Statements Effortlessly** - Upload your PDF bank statements and instantly visualize inflow & outflow trends, detect anomalies, and gain financial insights.

## 🚀 Features

### 📊 **inSight Model**
- **Financial Health Dashboard** - Quick overview of your financial status
- **Net Flow Analysis** - Track income vs expenses with smart insights
- **Interactive Date Filtering** - Analyze specific time periods
- **Key Financial Metrics** - Current balance, transaction counts, and spending patterns
- **Fixed Deposit Tracking** - Monitor your savings and profit calculations

### 💴 **Inflow Patterns**
- **Income Source Analysis** - Understand where your money comes from
- **Top Inflow Categories** - Visualize your main income streams
- **Transaction Frequency** - Track how often you receive money
- **Sender Analysis** - Identify top money senders
- **Monthly Trends** - Monitor income patterns over time

### 💸 **Outflow Patterns**
- **Spending Habit Analysis** - Detailed breakdown of your expenses
- **Category-wise Spending** - See where your money goes
- **Channel Analysis** - Track spending by payment method (ATM, POS, etc.)
- **Recipient Tracking** - Monitor outgoing bank transfers
- **Balance Trends** - Daily balance visualization

### 🚨 **Detected Anomalies**
- **Statistical Detection** - Quartile-based analysis identifies unusual patterns
- **Risk Assessment** - High-risk and unusual activity flagging
- **Late Night Transactions** - Detect suspicious timing (11 PM - 6 AM)
- **Large Amount Alerts** - Flag transactions in top 1% and 0.1%
- **Rapid Transaction Detection** - Identify multiple large transactions within minutes
- **Security Profile** - Personalized security overview and recommendations

### 🤖 **FinSight AI** (Coming Soon)
- **Smart Chat** - Ask questions about your finances in natural language
- **Deep Analysis** - Uncover hidden patterns in your spending
- **Personalized Tips** - Get tailored financial advice and recommendations

## 🏦 Supported Banks

- ✅ **OPay** - Full support for wallet and OWealth transactions
- 🚧 **GTBank** - Coming soon
- 🚧 **Zenith Bank** - Coming soon
- 🚧 **Kuda Bank** - Coming soon
- 🚧 **Access Bank** - Coming soon

## 📋 Requirements

```txt
streamlit>=1.28.0
PyMuPDF>=1.23.0
pandas>=2.0.0
plotly>=5.15.0
numpy>=1.24.0
streamlit-option-menu>=0.3.6
openpyxl>=3.1.0
```

## 🛠️ Installation

1. **Clone the repository:**
```bash
git clone https://github.com/GRIITTYY/finsight.git
cd finsight
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Run the application:**
```bash
streamlit run app.py
```

## 📁 Project Structure

```
finsight/
├── app.py                    # Main Streamlit application
├── plots.py                   # Visualization functions
├── requirements.txt           # Python dependencies
├── README.md                  # Project documentation
└── .gitignore                # Git ignore file
```

## 🔧 Usage

1. **Upload Statement**: Select OPay from the bank dropdown and upload your PDF statement
2. **Process Data**: The app automatically extracts and cleans transaction data
3. **Explore Insights**: Navigate through different pages to analyze your financial patterns:
   - **inSight Model** - Overview and key metrics
   - **Inflow Patterns** - Income analysis
   - **Outflow Patterns** - Spending analysis
   - **Detected Anomalies** - Security and fraud detection
4. **Download Data**: Export your processed data as Excel files

## 🎯 Key Capabilities

### Data Processing
- **PDF Parsing**: Extracts text from bank statement PDFs using PyMuPDF
- **Data Cleaning**: Handles date formatting, amount parsing, and transaction categorization
- **Error Handling**: Robust parsing with automatic error correction
- **Session Management**: Persistent data storage across page navigation

### Transaction Categorization
- **24 Categories**: Mobile data, card payments, transfers, utilities, and more
- **Smart Parsing**: Regex-based pattern matching for accurate categorization
- **Transfer Detection**: Automatic identification of incoming/outgoing transfers
- **Merchant Recognition**: Identifies common payment platforms and services

### Visualization
- **Interactive Charts**: Plotly-powered dashboards with zoom and filter capabilities
- **Responsive Design**: Mobile-friendly interface with wide layout support
- **Color-coded Insights**: Visual indicators for different transaction types and risk levels
- **Progressive Disclosure**: Expandable sections for detailed analysis

### Security Features
- **Privacy First**: No data collection or external processing
- **Local Processing**: All analysis happens on your device
- **Anomaly Detection**: Statistical analysis using dynamic thresholds
- **Risk Classification**: High, medium, and normal risk transaction flagging

## 📊 Analytics Features

### Statistical Analysis
- **Quartile Analysis**: Top 0.1%, 1%, and 5% transaction identification
- **Time-based Patterns**: Hour, day, and weekend spending analysis
- **Monthly Aggregation**: Period-based financial summaries
- **Trend Analysis**: Balance progression and spending velocity

### Rule-Based Detection
- **Dynamic Thresholds**: Personalized anomaly detection based on user patterns
- **Pattern Recognition**: Unusual timing, amount, and frequency detection
- **Risk Scoring**: Multi-factor risk assessment for transactions
- **Behavioral Analysis**: Spending habit profiling and deviation detection

## 🎨 User Interface

### Design System
- **Modern Gradient Themes**: Beautiful color schemes with proper contrast
- **Card-based Layout**: Clean, organized information presentation
- **Responsive Typography**: Readable fonts with proper hierarchy
- **Interactive Elements**: Hover effects and smooth transitions

### Navigation
- **Sidebar Menu**: Easy page switching with descriptive icons
- **State Management**: Seamless data persistence between pages
- **Progressive Loading**: Efficient data loading with caching
- **Beautiful HTML Cards**: Custom styled success, error, and warning messages

## 🔐 Privacy & Security

- **No Cloud Storage**: All data processing happens locally
- **No User Tracking**: Zero analytics or user behavior collection
- **Secure PDF Processing**: Safe handling of sensitive financial documents
- **Memory Management**: Proper cleanup of sensitive data after processing

## 🚀 Performance

- **Optimized Parsing**: Efficient PDF text extraction with error correction
- **Caching**: Smart data caching for improved responsiveness
- **Memory Efficient**: Proper resource management for large datasets
- **Fast Rendering**: Optimized Plotly charts with container width scaling

## 📞 Support & Contact

- **LinkedIn**: [Samuel O. Momoh](https://www.linkedin.com/in/samuel-o-momoh/)
- **Twitter**: [@griittyy](https://twitter.com/griittyy)
- **GitHub**: [GRIITTYY](https://github.com/GRIITTYY)

## 📄 License

This project is developed and maintained by Samuel O. Momoh (GRIITTYY).

## 🔄 Version History

- **v1.1.0** (Current) - Enhanced UI, anomaly detection, and comprehensive analytics
- **v1.0.0** - Initial release with basic OPay statement processing

## 🙏 Acknowledgments

- **Streamlit** - For the amazing web app framework
- **Plotly** - For interactive visualizations
- **PyMuPDF** - For PDF processing capabilities
- **OPay** - For providing detailed transaction data

---

<div align="center">

**FinSight** - Empowering financial literacy through intelligent bank statement analysis 💪📊

**Made with ❤️ by [GRIITTYY](https://github.com/GRIITTYY)**

*Transform your financial data into actionable insights today!*

⭐ **Star this repo if you found it helpful!** ⭐

</div>

---

*Built with ❤️ using Streamlit, Plotly, PyMuPDF, HTML, and CSS*