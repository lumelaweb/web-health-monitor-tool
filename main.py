import streamlit as st
import pandas as pd
import datetime
from openai import OpenAI

st.set_page_config(page_title="Website Health Monitor", layout="centered")
st.title("📊 Website Health Monitor")

st.markdown("Upload your monthly GA4 or GSC CSV export directly—no editing needed. Get AI-powered summaries and actionable growth tips.")

business_name = st.text_input("Enter business or brand name")

uploaded_file = st.file_uploader("📁 Upload your GA4 or GSC .csv file", type="csv")

def try_parse_csv(file):
    try:
        lines = file.getvalue().decode('utf-8').splitlines()
        header_line_index = next((i for i, line in enumerate(lines) if not line.startswith("#") and "," in line), None)
        if header_line_index is None:
            return None
        file.seek(0)
        return pd.read_csv(file, skiprows=header_line_index)
    except:
        return None

def identify_report_type(df):
    cols = df.columns.str.lower().tolist()
    if "sessions" in cols and "users" in cols:
        return "GA4"
    if "query" in cols and "clicks" in cols:
        return "GSC"
    return "Unknown"

def format_prompt(business, df, report_type):
    preview = df.head(7).to_string(index=False)
    prompt = (
        f"Here is a {report_type} website report for a business named {business}.

"
        f"{preview}

"
        "Please provide:
"
        "- 3 insights about performance or trends
"
        "- 1 issue or red flag worth noting
"
        "- 1 growth suggestion for next month

"
        "Use a clear, encouraging tone suitable for a small business owner with limited technical knowledge."
    )
    return prompt

if uploaded_file and business_name:
    df = try_parse_csv(uploaded_file)
    if df is not None:
        df.columns = df.columns.str.strip()
        df = df.loc[:, ~df.columns.str.contains("^Unnamed")]

        report_type = identify_report_type(df)

        if report_type == "Unknown":
            st.error("❌ Unsupported report format. Please upload a GA4 or GSC .csv file.")
        else:
            st.success(f"✅ Detected report type: {report_type}")
            st.dataframe(df.head(10))

            if st.button("🧠 Generate Summary"):
                try:
                    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
                    prompt = format_prompt(business_name, df, report_type)

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
                        file_name=f"{business_name}_Insights_{datetime.date.today()}.txt",
                        mime="text/plain"
                    )
                except Exception as e:
                    st.error(f"❌ GPT generation failed: {e}")
    else:
        st.error("❌ Could not parse this file. Please try another GA4 or GSC .csv export.")
