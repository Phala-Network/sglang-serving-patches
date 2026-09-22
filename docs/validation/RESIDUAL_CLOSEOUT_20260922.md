# Independent residual closeout, September 22, 2026

The independent review accepted both historical residuals at the source/CPU
boundary with no P1/P2 finding within its bounded scope.
Reviewed commits: `f172f7f6e2d3917c6f11491d0ef859ac76c2669d` and
`228f7d93dc7ab0f5b08bc714eb5d4a29afc01d33`;
final tree `0af2ff1dbe241285caacf8e8236c918a434b9889`.
The original fixed-head `05a0fe7` audit remains historical evidence, not rewritten.

## Malformed weight updates

Record `legacy-2224d5c89971` is closed for its missing shared hunks:

- Own-rank deserialization failures return a controlled error without calling
  the updater; unrelated ranks are not decoded.
- Payload/name/envelope/rank/format/metadata validation precedes device access
  and loading. Existing DS derived-cache and active-cache guards keep ordering.
- The complete ordinary tensor list is unwrapped before loading.
- Flattened reconstruction eagerly creates a complete list before model
  mutation. Shape mismatch, incompatible dtype view and boolean shape on a
  later entry return failure even after a valid first entry, without a loader call.
- Valid default/direct/custom/flattened loading remains covered.

Independent run: `test/manual/phala/test_malformed_weight_update_cpu.py`,
16 passed, zero failures/skips. Removing only validation lets a malformed
integer reach the unavailable device and raise; the positive path rejects it
before device access. The reconstruction boundary uses the real consumer
instead of duplicating byte/shape arithmetic.
This does not promise rollback for arbitrary loader failures after successful
reconstruction.

## Initial SSE error status

Record `legacy-5f9f960c28a1` is closed for the missing pre-header hunk.
The common method promotes only an initial encoded 4xx/5xx error, preserves
message/type/param, and closes its generator without requesting another event.
Missing code defaults to 400. Invalid/nonerror data retain streaming behavior;
a later error stays SSE with HTTP 200 and unchanged body bytes.
Existing ownership and raised-ValueError cleanup remain in use.

Independent run: `test/manual/phala/test_initial_stream_error_cpu.py`,
7 passed, zero failures/skips. Real Starlette ASGI calls cover normal completion
and header-send failure cleanup. Removing only promotion reproduces the initial
503 event being incorrectly returned with HTTP 200.
The real chat callsite delegates to this shared method.

## Execution and boundary

Python 3.12.14, Torch 2.13.0+cpu and isolated FastAPI/Starlette/ORJSON packages
ran both actual-source-method suites: 23 passed in total. Loader mocks and
CPU pickle fixtures are explicit. An initial wrong-interpreter setup failure
was excluded; FastAPI's deprecation warning is not a failed test.
The SSE suite is in shared CI35743592888 (passed); the Torch suite was executed
locally, not claimed as a dependency-light CI run.

No CUDA IPC, distributed atomicity, GPU numerics, full server imports, live
generation/ingress, image contents or deployment acceptance is established.
The production/repair skills kept the review focused on affected CPU tests and
ablations; no new build, GPU operation or broad suite was required.
The original full workspace receipt's SHA256 is retained in
`docs/SUCCESSOR_COVERAGE_20260922.json`.
