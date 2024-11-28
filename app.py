import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

def setup_page():
    st.set_page_config(
        page_title="Property Management System",
        layout="wide"
    )
    st.title("Property Management System")

def load_data():
    try:
        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/spreadsheets',
                 'https://www.googleapis.com/auth/drive']

        credentials = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=scope
        )

        client = gspread.authorize(credentials)
        spreadsheet_url = "https://docs.google.com/spreadsheets/d/1tdc4LriOTRz2LFfau72zgK32nPbpV78u3sO9enmTx8s/edit#gid=0"
        spreadsheet = client.open_by_url(spreadsheet_url)
        worksheet = spreadsheet.worksheet("Property Details")
        
        all_values = worksheet.get_all_values()
        headers = all_values[0]
        data = all_values[1:]
        df = pd.DataFrame(data, columns=headers)
        
        # Convert numeric columns
        numeric_columns = ["Area Sq.Mt", "Bhag Sq.Mt", "Percentage", "Aakar"]
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
        # Convert date column
        df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y', errors='coerce')
        
        return df

    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

def main():
    setup_page()
    
    # Add a refresh button
    if st.button("🔄 Refresh Data"):
        st.rerun()  # Updated from experimental_rerun()
    
    try:
        df = load_data()
        
        if df is not None and not df.empty:
            # Search functionality
            search_term = st.text_input("🔍 Search by Moje (Property Name) or Owner Name")
            
            # Filter data based on search
            filtered_df = df.copy()
            if search_term:
                search_term = search_term.lower()
                filtered_df = filtered_df[
                    filtered_df["Moje"].str.lower().str.contains(search_term, na=False) |
                    filtered_df["Owner Name"].str.lower().str.contains(search_term, na=False)
                ]
            
            # Remove Index Number column for display
            display_df = filtered_df.drop('Index Number', axis=1)
            
            # Display data
            st.dataframe(
                display_df,
                column_config={
                    "Moje": st.column_config.TextColumn("Moje"),
                    "Owner Name": st.column_config.TextColumn("Owner Name"),
                    "S.No": st.column_config.TextColumn("Survey No"),
                    "B.No": st.column_config.TextColumn("Block No"),
                    "F.P": st.column_config.TextColumn("F.P"),
                    "O.P": st.column_config.TextColumn("O.P"),
                    "Plot Number": st.column_config.TextColumn("Plot No"),
                    "Flat/Shop/Plot": st.column_config.TextColumn("Type"),
                    "Dastavej Number": st.column_config.TextColumn("Dastavej No"),
                    "Date": st.column_config.DateColumn("Date", format="DD/MM/YYYY"),
                    "Area Sq.Mt": st.column_config.NumberColumn("Area (Sq.Mt)", format="%.2f"),
                    "Bhag Sq.Mt": st.column_config.NumberColumn("Bhag (Sq.Mt)", format="%.2f"),
                    "Percentage": st.column_config.NumberColumn("Percentage", format="%.2f%%"),
                    "Aakar": st.column_config.NumberColumn("Aakar", format="%.2f")
                },
                hide_index=True,
                width=None
            )

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()