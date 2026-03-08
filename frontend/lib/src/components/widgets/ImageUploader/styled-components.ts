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

export const StyledImageUploader = styled.div({
  width: "100%",
})

export interface StyledCircleContainerProps {
  disabled: boolean
}

export const StyledCircleContainer = styled.div<StyledCircleContainerProps>(
  ({ theme, disabled }) => ({
    position: "relative",
    width: theme.sizes.imageUploaderSize,
    height: theme.sizes.imageUploaderSize,
    borderRadius: "50%",
    overflow: "hidden",
    border: `${theme.sizes.borderWidth} solid ${theme.colors.borderColor}`,
    backgroundColor: theme.colors.secondaryBg,
    cursor: disabled ? "default" : "pointer",
    opacity: disabled ? 0.4 : 1,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    transition: "border-color 0.2s ease",
    ...(!disabled && {
      "&:hover": {
        borderColor: theme.colors.primary,
      },
    }),
  })
)

export const StyledPreviewImage = styled.img({
  width: "100%",
  height: "100%",
  objectFit: "cover",
})

export const StyledPlaceholderIcon = styled.div(({ theme }) => ({
  color: theme.colors.fadedText40,
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
}))

export interface StyledOverlayProps {
  isVisible: boolean
}

export const StyledOverlay = styled.div<StyledOverlayProps>(
  ({ theme, isVisible }) => ({
    position: "absolute",
    top: 0,
    left: 0,
    width: "100%",
    height: "100%",
    borderRadius: "50%",
    backgroundColor: theme.colors.darkenedBgMix100,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    color: theme.colors.white,
    opacity: isVisible ? 0.7 : 0,
    transition: "opacity 0.2s ease",
    pointerEvents: "none",
  })
)

export const StyledProgressContainer = styled.div(({ theme }) => ({
  position: "absolute",
  bottom: 0,
  left: 0,
  right: 0,
  padding: theme.spacing.twoXS,
}))
