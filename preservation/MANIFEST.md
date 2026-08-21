# Preservation manifest

Recovery dates are in UTC. Files were supplied or recovered through the OpenMaxFire research conversation and organized on 2026-08-20.

> **Have an unlisted version?** If you have any BixCheck software, MaxFire
> firmware, manual, hardware documentation, or related material from a version
> not listed in this manifest, please contact me at [openmaxfire@mailbruh.com](mailto:openmaxfire@mailbruh.com) or open a pull request so it
> can be preserved and reverse-engineered.

## Original vendor packages

| Path | Bytes | SHA-256 | Provenance |
| --- | ---: | --- | --- |
| `original/vendor-packages/BixCheck_080206.zip` | 155241 | `37137f99cb6090e7168ae91483a44dadea2ca2cebf5720495cbad186b271d8d5` | User-supplied factory package; contains BixCheck 5.5.00 / firmware 2.70 generation executable |
| `original/vendor-packages/BixCheck_080315.zip` | 156146 | `ffbfbbc29b2ebd4bd6d6e2ebddb4b1c3e23358a120f7506588b2c03390b1c344` | User-supplied factory package; contains BixCheck 5.5.01 / firmware 2.71 generation executable |
| `original/vendor-packages/Bixby110_115_02060021_and_manual.zip` | 1487366 | `140ca903bb23667f831a28a4b0f1966bc856a9584c5b897ffecec1890f5222ac` | User-supplied Bixby 2.06/BixCheck 5.0.21 release package |
| `original/binaries/BixCheck_080315.exe` | 464650 | `b681f79d284bc5da6d087ce052f916853402144430d4adbceaa2ed2e911c2792` | Separately recovered executable; byte-identical to ZIP member |
| `original/manuals/1394047.pdf` | 1729968 | `0e8918ed62ae34d0984957ba466f3cee0adb07c69539a5348f305ba0f2c40739` | BixCheck How-To Guide, 2023480 Rev. A; byte-identical to `2023480-A.pdf` in the 2.06 package |

## 2.06 package members

These files remain inside the original ZIP; hashes were recorded after non-destructive extraction for verification.

| Member | Bytes | SHA-256 |
| --- | ---: | --- |
| `Bixby_02060021_Downloader.hex` | 42831 | `90a5289f273d79bf1ee0029777940d6d4cecfc15041d12f5b24a869ce9b30f0b` |
| `Bixby_02060021_PICkit.hex` | 47596 | `2adb6dca20a0318662aa73d96b700d5f83a76b36779596fa0e9db8a26db357d4` |
| `BixCheck_5021.exe` | 441552 | `0f51f1b9ffe12011928c7821ecc07db92b2bf98a1d82e5fcf605d464316d52d4` |
| `2023480-A.pdf` | 1729968 | `0e8918ed62ae34d0984957ba466f3cee0adb07c69539a5348f305ba0f2c40739` |
| `Bixby_02060021_Notes.txt` | 6515 | `c0086fadd9ea2c11f3ae671c6c4062580a5e59b949e4dd08a2835650d2a3d49c` |

## Photographs

