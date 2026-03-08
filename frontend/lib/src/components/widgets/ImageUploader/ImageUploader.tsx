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

import {
  memo,
  useCallback,
  useEffect,
  useLayoutEffect,
  useMemo,
  useRef,
  useState,
} from "react"

import {
  AddAPhoto,
  Image as ImageIcon,
} from "@emotion-icons/material-outlined"
import { isEqual } from "lodash-es"
import { flushSync } from "react-dom"

import {
  FileUploaderState as FileUploaderStateProto,
  FileURLs as FileURLsProto,
  IFileURLs,
  ImageUploader as ImageUploaderProto,
  UploadedFileInfo as UploadedFileInfoProto,
} from "@streamlit/protobuf"

import Icon from "~lib/components/shared/Icon"
import ProgressBar, { Size } from "~lib/components/shared/ProgressBar"
import {
  WidgetLabel,
  WidgetLabelHelpIcon,
} from "~lib/components/widgets/BaseWidget"
import {
  UploadedStatus,
  UploadFileInfo,
  UploadingStatus,
} from "~lib/components/widgets/FileUploader/UploadFileInfo"
import { useFormClearHelper } from "~lib/components/widgets/Form"
import { FileUploadClient } from "~lib/FileUploadClient"
import {
  isNullOrUndefined,
  labelVisibilityProtoValueToEnum,
} from "~lib/util/utils"
import { WidgetStateManager } from "~lib/WidgetStateManager"

import {
  StyledCircleContainer,
  StyledImageUploader,
  StyledOverlay,
  StyledPlaceholderIcon,
  StyledPreviewImage,
  StyledProgressContainer,
} from "./styled-components"

type FileUploaderStatus = "ready" | "updating"

export interface Props {
  element: ImageUploaderProto
  widgetMgr: WidgetStateManager
  uploadClient: FileUploadClient
  disabled: boolean
  fragmentId?: string
}

const toWidgetState = (
  targetFiles: UploadFileInfo[]
): FileUploaderStateProto => {
  const uploadedFileInfo: UploadedFileInfoProto[] = targetFiles
    .filter(f => f.status.type === "uploaded")
    .map(f => {
      const { name, size, status } = f
      const { fileId, fileUrls } = status as UploadedStatus

      return new UploadedFileInfoProto({
        fileId,
        fileUrls,
        name,
        size,
      })
    })

  return new FileUploaderStateProto({ uploadedFileInfo })
}

const createInitialFiles = (
  element: ImageUploaderProto,
  widgetMgr: WidgetStateManager
): { files: UploadFileInfo[]; nextLocalId: number; imgSrc: string | null } => {
  const widgetValue = widgetMgr.getFileUploaderStateValue(element)
  if (isNullOrUndefined(widgetValue)) {
    return { files: [], nextLocalId: 1, imgSrc: null }
  }

  const { uploadedFileInfo } = widgetValue
  if (isNullOrUndefined(uploadedFileInfo) || uploadedFileInfo.length === 0) {
    return { files: [], nextLocalId: 1, imgSrc: null }
  }

  let nextLocalId = 1
  const files = uploadedFileInfo.map(f => {
    const name = f.name as string
    const size = f.size as number
    const fileId = f.fileId as string
    const fileUrls = f.fileUrls as FileURLsProto

    const uploadFile = new UploadFileInfo(name, size, nextLocalId, {
      type: "uploaded",
      fileId,
      fileUrls,
    })
    nextLocalId += 1
    return uploadFile
  })

  return {
    files,
    nextLocalId,
    // When restoring from widget state, we don't have the object URL,
    // but we know there's an image. The actual preview won't be available
    // since we can't reconstruct object URLs from server-side files.
    // The user will see the placeholder or default until they upload again.
    imgSrc: null,
  }
}

/**
 * Construct the accept attribute for a file input from an array of extensions.
 */
const getAcceptString = (types: string[]): string =>
  types.map(t => (t.startsWith(".") ? t : `.${t}`)).join(",")

