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

from __future__ import annotations

from dataclasses import dataclass
from textwrap import dedent
from typing import TYPE_CHECKING, TypeAlias, cast

from streamlit import config
from streamlit.elements.lib.file_uploader_utils import (
    enforce_filename_restriction,
    normalize_upload_file_type,
)
from streamlit.elements.lib.form_utils import current_form_id
from streamlit.elements.lib.image_utils import AtomicImage, image_to_url
from streamlit.elements.lib.layout_utils import LayoutConfig, validate_width
from streamlit.elements.lib.policies import (
    check_widget_policies,
    maybe_raise_label_warnings,
)
from streamlit.elements.lib.utils import (
    Key,
    LabelVisibility,
    compute_and_register_element_id,
    get_label_visibility_proto_value,
    to_key,
)
from streamlit.elements.widgets.file_uploader import _get_upload_files
from streamlit.errors import StreamlitAPIException
from streamlit.proto.Common_pb2 import FileUploaderState as FileUploaderStateProto
from streamlit.proto.Common_pb2 import UploadedFileInfo as UploadedFileInfoProto
from streamlit.proto.ImageUploader_pb2 import ImageUploader as ImageUploaderProto
from streamlit.runtime.metrics_util import gather_metrics
from streamlit.runtime.scriptrunner import ScriptRunContext, get_script_run_ctx
from streamlit.runtime.state import (
    WidgetArgs,
    WidgetCallback,
    WidgetKwargs,
    register_widget,
)
from streamlit.runtime.uploaded_file_manager import DeletedFile, UploadedFile

if TYPE_CHECKING:
    from collections.abc import Sequence

    from streamlit.delta_generator import DeltaGenerator
    from streamlit.elements.lib.layout_utils import WidthWithoutContent

SomeUploadedImageFile: TypeAlias = UploadedFile | DeletedFile | None

# Default image types accepted by the image uploader.
_DEFAULT_IMAGE_TYPES: list[str] = ["png", "jpg", "jpeg", "gif", "webp", "svg"]


@dataclass
class ImageUploaderSerde:
    allowed_types: Sequence[str] | None = None

    def serialize(
        self,
        snapshot: SomeUploadedImageFile,
    ) -> FileUploaderStateProto:
        state_proto = FileUploaderStateProto()

        if snapshot is None or isinstance(snapshot, DeletedFile):
            return state_proto

        file_info: UploadedFileInfoProto = state_proto.uploaded_file_info.add()
        file_info.file_id = snapshot.file_id
        file_info.name = snapshot.name
        file_info.size = snapshot.size
        file_info.file_urls.CopyFrom(snapshot._file_urls)

        return state_proto

    def deserialize(
        self, ui_value: FileUploaderStateProto | None
    ) -> SomeUploadedImageFile:
        upload_files = _get_upload_files(ui_value)
        return_value = None if len(upload_files) == 0 else upload_files[0]
        if (
            return_value is not None
            and not isinstance(return_value, DeletedFile)
            and self.allowed_types
        ):
            enforce_filename_restriction(return_value.name, self.allowed_types)
        return return_value


