"""
Agent Zero — Layer 8: Evolution Engine
Source: Entwickler (kevinleestites2-dev/Entwickler)

Self-evolving coding agent. Patches failing layers autonomously.
Triggered by SAFLA when cycle score < 0.40 or on Forgemaster command.
"""

import json
import os
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
import urllib.request


GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_API = "https://api.github.com"
JOURNAL_FILE = Path("JOURNAL.md")
MAX_ATTEMPTS = 3


def _llm_patch(source: str, error_context: str, github_token: str) -> str:
    """Ask the LLM to generate a minimal patch for the failing source."""
    payload = json.dumps({
        "model": "gpt-4o",
        "messages": [
            {"role": "system", "content": (
                "You are a surgical code patcher. Given source code and an error/performance "
                "issue, generate the minimal corrected version of the FULL file. "
                "Preserve all existing logic. Fix only what is broken. "
                "Return ONLY the corrected Python source code, no explanation."
            )},
            {"role": "user", "content": (
                f"SOURCE:\n```python\n{source}\n```\n\n"
                f"ISSUE:\n{error_context}"
            )}
        ],
        "max_tokens": 2000
    }).encode()

    req = urllib.request.Request(
        "https://models.inference.ai.azure.com/chat/completions",
        data=payload, method="POST",
        headers={
            "Authorization": f"Bearer {github_token}",
            "Content-Type": "application/json"
        }
    )
    with urllib.request.urlopen(req) as resp:
        d = json.loads(resp.read())
        return d["choices"][0]["message"]["content"].strip()


def _run_tests(test_cmd: str) -> tuple[bool, str]:
    """Run tests. Returns (passed, output)."""
    result = subprocess.run(
        test_cmd, shell=True, capture_output=True, text=True, timeout=60
    )
    passed = result.returncode == 0
    output = (result.stdout + result.stderr)[:1000]
    return passed, output


def _append_journal(entry: str):
    """Append evolution cycle to JOURNAL.md."""
    current = JOURNAL_FILE.read_text() if JOURNAL_FILE.exists() else ""
    JOURNAL_FILE.write_text(entry + "\n\n" + current)


def evolve(
    layer_file: str,
    error_context: str,
    test_cmd: Optional[str] = None,
    github_token: str = ""
) -> dict:
    """
    Run an evolution cycle on a failing layer.

    Args:
        layer_file:    Path to the Python source to evolve
        error_context: Description of the failure or SAFLA score
        test_cmd:      Shell command to run tests (optional)
        github_token:  GitHub PAT for LLM calls

    Returns:
        { success, attempts, patch_summary, journal_entry }
    """
    token = github_token or GITHUB_TOKEN
    path = Path(layer_file)

    if not path.exists():
        return {"success": False, "error": f"File not found: {layer_file}"}

    original_source = path.read_text()
    backup = path.with_suffix(".py.bak")
    backup.write_text(original_source)

    result = {"success": False, "attempts": 0, "layer": layer_file}
    ts = datetime.now(timezone.utc).isoformat()

    for attempt in range(1, MAX_ATTEMPTS + 1):
        result["attempts"] = attempt
        print(f"[Evolution] Attempt {attempt}/{MAX_ATTEMPTS} on {layer_file}")

        # Generate patch
        patched = _llm_patch(original_source, error_context, token)

        # Strip markdown fences if present
        if patched.startswith("```"):
            lines = patched.split("\n")
            patched = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])

        # Write patch
        path.write_text(patched)

        # Test
        if test_cmd:
            passed, test_output = _run_tests(test_cmd)
        else:
            # Syntax check at minimum
            import ast as _ast
            try:
                _ast.parse(patched)
                passed, test_output = True, "syntax ok"
            except SyntaxError as e:
                passed, test_output = False, str(e)

        if passed:
            summary = f"Attempt {attempt}: patch applied, tests passed"
            journal = (
                f"## [{ts}] Evolution Cycle — {layer_file}\n"
                f"- Trigger: {error_context[:200]}\n"
                f"- Attempts: {attempt}\n"
                f"- Result: ✅ PASS\n"
                f"- Test output: {test_output[:300]}\n"
            )
            _append_journal(journal)
            backup.unlink(missing_ok=True)
            result.update({"success": True, "patch_summary": summary,
                           "journal_entry": journal})
            print(f"[Evolution] ✅ Success on attempt {attempt}")
            return result
        else:
            print(f"[Evolution] ❌ Attempt {attempt} failed: {test_output[:200]}")
            # Revert and try again with more context
            path.write_text(original_source)
            error_context += f"\n\nPrevious patch failed with: {test_output[:300]}"

    # All attempts failed
    path.write_text(original_source)  # restore original
    backup.unlink(missing_ok=True)
    journal = (
        f"## [{ts}] Evolution Cycle — {layer_file}\n"
        f"- Trigger: {error_context[:200]}\n"
        f"- Attempts: {MAX_ATTEMPTS}\n"
        f"- Result: ❌ FAILED — reverted to original\n"
    )
    _append_journal(journal)
    result["journal_entry"] = journal
    result["error"] = "All evolution attempts failed. Original restored. Escalate to Forgemaster."
    return result


if __name__ == "__main__":
    # Demo: try to evolve a trivially broken file
    import tempfile, os
    broken = "def add(a, b):\n    return a - b  # bug: should be +"
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(broken)
        fname = f.name

    r = evolve(
        layer_file=fname,
        error_context="add(2, 3) returns -1 but should return 5",
        test_cmd=None,
        github_token=os.environ.get("GITHUB_TOKEN", "")
    )
    print(json.dumps(r, indent=2))
    os.unlink(fname)
