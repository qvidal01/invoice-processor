"""
OCR Engine for extracting text from PDF and image files.

This module provides functionality to extract text from invoice documents
using Tesseract OCR and PDF text extraction libraries.
"""

import logging
import re
from pathlib import Path
from typing import Optional

from PIL import Image
from PyPDF2 import PdfReader

logger = logging.getLogger(__name__)


class OCREngine:
    """
    Engine for optical character recognition on invoice documents.

    Supports PDF and image formats (PNG, JPEG, TIFF).
    """

    def __init__(self, language: str = "eng", config: Optional[dict] = None) -> None:
        """
        Initialize OCR engine.

        Args:
            language: Tesseract language code (default: 'eng')
            config: Optional configuration dictionary

        Raises:
            ImportError: If required OCR libraries are not installed
        """
        self.language = language
        self.config = config or {}
        logger.info(f"OCR Engine initialized with language: {language}")

    def extract_text_from_pdf(self, file_path: Path) -> str:
        """
        Extract text from a PDF file.

        First attempts direct text extraction, falls back to OCR for scanned PDFs.

        Args:
            file_path: Path to PDF file

        Returns:
            Extracted text content

        Raises:
            FileNotFoundError: If file does not exist
            ValueError: If file is not a valid PDF
        """
        if not file_path.exists():
            raise FileNotFoundError(f"PDF file not found: {file_path}")
        if file_path.suffix.lower() != ".pdf":
            raise ValueError(f"Expected a PDF file, got: {file_path.suffix}")

        logger.info(f"Extracting text from PDF: {file_path}")

        with file_path.open("rb") as fh:
            reader = PdfReader(fh)
            extracted_text = " ".join(filter(None, (page.extract_text() for page in reader.pages)))

        if extracted_text.strip():
            return extracted_text

        logger.info("Direct PDF extraction returned empty text; falling back to OCR")
        try:
            import pytesseract
            from pdf2image import convert_from_path
        except ImportError as exc:
            raise ImportError(
                "OCR fallback requires pdf2image and pytesseract to be installed"
            ) from exc

        images = convert_from_path(str(file_path))
        text_chunks = []
        for image in images:
            processed = self.preprocess_image(image)
            text_chunks.append(pytesseract.image_to_string(processed, lang=self.language))

        return "\n".join(text_chunks)

    def extract_text_from_image(self, file_path: Path) -> str:
        """
        Extract text from an image file using OCR.

        Args:
            file_path: Path to image file (PNG, JPEG, TIFF)

        Returns:
            Extracted text content

        Raises:
            FileNotFoundError: If file does not exist
            ValueError: If file is not a valid image
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Image file not found: {file_path}")

        logger.info(f"Extracting text from image: {file_path}")

        try:
            import pytesseract
        except ImportError as exc:
            raise ImportError("Image OCR requires pytesseract to be installed") from exc

        image = Image.open(file_path)
        processed = self.preprocess_image(image)
        return pytesseract.image_to_string(processed, lang=self.language)

    def preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Preprocess image to improve OCR accuracy.

        Applies:
        - Grayscale conversion
        - Noise reduction
        - Contrast enhancement
        - Deskewing

        Args:
            image: PIL Image object

        Returns:
            Preprocessed image
        """
        logger.debug("Preprocessing image for OCR")

        from PIL import ImageFilter, ImageOps

        grayscale = image.convert("L")
        denoised = grayscale.filter(ImageFilter.MedianFilter())
        contrasted = ImageOps.autocontrast(denoised)

        rotation = self.detect_orientation(contrasted)
        if rotation:
            contrasted = contrasted.rotate(-rotation, expand=True)

        return contrasted

    def detect_orientation(self, image: Image.Image) -> int:
        """
        Detect image orientation in degrees.

        Args:
            image: PIL Image object

        Returns:
            Rotation angle (0, 90, 180, or 270)
        """
        try:
            import pytesseract
        except ImportError:
            return 0

        try:
            osd = pytesseract.image_to_osd(image)
        except Exception:
            return 0

        match = re.search(r"Rotate: (\d+)", osd)
        if match:
            return int(match.group(1))
        return 0
