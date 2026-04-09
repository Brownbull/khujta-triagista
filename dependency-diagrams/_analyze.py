#!/usr/bin/env python3
"""Python dependency analyzer — generates DOT graph + metrics from import statements."""

import ast
import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
APP_DIR = PROJECT_ROOT / "app"
PACKAGE = "app"

# Layer classification for architectural analysis
LAYER_ORDER = {
    "config": 0,
    "database": 1,
    "models": 2,
    "schemas": 3,
    "services": 4,
    "pipeline": 5,
    "routes": 6,
    "main": 7,
}

def classify_layer(module_path: str) -> str:
    """Classify a module into an architectural layer."""
    parts = module_path.replace("app/", "").split("/")
    if not parts:
        return "unknown"
    first = parts[0].replace(".py", "")
    if first in LAYER_ORDER:
        return first
    return "unknown"

def get_layer_rank(layer: str) -> int:
    return LAYER_ORDER.get(layer, -1)

def extract_imports(filepath: Path) -> list[str]:
    """Extract internal (app.*) imports from a Python file."""
    try:
        source = filepath.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(filepath))
    except (SyntaxError, UnicodeDecodeError):
        return []

    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            if node.module.startswith(PACKAGE + ".") or node.module == PACKAGE:
                imports.append(node.module)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith(PACKAGE + "."):
                    imports.append(alias.name)
    return imports

def module_to_path(module: str) -> str:
    """Convert dotted module to relative path (app.models.incident -> app/models/incident.py)."""
    parts = module.split(".")
    # Could be a package (__init__) or a module (.py)
    path = "/".join(parts) + ".py"
    if (PROJECT_ROOT / path).is_file():
        return path
    init = "/".join(parts) + "/__init__.py"
    if (PROJECT_ROOT / init).is_file():
        return init
    # Best guess
    return path

def path_to_module(filepath: Path) -> str:
    """Convert file path to relative module path string."""
    rel = filepath.relative_to(PROJECT_ROOT)
    return str(rel)

def find_cycles(graph: dict[str, set[str]]) -> list[list[str]]:
    """DFS cycle detection."""
    cycles = []
    visited = set()
    rec_stack = set()
    path = []

    def dfs(node):
        visited.add(node)
        rec_stack.add(node)
        path.append(node)

        for neighbor in sorted(graph.get(node, set())):
            if neighbor not in visited:
                dfs(neighbor)
            elif neighbor in rec_stack:
                idx = path.index(neighbor)
                cycle = path[idx:] + [neighbor]
                cycles.append(cycle)

        path.pop()
        rec_stack.discard(node)

    for node in sorted(graph.keys()):
        if node not in visited:
            dfs(node)

    return cycles

def main():
    # Collect all Python files
    py_files = sorted(APP_DIR.rglob("*.py"))

    # Build dependency graph
    edges: list[tuple[str, str]] = []
    graph: dict[str, set[str]] = defaultdict(set)
    all_nodes: set[str] = set()

    for filepath in py_files:
        src = path_to_module(filepath)
        all_nodes.add(src)
        imports = extract_imports(filepath)
        for imp in imports:
            target = module_to_path(imp)
            all_nodes.add(target)
            edges.append((src, target))
            graph[src].add(target)

    # Metrics
    fan_out = defaultdict(int)
    fan_in = defaultdict(int)
    for src, tgt in edges:
        fan_out[src] += 1
        fan_in[tgt] += 1

    # Orphaned modules (no in, no out)
    orphans = [n for n in all_nodes if fan_in[n] == 0 and fan_out[n] == 0]

    # Entry points (outgoing but no incoming)
    entry_points = [n for n in all_nodes if fan_in[n] == 0 and fan_out[n] > 0]

    # Cycles
    cycles = find_cycles(graph)

    # Layer violations (lower layer importing higher layer)
    # Allowed: config <- models <- schemas <- services <- pipeline <- routes <- main
    # Violation: e.g., models importing routes
    violations = []
    for src, tgt in edges:
        src_layer = classify_layer(src)
        tgt_layer = classify_layer(tgt)
        src_rank = get_layer_rank(src_layer)
        tgt_rank = get_layer_rank(tgt_layer)
        if src_rank >= 0 and tgt_rank >= 0 and src_rank < tgt_rank:
            violations.append((src, tgt, src_layer, tgt_layer))

    # Cross-layer matrix
    layer_matrix = defaultdict(lambda: defaultdict(int))
    for src, tgt in edges:
        sl = classify_layer(src)
        tl = classify_layer(tgt)
        layer_matrix[sl][tl] += 1

    # Sub-package cross-imports (e.g., pipeline/triage -> pipeline/guardrail)
    subpkg_cross = []
    for src, tgt in edges:
        src_parts = src.split("/")
        tgt_parts = tgt.split("/")
        if len(src_parts) >= 3 and len(tgt_parts) >= 3:
            if src_parts[1] == tgt_parts[1]:  # same layer
                if src_parts[2] != tgt_parts[2]:  # different sub-package
                    subpkg_cross.append((src, tgt))

    # Generate DOT file
    dot_lines = ['digraph "python-deps" {', '  rankdir=LR;', '  node [shape=box, style=filled, fillcolor="#e8e8e8"];']

    # Color nodes by layer
    layer_colors = {
        "config": "#f9e2af",
        "database": "#f9e2af",
        "models": "#a6e3a1",
        "schemas": "#89dceb",
        "services": "#cba6f7",
        "pipeline": "#f38ba8",
        "routes": "#fab387",
        "main": "#eba0ac",
        "unknown": "#e8e8e8",
    }

    for node in sorted(all_nodes):
        layer = classify_layer(node)
        color = layer_colors.get(layer, "#e8e8e8")
        label = node.replace("app/", "").replace(".py", "").replace("/__init__", "/")
        dot_lines.append(f'  "{node}" [label="{label}", fillcolor="{color}"];')

    for src, tgt in sorted(set(edges)):
        dot_lines.append(f'  "{src}" -> "{tgt}";')

    dot_lines.append("}")
    dot_content = "\n".join(dot_lines)

    out_dir = PROJECT_ROOT / "dependency-diagrams"
    out_dir.mkdir(exist_ok=True)

    (out_dir / "dependency-graph.dot").write_text(dot_content)

    # Try to generate SVG
    import subprocess
    try:
        subprocess.run(
            ["dot", "-Tsvg", "-o", str(out_dir / "dependency-graph.svg")],
            input=dot_content, text=True, check=True, capture_output=True,
        )
        svg_ok = True
    except (subprocess.CalledProcessError, FileNotFoundError):
        svg_ok = False

    # Output JSON metrics for report generation
    results = {
        "total_modules": len(all_nodes),
        "total_edges": len(edges),
        "unique_edges": len(set(edges)),
        "cycles": [list(c) for c in cycles],
        "orphans": sorted(orphans),
        "entry_points": sorted(entry_points),
        "fan_out_top": sorted(fan_out.items(), key=lambda x: -x[1])[:15],
        "fan_in_top": sorted(fan_in.items(), key=lambda x: -x[1])[:15],
        "violations": [(s, t, sl, tl) for s, t, sl, tl in violations],
        "subpkg_cross": subpkg_cross,
        "layer_matrix": {k: dict(v) for k, v in layer_matrix.items()},
        "svg_generated": svg_ok,
        "all_nodes": sorted(all_nodes),
    }

    (out_dir / "_metrics.json").write_text(json.dumps(results, indent=2))
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
