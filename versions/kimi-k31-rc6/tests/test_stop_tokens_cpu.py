"""Execute real vendor factory/constructor AST with CPU-only boundary doubles.

No implementation is copied or patched in this harness. Native grammar compiler,
runtime-context and backend construction boundaries are replaced, as in the
upstream factory regression tests. Native FSM masks and model inference are not
validated here. The same command can target the final image's installed files.
"""
from __future__ import annotations

import argparse
import ast
import datetime
import hashlib
import json
import sys
import threading
import types
from pathlib import Path
from unittest.mock import MagicMock, patch


REGRESSIONS = {
    "custom_backend_startup_union",
    "huggingface_xgrammar_startup_union",
    "llguidance_startup_union",
    "init_xgrammar_override_union",
}


def check(value, message="contract_assertion_failed"):
    if not value:
        raise AssertionError(message)


class Harness:
    def __init__(self, source):
        self.name = "xgrammar"
        self.parallel = types.SimpleNamespace(pp_size=1)
        self.serving = types.SimpleNamespace(
            constrained_json_whitespace_pattern=None,
            constrained_json_disable_any_whitespace=False,
            constrained_json_max_whitespace_cnt=None,
            enable_strict_thinking=False,
            reasoning_parser=None,
        )
        self.overrides = []
        self.logger = MagicMock()
        self.args = object()
        self.namespace = {
            "__name__": "vendor_grammar_cpu_boundary",
            "GRAMMAR_BACKEND_REGISTRY": {},
            "get_exec": lambda: types.SimpleNamespace(
                kernel=types.SimpleNamespace(grammar_backend=self.name)
            ),
            "get_parallel": lambda: self.parallel,
            "get_serving": lambda: self.serving,
            "get_context": lambda: self,
            "logger": self.logger,
            "threading": threading,
            "envs": types.SimpleNamespace(
                SGLANG_XGRAMMAR_CACHE_MAX_BYTES=types.SimpleNamespace(get=lambda: 1048576),
                SGLANG_XGRAMMAR_MAX_THREADS=types.SimpleNamespace(get=lambda: 3),
            ),
        }
        self.namespace["ReasoningParser"] = lambda **kw: types.SimpleNamespace(**kw)

        class Compiler:
            def __init__(self, **kw):
                self.kwargs = kw

        class TokenizerInfo:
            @staticmethod
            def from_huggingface(tokenizer, **kw):
                return types.SimpleNamespace(tokenizer=tokenizer, **kw)

        harness = self

        class BackendBase:
            def __init__(self):
                self.use_cache_budget = harness.namespace["grammar_cache_budget_enabled"]()

            def _new_framing_compiler(self, tokenizer_info):
                return Compiler(tokenizer_info=tokenizer_info)

        class TokenizerNotSupportedError(Exception):
            pass

        self.error_type = TokenizerNotSupportedError
        self.namespace.update(
            GrammarCompiler=Compiler,
            TokenizerInfo=TokenizerInfo,
            TokenizerNotSupportedError=TokenizerNotSupportedError,
            BackendBase=BackendBase,
        )
        wanted = {
            "grammar_cache_budget_enabled",
            "register_grammar_backend",
            "grammar_stop_token_ids",
            "create_grammar_backend",
        }
        base_nodes = [
            n for n in ast.parse(source["base_grammar_backend.py"]).body
            if isinstance(n, ast.FunctionDef) and n.name in wanted
        ]
        self.production_ast = [n.name for n in base_nodes]
        # Deferred annotations avoid importing framework types; executable bodies
        # below are the unmodified nodes parsed from the installed source.
        preamble = ast.ImportFrom(module="__future__", names=[ast.alias(name="annotations")], level=0)
        module = ast.fix_missing_locations(ast.Module(body=[preamble, *base_nodes], type_ignores=[]))
        exec(compile(module, "<actual-base_grammar_backend.py>", "exec"), self.namespace)

        xclass = next(n for n in ast.parse(source["xgrammar_backend.py"]).body if isinstance(n, ast.ClassDef) and n.name == "XGrammarGrammarBackend")
        ctor = next(n for n in xclass.body if isinstance(n, ast.FunctionDef) and n.name == "__init__")
        # Keep the real constructor inside a class so zero-argument super() has
        # its normal __class__ cell. Only the unmodified constructor is selected.
        selected_class = ast.ClassDef(name="XGrammarGrammarBackend", bases=[ast.Name(id="BackendBase", ctx=ast.Load())], keywords=[], body=[ctor], decorator_list=[])
        module = ast.fix_missing_locations(ast.Module(body=[preamble, selected_class], type_ignores=[]))
        exec(compile(module, "<actual-xgrammar_backend.py>", "exec"), self.namespace)
        self.production_ast.append("XGrammarGrammarBackend.__init__")
        self.backend_class = self.namespace["XGrammarGrammarBackend"]

        self.modules = {}
        for name in [
            "sglang", "sglang.srt", "sglang.srt.constrained",
            "sglang.srt.constrained.xgrammar_backend",
            "sglang.srt.constrained.llguidance_backend",
            "sglang.srt.constrained.outlines_backend",
            "sglang.srt.constrained.reasoner_grammar_backend",
        ]:
            value = types.ModuleType(name)
            value.__path__ = []
            self.modules[name] = value
        xmodule = self.modules["sglang.srt.constrained.xgrammar_backend"]
        xmodule.XGrammarGrammarBackend = self.backend_class
        xmodule.TokenizerNotSupportedError = TokenizerNotSupportedError
        self.modules["sglang.srt.constrained.llguidance_backend"].GuidanceBackend = lambda **kw: types.SimpleNamespace(kind="llguidance", **kw)
        self.modules["sglang.srt.constrained.outlines_backend"].OutlinesGrammarBackend = lambda tokenizer, **kw: types.SimpleNamespace(kind="outlines", tokenizer=tokenizer, **kw)
        self.modules["sglang.srt.constrained.reasoner_grammar_backend"].ReasonerGrammarBackend = lambda *args, **kw: types.SimpleNamespace(kind="reasoner", args=args, kwargs=kw)

    def override(self, source, **changes):
        self.overrides.append((source, changes))
        self.name = changes.get("grammar_backend", self.name)

    def create(self, tokenizer=None, eos=None, think_end_ids=None):
        with patch.dict(sys.modules, self.modules):
            return self.namespace["create_grammar_backend"](
                self.args, tokenizer, 50000, eos, think_end_ids
            )

    def capture_custom(self, tokenizer, eos):
        self.name = "capture"
        self.namespace["register_grammar_backend"](
            self.name,
            lambda args, tok, vocab, stops: types.SimpleNamespace(
                args=args, tokenizer=tok, vocab_size=vocab, stops=stops
            ),
        )
        return self.create(tokenizer, eos)