| Current path | Earlier upload name | SHA-256 | Note |
| --- | --- | --- | --- |
| `original/photos/nameplate-serial-5215.png` | `chart-1.png` | `db3fb1bad3e1138aa914d8e6f28816737f2f1917114de21ec97d82a41bfa5170` | Stove nameplate and serial |
| `original/photos/safety-labels.png` | `chart-2.png` | `89765674d0324f6c7c7d5c9bc0469d62343914cfb21d20cf7f886e63a9b1846a` | Side-panel/electrical warnings |
| `original/photos/front-control-panel.jpg` | `IMG_20260527_194238_134.jpg` | `a768c82119606b59bc1c4479a9019d0d659df352f21757c793fd79d7a5752cdc` | Four-button panel and LEDs |
| `original/photos/serial-5215-installed-controller/1000000390.jpg` | `1000000390.jpg` | `bd5c8933c52ad669f6f36bf8cc0462fd86c771c760c20fb7f0ff8b1043b8575e` | Owner-supplied 2026-08-21; main PCB component/power-section view |
| `original/photos/serial-5215-installed-controller/1000000391.jpg` | `1000000391.jpg` | `7c5d0a55e58930aace32d15bcd0148667b1e4cd53065d07d9300ce0796cd41ea` | Owner-supplied 2026-08-21; visible installed-PCB `-0604` suffix and connector bank |
| `original/photos/serial-5215-installed-controller/1000000392.jpg` | `1000000392.jpg` | `d2bda6b4775829bf3743f1637ca1e6033c98a5aae3a4a03fd9ece402b4af5bbe` | Owner-supplied 2026-08-21; J16/J17 and auxiliary-board harness view |
| `original/photos/serial-5215-installed-controller/1000000394.jpg` | `1000000394.jpg` | `0a1f0180b0d9e654777088d77f5c9170fb1d68843f6c8de388f4531e6425a656` | Owner-supplied 2026-08-21; close-up of four-contact main-board J3 |
| `original/photos/serial-5215-installed-controller/1000000395.jpg` | `1000000395.jpg` | `d9b961e2f26d7a29fc5cf5b09106076341e06a54cadbb3fa323687b8559cbc37` | Owner-supplied 2026-08-21; installed wiring and board copyright marking |
| `original/photos/serial-5215-installed-controller/1000000396.jpg` | `1000000396.jpg` | `301901d463d3be2b0dbd7a4a9ee84e80a4b6bfa83e66323d24669126b451168f` | Owner-supplied 2026-08-21; wider J3/J7/controller view |
| `original/photos/serial-5215-installed-controller/1000000397.jpg` | `1000000397.jpg` | `59beca6ffbb347d3e3e7fbce6dcb7cc813fecf62c8b4fb474d5fffbc314bba3c` | Owner-supplied 2026-08-21; exposed J15/J16/J17 and fuse/output area |
| `original/photos/serial-5215-installed-controller/1000000398.jpg` | `1000000398.jpg` | `f9284e4b5391c625f8df746ba232a79ac478792063ac856f44e3920e2d4e20a4` | Owner-supplied 2026-08-21; auxiliary igniter/output PCB and ducting |
| `original/photos/serial-5215-installed-controller/1000000399.jpg` | `1000000399.jpg` | `3c5e11f487ec9358b12ff434769c3dc11cfcab715b03f9914032a1550f593ba7` | Owner-supplied 2026-08-21; installed controller stack overview |
| `original/photos/serial-5215-installed-controller/1000000400.jpg` | `1000000400.jpg` | `d41ac7a03e2b88b0e306ed5e5bd43fad28b42b38c5e8d0652c688d36f3d01224` | Owner-supplied 2026-08-21; wide stove-interior overview |

## Hardware diagrams

| Current path | Earlier upload name | Bytes | SHA-256 | Note |
| --- | --- | ---: | --- | --- |
| `original/diagrams/maxfire-mother-board-pinout.jpg` | `1000000387.jpg` | 321847 | `22dad1271b3780b5867a4be6bf9875495aa4fe39b218352a9121097920145975` | User-supplied online-found diagram; visibly depicts PCB `9067-0404`, not serial 5215's owner-reported/photo-corroborated `9067-0604`; authorship/date/vendor status unverified |

## Derived firmware and project bundles

| Path | SHA-256 | Relationship |
| --- | --- | --- |
| `../reverse-engineering/firmware/2.71/extracted/Bixby_0271_080315.hex` | `dc4dcf7aeb83c95525053018e010194c55498796b0b65c0ff26a11eb695e556b` | Extracted from the BixCheck 5.5.01 embedded resource |
| `../reverse-engineering/firmware/2.70/extracted/Bixby_0270_070206.hex` | `c6decc8173cadd13f59743df416d783c6de22e55cc9636f5f79dd22dec3e7bca` | Deterministically extracted from the BixCheck 5.5.00 executable |
| `../reverse-engineering/firmware/2.06/extracted/Bixby_02060021_Downloader.hex` | `90a5289f273d79bf1ee0029777940d6d4cecfc15041d12f5b24a869ce9b30f0b` | Exact copy of the 2.06 vendor-package member |
| `../reverse-engineering/firmware/2.06/extracted/Bixby_02060021_PICkit.hex` | `2adb6dca20a0318662aa73d96b700d5f83a76b36779596fa0e9db8a26db357d4` | Exact copy of the 2.06 vendor-package member |
| `../reverse-engineering/firmware/2.71/bundles/Bixby_0271_080315_DISASSEMBLED.tar.gz` | `98fbbb0246c36177a298a1a745646fe9b6e23ab34c6ad77fb85f458d870b262f` | User-generated gpdasm/disassembly bundle |
| `../reverse-engineering/firmware/2.71/bundles/bixby_hex_analysis_20260820_133700.tar.gz` | `ad62f89980abeacef987648b5cc8ef17d8e0f8f741850fe03d61a7daad1a80b1` | First Debian HEX inspection bundle |
| `project-snapshots/openmaxfire-v0.1.zip` | `22d009a51d2baaa16ea7230088cd120bdaf7f1545c02ab347a6e580d1b641720` | Earlier generated project foundation, preserved before reorganization |

## External archive

Archive.org status: **not yet uploaded**.
