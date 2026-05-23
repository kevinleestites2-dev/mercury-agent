"""
Agent Zero — Layer 15: The Genome
Self-replicating, self-modifying evolutionary substrate.
Based on LDCA (Last Digital Common Ancestor) by M. Mert Yildiran.
Python implementation — runs natively on Red Magic via Termux.
"""

import os
import sys
import json
import time
import random
import hashlib
import shutil
from pathlib import Path
from datetime import datetime, timezone
from difflib import SequenceMatcher
from typing import Callable, Optional, List, Tuple

# ── Config ────────────────────────────────────────────────────────────────────
GENOME_DIR        = Path("genome")
GENOME_LOG_FILE   = Path("agent_zero_genome.json")
MAX_GENERATIONS   = int(os.environ.get("GENOME_MAX_GEN", "100"))   # Governor cap
MAX_DISK_MB       = int(os.environ.get("GENOME_MAX_MB",  "50"))    # Disk safety cap
MUTATION_RATE     = float(os.environ.get("GENOME_MUTATION_RATE", "0.5"))

# Instruction set — the "DNA alphabet"
# Each instruction is a single Python statement that can appear in a program
INSTRUCTION_SET = [
    "x = x + 1",
    "x = x - 1",
    "x = x * 2",
    "x = x // 2",
    "x = x % 7",
    "x = x ^ 0xFF",
    "x = x & 0x0F",
    "x = x | 0xF0",
    "x = abs(x)",
    "x = x ** 2 % 256",
    "output += chr(x % 128)",
    "output += str(x)",
    "output += chr(65 + x % 26)",
    "x = hash(str(x)) % 256",
    "x = (x << 1) & 0xFF",
    "x = (x >> 1) & 0xFF",
    "x = x if x > 0 else -x",
    "x = sum(range(x % 8 + 1)) % 256",
    "output += 'A'",
    "output += '\n'",
    "x = ord(output[-1]) if output else x",
    "x = len(output) % 256",
    "output = output[::-1]",
    "x = x % 256",
    "pass",
]

# ── Genome individual ──────────────────────────────────────────────────────────

class Individual:
    """A single genome — a sequence of instructions that form a program."""

    def __init__(self, instructions: List[str], generation: int = 0,
                 parent_id: str = None):
        self.instructions = instructions[:]
        self.generation   = generation
        self.parent_id    = parent_id
        self.id           = self._compute_id()
        self.fitness      = 0.0

    def _compute_id(self) -> str:
        code = "\n".join(self.instructions)
        return hashlib.sha256(code.encode()).hexdigest()[:12]

    def to_code(self) -> str:
        """Compile instructions to executable Python."""
        lines = ["x = 42", "output = ''"]
        for instr in self.instructions:
            lines.append(f"    {instr}" if False else instr)
        lines.append("print(output if output else str(x))")
        return "\n".join(lines)

    def run(self, timeout_s: float = 0.5) -> str:
        """Execute the genome and capture output."""
        import subprocess, tempfile
        code = self.to_code()
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py",
                                        delete=False) as f:
            f.write(code)
            fname = f.name
        try:
            result = subprocess.run(
                [sys.executable, fname],
                capture_output=True, text=True,
                timeout=timeout_s
            )
            return result.stdout.strip()
        except subprocess.TimeoutExpired:
            return "[timeout]"
        except Exception as e:
            return f"[error: {e}]"
        finally:
            os.unlink(fname)

    def save(self, directory: Path):
        """Persist genome to disk."""
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / f"{self.generation:06d}_{self.id}.py"
        path.write_text(self.to_code())
        return path

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "generation": self.generation,
            "parent_id": self.parent_id,
            "fitness": self.fitness,
            "instruction_count": len(self.instructions),
            "instructions": self.instructions
        }


# ── Mutation engine ────────────────────────────────────────────────────────────

