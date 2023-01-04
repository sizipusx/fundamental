import pandas as pd
import pandas_profiling 
import streamlit as st

from streamlit_pandas_profiling import st_profile_report

@st.cache(allow_output_mutation=True)
def gen_profile_report(df, *report_args, **report_kwargs):
    return df.profile_report(*report_args, **report_kwargs)

uploaded_file = st.file_uploader('Choose a file')
if uploaded_file is not None:
    #read csv
    #df1=pd.read_csv(uploaded_file)
    try:
        #read xls or xlsx
        df=pd.read_excel(uploaded_file)
        st.write('Data uploaded successfully. These are the first 5 rows.')
        st.dataframe(df.head(5))
        pr = gen_profile_report(df, explorative=True)

        with st.expander("REPORT", expanded=True):
            st_profile_report(pr)
    except Exception as e:
            st.write(e)
else:
    st.warning("you need to upload a csv or excel file.")


