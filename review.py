"""Review the scope of a real Git milestone without executing repository code."""
import argparse
import json
import subprocess
from pathlib import Path


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], check=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout


def review(repo, base, head):
    base_sha = git(repo, "rev-parse", "--verify", "--end-of-options", base + "^{commit}").decode().strip()
    head_sha = git(repo, "rev-parse", "--verify", "--end-of-options", head + "^{commit}").decode().strip()
    commits = git(repo, "rev-list", "--reverse", base_sha + ".." + head_sha).decode().splitlines()
    paths = [p.decode("utf-8", "surrogateescape") for p in
             git(repo, "diff", "--name-only", "-z", base_sha, head_sha).split(b"\0") if p]
    areas = {}
    for p in paths:
        area = p.split("/", 1)[0] if "/" in p else "[root]"
        areas.setdefault(area, []).append(p)
    ancestor = subprocess.run(["git", "-C", str(repo), "merge-base", "--is-ancestor", base_sha, head_sha],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if ancestor.returncode not in (0, 1):
        raise ValueError("Cannot establish commit ancestry")
    return {
        "schema_version": 1,
        "base_commit": base_sha,
        "head_commit": head_sha,
        "base_is_ancestor": ancestor.returncode == 0,
        "commits_reachable_from_head_not_base": commits,
        "changed_paths": paths,
        "areas": areas,
        "review_questions": [
            "Does each changed area serve the stated milestone acceptance criteria?",
            "Are unrelated refactors separated from the requested behavior?",
            "Do tests cover the changed behavior and known failure modes?",
            "Have CI results been verified at this exact head commit?",
            "Are setup instructions and licensing suitable for collection?",
        ],
        "limitations": [
            "This is an endpoint comparison; intermediate changes later reverted are omitted.",
            "Commit range means reachable from head but not base; it is not a release history claim.",
            "Top-level directory groups are navigation aids, not architectural conclusions.",
            "No quality score, test execution, CI success, or external review is inferred.",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repository", type=Path)
    parser.add_argument("--base", required=True)
    parser.add_argument("--head", default="HEAD")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    try:
        result = review(args.repository, args.base, args.head)
        with args.output.open("x") as stream:
            json.dump(result, stream, ensure_ascii=True, indent=2)
            stream.write("\n")
    except (subprocess.CalledProcessError, OSError, ValueError):
        parser.exit(1, "Review failed: check repository, refs, and a new output path.\n")


if __name__ == "__main__":
    main()
