"""Plain-python test runner (no pytest required).

Run:  python3 tests/run_all.py
"""

import importlib
import os
import sys
import traceback

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

TEST_MODULES = [
    "test_types",
    "test_speech_model",
    "test_script_engine",
    "test_claims",
    "test_validator",
    "test_repair",
    "test_reference_brand",
    "test_pipeline",
]


def main():
    passed = 0
    failed = 0
    failures = []
    for mod_name in TEST_MODULES:
        mod = importlib.import_module(mod_name)
        funcs = sorted(
            (n, f) for n, f in vars(mod).items()
            if callable(f) and n.startswith("test_")
        )
        if not funcs:
            continue
        print(f"== {mod_name}")
        for fname, fn in funcs:
            try:
                fn()
                passed += 1
                print(f"   ok  {fname}")
            except Exception:
                failed += 1
                failures.append(f"{mod_name}.{fname}")
                print(f"   FAIL {fname}")
                traceback.print_exc()
                print("  " + "-" * 40)
    print(f"\n{passed} passed, {failed} failed")
    if failures:
        print("Failures:")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)


if __name__ == "__main__":
    main()