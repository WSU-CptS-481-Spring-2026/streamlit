/**
 * Copyright (c) Streamlit Inc. (2018-2022) Snowflake Inc. (2022-2026)
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import { mockTheme } from "~lib/mocks/mockTheme"

import {
  getClearIconSvgStyle,
  getInputBorderStyles,
  getLonghandBorderStyles,
} from "./styled-components"

describe("getInputBorderStyles", () => {
  it("returns longhand border styles with widget border color when not focused", () => {
    const styles = getInputBorderStyles(
      mockTheme.emotion.sizes.borderWidth,
      mockTheme.emotion.colors,
      false
    )

    expect(styles).toEqual({
      borderLeftWidth: mockTheme.emotion.sizes.borderWidth,
      borderRightWidth: mockTheme.emotion.sizes.borderWidth,
      borderTopWidth: mockTheme.emotion.sizes.borderWidth,
      borderBottomWidth: mockTheme.emotion.sizes.borderWidth,
      borderTopColor:
        mockTheme.emotion.colors.widgetBorderColor ??
        mockTheme.emotion.colors.secondaryBg,
      borderRightColor:
        mockTheme.emotion.colors.widgetBorderColor ??
        mockTheme.emotion.colors.secondaryBg,
      borderBottomColor:
        mockTheme.emotion.colors.widgetBorderColor ??
        mockTheme.emotion.colors.secondaryBg,
      borderLeftColor:
        mockTheme.emotion.colors.widgetBorderColor ??
        mockTheme.emotion.colors.secondaryBg,
    })
  })

  it("returns primary border colors when focused", () => {
    const styles = getInputBorderStyles(
      mockTheme.emotion.sizes.borderWidth,
      mockTheme.emotion.colors,
      true
    )

    expect(styles).toEqual({
      borderLeftWidth: mockTheme.emotion.sizes.borderWidth,
      borderRightWidth: mockTheme.emotion.sizes.borderWidth,
      borderTopWidth: mockTheme.emotion.sizes.borderWidth,
      borderBottomWidth: mockTheme.emotion.sizes.borderWidth,
      borderTopColor: mockTheme.emotion.colors.primary,
      borderRightColor: mockTheme.emotion.colors.primary,
      borderBottomColor: mockTheme.emotion.colors.primary,
      borderLeftColor: mockTheme.emotion.colors.primary,
    })
  })
})

describe("getLonghandBorderStyles", () => {
  it("returns longhand border styles using the provided border color", () => {
    const styles = getLonghandBorderStyles(
      mockTheme.emotion.sizes.borderWidth,
      mockTheme.emotion.colors.redTextColor
    )

    expect(styles).toEqual({
      borderLeftWidth: mockTheme.emotion.sizes.borderWidth,
      borderRightWidth: mockTheme.emotion.sizes.borderWidth,
      borderTopWidth: mockTheme.emotion.sizes.borderWidth,
      borderBottomWidth: mockTheme.emotion.sizes.borderWidth,
      borderTopColor: mockTheme.emotion.colors.redTextColor,
      borderRightColor: mockTheme.emotion.colors.redTextColor,
      borderBottomColor: mockTheme.emotion.colors.redTextColor,
      borderLeftColor: mockTheme.emotion.colors.redTextColor,
    })
  })
})

describe("getClearIconSvgStyle", () => {
  it("returns shared clear icon styles", () => {
    expect(getClearIconSvgStyle(mockTheme.emotion)).toEqual({
      color: mockTheme.emotion.colors.grayTextColor,
      padding: mockTheme.emotion.spacing.threeXS,
      height: mockTheme.emotion.sizes.clearIconSize,
      width: mockTheme.emotion.sizes.clearIconSize,
      ":hover": {
        fill: mockTheme.emotion.colors.bodyText,
      },
    })
  })
})
