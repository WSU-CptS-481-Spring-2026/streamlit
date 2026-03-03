# Copyright (c) Streamlit Inc. (2018-2022) Snowflake Inc. (2022-2026)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import streamlit as st

st.set_page_config(layout="wide")

st.title("Checkbox Margin Consistency Fix")

st.markdown(
    """
This test verifies that checkboxes in horizontal containers have consistent
margins regardless of their position (first, middle, or last).
"""
)

# Test: Checkboxes in horizontal container
st.header("Checkboxes in Horizontal Container")
with st.container(horizontal=True):
    st.checkbox("Checkbox 1", key="horizontal_checkbox_1")
    st.checkbox("Checkbox 2", key="horizontal_checkbox_2")
    st.checkbox("Checkbox 3", key="horizontal_checkbox_3")

st.write(
    "Horizontal checkbox 1 state:", st.session_state.get("horizontal_checkbox_1", False)
)
st.write(
    "Horizontal checkbox 2 state:", st.session_state.get("horizontal_checkbox_2", False)
)
st.write(
    "Horizontal checkbox 3 state:", st.session_state.get("horizontal_checkbox_3", False)
)

# Test: Checkboxes in columns with different vertical alignments
st.header("Checkboxes in Columns with Different Vertical Alignments")

st.subheader("Top Alignment (default)")
cols_top = st.columns(2)
with cols_top[0]:
    st.write("Reference content")
with cols_top[1]:
    with st.container(horizontal=True):
        st.checkbox("Checkbox A", key="top_checkbox_a")
        st.checkbox("Checkbox B", key="top_checkbox_b")

st.subheader("Center Alignment")
cols_center = st.columns(2, vertical_alignment="center")
with cols_center[0]:
    st.write("Reference content")
with cols_center[1]:
    with st.container(horizontal=True):
        st.checkbox("Checkbox C", key="center_checkbox_c")
        st.checkbox("Checkbox D", key="center_checkbox_d")

st.subheader("Bottom Alignment")
cols_bottom = st.columns(2, vertical_alignment="bottom")
with cols_bottom[0]:
    st.write("Reference content")
with cols_bottom[1]:
    with st.container(horizontal=True):
        st.checkbox("Checkbox E", key="bottom_checkbox_e")
        st.checkbox("Checkbox F", key="bottom_checkbox_f")

# Test: Nested horizontal containers
st.header("Nested Horizontal Containers")
with st.container(horizontal=True):
    with st.container(horizontal=True):
        st.checkbox("Nested 1", key="nested_checkbox_1")
        st.checkbox("Nested 2", key="nested_checkbox_2")
    st.checkbox("Nested 3", key="nested_checkbox_3")

st.write("Nested checkbox 1 state:", st.session_state.get("nested_checkbox_1", False))
st.write("Nested checkbox 2 state:", st.session_state.get("nested_checkbox_2", False))
st.write("Nested checkbox 3 state:", st.session_state.get("nested_checkbox_3", False))
