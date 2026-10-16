# Kimi reference/length repair and buffered tool progress

The bounded Schema reducer rejected valid local-reference intersections involving minLength, maxLength and type. This release merges length bounds and type constraints along reference chains, preserves nullable/non-string alternatives, and removes integer minLength=0 as a no-op. Derived-definition cache identity includes every applied constraint. Unsupported combinations still fail explicitly; it does not implement general JSON Schema intersection.

It inherits the reviewed protocol3-stream1 fix: after a real first model event, a Kimi Chat tool stream emits at most one fixed SSE comment per 15 seconds only while completion tokens advance without a data event. No premature success response or background keep-alive task is added. Native libraries, dependencies, credentials and loading mode are unchanged.

Synthetic baseline: seven rejected valid combinations out of eight. Candidate source: 54 passed and eight subtests. Final installed image: 157 passed and eight subtests, no product overlays, plus direct HF/SGLang CLI checks. Official SGLang v0.5.21 plus 27 patches replay exactly; the first 26 patches remain unchanged. Tests cover native grammar/jsonschema agreement, actual Kimi constrained json-string encoding, dialect behavior, invalid inputs, reference chains, stream status and cleanup. No production TPS claim is made.

Three observed tool-constraint errors share the reference-intersection category; their customer Schemas were neither exported nor replayed, so exact request coverage is not established. Memory growth, image/transport errors and overall production stability are not declared resolved. Source and image publication are separate from target acceptance.

User-authorized maintenance-branch release. Engine main is preserved; only node 101 is authorized for rollout. Formal deployment must not use fastsafetensors.
