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

import { CSSProperties } from "react"

import styled from "@emotion/styled"

import { EmotionThemeColors } from "~lib/theme/types"

export const Box = styled.div<{
  width?: CSSProperties["width"]
  height?: CSSProperties["height"]
}>(({ width = "100%", height }) => ({
  width,
  height,
}))

/**
 * Helper function to handle the border color for baseweb input widgets
 * @see Selectbox
 * @see Multiselect
 * @see DateInput
 * @see TimeInput
 * @see TextInput
 * @see TextArea
 * Note: NumberInput exhibits same styling but doesn't directly use this function -
 * border color is handled in StyledInputContainer instead of the baseweb overrides.
 */
export const getBorderColor = (
  colors: EmotionThemeColors,
  $isFocused: boolean
): string => {
  let borderColor = colors.widgetBorderColor ?? colors.secondaryBg
  if ($isFocused) {
    borderColor = colors.primary
  }
  return borderColor
}

/**
 * Helper function to get the long-hand border styles, which is required for baseweb components as short-hand border styles cause bugs and warnings
 * @param borderWidth Border width to be applied to all sides of the input widget
 * @param borderColor Border color to be applied to all sides of the input widget
 * @returns CSSProperties object containing the long-hand border styles to be applied to the input widget
 * @see getInputBorderStyles
 */
export const getLonghandBorderStyles = (
  borderWidth: CSSProperties["borderWidth"],
  borderColor: CSSProperties["borderColor"]
): CSSProperties => ({
  borderLeftWidth: borderWidth,
  borderRightWidth: borderWidth,
  borderTopWidth: borderWidth,
  borderBottomWidth: borderWidth,
  borderTopColor: borderColor,
  borderRightColor: borderColor,
  borderBottomColor: borderColor,
  borderLeftColor: borderColor,
})

/**
 * Helper function to get the border styles for baseweb input widgets
 * @param borderWidth Border width to be applied to all sides of the input widget
 * @param colors Emotion theme colors, used to determine the appropriate border color based on focus state
 * @param isFocused Whether the input widget is currently focused, used to determine the appropriate border color
 * @returns CSSProperties object containing the long-hand border styles to be applied to the input widget
 */
export const getInputBorderStyles = (
  borderWidth: CSSProperties["borderWidth"],
  colors: EmotionThemeColors,
  isFocused: boolean
): CSSProperties => {
  const borderColor = getBorderColor(colors, isFocused)

  // Baseweb requires long-hand props, short-hand leads to weird bugs & warnings.
  return getLonghandBorderStyles(borderWidth, borderColor)
}

interface ClearIconStyleTheme {
  colors: Pick<EmotionThemeColors, "grayTextColor" | "bodyText">
  spacing: {
    threeXS: CSSProperties["padding"]
  }
  sizes: {
    clearIconSize: CSSProperties["height"]
  }
}

type ClearIconSvgStyle = CSSProperties & {
  ":hover": {
    fill: CSSProperties["fill"]
  }
}

/**
 * Helper function to handle the shared styles for clear icons in baseweb input widgets
 * @param theme Theme object containing the necessary properties for styling the icon
 * @returns CSSProperties object with the styles for the clear icon, including a hover state
 */
export const getClearIconSvgStyle = (
  theme: ClearIconStyleTheme
): ClearIconSvgStyle => ({
  color: theme.colors.grayTextColor,
  // Setting this width and height makes the clear-icon align with dropdown arrows.
  padding: theme.spacing.threeXS,
  height: theme.sizes.clearIconSize,
  width: theme.sizes.clearIconSize,
  ":hover": {
    fill: theme.colors.bodyText,
  },
})
