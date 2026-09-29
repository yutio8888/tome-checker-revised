# Abashed Expanse static floating tree, T5

`export.py` composites the existing native-alpha [approved burnt-tree master](../terrain-burnt-v1/masters/burnt-tree-v1.png) over each of the 16 existing connected floating-rock masks, then applies the established parity treatment. No new ImageGen call or new threshold. The 32 RGB 128px exports and source-master SHA256 are recorded in [the manifest](export-manifest.json).

[48px](review/contact-48.png), [64px](review/contact-64.png), and [96px](review/contact-96.png) contacts show a distinct blocking tree silhouette on a rock platform, while platform edges connect to adjacent bare rocks. All 16 parity pairs exceed 10%; the minimum is 16.80%. Shader-on 64px prop close-ups and 48/64/96px open-area frames were checked for all three levels in `evidence/t5-20260929/`.

This visual only admits native `BURNT_TREE` variants with the Abashed-specific floating-rock base image and unchanged move/sight/dig/pass-tree rules. WORMHOLE remains native.
