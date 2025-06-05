import streamlit as st
import pandas as pd
import datetime
from openai import OpenAI

st.set_page_config(page_title="Website Health Monitor", layout="centered")
st.title("📊 Website Health Monitor")
st.markdown("""
Upload your monthly website data from **Google Analytics, Search Console, ConvertKit**, or **Clarity**  
to receive a summarized AI-powered insight report + growth tip for your business.
""")

business_name = st.selectbox(
    "Select your business/client:",
    ["-- Select --", "LumelaWeb", "Client A", "Client B", "Other"]
)

def try_parse_csv(file):
    try:
        file.seek(0)
        return pd.read_csv(file)
    except:
        pass
    try:
        file.seek(0)
        return pd.read_csv(file, encoding='ISO-8859-1')
    except:
        pass
    try:
        file.seek(0)
        return pd.read_csv(file, sep=';', engine='python')
    except:
        pass
    try:
        file.seek(0)
        return pd.read_csv(file, sep='\t', engine='python')
    except:
        return None

st.subheader("📁 Upload Monthly CSV Data")
uploaded_file = st.file_uploader("Upload your combined CSV file", type="csv")

data = None
if uploaded_file:
    data = try_parse_csv(uploaded_file)
    if data is not None:
        st.success("✅ Data uploaded successfully!")
        st.dataframe(data.head())

        if st.button("🧠 Generate GPT Summary"):
            try:
                client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
                sample_data = data.head().to_string(index=False)

                prompt = f"""
You are a web analytics expert. This is a monthly performance report for a business named {business_name}.

Based on the following data:

{sample_data}

Please provide:
- 3 traffic or performance insights
- 1 issue or red flag
- 1 growth tip for next month

Use a warm, consultative tone that is easy to understand.
"""

                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}]
                )

                summary = response.choices[0].message.content

                st.subheader("💡 AI-Generated Insights")
                st.markdown(summary)

                st.download_button(
                    label="📄 Download Summary",
                    data=summary,
                    file_name=f"{business_name}_Health_Report_{datetime.date.today()}.txt",
                    mime="text/plain"
                )

            except Exception as e:
                st.error(f"❌ GPT-4 failed to generate summary: {e}")
    else:
        st.error("❌ Unable to parse this CSV. Please re-export as UTF-8 CSV from Excel or Google Sheets.")

st.subheader("🔗 Notion Dashboard (Optional)")
notion_link = st.text_input("Paste your Notion dashboard URL here:")
if notion_link:
    st.markdown(f"[→ View Dashboard]({notion_link})")

st.markdown("---")
st.caption("🛠️ Built by LumelaWeb • Powered by Streamlit & OpenAI")
