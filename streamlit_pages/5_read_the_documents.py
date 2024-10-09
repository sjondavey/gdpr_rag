import os
import streamlit as st
from streamlit_common import _get_blob_for_session_data_logging, setup_log_storage

st.title('Documentation')



with st.sidebar:
    st.markdown('Thanks for reading the instructions. You are one of a small minority of people and you deserve a gold star!')



d = '''This Question Answering service is an example of **Retrieval Augmented Generation (RAG)**. It uses a Large Language Model to answer questions based on its reference material (which you can see the in the Table of Contents page). This service is not official nor endorsed by anyone relevant. Its answers should be treated as guidance, not law. If you use these answers as the basis to perform an action and that action is illegal, there is nobody to sue or join with you in your court case. You will be on your own, with only your blind faith in Large Language Models for company. 

To reduce the chance of incorrect answers, a key feature of this service is its ability not to answer when it cannot find relevant source material (and ONLY the reference material). There may be times when this feature feels more like a bug. In those cases, there are a few things you can try:

- **Be realistic**: The source material is ONLY the regulation and the generally applicable guidelines documented <a href="https://www.edpb.europa.eu/our-work-tools/general-guidance/guidelines-recommendations-best-practices_en" target="_blank">here</a>)'. Country specific guidance can be added in time.

- **Ensure the question is complete**: If the question only makes sense in the context of the chat (e.g., "Can it be used in automated decision making?"), rephrase it as a complete question. For example, ask "Can special categories of personal data be used in automated decision-making?"


If you want to get some insight into how this app was built, have a look [here](https://www.aleph-one.co).

If you want to request specific features or source documentation get added, reach out to me on <a href="https://www.linkedin.com/in/steven-davey-12295415" target="_blank">linkedin</a>
'''

st.markdown(d, unsafe_allow_html=True)

