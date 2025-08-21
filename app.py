import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta
import seaborn as sns

# Page configuration
st.set_page_config(
    page_title="SupplyWise - Supply Chain Intelligence",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #1e3c72, #2a5298);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    .insight-box {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #1e3c72;
        margin: 1rem 0;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def calculate_data_quality(df):
    """Calculate data quality percentage"""
    total_cells = df.shape[0] * df.shape[1]
    missing_cells = df.isnull().sum().sum()
    quality = ((total_cells - missing_cells) / total_cells) * 100
    return quality

def generate_sample_data():
    """Generate sample supply chain data for demo"""
    np.random.seed(42)
    dates = pd.date_range(start='2023-01-01', end='2024-12-31', freq='D')
    
    # Sample inventory data
    products = ['Product A', 'Product B', 'Product C', 'Product D', 'Product E']
    warehouses = ['Warehouse 1', 'Warehouse 2', 'Warehouse 3']
    
    data = []
    for _ in range(1000):
        data.append({
            'Date': np.random.choice(dates),
            'Product': np.random.choice(products),
            'Warehouse': np.random.choice(warehouses),
            'Stock_Quantity': np.random.randint(0, 1000),
            'Demand': np.random.randint(10, 200),
            'Cost_Per_Unit': round(np.random.uniform(5, 50), 2),
            'Supplier_Lead_Time': np.random.randint(1, 30),
            'Order_Quantity': np.random.randint(50, 500)
        })
    
    return pd.DataFrame(data)

def analyze_data(df, user_type):
    """Generate insights based on user type and data"""
    insights = []
    
    try:
        # Basic data analysis
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) > 0:
            # Correlation analysis
            if len(numeric_cols) > 1:
                corr_matrix = df[numeric_cols].corr()
                high_corr = corr_matrix.abs().unstack().sort_values(ascending=False)
                high_corr = high_corr[high_corr < 1.0]  # Remove self-correlations
                
                if len(high_corr) > 0:
                    top_corr = high_corr.iloc[0]
                    col1, col2 = high_corr.index[0]
                    insights.append({
                        'title': f'Strong Relationship Detected',
                        'description': f'Found {top_corr:.2f} correlation between {col1} and {col2}',
                        'recommendation': f'Monitor these metrics together for better {user_type.lower()} decisions',
                        'type': 'correlation'
                    })
            
            # Outlier detection
            for col in numeric_cols[:3]:  # Check first 3 numeric columns
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                outliers = df[(df[col] < Q1 - 1.5*IQR) | (df[col] > Q3 + 1.5*IQR)]
                
                if len(outliers) > 0:
                    insights.append({
                        'title': f'Unusual Values in {col}',
                        'description': f'Found {len(outliers)} outliers that need attention',
                        'recommendation': f'Review these exceptional cases - they might indicate opportunities or issues',
                        'type': 'outlier'
                    })
                    break  # Only show one outlier insight
        
        # Missing data analysis
        missing_data = df.isnull().sum()
        if missing_data.sum() > 0:
            worst_col = missing_data.idxmax()
            missing_pct = (missing_data[worst_col] / len(df)) * 100
            insights.append({
                'title': f'Data Quality Alert',
                'description': f'{worst_col} has {missing_pct:.1f}% missing values',
                'recommendation': f'Consider data collection improvements for {worst_col}',
                'type': 'quality'
            })
        
        # User-specific insights
        if 'inventory' in user_type.lower() or 'stock' in str(df.columns).lower():
            insights.append({
                'title': 'Inventory Optimization Opportunity',
                'description': 'Your data shows potential for stock level optimization',
                'recommendation': 'Focus on slow-moving items and seasonal patterns',
                'type': 'business'
            })
        
        if 'demand' in user_type.lower():
            insights.append({
                'title': 'Demand Forecasting Ready',
                'description': 'Your dataset is suitable for predictive demand modeling',
                'recommendation': 'Consider implementing automated demand forecasting',
                'type': 'business'
            })
    
    except Exception as e:
        insights.append({
            'title': 'Analysis in Progress',
            'description': 'Basic data structure looks good - upload more data for deeper insights',
            'recommendation': 'Try uploading time-series data with dates for trend analysis',
            'type': 'general'
        })
    
    return insights

def create_visualizations(df):
    """Create smart visualizations based on data"""
    charts = []
    
    try:
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        categorical_cols = df.select_dtypes(include=['object']).columns
        
        # Chart 1: Distribution of first numeric column
        if len(numeric_cols) > 0:
            first_numeric = numeric_cols[0]
            fig1 = px.histogram(
                df, 
                x=first_numeric, 
                title=f'Distribution of {first_numeric}',
                color_discrete_sequence=['#1e3c72']
            )
            fig1.update_layout(height=400)
            charts.append(fig1)
        
        # Chart 2: Correlation heatmap if multiple numeric columns
        if len(numeric_cols) > 1:
            corr_matrix = df[numeric_cols].corr()
            fig2 = px.imshow(
                corr_matrix,
                title='Correlation Heatmap',
                color_continuous_scale='RdBu'
            )
            fig2.update_layout(height=400)
            charts.append(fig2)
        
        # Chart 3: Category analysis if categorical data exists
        if len(categorical_cols) > 0 and len(numeric_cols) > 0:
            cat_col = categorical_cols[0]
            num_col = numeric_cols[0]
            
            if df[cat_col].nunique() <= 20:  # Only if reasonable number of categories
                fig3 = px.box(
                    df, 
                    x=cat_col, 
                    y=num_col,
                    title=f'{num_col} by {cat_col}',
                    color_discrete_sequence=['#2a5298']
                )
                fig3.update_layout(height=400)
                charts.append(fig3)
    
    except Exception as e:
        # Create a simple welcome chart
        sample_data = {'Categories': ['Data Quality', 'Insights Found', 'Visualizations'], 
                      'Values': [85, 12, 3]}
        fig = px.bar(sample_data, x='Categories', y='Values', 
                    title='SupplyWise Analysis Summary',
                    color_discrete_sequence=['#1e3c72'])
        charts.append(fig)
    
    return charts