const ImageUploader = ({
  element,
  widgetMgr,
  uploadClient,
  disabled,
  fragmentId,
}: Props): React.ReactElement => {
  const fileInputRef = useRef<HTMLInputElement>(null)

  const initialStateRef = useRef<ReturnType<typeof createInitialFiles> | null>(
    null
  )
  if (initialStateRef.current === null) {
    initialStateRef.current = createInitialFiles(element, widgetMgr)
  }
  const {
    files: initialFiles,
    nextLocalId: initialNextLocalId,
    imgSrc: initialImgSrc,
  } = initialStateRef.current

  const localFileIdCounterRef = useRef(initialNextLocalId)

  const [files, setFiles] = useState(() => initialFiles)
  const filesRef = useRef(files)
  useLayoutEffect(() => {
    filesRef.current = files
  }, [files])

  const [imgSrc, setImgSrc] = useState<string | null>(() => initialImgSrc)
  const [isHovered, setIsHovered] = useState(false)

  const nextLocalFileId = useCallback((): number => {
    const id = localFileIdCounterRef.current
    localFileIdCounterRef.current += 1
    return id
  }, [])

  const status: FileUploaderStatus = useMemo(() => {
    if (files.some(file => file.status.type === "uploading")) {
      return "updating"
    }
    return "ready"
  }, [files])

  const progress: number | undefined = useMemo(() => {
    if (
      files.length > 0 &&
      files[files.length - 1].status.type === "uploading"
    ) {
      return (files[files.length - 1].status as UploadingStatus).progress
    }
    return undefined
  }, [files])

  const getFile = useCallback(
    (fileId: number): UploadFileInfo | undefined =>
      filesRef.current.find(file => file.id === fileId),
    []
  )

  const addFile = useCallback((file: UploadFileInfo): void => {
    /* eslint-disable-next-line @eslint-react/dom/no-flush-sync --
     * Using flushSync here because we need the state to be immediately updated
     * before any subsequent file upload operations occur. See CameraInput for
     * detailed explanation.
     */
    flushSync(() => {
      setFiles(prevFiles => [...prevFiles, file])
    })
  }, [])

  const removeFile = useCallback((idToRemove: number): void => {
    setFiles(prevFiles => prevFiles.filter(file => file.id !== idToRemove))
  }, [])

  const updateFile = useCallback(
    (curFileId: number, newFile: UploadFileInfo): void => {
      setFiles(prevFiles =>
        prevFiles.map(file => (file.id === curFileId ? newFile : file))
      )
    },
    []
  )

  const onUploadComplete = useCallback(
    (localFileId: number, fileUrls: IFileURLs): void => {
      const curFile = getFile(localFileId)
      if (isNullOrUndefined(curFile) || curFile.status.type !== "uploading") {
        return
      }

      updateFile(
        curFile.id,
        curFile.setStatus({
          type: "uploaded",
          fileId: fileUrls.fileId as string,
          fileUrls,
        })
      )
    },
    [getFile, updateFile]
  )

  const onUploadProgress = useCallback(
    (event: ProgressEvent, fileId: number): void => {
      const file = getFile(fileId)
      if (isNullOrUndefined(file) || file.status.type !== "uploading") {
        return
      }

      const newProgress = Math.round((event.loaded * 100) / event.total)
      if (file.status.progress === newProgress) {
        return
      }

      updateFile(
        fileId,
        file.setStatus({
          type: "uploading",
          abortController: file.status.abortController,
          progress: newProgress,
        })
      )
    },
    [getFile, updateFile]
  )

  const uploadFileToServer = useCallback(
    (fileURLs: IFileURLs, file: File): void => {
      const abortController = new AbortController()
      const uploadingFileInfo = new UploadFileInfo(
        file.name,
        file.size,
        nextLocalFileId(),
        {
          type: "uploading",
          abortController,
          progress: 1,
        }
      )
      addFile(uploadingFileInfo)

      uploadClient
        .uploadFile(
          element,
          fileURLs.uploadUrl as string,
          file,
          e => onUploadProgress(e, uploadingFileInfo.id),
          abortController.signal
        )
        .then(() => onUploadComplete(uploadingFileInfo.id, fileURLs))
        .catch(err => {
          if (!(err instanceof DOMException && err.name === "AbortError")) {
            updateFile(
              uploadingFileInfo.id,
              uploadingFileInfo.setStatus({
                type: "error",
                errorMessage: err ? err.toString() : "Unknown error",
              })
            )
          }
        })
    },
    [
      addFile,
      element,
      nextLocalFileId,
      onUploadComplete,
      onUploadProgress,
      updateFile,
      uploadClient,
    ]
  )

  const deleteFile = useCallback(
    (fileId: number): void => {
      const file = getFile(fileId)
      if (isNullOrUndefined(file)) {
        return
      }

      if (file.status.type === "uploading") {
        file.status.abortController.abort()
      }

      if (file.status.type === "uploaded" && file.status.fileUrls.deleteUrl) {
        void uploadClient.deleteFile(file.status.fileUrls.deleteUrl)
      }
      removeFile(fileId)
    },
    [getFile, removeFile, uploadClient]
  )

  const handleFileSelected = useCallback(
    (event: React.ChangeEvent<HTMLInputElement>): void => {
      const selectedFiles = event.target.files
      if (!selectedFiles || selectedFiles.length === 0) {
        return
      }

      const file = selectedFiles[0]

      // Clear previous files
      files.forEach(f => deleteFile(f.id))

      // Create preview from the selected file
      const objectUrl = URL.createObjectURL(file)
      setImgSrc(objectUrl)

      // Upload the file
      uploadClient
        .fetchFileURLs([file])
        .then(fileURLsArray => {
          uploadFileToServer(fileURLsArray[0], file)
        })
        .catch(() => {
          // Reset on error
          setImgSrc(null)
        })

      // Reset the input so the same file can be re-selected
      if (fileInputRef.current) {
        fileInputRef.current.value = ""
      }
    },
    [files, deleteFile, uploadClient, uploadFileToServer]
  )

  const handleClick = useCallback((): void => {
    if (!disabled) {
      fileInputRef.current?.click()
    }
  }, [disabled])

  const handleKeyDown = useCallback(
    (event: React.KeyboardEvent): void => {
      if (!disabled && (event.key === "Enter" || event.key === " ")) {
        event.preventDefault()
        fileInputRef.current?.click()
      }
    },
    [disabled]
  )

  // Set initial widget value on mount
  useEffect(() => {
    const prevWidgetValue = widgetMgr.getFileUploaderStateValue(element)
    if (prevWidgetValue === undefined) {
      widgetMgr.setFileUploaderStateValue(
        element,
        toWidgetState(files),
        { fromUi: false },
        fragmentId
      )
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  // Update widget value when status is ready
  useEffect(() => {
    if (status !== "ready") {
      return
    }

    const newWidgetValue = toWidgetState(files)
    const prevWidgetValue = widgetMgr.getFileUploaderStateValue(element)
    if (!isEqual(newWidgetValue, prevWidgetValue)) {
      widgetMgr.setFileUploaderStateValue(
        element,
        newWidgetValue,
        { fromUi: true },
        fragmentId
      )
    }
  }, [status, files, widgetMgr, element, fragmentId])

  // Form clear handler
  const onFormCleared = useCallback((): void => {
    setFiles([])
    setImgSrc(null)

    const newWidgetValue = toWidgetState([])
    widgetMgr.setFileUploaderStateValue(
      element,
      newWidgetValue,
      { fromUi: true },
      fragmentId
    )
  }, [element, fragmentId, widgetMgr])

  useFormClearHelper({ element, widgetMgr, onFormCleared })

  // Clean up object URLs on unmount
  useEffect(() => {
    return (): void => {
      if (imgSrc?.startsWith("blob:")) {
        URL.revokeObjectURL(imgSrc)
      }
    }
  }, [imgSrc])

  // Determine what image to show: uploaded preview > default > placeholder
  const displaySrc = imgSrc ?? element.default ?? null
  const hasImage = displaySrc !== null && displaySrc !== ""
  const acceptString = getAcceptString(element.type as string[])

  return (
    <StyledImageUploader
      className="stImageUploader"
      data-testid="stImageUploader"
    >
      <WidgetLabel
        label={element.label}
        disabled={disabled}
        labelVisibility={labelVisibilityProtoValueToEnum(
          element.labelVisibility?.value
        )}
      >
        {element.help && (
          <WidgetLabelHelpIcon content={element.help} label={element.label} />
        )}
      </WidgetLabel>
      <StyledCircleContainer
        disabled={disabled}
        data-testid="stImageUploaderCircle"
        role="button"
        tabIndex={disabled ? -1 : 0}
        aria-label={`${element.label} - Click to upload an image`}
        aria-disabled={disabled}
        onClick={handleClick}
        onKeyDown={handleKeyDown}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
      >
        {hasImage ? (
          <StyledPreviewImage
            src={displaySrc}
            alt="Uploaded image preview"
            data-testid="stImageUploaderPreview"
          />
        ) : (
          <StyledPlaceholderIcon data-testid="stImageUploaderPlaceholder">
            <Icon content={ImageIcon} size="threeXL" />
          </StyledPlaceholderIcon>
        )}
        <StyledOverlay isVisible={!disabled && isHovered}>
          <Icon content={AddAPhoto} size="twoXL" />
        </StyledOverlay>
        {progress !== undefined && (
          <StyledProgressContainer>
            <ProgressBar value={progress} size={Size.SMALL} />
          </StyledProgressContainer>
        )}
      </StyledCircleContainer>
      <input
        ref={fileInputRef}
        type="file"
        accept={acceptString}
        onChange={handleFileSelected}
        data-testid="stImageUploaderInput"
        style={{ display: "none" }}
        aria-hidden="true"
        tabIndex={-1}
      />
    </StyledImageUploader>
  )
}

export default memo(ImageUploader)
