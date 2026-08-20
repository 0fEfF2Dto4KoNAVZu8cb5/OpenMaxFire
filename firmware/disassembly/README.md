# Firmware disassembly

Generated from `Bixby_0271_080315.hex` using GNU PIC utilities (`gpdasm`) targeting `PIC16F877A`.

- `*_disassembly.asm` — readable gpdasm listing.
- `*_reassemblable.asm` — alternate output intended to be closer to reassemblable source.
- `*_annotated.asm` — analysis copy containing OpenMaxFire notes around key routines.

The annotated file preserves instruction bytes/instructions from the generated disassembly while adding comments. `gpdasm` banked register names must be checked against STATUS bank-selection bits.
