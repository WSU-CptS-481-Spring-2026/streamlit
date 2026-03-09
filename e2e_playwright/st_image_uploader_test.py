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

from playwright.sync_api import FilePayload, Page, expect

from e2e_playwright.conftest import ImageCompareFunction, wait_for_app_run
from e2e_playwright.shared.app_utils import (
    check_top_level_class,
    click_toggle,
    expect_help_tooltip,
    expect_prefixed_markdown,
    get_element_by_key,
    get_image_uploader,
)

# Minimal valid 1x1 red PNG (67 bytes).
_PNG_BYTES = (
    b"\x89PNG\r\n\x1a\n"  # signature
    b"\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02"
    b"\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx"
    b"\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18\xd8N"
    b"\x00\x00\x00\x00IEND\xaeB`\x82"
)

NUM_IMAGE_UPLOADERS = 12


def _upload_image_to(app: Page, label: str):
    """Helper: trigger the hidden file input on an image uploader and upload a PNG."""
    el = get_image_uploader(app, label)
    circle = el.get_by_test_id("stImageUploaderCircle")
    expect(circle).to_be_visible()

    with app.expect_file_chooser() as fc_info:
        circle.click()
    file_chooser = fc_info.value
    file_chooser.set_files(
        files=[
            FilePayload(name="test_image.png", mimeType="image/png", buffer=_PNG_BYTES)
        ]
    )
    wait_for_app_run(app)


# ---------------------------------------------------------------------------
# Visual / rendering tests
# ---------------------------------------------------------------------------


def test_displays_correct_number_of_elements(app: Page):
    """Test that the expected number of image uploader widgets are rendered."""
    uploaders = app.get_by_test_id("stImageUploader")
    expect(uploaders).to_have_count(NUM_IMAGE_UPLOADERS)


def test_check_top_level_class(app: Page):
    """Check that the top level class is correctly set."""
    check_top_level_class(app, "stImageUploader")


def test_placeholder_icon_is_shown_by_default(app: Page):
    """Test that the placeholder icon is visible when no image has been uploaded."""
    uploader = get_image_uploader(app, "Upload a profile picture")
    expect(uploader.get_by_test_id("stImageUploaderPlaceholder")).to_be_visible()
    # Preview image must not be present
    expect(uploader.get_by_test_id("stImageUploaderPreview")).not_to_be_attached()


def test_snapshot_default_state(
    themed_app: Page,
    assert_snapshot: ImageCompareFunction,
):
    """Snapshot the image uploader in its default (empty) state."""
    uploader = get_image_uploader(themed_app, "Upload a profile picture")
    assert_snapshot(uploader, name="st_image_uploader-default")


def test_snapshot_disabled_state(
    themed_app: Page,
    assert_snapshot: ImageCompareFunction,
):
    """Snapshot the image uploader in the disabled state."""
    uploader = get_image_uploader(themed_app, "Disabled uploader")
    assert_snapshot(uploader, name="st_image_uploader-disabled")


def test_snapshot_hidden_label(app: Page, assert_snapshot: ImageCompareFunction):
    """Snapshot the image uploader with a hidden label."""
    uploader = get_element_by_key(app, "hidden_label_uploader")
    assert_snapshot(uploader, name="st_image_uploader-hidden_label")


def test_snapshot_collapsed_label(app: Page, assert_snapshot: ImageCompareFunction):
    """Snapshot the image uploader with a collapsed label."""
    uploader = get_element_by_key(app, "collapsed_label_uploader")
    assert_snapshot(uploader, name="st_image_uploader-collapsed_label")


# ---------------------------------------------------------------------------
# Interactivity tests
# ---------------------------------------------------------------------------


def test_upload_image_shows_preview(app: Page):
    """Test that uploading an image replaces the placeholder with a preview."""
    _upload_image_to(app, "Upload a profile picture")

    uploader = get_image_uploader(app, "Upload a profile picture")
    expect(uploader.get_by_test_id("stImageUploaderPreview")).to_be_visible()
    # Placeholder should be gone
    expect(uploader.get_by_test_id("stImageUploaderPlaceholder")).not_to_be_attached()


def test_upload_image_returns_value(app: Page):
    """Test that the uploaded file value is returned to the Streamlit app."""
    _upload_image_to(app, "Upload a profile picture")

    expect_prefixed_markdown(app, "Uploaded file name:", "test_image.png")


def test_disabled_uploader_cannot_be_clicked(app: Page):
    """Test that a disabled image uploader does not open a file chooser."""
    uploader = get_image_uploader(app, "Disabled uploader")
    circle = uploader.get_by_test_id("stImageUploaderCircle")
    expect(circle).to_have_attribute("aria-disabled", "true")


