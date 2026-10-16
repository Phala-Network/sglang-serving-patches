# Kimi shared-reference rebinding repair

Union type restriction can reuse nested dictionaries from a referenced target. Deepcopy preserves those aliases; argument-schema extraction previously rewrote the same reference twice, then tried to resolve the new document-local pointer against the original root. This rejected valid repeated-union Schemas. A seven-line repair rebinds each shared node once, preserving all branches and constraints.

This release inherits protocol3-ref1 length/type intersections and protocol3-stream1 progress comments during buffered tool generation. Native libraries, dependencies, model/loading configuration and token-loop behavior remain unchanged. Formal production loading excludes fastsafetensors.

Two synthetic cases reproduce the exact observed source failure on installed ref1. Candidate CPU: 112 passed plus eight subtests. Final installed image: 215 passed plus eight subtests without product overlays, plus direct HF/SGLang CLI checks. Official v0.5.21 plus 28 patches replay exactly, first 27 patches unchanged. Object/array targets, single-branch controls, original input immutability, constraints and independent native/jsonschema validation are covered.

Customer Schemas were not exported or replayed; exact live input coverage and production improvement require observation. This release does not claim memory stability or resolution of every image/transport/HA error. Only node 101 is authorized for rollout. User-approved maintenance-branch publication preserves engine main. Source/image publication is separate from production acceptance.
