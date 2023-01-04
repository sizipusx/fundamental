import pandas as pd
import pandas_profiling
import streamlit as st


uploaded_file = st.file_uploader('Choose a file')
if uploaded_file is not None:
    #read csv
    #df1=pd.read_csv(uploaded_file)
    try:
        #read xls or xlsx
        df=pd.read_excel(uploaded_file)
        st.write('Data uploaded successfully. These are the first 5 rows.')
        st.dataframe(df.head(5))
        pr = df.profile_report()
        st_profile_report(pr)
    except Exception as e:
            st.write(e)
else:
    st.warning("you need to upload a csv or excel file.")


