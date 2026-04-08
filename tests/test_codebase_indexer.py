"""Tests for the codebase indexer service."""

import os
import tempfile
from pathlib import Path

from app.services.codebase_indexer import (
    CodebaseIndex,
    build_index,
    search_files,
    _extract_keywords,
)


def _make_repo(tmp: str) -> str:
    """Create a minimal fake repo structure for testing."""
    root = Path(tmp)

    # Models
    models_dir = root / "app" / "models"
    models_dir.mkdir(parents=True)
    (models_dir / "order.rb").write_text(
        "class Spree::Order < ApplicationRecord\n"
        "  has_many :line_items\n"
        "  has_many :payments\n"
        "  belongs_to :user\n"
        "  def total\n"
        "    line_items.sum(&:amount)\n"
        "  end\n"
        "end\n"
    )
    (models_dir / "payment.rb").write_text(
        "class Spree::Payment < ApplicationRecord\n"
        "  belongs_to :order\n"
        "  has_one :source\n"
        "  def process!\n"
        "    gateway.purchase(amount)\n"
        "  end\n"
        "end\n"
    )

    # Controllers
    ctrl_dir = root / "app" / "controllers"
    ctrl_dir.mkdir(parents=True)
    (ctrl_dir / "checkout_controller.rb").write_text(
        "class Spree::CheckoutController < ApplicationController\n"
        "  def update\n"
        "    # handles checkout steps\n"
        "  end\n"
        "end\n"
    )

    # Config
    (root / "config.yml").write_text("database: postgres\n")

    # Should be skipped
    git_dir = root / ".git"
    git_dir.mkdir()
    (git_dir / "HEAD").write_text("ref: refs/heads/main\n")

    # README
    (root / "README.md").write_text("# Solidus E-Commerce\nA Rails e-commerce platform.\n")

    return str(root)


def test_build_index_creates_file_entries():
    with tempfile.TemporaryDirectory() as tmp:
        repo_path = _make_repo(tmp)
        index = build_index(repo_path)

        assert index.file_count >= 3  # 2 models + 1 controller + config
        paths = {f.path for f in index.files}
        assert "app/models/order.rb" in paths
        assert "app/models/payment.rb" in paths
        assert "app/controllers/checkout_controller.rb" in paths


def test_build_index_skips_git_dir():
    with tempfile.TemporaryDirectory() as tmp:
        repo_path = _make_repo(tmp)
        index = build_index(repo_path)

        paths = {f.path for f in index.files}
        assert not any(".git" in p for p in paths)


def test_build_index_reads_readme():
    with tempfile.TemporaryDirectory() as tmp:
        repo_path = _make_repo(tmp)
        index = build_index(repo_path)

        assert "Solidus" in index.readme_content


def test_build_index_missing_repo():
    index = build_index("/nonexistent/path/to/repo")
    assert index.file_count == 0


def test_search_files_finds_payment():
    with tempfile.TemporaryDirectory() as tmp:
        repo_path = _make_repo(tmp)
        index = build_index(repo_path)

        results = search_files(index, "payment processing gateway error")
        assert len(results) > 0
        paths = [f.path for f in results]
        assert "app/models/payment.rb" in paths


def test_search_files_finds_checkout():
    with tempfile.TemporaryDirectory() as tmp:
        repo_path = _make_repo(tmp)
        index = build_index(repo_path)

        results = search_files(index, "checkout page 500 error update step")
        assert len(results) > 0
        paths = [f.path for f in results]
        assert "app/controllers/checkout_controller.rb" in paths


def test_search_files_finds_order():
    with tempfile.TemporaryDirectory() as tmp:
        repo_path = _make_repo(tmp)
        index = build_index(repo_path)

        results = search_files(index, "order total line items calculation wrong")
        assert len(results) > 0
        paths = [f.path for f in results]
        assert "app/models/order.rb" in paths


def test_search_files_empty_query():
    index = CodebaseIndex(repo_path="/tmp")
    results = search_files(index, "")
    assert results == []


def test_search_files_no_matches():
    with tempfile.TemporaryDirectory() as tmp:
        repo_path = _make_repo(tmp)
        index = build_index(repo_path)

        results = search_files(index, "xyzzy nonexistent gibberish")
        assert results == []


def test_extract_keywords_from_ruby():
    content = (
        "class Spree::Payment < ApplicationRecord\n"
        "  belongs_to :order\n"
        "  def process!\n"
        "    gateway.purchase(amount)\n"
        "  end\n"
        "end\n"
    )
    keywords = _extract_keywords(content, "app/models/payment.rb")
    assert "payment" in keywords
    assert "order" in keywords
    assert "spree" in keywords


def test_structure_summary_generated():
    with tempfile.TemporaryDirectory() as tmp:
        repo_path = _make_repo(tmp)
        index = build_index(repo_path)

        assert "app/models" in index.structure_summary
        assert "app/controllers" in index.structure_summary
