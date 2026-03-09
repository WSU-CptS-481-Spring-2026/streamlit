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
from streamlit.hello.utils import show_code


def anchors_disabled_demo() -> None:
    st.markdown("### My heading", anchors=False)


st.set_page_config(page_title="Anchors disabled demo")
st.title("Anchors disabled demo")
st.write(
    """
    This page helps test anchors being enabled or disabled for markdown files.
    """
)
anchors_disabled_demo()
show_code(anchors_disabled_demo)
