import os
import subprocess
import json
import argparse
from graphviz import Digraph

def get_commits_from_cache(repo_path, commit_date):
    try:
        log_format = "--pretty=format:%H;%P" 
        git_command = [
            "git",
            "-C",
            repo_path,
            "log",
            f"--since={commit_date}",
            log_format,
        ]
        result = subprocess.run(
            git_command, capture_output=True, text=True, check=True
        )

        commits = []
        for line in result.stdout.strip().split("\n"):
            parts = line.split(";")
            commit = {
                "hash": parts[0],
                "parents": parts[1].split() if len(parts) > 1 and parts[1] else [],
            }
            commits.append(commit)
        return commits

    except subprocess.CalledProcessError as e:
        print(f"Ошибка при выполнении команды git: {e.stderr}")
        return []


def get_all_dependencies(commit, commits_map):
    dependencies = set(commit["parents"])  

    for parent_hash in commit["parents"]:
        parent_commit = commits_map.get(parent_hash)
        if parent_commit:
            dependencies.update(
                get_all_dependencies(parent_commit, commits_map))  

    return dependencies


def generate_graphviz_tree(commits):
    dot = Digraph(format="png")
    commits_map = {commit["hash"]: commit for commit in commits}  

    for commit in commits:
        dot.node(commit["hash"], label=commit["hash"])
        for parent in commit["parents"]:
            dot.edge(commit["hash"], parent)

    return dot


def save_graph_to_png(graph, output_file_path):

    output_file_path = str(output_file_path) 
    graph.render(filename=output_file_path, cleanup=True)


def main():
  
    parser = argparse.ArgumentParser(description="Git Dependency Visualizer")
    parser.add_argument("repo_path", help="Путь к репозиторию")
    parser.add_argument("commit_date", help="Дата коммитов для фильтрации (например, '2024-01-01')")
    parser.add_argument("output_file_path", help="Путь для сохранения изображения графа зависимостей")
    args = parser.parse_args()

    commits = get_commits_from_cache(args.repo_path, args.commit_date)

    graph = generate_graphviz_tree(commits)

    save_graph_to_png(graph, args.output_file_path)
    print(f"\nГраф зависимостей сохранен в файл: {args.output_file_path}.png")


if __name__ == "__main__":
    main()
