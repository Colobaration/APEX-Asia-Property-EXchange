#!/usr/bin/env python3
import json
import os
import subprocess
import sys
from pathlib import Path


def run(cmd, check=True, capture_output=True, text=True, env=None):
    result = subprocess.run(cmd, check=check, capture_output=capture_output, text=text, env=env)
    return result.stdout.strip()


def load_yaml(path: Path):
    try:
        import yaml  # type: ignore
    except ImportError:
        print("PyYAML is required. Please install it: pip install pyyaml", file=sys.stderr)
        sys.exit(1)
    with path.open("r", encoding="utf-8") as f:
        # Support multiple YAML documents; merge their tasks arrays
        docs = [d for d in (yaml.safe_load_all(f)) if d]
    if not docs:
        return {"tasks": []}
    if len(docs) == 1:
        return docs[0]
    merged_tasks: list[dict] = []
    for d in docs:
        if isinstance(d, dict) and isinstance(d.get("tasks"), list):
            merged_tasks.extend(d["tasks"]) 
    return {"tasks": merged_tasks}


def gh_json(args):
    out = run(["gh"] + args + ["--format", "json"])
    return json.loads(out) if out else {}


def get_project_number() -> int:
    path = Path(__file__).resolve().parent / ".project_number"
    if not path.exists():
        print("ops/.project_number not found. Run ops/project_bootstrap.sh first.", file=sys.stderr)
        sys.exit(1)
    return int(path.read_text(encoding="utf-8").strip())


def ensure_issue(owner_repo: str, title: str, body: str, labels: list[str], assignee: str | None) -> int:
    # Try to find issue by exact title
    issues_json = run([
        "gh", "issue", "list", "-R", owner_repo, "--state", "all", "--json", "number,title",
    ])
    issues = json.loads(issues_json) if issues_json else []
    for it in issues:
        if it.get("title") == title:
            return int(it["number"])

    # Create new issue
    cmd = ["gh", "issue", "create", "-R", owner_repo, "--title", title, "--body", body]
    if labels:
        for lb in labels:
            cmd += ["--label", lb]
    if assignee:
        cmd += ["--assignee", assignee]
    url = run(cmd)
    # Extract number from URL
    number = int(url.rsplit("/", 1)[-1])
    return number


def get_existing_label_names(owner_repo: str) -> set[str]:
    out = run(["gh", "label", "list", "-R", owner_repo, "--json", "name"])
    try:
        data = json.loads(out) if out else []
    except json.JSONDecodeError:
        data = []
    return {it.get("name") for it in data if isinstance(it, dict) and it.get("name")}


def ensure_labels(owner_repo: str, issue_number: int, labels: list[str]):
    if not labels:
        return
    existing = get_existing_label_names(owner_repo)
    for lb in labels:
        if lb not in existing:
            # create label non-interactively with a default color
            try:
                run(["gh", "label", "create", "-R", owner_repo, lb, "--color", "ededed"], check=False)
            except subprocess.CalledProcessError:
                pass
            existing.add(lb)
    cmd = ["gh", "issue", "edit", "-R", owner_repo, str(issue_number)]
    for lb in labels:
        cmd += ["--add-label", lb]
    run(cmd)


def ensure_assignee(owner_repo: str, issue_number: int, assignee: str | None):
    if not assignee:
        return
    # If user isn't a collaborator this may fail; don't crash the whole import
    try:
        run(["gh", "issue", "edit", "-R", owner_repo, str(issue_number), "--add-assignee", assignee])
    except subprocess.CalledProcessError:
        pass


def add_depends_body(owner_repo: str, issue_number: int, dep_issue_numbers: list[int]):
    if not dep_issue_numbers:
        return
    # Get current body
    issue = gh_json(["issue", "view", "-R", owner_repo, str(issue_number), "--json", "body"])
    current_body = issue.get("body") or ""
    new_lines = []
    for dep in dep_issue_numbers:
        line = f"Зависит от #{dep}"
        if line not in current_body:
            new_lines.append(line)
    if not new_lines:
        return
    new_body = (current_body + "\n\n" + "\n".join(new_lines)).strip()
    run(["gh", "issue", "edit", "-R", owner_repo, str(issue_number), "--body", new_body])


def get_field_ids(owner: str, project_number: int):
    data = gh_json(["project", "field-list", str(project_number), "--owner", owner])
    if isinstance(data, dict):
        fields = data.get("fields", [])
    else:
        fields = data if isinstance(data, list) else []
    by_name = {f.get("name"): f for f in fields if isinstance(f, dict) and f.get("name")}
    return by_name