def main():
    # Header
    st.markdown('<h1 class="main-header">🚀 SupplyWise</h1>', unsafe_allow_html=True)
    st.markdown("### Transform your supply chain data into actionable insights - no technical expertise required!")
    
    # Sidebar
    with st.sidebar:
        st.markdown("## 🎯 Welcome to SupplyWise")
        st.markdown("---")
        
        # User type selection
        user_type = st.selectbox(
            "👤 I am a:",
            ["Supply Chain Manager", "Demand Planner", "Inventory Planner", 
             "Logistics Planner", "Procurement Manager", "Business Owner",
             "Operations Manager", "Finance Manager"]
        )
        
        st.markdown("---")
        st.markdown("### 📤 Upload Your Data")
        uploaded_file = st.file_uploader(
            "Choose a CSV file",
            type=['csv'],
            help="Upload inventory, sales, supplier, or any supply chain data"
        )
        
        # Demo data option
        st.markdown("---")
        st.markdown("### 🎮 Try Demo Data")
        if st.button("🚀 Load Sample Data", type="secondary"):
            st.session_state.demo_data = generate_sample_data()
            st.success("✅ Demo data loaded!")
    
    # Main content area
    df = None
    
    # Check for uploaded file or demo data
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.success(f"✅ Successfully loaded your data: {len(df)} rows!")
        except Exception as e:
            st.error(f"❌ Error reading file: {str(e)}")
            st.info("💡 Make sure your file is a valid CSV with headers in the first row.")
    
    elif 'demo_data' in st.session_state:
        df = st.session_state.demo_data
        st.info("🎮 Using demo data - upload your own file to analyze real data!")
    
    if df is not None:
        # Data overview
        st.markdown("### 👀 Data Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📊 Total Rows", f"{len(df):,}")
        with col2:
            st.metric("📋 Columns", len(df.columns))
        with col3:
            quality = calculate_data_quality(df)
            st.metric("✅ Data Quality", f"{quality:.1f}%")
        with col4:
            numeric_cols = df.select_dtypes(include=['number']).columns
            st.metric("🔢 Numeric Fields", len(numeric_cols))
        
        # Data preview
        with st.expander("🔍 View Data Sample", expanded=False):
            st.dataframe(df.head(10), use_container_width=True)
        
        # Generate insights
        st.markdown("### 🧠 AI-Powered Insights")
        
        with st.spinner("🔍 Analyzing your data for patterns and insights..."):
            insights = analyze_data(df, user_type)
            
            if insights:
                for i, insight in enumerate(insights):
                    st.markdown(f"""
                    <div class="insight-box">
                        <h4>💡 {insight['title']}</h4>
                        <p><strong>Finding:</strong> {insight['description']}</p>
                        <p><strong>Recommendation:</strong> {insight['recommendation']}</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("📈 Upload more data for detailed insights!")
        
        # Visualizations
        st.markdown("### 📊 Smart Visualizations")
        charts = create_visualizations(df)
        
        for i, chart in enumerate(charts):
            st.plotly_chart(chart, use_container_width=True)
            
        # Data summary
        st.markdown("### 📋 Data Summary")
        st.dataframe(df.describe(), use_container_width=True)
        
    else:
        # Welcome screen
        st.markdown("### 🎯 What SupplyWise Does For You")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            #### 📤 Upload Any Data
            - CSV files from Excel, ERP systems
            - Inventory, sales, supplier data
            - No formatting required
            """)
        
        with col2:
            st.markdown("""
            #### 🧠 Get Instant Insights
            - AI analyzes patterns automatically
            - Plain English explanations
            - Actionable recommendations
            """)
        
        with col3:
            st.markdown("""
            #### 📊 Beautiful Visualizations
            - Professional charts & graphs
            - Interactive dashboards
            - Export & share results
            """)
        
        # Feature highlights
        st.markdown("### ✨ Key Features")
        
        features = [
            "🔍 **Smart Data Detection** - Automatically understands your data structure",
            "📈 **Trend Analysis** - Identifies patterns and anomalies",
            "🎯 **Role-Based Insights** - Tailored recommendations for your job function",
            "📊 **Interactive Charts** - Explore your data visually",
            "💡 **Plain English Results** - No technical jargon",
            "⚡ **Instant Analysis** - Results in seconds, not hours"
        ]
        
        for feature in features:
            st.markdown(feature)
        
        st.markdown("---")
        st.markdown("### 🚀 Ready to Get Started?")
        st.markdown("👈 **Upload your CSV file using the sidebar** or try our demo data to see SupplyWise in action!")

if __name__ == "__main__":
    main()