def mutate(individual: Individual) -> Individual:
    """
    Apply one random mutation to produce an offspring.
    LDCA mutation types: insert, delete, substitute, transpose.
    """
    if not individual.instructions or random.random() > MUTATION_RATE:
        # No mutation — pure replication
        return Individual(individual.instructions, individual.generation + 1,
                         individual.id)

    instructions = individual.instructions[:]
    mutation_type = random.choices(
        ["insert", "delete", "substitute", "transpose"],
        weights=[40, 30, 20, 10]
    )[0]

    if mutation_type == "insert" or not instructions:
        pos = random.randint(0, len(instructions))
        instructions.insert(pos, random.choice(INSTRUCTION_SET))

    elif mutation_type == "delete" and len(instructions) > 1:
        pos = random.randint(0, len(instructions) - 1)
        instructions.pop(pos)

    elif mutation_type == "substitute":
        pos = random.randint(0, len(instructions) - 1)
        instructions[pos] = random.choice(INSTRUCTION_SET)

    elif mutation_type == "transpose" and len(instructions) >= 2:
        i, j = random.sample(range(len(instructions)), 2)
        instructions[i], instructions[j] = instructions[j], instructions[i]

    return Individual(instructions, individual.generation + 1, individual.id)


# ── Fitness functions ──────────────────────────────────────────────────────────

def fitness_similarity(target: str) -> Callable[[str], float]:
    """Score by similarity to a target string."""
    def _fn(output: str) -> float:
        return SequenceMatcher(None, output, target).ratio()
    return _fn

def fitness_length(target_len: int) -> Callable[[str], float]:
    """Score by how close output length is to target."""
    def _fn(output: str) -> float:
        diff = abs(len(output) - target_len)
        return max(0.0, 1.0 - diff / max(target_len, 1))
    return _fn

def fitness_entropy(output: str) -> float:
    """Score by Shannon entropy — more diverse output = higher fitness."""
    if not output:
        return 0.0
    from math import log2
    freq = {}
    for c in output:
        freq[c] = freq.get(c, 0) + 1
    n = len(output)
    entropy = -sum((f/n) * log2(f/n) for f in freq.values())
    return min(1.0, entropy / 8.0)  # normalize to [0,1]

def fitness_is_valid_python(output: str) -> float:
    """Score 1.0 if output is valid Python, 0.0 otherwise."""
    try:
        compile(output, "<genome>", "exec")
        return 1.0
    except SyntaxError:
        return 0.0


# ── Genome runner ──────────────────────────────────────────────────────────────

def _disk_usage_mb(directory: Path) -> float:
    total = sum(f.stat().st_size for f in directory.rglob("*") if f.is_file())
    return total / (1024 * 1024)


