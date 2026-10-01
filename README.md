# Milestone Review Kit

Produce a review packet from two real Git commits: exact endpoint SHAs, commit range, changed paths, directory groups, and questions for a human assessor.

Requires Python 3.9+ and Git; no third-party dependencies.

```sh
python3 review.py /path/to/repository --base v0.1 --head HEAD --output milestone.json
python3 -m unittest discover -s tests -v
```

The output file must not exist. The tool does not execute inspected repository code. It compares endpoint trees and reports whether the base is an ancestor. Commit lists mean reachable from head but not base; reversed or diverged refs are not interpreted as a linear milestone.

## Human assessment workflow

1. Record the actual issue or milestone acceptance criteria.
2. Resolve the two refs and produce this packet.
3. Read diffs for every changed area and identify unrelated work.
4. Run appropriate tests in an isolated environment and verify CI at the head SHA.
5. Record evidence, limitations, and an accept/reject decision with reasons.

Directory grouping does not prove architecture quality. The tool does not invent a quality score, successful CI, releases, or third-party acceptance.

## Provenance and milestones

Initial implementation created with Codex assistance. This newly created project does not represent prior open-source contribution experience. v0.1 implements local endpoint review. Future work: explicit acceptance-criteria input and links to verified CI evidence. These future features are not implemented.
