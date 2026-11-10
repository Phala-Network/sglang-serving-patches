"""Run exact vendor method ASTs with CPU fixtures; no engine/GPU imports.

The methods under test are not reimplemented. Tensor transport and prefix-cache
storage are fixtures; ReqKvInfo, Req.finish handling, packed cursor helpers and
the complete KV release function execute directly from exported rc6 source.
"""
from __future__ import annotations

import ast
import argparse
import copy
import dataclasses
import json
import logging
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace as NS
import unittest
from unittest.mock import Mock

HERE = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument("--baseline", action="store_true")
parser.add_argument("--source-root", type=Path)
parser.add_argument("--runtime-root", type=Path)
parser.add_argument("--receipt-dir", type=Path, default=HERE)
args = parser.parse_args()
SOURCE = args.source_root or HERE.parent / "vendor-rc6-source"
MODE = "installed" if args.runtime_root else ("baseline" if args.baseline else "candidate")
RUNTIME = args.runtime_root or (SOURCE if MODE == "baseline" else HERE / "candidate")
SCHEDULE = "python/sglang/srt/managers/schedule_batch.py"
RESULT = "python/sglang/srt/managers/scheduler_components/batch_result_processor.py"
SCHEDULER = "python/sglang/srt/managers/scheduler.py"
COMMON = "python/sglang/srt/mem_cache/common.py"


class Vector:
    def __init__(self, value): self.value = value
    def __getitem__(self, index): return Vector(self.value[index])
    def tolist(self): return copy.deepcopy(self.value)
    def cpu(self): return self
    def clone(self): return Vector(copy.deepcopy(self.value))


class Capture(int):
    def is_full(self): return self == 2
    def is_last(self): return self == 1


class Grammar:
    def __init__(self): self.accepted = []; self.finished = False
    def accept_token(self, token): self.accepted.append(token)
    def is_terminated(self): return False


class Batch:
    def __init__(self, reqs, **kwargs):
        self.reqs = reqs
        self.decoding_reqs = []
        self.chunked_req = None
        self.forward_mode = NS(is_extend=lambda: True, is_decode=lambda: False)
        self.is_prefill_only = False
        self.batch_is_full = False
        self.return_logprob = True
        self.return_hidden_states = True
        self.return_hidden_states_mode = Capture(1)
        self.has_grammar = True
        self.spec_info = None
        self.spec_algorithm = NS(is_none=lambda: True)
        self.prefill_stats = None
        self.dp_cooperation_info = None
        self.__dict__.update(kwargs)
    def __getattr__(self, name): return None
    def batch_size(self): return len(self.reqs)
    def is_empty(self): return not self.reqs
    def filter_batch(self, reqs_to_exclude=()):
        self.reqs = [r for r in self.reqs if not r.finished() and r not in reqs_to_exclude]
    def merge_batch(self, other): self.reqs = self.reqs + other.reqs


