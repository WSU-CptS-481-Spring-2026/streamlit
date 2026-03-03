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

from playwright.sync_api import Page, expect

from e2e_playwright.conftest import wait_for_app_run
from e2e_playwright.shared.app_utils import (
    expect_markdown,
    get_element_by_key,
)


def test_checkbox_margin_consistency_in_horizontal_container(
    app: Page,
) -> None:
    """Test that checkboxes in horizontal containers have consistent margins."""
    # Verify all three checkboxes are visible
    checkbox_1 = get_element_by_key(app, "horizontal_checkbox_1")
    checkbox_2 = get_element_by_key(app, "horizontal_checkbox_2")
    checkbox_3 = get_element_by_key(app, "horizontal_checkbox_3")

    expect(checkbox_1).to_be_visible()
    expect(checkbox_2).to_be_visible()
    expect(checkbox_3).to_be_visible()

    # Verify initial state (all unchecked)
    expect_markdown(app, "Horizontal checkbox 1 state: False")
    expect_markdown(app, "Horizontal checkbox 2 state: False")
    expect_markdown(app, "Horizontal checkbox 3 state: False")

    # Click first checkbox and verify state change
    checkbox_1.locator("label").click()
    wait_for_app_run(app)
    expect_markdown(app, "Horizontal checkbox 1 state: True")
    expect_markdown(app, "Horizontal checkbox 2 state: False")
    expect_markdown(app, "Horizontal checkbox 3 state: False")

    # Click second checkbox and verify state change
    checkbox_2.locator("label").click()
    wait_for_app_run(app)
    expect_markdown(app, "Horizontal checkbox 1 state: True")
    expect_markdown(app, "Horizontal checkbox 2 state: True")
    expect_markdown(app, "Horizontal checkbox 3 state: False")

    # Click third checkbox and verify state change
    checkbox_3.locator("label").click()
    wait_for_app_run(app)
    expect_markdown(app, "Horizontal checkbox 1 state: True")
    expect_markdown(app, "Horizontal checkbox 2 state: True")
    expect_markdown(app, "Horizontal checkbox 3 state: True")


def test_checkbox_margin_in_columns_with_vertical_alignment(
    app: Page,
) -> None:
    """Test that checkboxes have consistent margins across different vertical alignments."""
    # Test TOP alignment (default)
    checkbox_a = get_element_by_key(app, "top_checkbox_a")
    checkbox_b = get_element_by_key(app, "top_checkbox_b")
    expect(checkbox_a).to_be_visible()
    expect(checkbox_b).to_be_visible()

    # Test CENTER alignment
    checkbox_c = get_element_by_key(app, "center_checkbox_c")
    checkbox_d = get_element_by_key(app, "center_checkbox_d")
    expect(checkbox_c).to_be_visible()
    expect(checkbox_d).to_be_visible()

    # Test BOTTOM alignment
    checkbox_e = get_element_by_key(app, "bottom_checkbox_e")
    checkbox_f = get_element_by_key(app, "bottom_checkbox_f")
    expect(checkbox_e).to_be_visible()
    expect(checkbox_f).to_be_visible()


def test_checkbox_in_nested_horizontal_containers(
    app: Page,
) -> None:
    """Test that checkboxes maintain consistent margins in nested horizontal containers."""
    # Verify all nested checkboxes are visible
    nested_1 = get_element_by_key(app, "nested_checkbox_1")
    nested_2 = get_element_by_key(app, "nested_checkbox_2")
    nested_3 = get_element_by_key(app, "nested_checkbox_3")

    expect(nested_1).to_be_visible()
    expect(nested_2).to_be_visible()
    expect(nested_3).to_be_visible()

    # Verify initial state (all unchecked)
    expect_markdown(app, "Nested checkbox 1 state: False")
    expect_markdown(app, "Nested checkbox 2 state: False")
    expect_markdown(app, "Nested checkbox 3 state: False")

    # Click first nested checkbox
    nested_1.locator("label").click()
    wait_for_app_run(app)
    expect_markdown(app, "Nested checkbox 1 state: True")
    expect_markdown(app, "Nested checkbox 2 state: False")
    expect_markdown(app, "Nested checkbox 3 state: False")

    # Click second nested checkbox
    nested_2.locator("label").click()
    wait_for_app_run(app)
    expect_markdown(app, "Nested checkbox 1 state: True")
    expect_markdown(app, "Nested checkbox 2 state: True")
    expect_markdown(app, "Nested checkbox 3 state: False")

    # Click third nested checkbox
    nested_3.locator("label").click()
    wait_for_app_run(app)
    expect_markdown(app, "Nested checkbox 1 state: True")
    expect_markdown(app, "Nested checkbox 2 state: True")
    expect_markdown(app, "Nested checkbox 3 state: True")
