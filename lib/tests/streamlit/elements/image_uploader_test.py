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

"""image_uploader unit test."""

from unittest.mock import MagicMock, patch

import pytest
from parameterized import parameterized

import streamlit as st
from streamlit.elements.widgets.image_uploader import ImageUploaderSerde
from streamlit.errors import StreamlitAPIException, StreamlitInvalidWidthError
from streamlit.proto.Common_pb2 import FileURLs as FileURLsProto
from streamlit.proto.LabelVisibility_pb2 import LabelVisibility
from streamlit.runtime.uploaded_file_manager import (
    DeletedFile,
    UploadedFile,
    UploadedFileRec,
)
from tests.delta_generator_test_case import DeltaGeneratorTestCase
from tests.streamlit.elements.layout_test_utils import WidthConfigFields


class ImageUploaderTest(DeltaGeneratorTestCase):
    def test_just_label(self):
        """Test that it can be called with only a label."""
        st.image_uploader("the label")

        c = self.get_delta_from_queue().new_element.image_uploader
        assert c.label == "the label"
        assert (
            c.label_visibility.value == LabelVisibility.LabelVisibilityOptions.VISIBLE
        )

    def test_default_types(self):
        """Test that default image types are set when type is not provided."""
        st.image_uploader("the label")

        c = self.get_delta_from_queue().new_element.image_uploader
        # Should include common image types
        assert ".png" in list(c.type)
        assert ".jpg" in list(c.type)
        assert ".jpeg" in list(c.type)
        assert ".gif" in list(c.type)
        assert ".webp" in list(c.type)
        assert ".svg" in list(c.type)

    def test_custom_types(self):
        """Test that custom types override the defaults."""
        st.image_uploader("the label", type=["png", "jpg"])

        c = self.get_delta_from_queue().new_element.image_uploader
        type_list = list(c.type)
        assert ".png" in type_list
        assert ".jpg" in type_list
        # Should not include types not specified (apart from aliases)
        assert ".gif" not in type_list
        assert ".webp" not in type_list

    def test_help_tooltip(self):
        """Test that it can be called with help parameter."""
        st.image_uploader("the label", help="help_label")

        c = self.get_delta_from_queue().new_element.image_uploader
        assert c.help == "help_label"

    @parameterized.expand(
        [
            ("visible", LabelVisibility.LabelVisibilityOptions.VISIBLE),
            ("hidden", LabelVisibility.LabelVisibilityOptions.HIDDEN),
            ("collapsed", LabelVisibility.LabelVisibilityOptions.COLLAPSED),
        ]
    )
    def test_label_visibility(self, label_visibility_value, proto_value):
        """Test that it can be called with label_visibility parameter."""
        st.image_uploader("the label", label_visibility=label_visibility_value)

        c = self.get_delta_from_queue().new_element.image_uploader
        assert c.label_visibility.value == proto_value

    def test_label_visibility_wrong_value(self):
        """Test that an invalid label_visibility raises an error."""
        with pytest.raises(StreamlitAPIException) as e:
            st.image_uploader("the label", label_visibility="wrong_value")
        assert "Unsupported label_visibility option 'wrong_value'" in str(e.value)

    def test_cached_widget_replay_warning(self):
        """Test that a warning is shown when this widget is used inside a cached function."""
        st.cache_data(lambda: st.image_uploader("the label"))()

        # The widget itself is still created, so we need to go back one element more:
        el = self.get_delta_from_queue(-3).new_element.exception
        assert el.type == "CachedWidgetWarning"
        assert el.is_warning

    def test_invalid_max_upload_size(self):
        """Test that invalid max_upload_size values raise an error."""
        with pytest.raises(StreamlitAPIException):
            st.image_uploader("the label", max_upload_size=-1)

        with pytest.raises(StreamlitAPIException):
            st.image_uploader("the label", max_upload_size=0)

    def test_valid_max_upload_size(self):
        """Test that a valid max_upload_size is passed to the proto."""
        st.image_uploader("the label", max_upload_size=10)

        c = self.get_delta_from_queue().new_element.image_uploader
        assert c.max_upload_size_mb == 10

    def test_disabled(self):
        """Test that the disabled parameter is passed to the proto."""
        st.image_uploader("the label", disabled=True)

        c = self.get_delta_from_queue().new_element.image_uploader
        assert c.disabled is True

    def test_not_disabled_by_default(self):
        """Test that the widget is not disabled by default."""
        st.image_uploader("the label")

        c = self.get_delta_from_queue().new_element.image_uploader
        assert c.disabled is False

    @patch("streamlit.elements.widgets.image_uploader._get_upload_files")
    def test_invalid_file_extension_raises_exception(self, get_upload_files_patch):
        """Test that uploading a non-image file raises an exception."""
        rec = UploadedFileRec("file1", "file1.txt", "text/plain", b"123")
        uploaded_files = [
            UploadedFile(
                rec, FileURLsProto(file_id="file1", delete_url="d1", upload_url="u1")
            ),
        ]

        get_upload_files_patch.return_value = uploaded_files
        with pytest.raises(StreamlitAPIException) as e:
            st.image_uploader("label")
        assert "Invalid file extension" in str(e.value)

    def test_default_image_with_url(self):
        """Test that a default image URL is passed to the proto."""
        st.image_uploader("the label", default="https://example.com/image.png")

        c = self.get_delta_from_queue().new_element.image_uploader
        assert c.default == "https://example.com/image.png"

    def test_no_default_image(self):
        """Test that no default is set when not provided."""
        st.image_uploader("the label")

        c = self.get_delta_from_queue().new_element.image_uploader
        assert not c.HasField("default")


