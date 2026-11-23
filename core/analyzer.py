from abc import ABC, abstractmethod
from io import BytesIO
from PIL import Image, ImageStat


class ExposureAnalyzer(ABC):
    """Abstract Parent Class untuk analisis pencahayaan foto (OOP 2)."""

    AUTO_LOW_LUMA = 55.0
    AUTO_HIGH_LUMA = 205.0

    EXIF_SUB_IFD_TAG = 0x8769       # Sub-IFD tempat data kamera tersimpan
    EXPOSURE_BIAS_TAG = 37380       # 0x9204 (ExposureBiasValue)

    def _open_image(self, image_source) -> tuple[Image.Image, bool]:
        if isinstance(image_source, Image.Image):
            return image_source, False
        if isinstance(image_source, (bytes, bytearray)):
            return Image.open(BytesIO(image_source)), True
        return Image.open(image_source), True

    def _extract_exposure_bias(self, img: Image.Image) -> float | None:
        try:
            exif = img.getexif()
            if not exif:
                return None

            exif_sub_ifd = exif.get_ifd(self.EXIF_SUB_IFD_TAG)
            raw_ev = exif_sub_ifd.get(self.EXPOSURE_BIAS_TAG)

            if raw_ev is None:
                raw_ev = exif.get(self.EXPOSURE_BIAS_TAG)

            if raw_ev is None:
                return None

            if isinstance(raw_ev, tuple) and len(raw_ev) == 2:
                if raw_ev[1] == 0:
                    return None
                return round(float(raw_ev[0]) / float(raw_ev[1]), 2)

            return round(float(raw_ev), 2)
        except Exception:
            return None

    def _analyze_grayscale(self, img: Image.Image, is_fallback: bool = False) -> tuple[float, str, str]:
        gray_img = img.resize((200, 200)).convert("L")
        mean_val = ImageStat.Stat(gray_img).mean[0]

        if mean_val < self.AUTO_LOW_LUMA:
            status = "Underexposed"
        elif mean_val > self.AUTO_HIGH_LUMA:
            status = "Overexposed"
        else:
            status = "Normal"

        prefix = "No EXIF -> Fallback Grayscale" if is_fallback else "Auto Grayscale"
        detail = f"{prefix} (Luma: {mean_val:.1f}/255)"
        return round(mean_val, 2), status, detail

    @abstractmethod
    def analyze(self, image_source) -> tuple[float, str, str]:
        pass


class ManualEVAnalyzer(ExposureAnalyzer):
    """Subclass 1: Mengecek metadata Exposure Bias dulu; fallback ke Grayscale jika tidak ada."""

    def __init__(self, min_ev: float = -2.0, max_ev: float = 2.0):
        self._min_ev = min_ev
        self._max_ev = max_ev

    def analyze(self, image_source) -> tuple[float, str, str]:
        img, should_close = self._open_image(image_source)
        try:
            ev_value = self._extract_exposure_bias(img)

            if ev_value is not None:
                if ev_value <= self._min_ev:
                    status = "Underexposed"
                elif ev_value >= self._max_ev:
                    status = "Overexposed"
                else:
                    status = "Normal"

                detail = (
                    f"EXIF EV: {ev_value:+.2f} EV "
                    f"(Batas: {self._min_ev:+.1f} / {self._max_ev:+.1f})"
                )
                return ev_value, status, detail

            return self._analyze_grayscale(img, is_fallback=True)
        finally:
            if should_close:
                img.close()


class AutoGrayscaleAnalyzer(ExposureAnalyzer):
    """Subclass 2: Langsung menggunakan metode konversi Grayscale tanpa parameter manual."""

    def analyze(self, image_source) -> tuple[float, str, str]:
        img, should_close = self._open_image(image_source)
        try:
            return self._analyze_grayscale(img, is_fallback=False)
        finally:
            if should_close:
                img.close()