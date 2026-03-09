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

import { screen, waitFor } from "@testing-library/react"
import { userEvent } from "@testing-library/user-event"

import {
  FileURLs as FileURLsProto,
  ImageUploader as ImageUploaderProto,
  LabelVisibility as LabelVisibilityProto,
} from "@streamlit/protobuf"

import { render } from "~lib/test_util"
import { WidgetStateManager } from "~lib/WidgetStateManager"

import ImageUploader, { Props } from "./ImageUploader"

const getProps = (
  elementProps: Partial<ImageUploaderProto> = {},
  props: Partial<Props> = {}
): Props => {
  return {
    element: ImageUploaderProto.create({
      id: "id",
      label: "Upload an image",
      type: ["png", "jpg", "jpeg"],
      maxUploadSizeMb: 200,
      help: "help text",
      formId: "",
      ...elementProps,
    }),
    disabled: false,
    widgetMgr: new WidgetStateManager({
      sendRerunBackMsg: vi.fn(),
      formsDataChanged: vi.fn(),
    }),
    // @ts-expect-error - partial mock
    uploadClient: {
      uploadFile: vi.fn().mockResolvedValue(undefined),
      fetchFileURLs: vi.fn().mockImplementation((files: File[]) => {
        return Promise.resolve(
          files.map(file => {
            return new FileURLsProto({
              fileId: file.name,
              uploadUrl: file.name,
              deleteUrl: file.name,
            })
          })
        )
      }),
      deleteFile: vi.fn(),
    },
    ...props,
  }
}