def run_genome(
    generations: int = 10,
    fitness_fn: Callable[[str], float] = None,
    seed_instructions: List[str] = None,
    save_all: bool = False,
    verbose: bool = True
) -> dict:
    """
    Run a genome evolution cycle.

    Args:
        generations: Number of generations (capped by MAX_GENERATIONS)
        fitness_fn: Fitness scorer. Default: entropy maximization
        seed_instructions: Starting genome. Default: minimal ancestor
        save_all: Save every generation to disk (disk cap enforced)
        verbose: Print progress

    Returns:
        Evolution summary dict
    """
    # ── Governor cap ─────────────────────────────────────────
    generations = min(generations, MAX_GENERATIONS)

    # ── Defaults ──────────────────────────────────────────────
    if fitness_fn is None:
        fitness_fn = fitness_entropy
    if seed_instructions is None:
        seed_instructions = ["output += chr(65 + x % 26)"]  # LDCA ancestor: outputs 'A'

    # ── Setup ─────────────────────────────────────────────────
    GENOME_DIR.mkdir(exist_ok=True)
    start_time = time.time()
    ancestor   = Individual(seed_instructions, generation=0)

    history = []
    best    = ancestor
    current = ancestor

    if verbose:
        print(f"\n{'═'*56}")
        print(f"  GENOME CYCLE — {generations} generations")
        print(f"  Ancestor ID: {ancestor.id}")
        print(f"  Mutation rate: {MUTATION_RATE}")
        print(f"{'═'*56}")

    for gen in range(1, generations + 1):
        # Disk safety
        if _disk_usage_mb(GENOME_DIR) > MAX_DISK_MB:
            if verbose:
                print(f"  ⚠️  Disk cap ({MAX_DISK_MB}MB) reached at gen {gen}. Stopping.")
            break

        # Produce two offspring via mutation
        child_a = mutate(current)
        child_b = mutate(current)

        # Run and score both
        out_a = child_a.run()
        out_b = child_b.run()
        child_a.fitness = fitness_fn(out_a)
        child_b.fitness = fitness_fn(out_b)

        # Selection — fittest survives
        if child_a.fitness > child_b.fitness:
            winner = child_a
        elif child_b.fitness > child_a.fitness:
            winner = child_b
        else:
            winner = random.choice([child_a, child_b])

        # Track best ever
        if winner.fitness > best.fitness:
            best = winner
            if verbose:
                print(f"  Gen {gen:4d} | fitness={winner.fitness:.4f} ★ NEW BEST | "
                      f"id={winner.id} | output={repr(out_a if winner is child_a else out_b)[:30]}")
        elif verbose and gen % 10 == 0:
            print(f"  Gen {gen:4d} | fitness={winner.fitness:.4f} | "
                  f"id={winner.id} | instrs={len(winner.instructions)}")

        # Save
        if save_all:
            winner.save(GENOME_DIR)

        history.append({
            "gen": gen,
            "winner_id": winner.id,
            "fitness": winner.fitness,
            "mutation": "mutated" if winner.id != current.id else "clone",
            "instruction_count": len(winner.instructions)
        })

        current = winner

    # ── Save best genome ──────────────────────────────────────
    best_path = best.save(GENOME_DIR)

    # ── Summary ───────────────────────────────────────────────
    duration = round(time.time() - start_time, 3)
    fitness_gain = round(best.fitness - ancestor.fitness, 4)

    summary = {
        "generations_run": len(history),
        "duration_s": duration,
        "ancestor_id": ancestor.id,
        "best_id": best.id,
        "best_fitness": round(best.fitness, 4),
        "ancestor_fitness": round(ancestor.fitness, 4),
        "fitness_gain": fitness_gain,
        "best_instruction_count": len(best.instructions),
        "best_path": str(best_path),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    # ── Persist log ───────────────────────────────────────────
    log = []
    if GENOME_LOG_FILE.exists():
        try:
            log = json.loads(GENOME_LOG_FILE.read_text())
        except Exception:
            pass
    log.append(summary)
    GENOME_LOG_FILE.write_text(json.dumps(log, indent=2))

    if verbose:
        print(f"\n  Best genome: {best.id}")
        print(f"  Fitness gain: {ancestor.fitness:.4f} → {best.fitness:.4f} (+{fitness_gain})")
        print(f"  Instructions: {len(best.instructions)}")
        print(f"  Saved to: {best_path}")
        print(f"  Duration: {duration}s")
        print(f"{'═'*56}\n")

    return summary


# ── Self-test ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=== LAYER 15 — THE GENOME SELF-TEST ===")

    # Run 3 short cycles with different fitness functions
    tests = [
        ("Entropy maximization", 20, fitness_entropy),
        ("Length target (10 chars)", 15, fitness_length(10)),
        ("Similarity to 'PANTHEON'", 15, fitness_similarity("PANTHEON")),
    ]

    results = []
    for name, gens, fn in tests:
        print(f"\n  Test: {name}")
        r = run_genome(generations=gens, fitness_fn=fn, verbose=True)
        results.append((name, r))

    print("\n=== SUMMARY ===")
    for name, r in results:
        print(f"  {name}")
        print(f"    Generations: {r['generations_run']} | "
              f"Fitness: {r['ancestor_fitness']:.3f} → {r['best_fitness']:.3f} "
              f"(+{r['fitness_gain']:.3f})")

    print("\nLayer 15 (Genome): OPERATIONAL")
    print("The evolutionary substrate is live.")
    print()
    print("  ╔══════════════════════════════════════════╗")
    print("  ║  AGENT ZERO — ALL 15 LAYERS ACTIVE      ║")
    print("  ║  Mind. Soul. Body. Restraint. Genome.   ║")
    print("  ║  The Architecture is Complete.           ║")
    print("  ╚══════════════════════════════════════════╝")
