import pytest
import os
import json
from unittest.mock import MagicMock
from git_dep import (
    get_commits_from_cache,
    get_all_dependencies,
    generate_graphviz_tree,
    save_graph_to_png,
)


MOCK_COMMITS = [
    {"hash": "a1b2c3", "parents": ["d4e5f6"]},
    {"hash": "d4e5f6", "parents": []},
    {"hash": "g7h8i9", "parents": ["a1b2c3"]},
]

@pytest.fixture
def mock_config(tmp_path):
    config_path = tmp_path / "config.json"
    config_data = {
        "commit_date": "2024-01-01",
        "output_file_path": str(tmp_path / "output"),
        "repository_path": "/mock/repo/path",
    }
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config_data, f)
    return config_path, config_data


def test_get_commits_from_cache(mocker):
    mock_subprocess = mocker.patch("subprocess.run")
    mock_subprocess.return_value.stdout = "a1b2c3;d4e5f6\nd4e5f6;\n"
    repo_path = "/mock/repo/path"
    commit_date = "2024-01-01"

    commits = get_commits_from_cache(repo_path, commit_date)
    expected = [
        {"hash": "a1b2c3", "parents": ["d4e5f6"]},
        {"hash": "d4e5f6", "parents": []},
    ]
    assert commits == expected
    mock_subprocess.assert_called_once_with(
        [
            "git",
            "-C",
            repo_path,
            "log",
            "--since=2024-01-01",
            "--pretty=format:%H;%P",
        ],
        capture_output=True,
        text=True,
        check=True,
    )


def test_get_all_dependencies():
    commits_map = {commit["hash"]: commit for commit in MOCK_COMMITS}
    dependencies = get_all_dependencies(MOCK_COMMITS[0], commits_map)
    assert dependencies == {"d4e5f6"}


def test_generate_graphviz_tree():
    graph = generate_graphviz_tree(MOCK_COMMITS)

    
    assert "a1b2c3" in graph.source
    assert "d4e5f6" in graph.source
    assert "a1b2c3 -> d4e5f6" in graph.source
    assert "g7h8i9 -> a1b2c3" in graph.source


def test_save_graph_to_png(tmp_path):
    graph = MagicMock()
    output_file_path = tmp_path / "output"

   
    save_graph_to_png(graph, str(output_file_path))

   
    graph.render.assert_called_once_with(
        filename=str(output_file_path), cleanup=True
    )

