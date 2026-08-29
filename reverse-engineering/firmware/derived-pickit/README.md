# Derived complete PICkit images

These are deterministic, complete PIC16F877A images constructed by applying
the recovered J3 resident-loader rules to an authenticated complete PICkit base.
They are **derived predictions, not vendor-supplied PICkit releases**.

Each image represents the complete chip immediately after the listed J3
Downloader sequence and **before** Individualize, Format, or calibration changes
data EEPROM. It contains all 8,192 program words, four User ID words, the
configuration word, and all 256 EEPROM bytes inherited from its named base.

## Image sets

| Lineage | Target | SHA-256 | Intended comparison |
| --- | --- | --- | --- |
| Factory 2.06 base | 2.70 | `3ea028e4bc075d76bba82778a3000b4fd17ee63ae2456ce447027480376d54bf` | Generic vendor-2.06-based lab prediction |
| Factory 2.06 base | 2.71 | `bfae5b976f264f8a7e1e5dc138b30d1f5d74612a23a38d41ea523b5e08dcae62` | Sequential 2.06→2.70→2.71 lab prediction |
| Serial 5215 original 2.02 base | 2.06 | `ba4f19565e7c84b60e372be130ed756e5ed7423894bf42bf7c2f5e02467b7885` | Expected serial-5215 read immediately after 2.02→2.06 |
| Serial 5215 original 2.02 base | 2.70 | `174aecf337b9df66ef5ad53ca80d23d834eaa8a0d6ebdf3fbfc5a57e9b8a5d75` | Expected serial-5215 read immediately after 2.02→2.06→2.70 |
| Serial 5215 original 2.02 base | 2.71 | `5fb6ba549dd152f24c277de3b1796a39e69740df1d6d59bdeea9a0e29582f468` | Expected serial-5215 read immediately after the complete sequence |

The serial-5215 lineage retains that controller's individualized EEPROM and is
not a generic image for another stove. The factory-2.06 lineage retains the
vendor 2.06 PICkit image's format-05 EEPROM defaults. Firmware 2.70/2.71 expects
format 07, so those files are deliberately labeled `precal`: they are not ready
for stove operation until the documented target-version formatting and
calibration procedure is completed.

## Composition rule

For each Downloader source word, the generator reproduces the resident loader:

- source words `0x0000`-`0x0003` are written to the application reset
  trampoline at `0x1E84`-`0x1E87`;
- ordinary source words below `0x1E80` replace the corresponding base word;
- direct source addresses at or above `0x1E80` are ignored;
- words absent from the sparse Downloader image remain exactly as they were in
  the base;
- the physical reset vector, resident loader except its four-word application
  trampoline, User IDs, configuration word, and EEPROM remain inherited from
  the base.

The sparse behavior matters. The predicted serial-5215 2.06 program memory has
111 application words that differ from the factory 2.06 PICkit file because the
2.06 J3 image does not transmit those addresses. They are preserved 2.02 words,
not a generator error.

## Validation status

There is one strong static golden check: applying the 2.06 Downloader over the
factory 2.06 PICkit base reproduces every mapped byte of the factory PICkit
image. Every generated image is then reparsed and required to preserve the
complete base reset/loader, User IDs, configuration, and EEPROM invariants.
All five complete images also boot through the inherited loader in the real
PIC14 emulator and return the target application's `CR0000` response.

What remains pending is the decisive physical comparison: perform a J3 update
on an expendable, recoverable PIC, read the entire chip with PICkit before any
calibration, and compare that read against the corresponding derived image.
Until that passes, use these only on spare PICs/bench controllers. Do not program
the original chip or treat them as production recovery images.

## Reproduction

From the repository root:

```bash
PYTHONPATH=src python tools/compose_pickit_image.py project --repo-root .
(cd reverse-engineering/firmware/derived-pickit && sha256sum -c SHA256SUMS)
```

[`manifest.json`](manifest.json) records every authenticated input, loader step,
preserved section, output hash, and qualification limitation.
