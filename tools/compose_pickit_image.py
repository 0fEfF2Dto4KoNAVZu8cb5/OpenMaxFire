#!/usr/bin/env python3
"""Compose complete, derived PICkit images using resident J3-loader rules.

This offline tool never communicates with a PIC, programmer, stove, or serial
port.  Its outputs are predictions of immediate post-J3/pre-calibration memory,
not vendor-supplied firmware images.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Sequence

from openmaxfire.firmware import FirmwareImage, FirmwareImageError
from openmaxfire.pickit import DERIVED_PICKIT_SCHEMA, compose_pickit_image


EXPECTED_INPUT_SHA256 = {
    "2.02-pickit": "272b12f6f1b42a934e8bb6dab79aa4e9c08748124f1a74ba1d5425b84decccab",
    "2.06-downloader": "90a5289f273d79bf1ee0029777940d6d4cecfc15041d12f5b24a869ce9b30f0b",
    "2.06-pickit": "2adb6dca20a0318662aa73d96b700d5f83a76b36779596fa0e9db8a26db357d4",
    "2.70-downloader": "c6decc8173cadd13f59743df416d783c6de22e55cc9636f5f79dd22dec3e7bca",
    "2.71-downloader": "dc4dcf7aeb83c95525053018e010194c55498796b0b65c0ff26a11eb695e556b",
}


def _load_verified(path: Path, expected_sha256: str) -> FirmwareImage:
    image = FirmwareImage.load(path)
    if image.sha256 != expected_sha256:
        raise FirmwareImageError(
            f"input hash mismatch for {path}: expected {expected_sha256}, "
            f"found {image.sha256}"
        )
    return image


def _write(path: Path, payload: str, *, overwrite: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = payload.encode("utf-8")
    if path.exists():
        if path.read_bytes() == encoded:
            return
        if not overwrite:
            raise FileExistsError(f"refusing to overwrite different file: {path}")
    path.write_bytes(encoded)


def compose_to_files(
    base_path: Path,
    downloader_paths: Sequence[Path],
    output_path: Path,
    *,
    manifest_path: Path | None = None,
    overwrite: bool = False,
) -> dict[str, object]:
    base = FirmwareImage.load(base_path)
    downloaders = [FirmwareImage.load(path) for path in downloader_paths]
    composed = compose_pickit_image(base, downloaders)
    payload = composed.to_intel_hex()
    manifest = composed.to_manifest(output_filename=output_path.name)
    manifest["source_paths"] = {
        "base": str(base_path),
        "loader_sequence": [str(path) for path in downloader_paths],
    }
    _write(output_path, payload, overwrite=overwrite)
    if manifest_path is not None:
        _write(
            manifest_path,
            json.dumps(manifest, indent=2, sort_keys=True) + "\n",
            overwrite=overwrite,
        )
    return manifest


def build_project_images(repo_root: Path) -> dict[str, object]:
    root = repo_root.resolve()
    firmware = root / "reverse-engineering/firmware"
    paths = {
        "2.02-pickit": firmware
        / "2.02/extracted/Bixby_0202_260827_PICkit.hex",
        "2.06-downloader": firmware
        / "2.06/extracted/Bixby_02060021_Downloader.hex",
        "2.06-pickit": firmware
        / "2.06/extracted/Bixby_02060021_PICkit.hex",
        "2.70-downloader": firmware
        / "2.70/extracted/Bixby_0270_070206.hex",
        "2.71-downloader": firmware
        / "2.71/extracted/Bixby_0271_080315.hex",
    }
    images = {
        key: _load_verified(path, EXPECTED_INPUT_SHA256[key])
        for key, path in paths.items()
    }

    golden = compose_pickit_image(
        images["2.06-pickit"],
        [images["2.06-downloader"]],
    ).to_firmware_image(filename="Bixby_02060021_Derived_PICkit.hex")
    golden_match = {
        "mapped_memory": golden.intel_hex.memory
        == images["2.06-pickit"].intel_hex.memory,
        "program": golden.program_words == images["2.06-pickit"].program_words,
        "user_ids": golden.user_id_words == images["2.06-pickit"].user_id_words,
        "configuration": golden.configuration_word
        == images["2.06-pickit"].configuration_word,
        "eeprom": golden.eeprom_words == images["2.06-pickit"].eeprom_words,
    }
    if not all(golden_match.values()):
        raise FirmwareImageError(
            "loader composition does not reproduce the factory 2.06 PICkit pair"
        )

    output_root = firmware / "derived-pickit"
    specifications = (
        (
            "factory-2.06-lineage",
            "vendor_2.06_pickit_base",
            "2.06-pickit",
            ("2.70-downloader",),
            "Bixby_0270_070206_Derived_PICkit_factory206_precal.hex",
        ),
        (
            "factory-2.06-lineage",
            "vendor_2.06_pickit_base",
            "2.06-pickit",
            ("2.70-downloader", "2.71-downloader"),
            "Bixby_0271_080315_Derived_PICkit_factory206_precal.hex",
        ),
        (
            "serial-5215-lineage",
            "serial_5215_original_2.02_base",
            "2.02-pickit",
            ("2.06-downloader",),
            "Bixby_02060021_Derived_PICkit_serial5215_precal.hex",
        ),
        (
            "serial-5215-lineage",
            "serial_5215_original_2.02_base",
            "2.02-pickit",
            ("2.06-downloader", "2.70-downloader"),
            "Bixby_0270_070206_Derived_PICkit_serial5215_precal.hex",
        ),
        (
            "serial-5215-lineage",
            "serial_5215_original_2.02_base",
            "2.02-pickit",
            ("2.06-downloader", "2.70-downloader", "2.71-downloader"),
            "Bixby_0271_080315_Derived_PICkit_serial5215_precal.hex",
        ),
    )

    outputs: list[dict[str, object]] = []
    checksums: list[tuple[str, str]] = []
    for directory, lineage, base_key, sequence_keys, filename in specifications:
        base = images[base_key]
        sequence = [images[key] for key in sequence_keys]
        composed = compose_pickit_image(base, sequence)
        output = output_root / directory / filename
        payload = composed.to_intel_hex()
        _write(output, payload, overwrite=True)
        document = composed.to_manifest(output_filename=filename)
        document["lineage"] = lineage
        document["source_paths"] = {
            "base": str(paths[base_key].relative_to(root)),
            "loader_sequence": [
                str(paths[key].relative_to(root)) for key in sequence_keys
            ],
        }
        document["output"]["path"] = str(output.relative_to(root))
        outputs.append(document)
        checksums.append((document["output"]["sha256"], str(output.relative_to(output_root))))

    project_manifest = {
        "schema": "openmaxfire.derived-pickit-project.v1",
        "image_schema": DERIVED_PICKIT_SCHEMA,
        "generation": "deterministic_offline_resident_loader_overlay",
        "physical_post_j3_readback_comparison": "pending",
        "factory_2_06_golden_pair": {
            "description": (
                "Applying the 2.06 Downloader over the factory 2.06 PICkit "
                "base reproduces every mapped memory section."
            ),
            **golden_match,
        },
        "authenticated_inputs": {
            key: {
                "path": str(paths[key].relative_to(root)),
                "sha256": image.sha256,
            }
            for key, image in images.items()
        },
        "images": outputs,
    }
    _write(
        output_root / "manifest.json",
        json.dumps(project_manifest, indent=2, sort_keys=True) + "\n",
        overwrite=True,
    )
    _write(
        output_root / "SHA256SUMS",
        "".join(f"{digest}  {path}\n" for digest, path in sorted(checksums)),
        overwrite=True,
    )
    return project_manifest


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    project = subparsers.add_parser(
        "project", help="regenerate the authenticated project image set"
    )
    project.add_argument("--repo-root", type=Path, default=Path("."))

    compose = subparsers.add_parser(
        "compose", help="compose one explicitly supplied base and update sequence"
    )
    compose.add_argument("--base", type=Path, required=True)
    compose.add_argument(
        "--downloader", type=Path, action="append", required=True
    )
    compose.add_argument("--output", type=Path, required=True)
    compose.add_argument("--manifest", type=Path)
    compose.add_argument("--overwrite", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "project":
        document = build_project_images(args.repo_root)
        print(
            json.dumps(
                {
                    "generated": len(document["images"]),
                    "manifest": str(
                        args.repo_root
                        / "reverse-engineering/firmware/derived-pickit/manifest.json"
                    ),
                },
                sort_keys=True,
            )
        )
        return 0
    manifest_path = args.manifest or args.output.with_suffix(".manifest.json")
    document = compose_to_files(
        args.base,
        args.downloader,
        args.output,
        manifest_path=manifest_path,
        overwrite=args.overwrite,
    )
    print(json.dumps(document, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