class ImageUploaderWidthTest(DeltaGeneratorTestCase):
    def test_with_width_pixels(self):
        """Test that image_uploader can be displayed with a specific width in pixels."""
        st.image_uploader("Label", width=500)
        c = self.get_delta_from_queue().new_element
        assert (
            c.width_config.WhichOneof("width_spec")
            == WidthConfigFields.PIXEL_WIDTH.value
        )
        assert c.width_config.pixel_width == 500

    def test_with_width_stretch(self):
        """Test that image_uploader can be displayed with a width of 'stretch'."""
        st.image_uploader("Label", width="stretch")
        c = self.get_delta_from_queue().new_element
        assert (
            c.width_config.WhichOneof("width_spec")
            == WidthConfigFields.USE_STRETCH.value
        )
        assert c.width_config.use_stretch

    def test_with_default_width(self):
        """Test that the default width is 'stretch'."""
        st.image_uploader("Label")
        c = self.get_delta_from_queue().new_element
        assert (
            c.width_config.WhichOneof("width_spec")
            == WidthConfigFields.USE_STRETCH.value
        )
        assert c.width_config.use_stretch

    @parameterized.expand(
        [
            "invalid",
            -1,
            0,
            100.5,
        ]
    )
    def test_width_config_invalid(self, invalid_width):
        """Test width config with various invalid values."""
        with pytest.raises(StreamlitInvalidWidthError):
            st.image_uploader("the label", width=invalid_width)

    def test_stable_id_with_key(self):
        """Test that the widget ID is stable when a stable key is provided."""
        with patch(
            "streamlit.elements.lib.utils._register_element_id",
            return_value=MagicMock(),
        ):
            st.image_uploader(
                "Label 1",
                key="image_uploader_key",
                help="Help 1",
                disabled=False,
                width="stretch",
                on_change=lambda: None,
                args=("arg1", "arg2"),
                kwargs={"kwarg1": "kwarg1"},
                label_visibility="visible",
            )
            c1 = self.get_delta_from_queue().new_element.image_uploader
            id1 = c1.id

            st.image_uploader(
                "Label 2",
                key="image_uploader_key",
                help="Help 2",
                disabled=True,
                width=200,
                on_change=lambda: None,
                args=("arg_1", "arg_2"),
                kwargs={"kwarg_1": "kwarg_1"},
                label_visibility="hidden",
            )
            c2 = self.get_delta_from_queue().new_element.image_uploader
            id2 = c2.id
            assert id1 == id2


class ImageUploaderSerdeTest(DeltaGeneratorTestCase):
    """Test ImageUploaderSerde serialization and deserialization."""

    def test_serialize_with_uploaded_file(self):
        """Test serialization of an uploaded image."""
        serde = ImageUploaderSerde()

        rec = UploadedFileRec("file123", "photo.png", "image/png", b"image_data")
        file_urls = FileURLsProto(
            file_id="file123", delete_url="delete_url", upload_url="upload_url"
        )
        uploaded_file = UploadedFile(rec, file_urls)

        result = serde.serialize(uploaded_file)

        assert len(result.uploaded_file_info) == 1
        file_info = result.uploaded_file_info[0]
        assert file_info.file_id == "file123"
        assert file_info.name == "photo.png"
        assert file_info.size == len(b"image_data")

    def test_serialize_with_none(self):
        """Test serialization when no image is uploaded."""
        serde = ImageUploaderSerde()
        result = serde.serialize(None)

        assert len(result.uploaded_file_info) == 0

    def test_serialize_with_deleted_file(self):
        """Test serialization with a deleted file."""
        serde = ImageUploaderSerde()
        deleted = DeletedFile("file123")
        result = serde.serialize(deleted)

        assert len(result.uploaded_file_info) == 0
