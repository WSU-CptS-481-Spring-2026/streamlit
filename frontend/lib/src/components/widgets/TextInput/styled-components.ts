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

import styled from "@emotion/styled"

export const StyledTextInput = styled.div`
  position: relative;
`
export const StyledInputWrapper = styled.div`
  position: relative;
`

export const StyledPlaceholder = styled.div<{ hasIcon?: boolean }>(
  ({ theme, hasIcon }) => {
    const iconOffset = `${theme.spacing.sm} + ${theme.iconSizes.lg} + ${theme.spacing.md}`
    const leftPadding = hasIcon ? iconOffset : theme.spacing.md

    return {
      position: "absolute",
      top: "50%",
      transform: "translateY(-50%)",
      left: `calc(${theme.sizes.borderWidth} + ${leftPadding})`,
      right: `calc(${theme.sizes.borderWidth} + ${theme.spacing.sm})`,
      color: theme.colors.fadedText60,
      pointerEvents: "none",
      userSelect: "none",
      overflow: "hidden",
      whiteSpace: "nowrap",
      fontSize: theme.fontSizes.md, // Override isLabel's smaller font size to match input
    }
  }
)
