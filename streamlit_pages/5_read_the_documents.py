import os
import streamlit as st
from streamlit_common import _get_blob_for_session_data_logging

st.title('Documentation')



with st.sidebar:
    st.markdown('Thanks for reading the instructions. You are one of a small minority of people and you deserve a gold star!')



d = '''This Question Answering service is an example of **Retrieval Augmented Generation (RAG)**. It uses a Large Language Model to answer questions based on its reference material (see the [Table of Contents](table_of_content) page). This service is not official nor endorsed by any relevant authority. Its answers should be treated as guidance, not law. You should always read the references quoted in the answer to make sure they are appropriate.

The model works in two modes:
1. Strict RAG: Will only answer if it can use reference material to answer the question.
2. Permissive RAG: Will try to answer relevant questions even if it cannot find reference material.

Strict RAG is more accurate but also more likely not to answer the question. In slightly more technical terms, insisting on source reference material reduces false positives (answering a question incorrectly) while increasing false negatives (not answering a question that should have been answered). The key concept behind strict RAG is the 'R' (retrieval). Your question is used to search a database that consists of sections of the reference material. To ensure good retrieval, questions should be complete and specific. Strict RAG does not rely on the conversation history for context. The search step tries to match the exact wording of the question to relevant sections of the reference material. There is no way to make Strict RAG answer a question like "Can it be used in automated decision making?" without increasing the chance of false positives (trying to guess what "it" is using the conversation history).

While Strict RAG is the most accurate mode, it can make for a very stilted conversation, with the model frequently refusing to answer. Ideally, you should try a few different ways to phrase the question to see if you can get a more useful answer. For example, in an earlier version of this model, it would not answer the question "Can employers monitor employees' emails?" but would answer the question "Can employers monitor workers' emails?".

The goal is that over time, Strict RAG will become more user-friendly. When strange inconsistencies (like the employee/worker example above) are identified, they will be fixed. Over time, the source reference material can also be expanded. All of this, however, can only happen as users interact with the model and provide feedback.

At this stage, the source material is ONLY the regulation and the generally applicable guidelines documented <a href="https://www.edpb.europa.eu/our-work-tools/general-guidance/guidelines-recommendations-best-practices_en" target="_blank">here</a>. Country-specific guidance has not yet been added.

If you want to get some insight into how this app was built, have a look [here](https://www.aleph-one.co).

If you want to request specific features or source documentation to be added, reach out to me on <a href="https://www.linkedin.com/in/steven-davey-12295415" target="_blank">LinkedIn</a>.
'''

st.markdown(d, unsafe_allow_html=True)


