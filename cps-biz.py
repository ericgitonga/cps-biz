import streamlit as st
from google.oauth2 import service_account
from gsheetsdb import connect
import pandas as pd
import re

st.title("CPS Class of 1990 Business Directory")

credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
    ],
)

conn = connect(credentials=credentials)

# Perform SQL query on the Google Sheet.
# Uses st.cache to only rerun when the query changes or after 10 min.
@st.cache(ttl=600)
def run_query(query):
    rows = conn.execute(query, headers=1)
    rows = rows.fetchall()
    return rows

sheet_url = st.secrets["private_gsheets_url"]
rows = run_query(f'SELECT * FROM "{sheet_url}"')

df = pd.DataFrame(rows)
df.drop("Timestamp", axis="columns", inplace=True)

df["First_Name"] = df["First_Name"].apply(lambda x: x.capitalize())
df["Second_Name"] = df["Second_Name"].apply(lambda x: x.capitalize())
df["Email_Address"] = df["Email_Address"].apply(lambda x: x.lower())


# df["Website"] = df["Website"].apply(lambda x: x.replace())

name = df["First_Name"] + " " + df["Second_Name"]

df.drop(["First_Name", "Second_Name"], axis="columns", inplace=True)
df.insert(loc=0, column="name", value=name)
df.columns = ["Name", "Email", "Phone", "Website", "Offering"]
st.dataframe(df)