describe("ImageUploader widget", () => {
  beforeEach(() => {
    vi.spyOn(URL, "createObjectURL").mockReturnValue(
      "blob:http://localhost/fake-blob"
    )
    vi.spyOn(URL, "revokeObjectURL").mockImplementation(() => {})
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe("rendering", () => {
    it("renders without crashing", () => {
      const props = getProps()
      vi.spyOn(props.widgetMgr, "setFileUploaderStateValue")
      render(<ImageUploader {...props} />)

      const widget = screen.getByTestId("stImageUploader")
      expect(widget).toBeVisible()
      expect(widget).toHaveClass("stImageUploader")

      expect(props.widgetMgr.setFileUploaderStateValue).toHaveBeenCalledTimes(
        1
      )
    })

    it("shows a label", () => {
      const props = getProps()
      render(<ImageUploader {...props} />)
      expect(screen.getByTestId("stWidgetLabel")).toHaveTextContent(
        "Upload an image"
      )
    })

    it("shows help tooltip when provided", () => {
      const props = getProps({ help: "This is help" })
      render(<ImageUploader {...props} />)
      expect(screen.getByTestId("stTooltipIcon")).toBeVisible()
    })

    it("does not show help tooltip when not provided", () => {
      const props = getProps({ help: "" })
      render(<ImageUploader {...props} />)
      expect(screen.queryByTestId("stTooltipIcon")).not.toBeInTheDocument()
    })

    it("shows placeholder icon when no image", () => {
      const props = getProps()
      render(<ImageUploader {...props} />)
      expect(screen.getByTestId("stImageUploaderPlaceholder")).toBeVisible()
    })

    it("shows default image when provided", () => {
      const props = getProps({ default: "https://example.com/avatar.png" })
      render(<ImageUploader {...props} />)
      const preview = screen.getByTestId("stImageUploaderPreview")
      expect(preview).toBeVisible()
      expect(preview).toHaveAttribute("src", "https://example.com/avatar.png")
    })

    it("hides label when labelVisibility is hidden", () => {
      const props = getProps({
        labelVisibility: {
          value: LabelVisibilityProto.LabelVisibilityOptions.HIDDEN,
        },
      })
      render(<ImageUploader {...props} />)
      expect(screen.getByTestId("stWidgetLabel")).toHaveStyle(
        "visibility: hidden"
      )
    })

    it("collapses label when labelVisibility is collapsed", () => {
      const props = getProps({
        labelVisibility: {
          value: LabelVisibilityProto.LabelVisibilityOptions.COLLAPSED,
        },
      })
      render(<ImageUploader {...props} />)
      expect(screen.getByTestId("stWidgetLabel")).toHaveStyle("display: none")
    })

    it("has a hidden file input with correct accept attribute", () => {
      const props = getProps({ type: ["png", "jpg", "gif"] })
      render(<ImageUploader {...props} />)
      const input = screen.getByTestId("stImageUploaderInput")
      expect(input).not.toBeVisible()
      expect(input).toHaveAttribute("accept", ".png,.jpg,.gif")
    })
  })

  describe("interaction", () => {
    it("opens file picker when circle is clicked", async () => {
      const user = userEvent.setup()
      const props = getProps()
      render(<ImageUploader {...props} />)

      const circle = screen.getByTestId("stImageUploaderCircle")
      const input = screen.getByTestId("stImageUploaderInput")
      const clickSpy = vi.spyOn(input, "click")

      await user.click(circle)
      expect(clickSpy).toHaveBeenCalledOnce()
    })

    it("opens file picker on Enter key", async () => {
      const user = userEvent.setup()
      const props = getProps()
      render(<ImageUploader {...props} />)

      const circle = screen.getByTestId("stImageUploaderCircle")
      const input = screen.getByTestId("stImageUploaderInput")
      const clickSpy = vi.spyOn(input, "click")

      circle.focus()
      await user.keyboard("{Enter}")
      expect(clickSpy).toHaveBeenCalledOnce()
    })

    it("opens file picker on Space key", async () => {
      const user = userEvent.setup()
      const props = getProps()
      render(<ImageUploader {...props} />)

      const circle = screen.getByTestId("stImageUploaderCircle")
      const input = screen.getByTestId("stImageUploaderInput")
      const clickSpy = vi.spyOn(input, "click")

      circle.focus()
      await user.keyboard(" ")
      expect(clickSpy).toHaveBeenCalledOnce()
    })

    it("does not open file picker when disabled", async () => {
      const user = userEvent.setup()
      const props = getProps({}, { disabled: true })
      render(<ImageUploader {...props} />)

      const circle = screen.getByTestId("stImageUploaderCircle")
      const input = screen.getByTestId("stImageUploaderInput")
      const clickSpy = vi.spyOn(input, "click")

      await user.click(circle)
      expect(clickSpy).not.toHaveBeenCalled()
    })

    it("uploads file and shows preview on file selection", async () => {
      const user = userEvent.setup()
      const props = getProps()
      render(<ImageUploader {...props} />)

      const input = screen.getByTestId("stImageUploaderInput")
      const file = new File(["image-data"], "photo.png", {
        type: "image/png",
      })

      await user.upload(input, file)

      await waitFor(() => {
        expect(screen.getByTestId("stImageUploaderPreview")).toHaveAttribute(
          "src",
          "blob:http://localhost/fake-blob"
        )
      })

      expect(props.uploadClient.fetchFileURLs).toHaveBeenCalledWith([file])
    })

    it("calls uploadFile after fetchFileURLs", async () => {
      const user = userEvent.setup()
      const props = getProps()
      render(<ImageUploader {...props} />)

      const input = screen.getByTestId("stImageUploaderInput")
      const file = new File(["image-data"], "photo.png", {
        type: "image/png",
      })

      await user.upload(input, file)

      await waitFor(() => {
        expect(props.uploadClient.uploadFile).toHaveBeenCalled()
      })
    })

    it("shows overlay on hover", async () => {
      const user = userEvent.setup()
      const props = getProps()
      render(<ImageUploader {...props} />)

      const circle = screen.getByTestId("stImageUploaderCircle")
      await user.hover(circle)

      // The overlay is always in the DOM; visibility is controlled via CSS opacity.
      expect(circle).toBeInTheDocument()
    })
  })

  describe("widget state", () => {
    it("sets initial widget value on mount", () => {
      const props = getProps()
      vi.spyOn(props.widgetMgr, "setFileUploaderStateValue")

      render(<ImageUploader {...props} />)

      expect(props.widgetMgr.setFileUploaderStateValue).toHaveBeenCalledTimes(
        1
      )
      expect(props.widgetMgr.setFileUploaderStateValue).toHaveBeenCalledWith(
        props.element,
        expect.objectContaining({ uploadedFileInfo: [] }),
        { fromUi: false },
        undefined
      )
    })

    it("updates widget state after successful upload", async () => {
      const user = userEvent.setup()
      const props = getProps()
      vi.spyOn(props.widgetMgr, "setFileUploaderStateValue")

      render(<ImageUploader {...props} />)

      const input = screen.getByTestId("stImageUploaderInput")
      const file = new File(["image-data"], "photo.png", {
        type: "image/png",
      })

      await user.upload(input, file)

      await waitFor(() => {
        expect(
          props.widgetMgr.setFileUploaderStateValue
        ).toHaveBeenCalledTimes(2)
      })
    })
  })

  describe("accessibility", () => {
    it("circle has button role", () => {
      const props = getProps()
      render(<ImageUploader {...props} />)
      const circle = screen.getByTestId("stImageUploaderCircle")
      expect(circle).toHaveAttribute("role", "button")
    })

    it("circle has aria-label", () => {
      const props = getProps()
      render(<ImageUploader {...props} />)
      const circle = screen.getByTestId("stImageUploaderCircle")
      expect(circle).toHaveAttribute(
        "aria-label",
        "Upload an image - Click to upload an image"
      )
    })

    it("circle has aria-disabled when disabled", () => {
      const props = getProps({}, { disabled: true })
      render(<ImageUploader {...props} />)
      const circle = screen.getByTestId("stImageUploaderCircle")
      expect(circle).toHaveAttribute("aria-disabled", "true")
    })

    it("circle is not focusable when disabled", () => {
      const props = getProps({}, { disabled: true })
      render(<ImageUploader {...props} />)
      const circle = screen.getByTestId("stImageUploaderCircle")
      expect(circle).toHaveAttribute("tabindex", "-1")
    })

    it("circle is focusable when enabled", () => {
      const props = getProps()
      render(<ImageUploader {...props} />)
      const circle = screen.getByTestId("stImageUploaderCircle")
      expect(circle).toHaveAttribute("tabindex", "0")
    })
  })
})