def ensure_in_project(owner: str, project_number: int, issue_url: str) -> str:
    # Try add; on success return item id
    try:
        out = run(["gh", "project", "item-add", str(project_number), "--owner", owner, "--url", issue_url, "--format", "json"])
        if out:
            data = json.loads(out)
            item_id = data.get("id") or data.get("item") or data.get("data", {}).get("id")
            if item_id:
                return str(item_id)
    except subprocess.CalledProcessError:
        pass

    # If exists, find item id via GraphQL
    # Get node_id of the issue
    issue_json = json.loads(run(["gh", "api", issue_url]))
    content_node_id = issue_json.get("node_id")
    q = {
        "query": """
        query($org:String!, $number:Int!) {
          organization(login:$org) {
            projectV2(number:$number) {
              items(first: 200) {
                nodes { id content { __typename ... on Issue { id } ... on PullRequest { id } } }
              }
            }
          }
        }
        """,
        "variables": {"org": owner, "number": project_number},
    }
    res = json.loads(run(["gh", "api", "graphql", "-f", f"query={json.dumps(q['query'])}", "-f", f"variables={json.dumps(q['variables'])}"]))
    nodes = res.get("data", {}).get("organization", {}).get("projectV2", {}).get("items", {}).get("nodes", [])
    for n in nodes:
        content = n.get("content") or {}
        if content.get("id") == content_node_id:
            return n.get("id")
    raise RuntimeError("Project item not found and could not be added")


def set_single_select(owner: str, project_number: int, item_id: str, field_name: str, option_name: str, fields_by_name: dict):
    field = fields_by_name[field_name]
    field_id = field["id"]
    # Find option id
    opt_id = None
    for opt in field.get("options", []):
        if opt.get("name") == option_name:
            opt_id = opt.get("id")
            break
    if not opt_id:
        raise RuntimeError(f"Option '{option_name}' not found for field '{field_name}'")
    run([
        "gh", "project", "item-edit", str(project_number), "--owner", owner, "--id", item_id,
        "--field", field_id, "--single-select-option-id", opt_id,
    ])


def set_text(owner: str, project_number: int, item_id: str, field_name: str, value: str, fields_by_name: dict):
    field = fields_by_name[field_name]
    field_id = field["id"]
    run([
        "gh", "project", "item-edit", str(project_number), "--owner", owner, "--id", item_id,
        "--field", field_id, "--text", value,
    ])


def main():
    gh_token = os.environ.get("GH_TOKEN")
    gh_owner = os.environ.get("GH_OWNER")
    dev_a = os.environ.get("DEV_A")
    dev_b = os.environ.get("DEV_B")
    if not gh_token or not gh_owner:
        print("GH_TOKEN and GH_OWNER are required in env", file=sys.stderr)
        sys.exit(1)

    os.environ["GH_TOKEN"] = gh_token

    repo = os.environ.get("GITHUB_REPOSITORY", "")
    project_number = get_project_number()

    tasks_data = load_yaml(Path(__file__).resolve().parent / "tasks.yaml")
    tasks = tasks_data.get("tasks", [])

    id_to_issue: dict[int, int] = {}
    owner_map = {"DEV_A": dev_a, "DEV_B": dev_b}

    for task in tasks:
        task_id = int(task["id"])
        title = str(task["title"])  # exact match
        body = str(task.get("body", "")).strip()
        labels = list(task.get("labels", []))
        owner_key = str(task.get("owner", "")).strip()
        area = str(task.get("area", "")).strip()
        priority = str(task.get("priority", "")).strip()
        depends = [int(x) for x in task.get("depends_on", [])] if task.get("depends_on") else []

        assignee = owner_map.get(owner_key)
        issue_number = ensure_issue(repo, title, body, labels, assignee)
        ensure_labels(repo, issue_number, labels)
        ensure_assignee(repo, issue_number, assignee)

        # Add depends lines if earlier issues known
        dep_issue_numbers = [id_to_issue[d] for d in depends if d in id_to_issue]
        add_depends_body(repo, issue_number, dep_issue_numbers)

        # Add to project and set fields
        issue_url = f"https://api.github.com/repos/{repo}/issues/{issue_number}"
        item_id = ensure_in_project(gh_owner, project_number, issue_url)
        fields_by_name = get_field_ids(gh_owner, project_number)
        set_single_select(gh_owner, project_number, item_id, "Статус", "К выполнению", fields_by_name)
        set_single_select(gh_owner, project_number, item_id, "Область", area, fields_by_name)
        set_single_select(gh_owner, project_number, item_id, "Приоритет", priority, fields_by_name)
        set_text(gh_owner, project_number, item_id, "Ответственный", owner_key, fields_by_name)

        id_to_issue[task_id] = issue_number
        print(f"Task {task_id}: issue #{issue_number} processed")

    print(f"Imported/updated {len(tasks)} tasks")


if __name__ == "__main__":
    main()