class ImageUploaderMixin:
    @gather_metrics("image_uploader")
    def image_uploader(
        self,
        label: str,
        *,
        type: str | Sequence[str] | None = None,
        max_upload_size: int | None = None,
        default: AtomicImage | None = None,
        key: Key | None = None,
        help: str | None = None,
        on_change: WidgetCallback | None = None,
        args: WidgetArgs | None = None,
        kwargs: WidgetKwargs | None = None,
        disabled: bool = False,
        label_visibility: LabelVisibility = "visible",
        width: WidthWithoutContent = "stretch",
    ) -> UploadedFile | None:
        r"""Display an image uploader widget.

        This widget allows the user to upload an image by clicking on a
        circular preview area. It is designed for use cases like profile
        picture selection, avatar uploads, or any scenario where users need
        to upload a single image.

        Parameters
        ----------
        label : str
            A short label explaining to the user what this image uploader is
            for. The label can optionally contain GitHub-flavored Markdown of
            the following types: Bold, Italics, Strikethroughs, Inline Code,
            Links, and Images. Images display like icons, with a max height
            equal to the font height.

            For accessibility reasons, you should never set an empty label, but
            you can hide it with ``label_visibility`` if needed. In the future,
            we may disallow empty labels by raising an exception.

        type : str, list of str, or None
            The allowed image file extension(s) for uploaded images. This can
            be one of the following types:

            - ``None`` (default): Common image extensions are allowed
              (png, jpg, jpeg, gif, webp, svg).
            - A string: A single file extension is allowed. For example,
              ``"png"``.
            - A sequence of strings: Multiple file extensions are allowed.
              For example, ``["jpg", "jpeg", "png"]``.

        max_upload_size : int or None
            The maximum allowed size of the uploaded image in megabytes.

            If this is ``None`` (default), the maximum file size is set by the
            ``server.maxUploadSize`` configuration option.

        default : image or None
            An optional default/placeholder image to display before the user
            uploads an image. This can be anything accepted by ``st.image``:
            a file path, URL, numpy array, PIL Image, or raw bytes. If
            ``None`` (default), a generic placeholder icon is shown.

        key : str or int
            An optional string or integer to use as the unique key for the
            widget. If this is omitted, a key will be generated for the widget
            based on its content. No two widgets may have the same key.

        help : str or None
            A tooltip that gets displayed next to the widget label. Streamlit
            only displays the tooltip when ``label_visibility="visible"``. If
            this is ``None`` (default), no tooltip is displayed.

        on_change : callable
            An optional callback invoked when this image_uploader's value
            changes.

        args : list or tuple
            An optional list or tuple of args to pass to the callback.

        kwargs : dict
            An optional dict of kwargs to pass to the callback.

        disabled : bool
            An optional boolean that disables the image uploader if set to
            ``True``. The default is ``False``.

        label_visibility : "visible", "hidden", or "collapsed"
            The visibility of the label. The default is ``"visible"``. If this
            is ``"hidden"``, Streamlit displays an empty spacer instead of the
            label, which can help keep the widget aligned with other widgets.
            If this is ``"collapsed"``, Streamlit displays no label or spacer.

        width : "stretch" or int
            The width of the image uploader widget.

        Returns
        -------
        UploadedFile or None
            The uploaded image as an ``UploadedFile`` object, or ``None`` if
            no image has been uploaded.

        Examples
        --------
        >>> import streamlit as st
        >>>
        >>> uploaded_image = st.image_uploader("Upload a profile picture")
        >>> if uploaded_image is not None:
        ...     st.image(uploaded_image)

        """
        ctx = get_script_run_ctx()
        return self._image_uploader(
            label=label,
            type=type,
            max_upload_size=max_upload_size,
            default=default,
            key=key,
            help=help,
            on_change=on_change,
            args=args,
            kwargs=kwargs,
            disabled=disabled,
            label_visibility=label_visibility,
            width=width,
            ctx=ctx,
        )

    def _image_uploader(
        self,
        label: str,
        *,
        type: str | Sequence[str] | None = None,
        max_upload_size: int | None = None,
        default: AtomicImage | None = None,
        key: Key | None = None,
        help: str | None = None,
        on_change: WidgetCallback | None = None,
        args: WidgetArgs | None = None,
        kwargs: WidgetKwargs | None = None,
        disabled: bool = False,
        label_visibility: LabelVisibility = "visible",
        width: WidthWithoutContent = "stretch",
        ctx: ScriptRunContext | None = None,
    ) -> UploadedFile | None:
        key = to_key(key)

        if max_upload_size is not None and (
            not isinstance(max_upload_size, int) or max_upload_size <= 0
        ):
            raise StreamlitAPIException(
                "The `max_upload_size` parameter must be a positive integer "
                "representing the maximum file size in megabytes, or None "
                "to fall back to the `server.maxUploadSize` configuration option."
            )

        check_widget_policies(
            self.dg,
            key,
            on_change,
            default_value=None,
            writes_allowed=False,
        )
        maybe_raise_label_warnings(label, label_visibility)

        element_id = compute_and_register_element_id(
            "image_uploader",
            user_key=key,
            max_upload_size=max_upload_size,
            key_as_main_identity={"type", "max_upload_size"},
            dg=self.dg,
            label=label,
            type=type,
            help=help,
            width=width,
        )

        normalized_type = (
            normalize_upload_file_type(type)
            if type
            else normalize_upload_file_type(_DEFAULT_IMAGE_TYPES)
        )

        image_uploader_proto = ImageUploaderProto()
        image_uploader_proto.id = element_id
        image_uploader_proto.label = label
        image_uploader_proto.type[:] = normalized_type
        if max_upload_size is not None:
            image_uploader_proto.max_upload_size_mb = max_upload_size
        else:
            image_uploader_proto.max_upload_size_mb = config.get_option(
                "server.maxUploadSize"
            )
        image_uploader_proto.form_id = current_form_id(self.dg)
        image_uploader_proto.disabled = disabled
        image_uploader_proto.label_visibility.value = get_label_visibility_proto_value(
            label_visibility
        )

        if help is not None:
            image_uploader_proto.help = dedent(help)

        if default is not None:
            default_url = image_to_url(
                default,
                layout_config=LayoutConfig(width=width),
                clamp=False,
                channels="RGB",
                output_format="auto",
                image_id=f"{self.dg._get_delta_path_str()}-image_uploader-default",
            )
            image_uploader_proto.default = default_url

        serde = ImageUploaderSerde(allowed_types=normalized_type)

        widget_state = register_widget(
            image_uploader_proto.id,
            on_change_handler=on_change,
            args=args,
            kwargs=kwargs,
            deserializer=serde.deserialize,
            serializer=serde.serialize,
            ctx=ctx,
            value_type="file_uploader_state_value",
        )

        validate_width(width)
        layout_config = LayoutConfig(width=width)

        self.dg._enqueue(
            "image_uploader", image_uploader_proto, layout_config=layout_config
        )

        if isinstance(widget_state.value, DeletedFile):
            return None
        return widget_state.value

    @property
    def dg(self) -> DeltaGenerator:
        """Get our DeltaGenerator."""
        return cast("DeltaGenerator", self)