module = ModuleType("vendor_prefill_abort_cpu")
sys.modules[module.__name__] = module
g = module.__dict__
g.update(dataclasses=dataclasses, torch=NS(Tensor=Vector), logger=logging.getLogger(__name__),
         get_serving=lambda: NS(strip_thinking_cache=False),
         get_spec=lambda: NS(speculative_algorithm="DFLASH4"),
         get_memory=lambda: NS(enable_hisparse=False),
         envs=NS(SGLANG_PP_SKIP_PURE_CHUNKED_OUTPUT_COMM=NS(get=lambda: False)),
         get_required_capture_hidden_mode=lambda mode, spec: mode,
         get_server_return_hidden_states_mode=lambda: Capture(0),
         NextBatchPlan=lambda **kwargs: NS(**kwargs),
         set_schedule_time_batch=lambda batch: None,
         ceil_align=lambda value, page: ((value + page - 1) // page) * page)


def load(path, class_name=None, methods=(), keep_class=False, names=()):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    if class_name:
        node = copy.deepcopy(next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == class_name))
        if not keep_class:
            node.bases = []
            node.decorator_list = []
            node.body = [n for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name in methods]
            for fn in node.body:
                fn.decorator_list = [d for d in fn.decorator_list if isinstance(d, ast.Name) and d.id in ("staticmethod", "classmethod", "property")]
        body = [node]
    else:
        body = [copy.deepcopy(n) for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names]
    code = ast.fix_missing_locations(ast.Module(body=[ast.ImportFrom(module="__future__", names=[ast.alias(name="annotations")], level=0), *body], type_ignores=[]))
    exec(compile(code, str(path), "exec"), g)


load(SOURCE / SCHEDULE, "ReqKvInfo", keep_class=True)
load(SOURCE / SCHEDULE, "Req", methods=("finished", "update_finish_state", "owned_kv_len"))
load(SOURCE / SCHEDULE, "ScheduleBatch", methods=("copy",))
Batch.copy = g["ScheduleBatch"].copy
g["ScheduleBatch"] = Batch
load(SOURCE / COMMON, names=("release_kv_cache", "_release_overallocated_kv_indices", "checkpoint_kv_cache"))
load(RUNTIME / RESULT, "SchedulerBatchResultProcessor", methods=(
    "process_batch_result_prefill", "_apply_prefill_logprobs", "_append_prefill_hidden_states",
    "_get_prefill_hidden_capture_mode", "_apply_prefill_grammar", "advance_grammar_fsm",
    "_maybe_collect_customized_info", "move_logprobs_to_cpu", "materialize_sampling_mask_output",
    "_validate_pp_skip_output_comm"))
load(RUNTIME / SCHEDULER, "Scheduler", methods=("get_next_batch_to_run",))
Req, Kv, Processor, Scheduler = (g[name] for name in ("Req", "ReqKvInfo", "SchedulerBatchResultProcessor", "Scheduler"))


def request(rid, row, *, aborted=False, middle=0, beam=None, reason=None):
    req = Req()
    req.rid = rid
    req.output_ids = []
    req.finished_reason = None
    req.finished_len = None
    req.to_finish = reason if reason is not None else (object() if aborted else None)
    req.discard_output_reason = None
    req.is_retracted = False
    req.inflight_middle_chunks = middle
    req.beam_group = beam
    req.return_hidden_states = "last"
    req.return_logprob = True
    req.return_sampling_mask = False
    req.hidden_states = []
    req.customized_info = None
    req.grammar = Grammar()
    req.time_stats = Mock()
    req.kv = Kv(req_pool_idx=row, cache_protected_len=2, kv_committed_len=5, kv_allocated_len=7)
    req.origin_input_ids = [1, 2, 3, 4, 5]
    req.extend_end = 5
    req.skip_radix_cache_insert = False
    req.reasoning_tokens = 0
    req.lock = object()
    req.sampling_params = NS(max_new_tokens=128)
    req._check_vocab_boundary_finish = lambda tokens: False
    req._check_str_based_finish = lambda count: False
    req._check_token_based_finish = lambda tokens: False
    req.refresh_fill_ids = Mock()
    req.decode_batch_idx = 0
    return req


class Storage:
    def __init__(self, reqs):
        self.rows = {r.kv.req_pool_idx: r for r in reqs}
        self.slots = {r.kv.req_pool_idx: set(range(7)) for r in reqs}
        self.freed = []
        self.releases = []
        self.req_to_token_pool = NS(free=self.free_row)
        self.token_to_kv_pool_allocator = NS(page_size=1)
        self.claim_kv_row = lambda req: False
        self.supports_mamba = lambda: False
        self.checkpoint = Mock()
        self.unlock = Mock()
    def free_row(self, req):
        row = req.kv.req_pool_idx
        assert self.rows.pop(row) is req, "row ownership changed"
        self.freed.append(row)
        req.kv.req_pool_idx = None
    def free_kv_row(self, kv, ranges):
        for begin, end in ranges:
            for slot in range(begin, end): self.slots[kv.req_pool_idx].remove(slot)
    def on_release(self, req, *, checkpointed): self.releases.append((req, checkpointed))


def processor(reqs):
    p = Processor()
    p.is_generation = True
    p.tree_cache = Storage(reqs)
    p.token_to_kv_pool_allocator = Mock()
    p.snapshot_auxiliary_output_starts = lambda batch, result: None
    p.logprob_result_processor = NS(
        calculate_num_input_logprobs=Mock(side_effect=lambda req, length, start: length - start),
        add_logprob_return_values=Mock())
    p.output_streamer = NS(stream_output=Mock())
    p.metrics_reporter = Mock()
    p.beam_coordinator = Mock()
    p._maybe_update_retained_reasoning_tokens = Mock()
    p._maybe_collect_routed_experts = Mock()
    p._maybe_collect_indexer_topk = Mock()
    p._prepare_kv_cache_release = Mock()
    p._accept_grammar_tokens = lambda req, token: req.grammar.accept_token(token)
    p.get_sampling_mask_finish_reason = Mock(return_value=object())
    return p


def result(batch, *, full=False):
    values = [[10], [11], [20], [21], [22]] if full else [[10], [20]]
    logits = NS(hidden_states=Vector(values), customized_info={"tag": ["abort-meta", "live-meta"]},
                sampling_mask_output=None, next_token_logprobs=None, input_token_logprobs=Vector([-1, -2, -10, -11, -12]),
                next_token_top_logprobs_val=[], next_token_token_ids_logprobs_val=[],
                next_token_sampling_mask_status=[99, None], finalize_input_logprobs=lambda: None)
    return NS(copy_done=None, auxiliary_host_output=None, routed_experts_output=None, indexer_topk_output=None,
              logits_output=logits, next_token_ids=Vector([101, 202][:len(batch.reqs)]), extend_input_len_per_req=[2, 3],
              extend_logprob_start_len_per_req=[0, 0], grammar_advanced=False, can_run_cuda_graph=False)


def scheduler(last, pending):
    s = Scheduler()
    s.process_pending_chunked_abort = lambda: None
    s._process_hicache_events = lambda: None
    s.dllm_config = None
    s.chunked_req = None
    s.enable_hisparse = False
    s.result_queue = [pending] if pending else []
    s._should_defer_prefill = lambda batch: False
    s.get_new_batch_prefill = lambda batch: NS(batch_to_run=None, running_batch=batch)
    s.require_mlp_sync = False
    def update(batch):
        for req in batch.reqs: req.decode_batch_idx += 1
        return batch
    s.update_running_batch = update
    s.dp_attn_adapter = NS(maybe_prepare_mlp_sync_batch=lambda batch, **kwargs: batch,
                          maybe_convert_decode_to_extend=lambda batch: batch)
    s._arm_prefill_decode_interval = lambda batch: None
    s.ngram_embedding_manager = NS(prepare_for_forward=lambda batch, **kwargs: batch)
    return s


class TestPrefillAbortCPU(unittest.TestCase):
    def test_delayed_snapshot_excludes_decode_and_releases_exact_owned_row(self):
        aborted, live = request("aborted", 11, aborted=True), request("live", 12)
        reason = aborted.to_finish
        last = Batch([aborted, live])
        queued = last.copy()
        self.assertIsNot(last.reqs, queued.reqs)
        s = scheduler(last, queued)
        plan = s.get_next_batch_to_run(Batch([]), last)
        self.assertNotIn(aborted, plan.running_batch.reqs)
        self.assertEqual(aborted.decode_batch_idx, 0)
        self.assertEqual(live.decode_batch_idx, 1)
        self.assertIn(aborted, queued.reqs)
        p = processor(queued.reqs)
        p.process_batch_result_prefill(queued, result(queued))
        self.assertEqual(aborted.output_ids, [])
        self.assertIs(aborted.finished_reason, reason)
        self.assertFalse(aborted.kv.holds_kv)
        self.assertTrue(aborted.kv.is_kv_released)
        self.assertEqual(p.tree_cache.freed, [11])
        self.assertEqual(p.tree_cache.slots[11], {0, 1})
        self.assertIs(p.tree_cache.rows[12], live)
        self.assertEqual(p.tree_cache.slots[12], set(range(7)))
        self.assertEqual(p.tree_cache.releases, [(aborted, False)])
        aborted.refresh_fill_ids.assert_not_called()

    def test_packed_hidden_logprob_and_customized_metadata_keep_live_offset(self):
        for full in (False, True):
            with self.subTest(full=full):
                aborted, live = request("aborted", 11, aborted=True), request("live", 12)
                batch = Batch([aborted, live], return_hidden_states_mode=Capture(2 if full else 1))
                p = processor(batch.reqs)
                p.process_batch_result_prefill(batch, result(batch, full=full))
                self.assertEqual(aborted.output_ids, [])
                self.assertEqual(aborted.hidden_states, [])
                self.assertIsNone(aborted.customized_info)
                self.assertEqual(aborted.grammar.accepted, [])
                self.assertEqual(live.output_ids, [202])
                self.assertEqual(live.hidden_states, [[22] if full else [20]])
                self.assertEqual(live.customized_info, {"tag": ["live-meta"]})
                self.assertEqual(live.grammar.accepted, [202])
                calls = p.logprob_result_processor.add_logprob_return_values.call_args_list
                self.assertEqual(len(calls), 1)
                self.assertEqual(calls[0].args[:3], (1, live, 2))
                self.assertEqual(p.logprob_result_processor.calculate_num_input_logprobs.call_count, 2)
                p._maybe_collect_routed_experts.assert_not_called()
                p._maybe_collect_indexer_topk.assert_not_called()

    def test_pending_abort_precedes_sampling_mask_error(self):
        aborted = request("aborted", 11, aborted=True)
        reason = aborted.to_finish
        aborted.return_sampling_mask = True
        batch = Batch([aborted])
        p = processor(batch.reqs)
        p.process_batch_result_prefill(batch, result(batch))
        self.assertIs(aborted.finished_reason, reason)
        p.get_sampling_mask_finish_reason.assert_not_called()

    def test_failed_kv_load_retains_existing_discard_reason_precedence(self):
        aborted = request("restore-failed", 11, aborted=True)
        abort = aborted.to_finish
        failure = aborted.discard_output_reason = object()
        batch = Batch([aborted])
        p = processor(batch.reqs)
        p.process_batch_result_prefill(batch, result(batch))
        self.assertIsNot(aborted.finished_reason, abort)
        self.assertIs(aborted.finished_reason, failure)
        self.assertEqual(aborted.output_ids, [])
        self.assertEqual(p.tree_cache.releases, [(aborted, False)])

    def test_mixed_decode_pending_abort_keeps_existing_partial_output(self):
        decoded = request("decode", 11, aborted=True)
        batch = Batch([decoded], decoding_reqs=[decoded])
        p = processor(batch.reqs)
        p.process_batch_result_prefill(batch, result(batch))
        self.assertEqual(decoded.output_ids, [101])
        p._prepare_kv_cache_release.assert_called_once_with(decoded)
        self.assertEqual(p.tree_cache.releases, [(decoded, True)])

    def test_beam_coordinator_keeps_its_existing_finish_ownership(self):
        beam = request("beam", 11, aborted=True, beam=object())
        batch = Batch([beam])
        s = scheduler(batch, batch.copy())
        self.assertIn(beam, s.get_next_batch_to_run(Batch([]), batch).running_batch.reqs)
        p = processor(batch.reqs)
        p.process_batch_result_prefill(batch, result(batch))
        p.beam_coordinator.commit_prefill.assert_called_once()
        self.assertEqual(p.tree_cache.freed, [])

    def test_eager_grammar_skips_aborted_prefill_but_keeps_mixed_decode(self):
        aborted, decoded = request("prefill", 11, aborted=True), request("decode", 12, aborted=True)
        batch = Batch([aborted, decoded], decoding_reqs=[decoded])
        p = processor(batch.reqs)
        r = result(batch)
        p.advance_grammar_fsm(r, batch)
        self.assertEqual(aborted.grammar.accepted, [])
        self.assertEqual(decoded.grammar.accepted, [202])
        self.assertTrue(r.grammar_advanced)

    def test_empty_result_queue_keeps_synchronous_merge(self):
        aborted = request("prefill", 11, aborted=True)
        batch = Batch([aborted])
        s = scheduler(batch, None)
        self.assertIn(aborted, s.get_next_batch_to_run(Batch([]), batch).running_batch.reqs)


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestPrefillAbortCPU)
    outcome = unittest.TextTestRunner(verbosity=2).run(suite)
    receipt = {"mode": MODE, "tests_run": outcome.testsRun, "failures": len(outcome.failures),
               "errors": len(outcome.errors), "passed": outcome.wasSuccessful(),
               "method_source": str(RUNTIME), "full_engine_imported": False, "gpu_tested": False,
               "failed_cases": [str(test) for test, _ in outcome.failures],
               "error_cases": [str(test) for test, _ in outcome.errors]}
    args.receipt_dir.mkdir(parents=True, exist_ok=True)
    (args.receipt_dir / ("cpu-" + MODE + ".json")).write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt))
    sys.exit(not outcome.wasSuccessful())
