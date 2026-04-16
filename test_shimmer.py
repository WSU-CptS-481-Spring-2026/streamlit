import streamlit as st

st.title("Shimmer Directive Demo — Issue #13247")

st.markdown("---")

st.subheader("Inline usage")
st.markdown("Status: :shimmer[Fetching data from AI model...]")

st.subheader("Standalone")
st.markdown(":shimmer[Loading results...]")

st.subheader("Inside a heading")
st.markdown("## :shimmer[Dynamic Title]")

st.subheader("Inside bold text")
st.markdown("**:shimmer[Bold shimmer loading...]**")

st.subheader("Inside a blockquote")
st.markdown("> :shimmer[Streaming response from Claude...]")

st.subheader("Multiple shimmers")
st.markdown(":shimmer[First] and :shimmer[Second] loading simultaneously.")
