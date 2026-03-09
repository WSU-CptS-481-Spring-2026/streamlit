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
from streamlit import runtime

# 1 - Basic image uploader
uploaded = st.image_uploader("Upload a profile picture", key="basic_uploader")
if uploaded is not None:
    st.write("Uploaded file name:", uploaded.name)
else:
    st.write("No image uploaded")

# 2 - Disabled image uploader
st.image_uploader("Disabled uploader", key="disabled_uploader", disabled=True)

# 3 - Image uploader with help tooltip
st.image_uploader("With help", key="help_uploader", help="Upload a PNG or JPG image")

# 4 - Image uploader with custom types
st.image_uploader(
    "PNG only", key="png_only_uploader", type=["png"], help="Only PNG allowed"
)

# 5 - Image uploader with hidden label
st.image_uploader(
    "Hidden label uploader",
    key="hidden_label_uploader",
    label_visibility="hidden",
)

# 6 - Image uploader with collapsed label
st.image_uploader(
    "Collapsed label uploader",
    key="collapsed_label_uploader",
    label_visibility="collapsed",
)

# 7 - Image uploader inside a form
with st.form("image_form"):
    form_image = st.image_uploader("Form image", key="form_image_uploader")
    submitted = st.form_submit_button("Submit")
    if submitted and form_image is not None:
        st.write("Form uploaded:", form_image.name)
    elif submitted:
        st.write("Form submitted without image")
    else:
        st.write("Form not submitted")


# 8 - Image uploader inside a fragment
@st.fragment
def image_fragment():
    frag_image = st.image_uploader("Fragment image", key="fragment_image_uploader")
    if frag_image is not None:
        st.write("Fragment has image: True")
    else:
        st.write("Fragment has image: False")


image_fragment()

# 9 - Image uploader with specific width (pixels)
st.image_uploader("Width 200px", key="width_200_uploader", width=200)

# 10 - Image uploader with stretch width
st.image_uploader("Width stretch", key="width_stretch_uploader", width="stretch")

# 11 - Dynamic props via toggle
if st.toggle("Update image uploader props"):
    st.image_uploader(
        "Updated image uploader",
        key="dynamic_image_uploader",
        help="updated help",
        width=200,
        disabled=False,
    )
else:
    st.image_uploader(
        "Initial image uploader",
        key="dynamic_image_uploader",
        help="initial help",
        width="stretch",
        disabled=False,
    )

# 12 - Image uploader with callback
if runtime.exists():
    callback_count = st.session_state.get("callback_count", 0)
    st.write("Callback count:", callback_count)


def on_image_change():
    if runtime.exists():
        st.session_state["callback_count"] = (
            st.session_state.get("callback_count", 0) + 1
        )


st.image_uploader(
    "Callback uploader", key="callback_uploader", on_change=on_image_change
)
