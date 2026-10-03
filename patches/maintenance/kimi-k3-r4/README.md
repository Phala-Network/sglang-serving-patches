# Kimi fixed-r4 maintenance release

This isolated maintenance stack preserves the explicitly requested historical
runtime. Apply the two patches in series to engine_base in manifest.json.
The first records existing installed privacy/framework source, without changing
its runtime. Only the second patch changes new image runtime behavior.
Do not append these historical restoration bytes to the current unified stack.
The final image is a single-file thin repair over base_image; no dependencies
are rebuilt. Capture methods match the cited upstream commit, without shifting
layer-output indices. Six offline focused tests pass; GPU acceptance is separate.