def run_cases(source):
    def custom(h):
        config = {0, 2}
        tokenizer = types.SimpleNamespace(eos_token_id=1, additional_stop_token_ids={3})
        result = h.capture_custom(tokenizer, config)
        check(result.stops == {0, 1, 2, 3}, "startup_stop_tokens_missing")
        check(config == {0, 2} and result.args is h.args and result.tokenizer is tokenizer and result.vocab_size == 50000)

    def huggingface(h):
        tok = types.SimpleNamespace(eos_token_id=163585, additional_stop_token_ids={7})
        result = h.create(tok, {163586})
        check(set(result._tokenizer_info.stop_token_ids) == {7, 163585, 163586}, "startup_stop_tokens_missing")

    def guidance(h):
        h.name = "llguidance"
        result = h.create(types.SimpleNamespace(eos_token_id=0, additional_stop_token_ids={3}), {2})
        check(result.eos_token_ids == {0, 2, 3}, "startup_stop_tokens_missing")
        check(result.n_vocab == 50000 and result.any_whitespace is True)

    def special(h):
        for prior in ([2], None):
            tokenizer = types.SimpleNamespace(init_xgrammar=lambda prior=prior: (object(), prior))
            backend = h.backend_class(tokenizer, 100, model_eos_token_ids=[2, 7])
            check(backend.override_stop_tokens == [2, 7], "startup_stop_tokens_missing")

    def no_startup(h):
        check(h.capture_custom(types.SimpleNamespace(), None).stops is None)

    def existing_set(h):
        original = {0, 2}
        result = h.capture_custom(types.SimpleNamespace(eos_token_id=0, additional_stop_token_ids={2}), original)
        check(result.stops == {0, 2} and original == {0, 2})

    def special_no_config(h):
        tokenizer = types.SimpleNamespace(init_xgrammar=lambda: (object(), [2]))
        check(h.backend_class(tokenizer, 100).override_stop_tokens == [2])

    def custom_priority(h):
        h.serving.reasoning_parser = "kimi"
        result = h.capture_custom(types.SimpleNamespace(), {2})
        check(result.stops == {2} and not hasattr(result, "kind"))

    def whitespace(h):
        h.serving.constrained_json_disable_any_whitespace = True
        h.serving.constrained_json_max_whitespace_cnt = 5
        result = h.create(types.SimpleNamespace(), {2})
        check(result.any_whitespace is False and result.max_whitespace_cnt == 5)
        check(result.grammar_compiler.kwargs["cache_limit_bytes"] == 1048576)
        check(result.grammar_compiler.kwargs["max_threads"] == 3)

    def pp_budget(h):
        h.parallel.pp_size = 2
        result = h.create(types.SimpleNamespace(), {2})
        check(result.use_cache_budget is False and set(result.grammar_compiler.kwargs) == {"tokenizer_info"})
        h.logger.info.assert_called_once()

    def unsupported_fallback(h):
        result = h.create(types.SimpleNamespace(init_xgrammar=lambda: (None, None)), {2})
        check(result is None and h.name == "none")
        check(h.overrides == [("grammar.import_fallback", {"grammar_backend": "none"})])

    def unsupported_strict(h):
        h.serving.enable_strict_thinking = True
        try:
            h.create(types.SimpleNamespace(init_xgrammar=lambda: (None, None)), {2})
        except ValueError as error:
            check("--enable-strict-thinking" in str(error))
        else:
            raise AssertionError("strict_thinking_did_not_fail_closed")
        check(h.name == "xgrammar" and not h.overrides)

    def none_strict(h):
        h.name = "none"
        h.serving.enable_strict_thinking = True
        try:
            h.create()
        except ValueError as error:
            check("--enable-strict-thinking" in str(error))
        else:
            raise AssertionError("strict_thinking_did_not_fail_closed")

    def reasoner(h):
        h.name = "outlines"
        h.serving.reasoning_parser = "kimi"
        h.serving.enable_strict_thinking = True
        h.serving.constrained_json_whitespace_pattern = r"[\n ]*"
        tokenizer = types.SimpleNamespace()
        result = h.create(tokenizer, {2}, [42])
        check(result.kind == "reasoner" and result.kwargs == {"enable_strict_thinking": True})
        check(result.args[0].whitespace_pattern == r"[\n ]*" and result.args[2] is tokenizer)

    cases = [
        ("custom_backend_startup_union", custom),
        ("huggingface_xgrammar_startup_union", huggingface),
        ("llguidance_startup_union", guidance),
        ("init_xgrammar_override_union", special),
        ("no_startup_tokens_remains_none", no_startup),
        ("existing_zero_and_config_set_preserved", existing_set),
        ("special_tokenizer_no_config_override_preserved", special_no_config),
        ("custom_priority_skips_reasoner_wrapper", custom_priority),
        ("whitespace_and_compiler_budget_preserved", whitespace),
        ("pp_budget_path_preserved", pp_budget),
        ("unsupported_tokenizer_nonstrict_fallback_preserved", unsupported_fallback),
        ("unsupported_tokenizer_strict_fails_closed", unsupported_strict),
        ("none_backend_strict_fails_closed", none_strict),
        ("reasoner_strict_and_outlines_whitespace_preserved", reasoner),
    ]
    results = []
    for name, call in cases:
        try:
            call(Harness(source))
            results.append({"name": name, "passed": True})
        except Exception as error:
            results.append({"name": name, "passed": False, "error_type": type(error).__name__, "error": str(error)})
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--expect", choices=("baseline", "fixed"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    names = ("base_grammar_backend.py", "xgrammar_backend.py")
    raw = {name: (args.source_dir / name).read_bytes() for name in names}
    source = {name: data.decode("utf-8") for name, data in raw.items()}
    results = run_cases(source)
    failed = {row["name"] for row in results if not row["passed"]}
    unexpected = failed if args.expect == "fixed" else failed.symmetric_difference(REGRESSIONS)
    unchanged = all((args.source_dir / name).read_bytes() == data for name, data in raw.items())
    output = {
        "utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "passed": not unexpected and unchanged,
        "expected_state": args.expect,
        "all_contracts_passed": not failed,
        "cases": len(results),
        "regression_failures": sorted(failed),
        "unexpected_results": sorted(unexpected),
        "results": results,
        "scope": "CPU_execute_actual_factory_and_constructor_AST_with_boundary_doubles",
        "production_ast": Harness(source).production_ast,
        "dependency_doubles": ["runtime context", "native grammar compiler and tokenizer-info construction", "backend initialization/wrapping boundaries"],
        "not_verified": ["full_runtime_module_import", "native_xgrammar_FSM_bitmasks", "real_model_tokenizer", "GPU_or_TEE_inference"],
        "source_sha256": {name: hashlib.sha256(data).hexdigest() for name, data in raw.items()},
        "harness_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "source_files_unchanged": unchanged,
        "python": sys.version,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2))
    raise SystemExit(0 if output["passed"] else 1)


if __name__ == "__main__":
    main()
