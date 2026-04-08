"""Codebase indexer — scans the Solidus e-commerce repo and builds a searchable file index.

Used at startup to pre-index the codebase, then at triage time to find relevant files
for a given incident description.
"""

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)

# File extensions we care about for triage context
INDEXABLE_EXTENSIONS = {
    ".rb", ".erb", ".haml", ".slim",  # Ruby/Rails
    ".js", ".ts", ".jsx", ".tsx",     # JavaScript/TypeScript
    ".yml", ".yaml",                   # Config
    ".json",                           # Config/data
    ".rake",                           # Rake tasks
}

# Directories to skip
SKIP_DIRS = {
    ".git", "node_modules", "vendor", "tmp", "log", "coverage",
    ".bundle", "spec/fixtures", "test/fixtures",
}

# Max file size to index (skip huge generated files)
MAX_FILE_SIZE = 50_000  # 50KB

# Max lines to include as snippet
MAX_SNIPPET_LINES = 80


@dataclass(frozen=True)
class IndexedFile:
    """A file in the codebase index."""
    path: str              # relative path from repo root
    extension: str
    size: int
    keywords: frozenset[str]  # extracted keywords for matching
    first_lines: str       # first N lines as preview


@dataclass
class CodebaseIndex:
    """Searchable index of a codebase."""
    repo_path: str
    files: list[IndexedFile] = field(default_factory=list)
    structure_summary: str = ""
    readme_content: str = ""

    @property
    def file_count(self) -> int:
        return len(self.files)


def _extract_keywords(content: str, filepath: str) -> frozenset[str]:
    """Extract searchable keywords from file content and path."""
    keywords: set[str] = set()

    # Path components as keywords
    parts = Path(filepath).parts
    for part in parts:
        # Split on underscores, hyphens, dots
        tokens = re.split(r"[_\-./]", part)
        keywords.update(t.lower() for t in tokens if len(t) > 2)

    # Class/module names (Ruby: class Foo, module Bar)
    for match in re.finditer(r"(?:class|module)\s+(\w+)", content):
        name = match.group(1)
        keywords.add(name.lower())
        # Also add snake_case version of CamelCase
        snake = re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()
        keywords.add(snake)

    # Method definitions (Ruby: def foo_bar)
    for match in re.finditer(r"def\s+(self\.)?(\w+)", content):
        keywords.add(match.group(2).lower())

    # Rails-specific: model associations, validations
    for match in re.finditer(
        r"(?:has_many|has_one|belongs_to|has_and_belongs_to_many)\s+:(\w+)", content
    ):
        keywords.add(match.group(1).lower())

    # Common domain terms from content
    domain_patterns = [
        r"(?:order|payment|checkout|cart|product|variant|shipment|inventory)",
        r"(?:user|admin|customer|address|tax|promotion|refund|return)",
        r"(?:stock|price|line_item|adjustment|credit_card|store)",
    ]
    for pattern in domain_patterns:
        for match in re.finditer(pattern, content, re.IGNORECASE):
            keywords.add(match.group(0).lower())

    return frozenset(keywords)


def _build_structure_summary(repo_path: Path, files: list[IndexedFile]) -> str:
    """Build a concise directory structure summary."""
    dirs: set[str] = set()
    for f in files:
        parent = str(Path(f.path).parent)
        if parent != ".":
            # Keep only top 2 levels
            parts = Path(parent).parts[:2]
            dirs.add("/".join(parts))

    sorted_dirs = sorted(dirs)
    lines = [f"Repository: {repo_path.name}", f"Total indexed files: {len(files)}", ""]
    lines.append("Key directories:")
    for d in sorted_dirs[:30]:  # cap at 30 dirs
        count = sum(1 for f in files if f.path.startswith(d))
        lines.append(f"  {d}/ ({count} files)")

    return "\n".join(lines)


def build_index(repo_path: str) -> CodebaseIndex:
    """Scan the codebase and build a searchable index.

    This runs at startup and is intentionally synchronous since it's a one-time
    cost that completes before the app starts serving requests.
    """
    root = Path(repo_path)
    if not root.exists():
        logger.warning("Codebase repo not found at %s — index will be empty", repo_path)
        return CodebaseIndex(repo_path=repo_path)

    files: list[IndexedFile] = []

    for filepath in root.rglob("*"):
        if not filepath.is_file():
            continue

        # Skip excluded directories
        rel = filepath.relative_to(root)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue

        # Skip non-indexable extensions
        if filepath.suffix not in INDEXABLE_EXTENSIONS:
            continue

        # Skip large files
        try:
            size = filepath.stat().st_size
        except OSError:
            continue
        if size > MAX_FILE_SIZE:
            continue

        try:
            content = filepath.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

        lines = content.splitlines()
        first_lines = "\n".join(lines[:MAX_SNIPPET_LINES])
        keywords = _extract_keywords(content, str(rel))

        files.append(
            IndexedFile(
                path=str(rel),
                extension=filepath.suffix,
                size=size,
                keywords=keywords,
                first_lines=first_lines,
            )
        )

    # Read README if available
    readme_content = ""
    for readme_name in ("README.md", "README.rdoc", "README.txt", "README"):
        readme_path = root / readme_name
        if readme_path.exists():
            try:
                readme_content = readme_path.read_text(encoding="utf-8", errors="replace")[:3000]
            except OSError:
                pass
            break

    structure = _build_structure_summary(root, files)

    index = CodebaseIndex(
        repo_path=repo_path,
        files=files,
        structure_summary=structure,
        readme_content=readme_content,
    )
    logger.info("Codebase index built: %d files from %s", len(files), repo_path)
    return index


def search_files(
    index: CodebaseIndex,
    query: str,
    max_results: int = 5,
) -> list[IndexedFile]:
    """Search the index for files relevant to a query string.

    Uses keyword overlap scoring — simple but effective for this use case.
    """
    # Tokenize query
    query_tokens = set(re.split(r"[\s_\-./,;:]+", query.lower()))
    query_tokens = {t for t in query_tokens if len(t) > 2}

    if not query_tokens:
        return []

    scored: list[tuple[float, IndexedFile]] = []
    for file in index.files:
        overlap = query_tokens & file.keywords
        if not overlap:
            continue

        # Score: overlap count + bonus for path matches
        score = len(overlap)

        # Boost .rb files (core Rails code)
        if file.extension == ".rb":
            score *= 1.5

        # Boost model/controller/service files
        path_lower = file.path.lower()
        if any(d in path_lower for d in ("models/", "controllers/", "services/")):
            score *= 1.3

        scored.append((score, file))

    # Sort by score descending
    scored.sort(key=lambda x: x[0], reverse=True)
    return [f for _, f in scored[:max_results]]