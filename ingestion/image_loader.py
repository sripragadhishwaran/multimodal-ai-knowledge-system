"""
Image Loader.

Loads image files and extracts text using OCR.
Optimized for:
- Tables
- Roadmaps
- Diagrams
- Structured images
- Screenshots
"""

from pathlib import Path

import pytesseract

from PIL import (
    Image,
    ImageEnhance,
    ImageOps,
    ImageFilter,
)

from config.logging_config import logger

from ingestion.base_loader import BaseLoader

from models.document import Document


class ImageLoader(BaseLoader):
    """
    Loader for image files using Tesseract OCR.

    Supports:
    - PNG
    - JPG
    - JPEG
    - WEBP
    """

    SUPPORTED_EXTENSIONS = {
        ".png",
        ".jpg",
        ".jpeg",
        ".webp",
    }

    # IMPORTANT:
    # Keep this as the real installation path on your PC.
    TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

    def load(
        self,
        file_path: str,
    ) -> list[Document]:
        """
        Load an image and extract text using multiple OCR
        configurations.

        Designed to work better with structured images,
        tables, roadmaps and screenshots.
        """

        path = Path(file_path)

        logger.info(f"Loading image: {file_path}")

        # ==================================================
        # VALIDATE EXTENSION
        # ==================================================

        if path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:

            logger.error(f"Unsupported image format: {path.suffix}")

            return []

        # ==================================================
        # VALIDATE FILE
        # ==================================================

        if not self.validate_file(file_path):

            logger.error(f"Image validation failed: {file_path}")

            return []

        # ==================================================
        # CONFIGURE TESSERACT
        # ==================================================

        pytesseract.pytesseract.tesseract_cmd = self.TESSERACT_PATH

        # ==================================================
        # OPEN IMAGE
        # ==================================================

        try:

            image = Image.open(file_path).convert("RGB")

            logger.info(f"Image opened successfully: {image.size}")

        except Exception as exc:

            logger.exception(f"Failed to open image: {exc}")

            return []

        # ==================================================
        # UPSCALE IMAGE
        # ==================================================

        try:

            width, height = image.size

            scale = 3

            image = image.resize(
                (
                    width * scale,
                    height * scale,
                ),
                Image.Resampling.LANCZOS,
            )

            logger.info(f"Image upscaled for OCR: {image.size}")

        except Exception as exc:

            logger.exception(f"Image resizing failed: {exc}")

            return []

        # ==================================================
        # CREATE MULTIPLE PREPROCESSING VERSIONS
        # ==================================================

        try:

            # ----------------------------------------------
            # VERSION 1: Grayscale
            # ----------------------------------------------

            gray = ImageOps.grayscale(image)

            gray = ImageEnhance.Contrast(gray).enhance(1.8)

            # ----------------------------------------------
            # VERSION 2: Sharpened grayscale
            # ----------------------------------------------

            sharpened = gray.filter(ImageFilter.SHARPEN)

            # ----------------------------------------------
            # VERSION 3: Binary threshold
            # ----------------------------------------------

            threshold = gray.point(lambda pixel: 255 if pixel > 170 else 0)

            logger.info("Image preprocessing completed.")

        except Exception as exc:

            logger.exception(f"Image preprocessing failed: {exc}")

            return []

        # ==================================================
        # OCR FUNCTION
        # ==================================================

        def run_ocr(
            img,
            psm: int,
        ) -> str:

            try:

                text = pytesseract.image_to_string(
                    img,
                    config=f"--psm {psm}",
                )

                return text.strip()

            except Exception as exc:

                logger.warning(f"OCR failed for PSM {psm}: {exc}")

                return ""

        # ==================================================
        # RUN MULTIPLE OCR CONFIGURATIONS
        # ==================================================

        ocr_results = []

        # PSM 6
        text = run_ocr(
            gray,
            6,
        )

        if text:
            ocr_results.append(("gray_psm6", text))

        # PSM 11
        text = run_ocr(
            gray,
            11,
        )

        if text:
            ocr_results.append(("gray_psm11", text))

        # PSM 12
        text = run_ocr(
            gray,
            12,
        )

        if text:
            ocr_results.append(("gray_psm12", text))

        # Sharpened PSM 6
        text = run_ocr(
            sharpened,
            6,
        )

        if text:
            ocr_results.append(("sharp_psm6", text))

        # Threshold PSM 6
        text = run_ocr(
            threshold,
            6,
        )

        if text:
            ocr_results.append(("threshold_psm6", text))

        # Threshold PSM 11
        text = run_ocr(
            threshold,
            11,
        )

        if text:
            ocr_results.append(("threshold_psm11", text))

        # ==================================================
        # CHECK OCR RESULTS
        # ==================================================

        if not ocr_results:

            logger.warning("No OCR result generated from image.")

            return []

        # ==================================================
        # LOG ALL OCR RESULTS
        # ==================================================

        for method, text in ocr_results:

            logger.info(f"\n========== OCR {method} ==========\n" f"{text[:2000]}")

        # ==================================================
        # SELECT BEST OCR RESULT
        # ==================================================

        #
        # For structured images, PSM 6 is usually good.
        # But instead of immediately throwing away other
        # OCR results, select the result containing the
        # largest amount of meaningful text.
        #

        best_method, extracted_text = max(
            ocr_results,
            key=lambda item: len(item[1]),
        )

        logger.info(f"Selected OCR result: {best_method}")

        # ==================================================
        # CLEAN OCR TEXT
        # ==================================================

        lines = []

        seen = set()

        for line in extracted_text.splitlines():

            line = line.strip()

            if not line:
                continue

            # Remove extremely short noise
            if len(line) <= 1:
                continue

            normalized = line.lower().replace(" ", "").replace("|", "")

            if normalized in seen:
                continue

            seen.add(normalized)

            lines.append(line)

        extracted_text = "\n".join(lines).strip()

        # ==================================================
        # EMPTY OCR RESULT
        # ==================================================

        if not extracted_text:

            logger.warning("OCR produced no usable text.")

            return []

        # ==================================================
        # LOG FINAL OCR RESULT
        # ==================================================

        logger.success(
            f"Successfully extracted "
            f"{len(extracted_text)} characters "
            f"from image using OCR."
        )

        logger.info("\n========== FINAL OCR TEXT ==========\n" + extracted_text[:3000])

        # ==================================================
        # CREATE DOCUMENT
        # ==================================================

        document = Document(
            content=extracted_text,
            source=str(path),
            source_type="image",
            metadata={
                "file_name": path.name,
                "extension": path.suffix.lower(),
                "content_type": "image",
                "extraction_method": (f"multi_psm_ocr_{best_method}"),
            },
        )

        # ==================================================
        # RETURN DOCUMENT
        # ==================================================

        return [document]