def test_snapshot_uploaded_state(app: Page, assert_snapshot: ImageCompareFunction):
    """Snapshot the image uploader after an image has been uploaded."""
    _upload_image_to(app, "Upload a profile picture")

    uploader = get_image_uploader(app, "Upload a profile picture")
    # Wait for the preview image to be stable
    expect(uploader.get_by_test_id("stImageUploaderPreview")).to_be_visible()
    assert_snapshot(uploader, name="st_image_uploader-uploaded")


# ---------------------------------------------------------------------------
# Help tooltip
# ---------------------------------------------------------------------------


def test_help_tooltip_is_displayed(app: Page):
    """Test that the help tooltip appears on hover."""
    uploader = get_image_uploader(app, "With help")
    expect_help_tooltip(app, uploader, "Upload a PNG or JPG image")


# ---------------------------------------------------------------------------
# Custom CSS class via key
# ---------------------------------------------------------------------------


def test_custom_css_class_via_key(app: Page):
    """Test that the element can have a custom css class via the key argument."""
    expect(get_element_by_key(app, "basic_uploader")).to_be_visible()


# ---------------------------------------------------------------------------
# Width variants
# ---------------------------------------------------------------------------


def test_width_200px(app: Page, assert_snapshot: ImageCompareFunction):
    """Snapshot the image uploader with a 200px width."""
    uploader = get_image_uploader(app, "Width 200px")
    assert_snapshot(uploader, name="st_image_uploader-width_200px")


def test_width_stretch(app: Page, assert_snapshot: ImageCompareFunction):
    """Snapshot the image uploader with stretch width."""
    uploader = get_image_uploader(app, "Width stretch")
    assert_snapshot(uploader, name="st_image_uploader-width_stretch")


# ---------------------------------------------------------------------------
# Form behaviour
# ---------------------------------------------------------------------------


def test_works_inside_form(app: Page):
    """Test that uploading an image inside a form sends data only on submit."""
    form_uploader = get_image_uploader(app, "Form image")
    circle = form_uploader.get_by_test_id("stImageUploaderCircle")

    with app.expect_file_chooser() as fc_info:
        circle.click()
    fc_info.value.set_files(
        files=[
            FilePayload(name="form_pic.png", mimeType="image/png", buffer=_PNG_BYTES)
        ]
    )
    wait_for_app_run(app)

    # The form has not been submitted yet - output should say "Form not submitted".
    expect(app.get_by_text("Form not submitted")).to_be_visible()

    # Submit the form
    app.get_by_test_id("stFormSubmitButton").first.locator("button").click()
    wait_for_app_run(app)

    expect(app.get_by_text("Form uploaded: form_pic.png")).to_be_visible()


# ---------------------------------------------------------------------------
# Fragment behaviour
# ---------------------------------------------------------------------------


def test_works_inside_fragment(app: Page):
    """Test that image uploader works correctly inside a fragment."""
    expect(app.get_by_text("Fragment has image: False")).to_be_visible()

    fragment_uploader = get_image_uploader(app, "Fragment image")
    circle = fragment_uploader.get_by_test_id("stImageUploaderCircle")

    with app.expect_file_chooser() as fc_info:
        circle.click()
    fc_info.value.set_files(
        files=[
            FilePayload(name="frag_pic.png", mimeType="image/png", buffer=_PNG_BYTES)
        ]
    )
    wait_for_app_run(app)

    expect(app.get_by_text("Fragment has image: True")).to_be_visible()


# ---------------------------------------------------------------------------
# Callback
# ---------------------------------------------------------------------------


def test_callback_is_triggered_on_upload(app: Page):
    """Test that the on_change callback fires when an image is uploaded."""
    expect_prefixed_markdown(app, "Callback count:", "0")

    _upload_image_to(app, "Callback uploader")

    expect_prefixed_markdown(app, "Callback count:", "1")


# ---------------------------------------------------------------------------
# Dynamic prop updates (identity via key)
# ---------------------------------------------------------------------------


def test_dynamic_props_update_while_keeping_key(app: Page):
    """Test that the image uploader retains its key-based identity when props change."""
    dynamic = get_element_by_key(app, "dynamic_image_uploader")
    expect(dynamic).to_be_visible()
    expect(dynamic).to_contain_text("Initial image uploader")

    # Check initial help tooltip
    uploader = dynamic.get_by_test_id("stImageUploader")
    expect_help_tooltip(app, uploader, "initial help")

    # Toggle to update props
    click_toggle(app, "Update image uploader props")

    expect(dynamic).to_contain_text("Updated image uploader")

    # Verify updated help tooltip
    expect_help_tooltip(app, uploader, "updated help")
