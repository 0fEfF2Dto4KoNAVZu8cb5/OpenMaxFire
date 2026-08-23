"""Machine-readable catalog and validation for preserved firmware images."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .firmware import FirmwareImage, FirmwareVariant


@dataclass(frozen=True, slots=True)
class FirmwareCorpusEntry:
    relative_path: str
    filename: str
    firmware_version: str
    variant: FirmwareVariant
    sha256: str
    file_size: int
    program_words: int
    configuration_word: int

    def to_dict(self) -> dict[str, object]:
        return {
            "relative_path": self.relative_path,
            "filename": self.filename,
            "firmware_version": self.firmware_version,
            "variant": self.variant.value,
            "sha256": self.sha256,
            "file_size": self.file_size,
            "program_words": self.program_words,
            "configuration_word": f"0x{self.configuration_word:04X}",
        }


FIRMWARE_CORPUS: tuple[FirmwareCorpusEntry, ...] = (
    FirmwareCorpusEntry(
        "reverse-engineering/firmware/2.06/extracted/Bixby_02060021_Downloader.hex",
        "Bixby_02060021_Downloader.hex",
        "2.06",
        FirmwareVariant.DOWNLOADER,
        "90a5289f273d79bf1ee0029777940d6d4cecfc15041d12f5b24a869ce9b30f0b",
        42831,
        7599,
        0x3F76,
    ),
    FirmwareCorpusEntry(
        "reverse-engineering/firmware/2.06/extracted/Bixby_02060021_PICkit.hex",
        "Bixby_02060021_PICkit.hex",
        "2.06",
        FirmwareVariant.PICKIT,
        "2adb6dca20a0318662aa73d96b700d5f83a76b36779596fa0e9db8a26db357d4",
        47596,
        8192,
        0x3F32,
    ),
    FirmwareCorpusEntry(
        "reverse-engineering/firmware/2.70/extracted/Bixby_0270_070206.hex",
        "Bixby_0270_070206.hex",
        "2.70",
        FirmwareVariant.EMBEDDED,
        "c6decc8173cadd13f59743df416d783c6de22e55cc9636f5f79dd22dec3e7bca",
        42336,
        7681,
        0x3F72,
    ),
    FirmwareCorpusEntry(
        "reverse-engineering/firmware/2.71/extracted/Bixby_0271_080315.hex",
        "Bixby_0271_080315.hex",
        "2.71",
        FirmwareVariant.EMBEDDED,
        "dc4dcf7aeb83c95525053018e010194c55498796b0b65c0ff26a11eb695e556b",
        42740,
        7755,
        0x3F72,
    ),
)


@dataclass(frozen=True, slots=True)
class FirmwareCorpusValidation:
    entry: FirmwareCorpusEntry
    present: bool
    valid: bool
    errors: tuple[str, ...]
    image: FirmwareImage | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "entry": self.entry.to_dict(),
            "present": self.present,
            "valid": self.valid,
            "errors": list(self.errors),
            "parsed": self.image.to_dict() if self.image is not None else None,
        }


@dataclass(frozen=True, slots=True)
class FirmwareCorpusReport:
    repo_root: str
    results: tuple[FirmwareCorpusValidation, ...]

    @property
    def valid(self) -> bool:
        return bool(self.results) and all(item.valid for item in self.results)

    @property
    def present_count(self) -> int:
        return sum(item.present for item in self.results)

    def to_dict(self) -> dict[str, object]:
        return {
            "schema": "openmaxfire.firmware-corpus-report.v1",
            "repo_root": self.repo_root,
            "expected_count": len(self.results),
            "present_count": self.present_count,
            "valid": self.valid,
            "results": [item.to_dict() for item in self.results],
        }


def validate_firmware_corpus(
    repo_root: str | Path,
    *,
    catalog: tuple[FirmwareCorpusEntry, ...] = FIRMWARE_CORPUS,
) -> FirmwareCorpusReport:
    """Parse and authenticate every cataloged image under ``repo_root``."""

    root = Path(repo_root)
    results: list[FirmwareCorpusValidation] = []
    for entry in catalog:
        path = root / entry.relative_path
        if not path.is_file():
            results.append(
                FirmwareCorpusValidation(entry, False, False, ("file is missing",))
            )
            continue
        errors: list[str] = []
        try:
            image = FirmwareImage.load(path)
        except Exception as exc:
            results.append(
                FirmwareCorpusValidation(
                    entry, True, False, (f"Intel HEX parse failed: {exc}",)
                )
            )
            continue
        actual_size = path.stat().st_size
        checks = (
            (image.filename == entry.filename, "filename mismatch"),
            (image.sha256 == entry.sha256, "SHA-256 mismatch"),
            (actual_size == entry.file_size, "file-size mismatch"),
            (image.firmware_version == entry.firmware_version, "firmware-version mismatch"),
            (image.variant is entry.variant, "firmware-variant mismatch"),
            (len(image.program_words) == entry.program_words, "program-word count mismatch"),
            (image.configuration_word == entry.configuration_word, "configuration-word mismatch"),
        )
        errors.extend(message for passed, message in checks if not passed)
        results.append(
            FirmwareCorpusValidation(entry, True, not errors, tuple(errors), image)
        )
    return FirmwareCorpusReport(str(root), tuple(results))


__all__ = [
    "FIRMWARE_CORPUS",
    "FirmwareCorpusEntry",
    "FirmwareCorpusReport",
    "FirmwareCorpusValidation",
    "validate_firmware_corpus",
]
