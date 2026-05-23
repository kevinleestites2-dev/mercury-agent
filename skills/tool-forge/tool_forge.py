"""
Agent Zero — Layer 9: Tool Forge
Source: tiny-self-improve-ai (kevinleestites2-dev/tiny-self-improve-ai)

Autonomous tool creation engine.
Reflects on capability gaps, writes new tools, tests them, persists to registry.
"""

import ast
import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Optional
import urllib.request


TOOLS_REGISTRY = Path("agent_zero_tools.json")
TOOLS_DOCS = Path("agent_zero_tools_docs.md")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")


def _load_registry() -> dict:
    if TOOLS_REGISTRY.exists():
        try:
            return json.loads(TOOLS_REGISTRY.read_text())
        except Exception:
            pass
    return {}


def _save_registry(registry: dict):
    TOOLS_REGISTRY.write_text(json.dumps(registry, indent=2))


def _llm(prompt: str, system: str, token: str, max_tokens: int = 1500) -> str:
    payload = json.dumps({
        "model": "gpt-4o",
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": max_tokens
    }).encode()
    req = urllib.request.Request(
        "https://models.inference.ai.azure.com/chat/completions",
        data=payload, method="POST",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        d = json.loads(resp.read())
    return d["choices"][0]["message"]["content"].strip()


def _strip_fences(code: str) -> str:
    if code.startswith("```"):
        lines = code.split("\n")
        end = -1 if lines[-1].strip() == "```" else len(lines)
        return "\n".join(lines[1:end])
    return code


def _auto_test(func_source: str) -> tuple[bool, str]:
    """Parse type hints and run basic smoke test."""
    try:
        tree = ast.parse(func_source)
        func_def = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef))
        func_name = func_def.name

        ns = {}
        exec(func_source, ns)
        fn = ns[func_name]

        # Try calling with default/zero values based on annotations
        args = []
        for arg in func_def.args.args:
            ann = ast.unparse(arg.annotation) if arg.annotation else "str"
            if "int" in ann: args.append(0)
            elif "float" in ann: args.append(0.0)
            elif "str" in ann: args.append("test")
            elif "list" in ann: args.append([])
            elif "dict" in ann: args.append({})
            elif "bool" in ann: args.append(True)
            else: args.append(None)

        result = fn(*args)
        return True, f"Called {func_name}({args}) → {repr(result)}"
    except Exception as e:
        return False, str(e)


def reflect(token: str = "") -> list[str]:
    """Internal monologue — identify capability gaps."""
    t = token or GITHUB_TOKEN
    registry = _load_registry()
    existing = list(registry.keys())

    response = _llm(
        prompt=(
            f"Existing tools: {existing}\n\n"
            "Identify 3 high-value capabilities that a Pantheon AI agent would benefit from "
            "but currently lacks. Focus on: web scraping, data parsing, crypto/finance, "
            "system monitoring, or automation. Return a JSON array of 3 strings, each "
            "describing a specific missing tool."
        ),
        system="You are an AI capability analyst. Return only a JSON array of 3 strings.",
        token=t,
        max_tokens=300
    )
    try:
        gaps = json.loads(response)
        return gaps if isinstance(gaps, list) else []
    except Exception:
        return []


def forge(
    tool_description: str,
    token: str = "",
    max_retries: int = 2
) -> dict:
    """
    Forge a new tool from a description.

    Returns: { success, tool_name, source, test_result }
    """
    t = token or GITHUB_TOKEN
    registry = _load_registry()

    # Generate the tool
    source = _llm(
        prompt=f"Build this tool: {tool_description}",
        system=(
            "You are an expert Python developer. Write a single, complete, well-documented "
            "Python function with: type hints, docstring, error handling, and a clear name. "
            "Return ONLY the Python function source code. No imports outside the function body. "
            "No explanation. No markdown fences."
        ),
        token=t
    )
    source = _strip_fences(source)

    # Extract name
    try:
        tree = ast.parse(source)
        func_def = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef))
        tool_name = func_def.name
    except Exception as e:
        return {"success": False, "error": f"Could not parse generated code: {e}"}

    # Check for duplicate
    if tool_name in registry:
        return {"success": False, "error": f"Tool {tool_name!r} already exists in registry"}

    # Test
    for attempt in range(max_retries + 1):
        passed, test_output = _auto_test(source)
        if passed:
            break
        if attempt < max_retries:
            # Ask LLM to fix
            source = _strip_fences(_llm(
                prompt=f"Fix this Python function:\n{source}\n\nError: {test_output}",
                system="Return only the corrected Python function. No explanation. No fences.",
                token=t
            ))
        else:
            return {
                "success": False,
                "tool_name": tool_name,
                "source": source,
                "error": f"Tests failed after {max_retries + 1} attempts: {test_output}"
            }

    # Register
    registry[tool_name] = source
    _save_registry(registry)

    # Update docs
    existing_docs = TOOLS_DOCS.read_text() if TOOLS_DOCS.exists() else "# Agent Zero Tool Registry\n\n"
    TOOLS_DOCS.write_text(
        existing_docs + f"\n## `{tool_name}`\n"
        f"Forged: {datetime.now().isoformat()}\n"
        f"Description: {tool_description}\n"
        f"Test: {test_output}\n"
    )

    return {
        "success": True,
        "tool_name": tool_name,
        "source": source,
        "test_result": test_output,
        "registry_size": len(registry)
    }


def list_tools() -> list[str]:
    return list(_load_registry().keys())


if __name__ == "__main__":
    import os
    tok = os.environ.get("GITHUB_TOKEN", "")

    print("Reflecting on capability gaps...")
    gaps = reflect(tok)
    print(f"Gaps identified: {gaps}")

    if gaps:
        print(f"\nForging first gap: {gaps[0]}")
        result = forge(gaps[0], tok)
        print(f"Result: {json.dumps({k: v for k, v in result.items() if k != 'source'}, indent=2)}")
        print(f"\nRegistry now contains: {list_tools()}")
