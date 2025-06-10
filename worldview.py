import argparse
import json
import os
from collections import defaultdict

DATA_FILE = "worldview.json"


class Worldview:
    def __init__(self, path: str = DATA_FILE):
        self.path = path
        self.concepts: dict[str, dict] = {}
        self.causations: dict[str, list[str]] = defaultdict(list)
        self.load()

    def load(self):
        if os.path.exists(self.path):
            with open(self.path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
                self.concepts = data.get("concepts", {})
                self.causations = defaultdict(list, data.get("causations", {}))

    def save(self):
        with open(self.path, "w", encoding="utf-8") as fh:
            json.dump({"concepts": self.concepts, "causations": self.causations}, fh, indent=2)

    def add_concept(self, name: str, description: str = ""):
        if name not in self.concepts:
            self.concepts[name] = {"description": description}

    def link(self, cause: str, effect: str):
        if cause not in self.concepts:
            raise ValueError(f"Unknown cause concept: {cause}")
        if effect not in self.concepts:
            raise ValueError(f"Unknown effect concept: {effect}")
        if effect not in self.causations[cause]:
            self.causations[cause].append(effect)

    def show(self):
        if not self.concepts:
            print("Worldview is empty")
            return
        roots = set(self.concepts) - {e for effects in self.causations.values() for e in effects}
        for root in sorted(roots):
            self._print_tree(root, set(), 0)

    def _print_tree(self, node: str, visited: set[str], indent: int):
        print("  " * indent + node)
        if node in visited:
            print("  " * (indent + 1) + "(cycle)")
            return
        visited.add(node)
        for child in self.causations.get(node, []):
            self._print_tree(child, visited, indent + 1)
        visited.remove(node)


def main():
    parser = argparse.ArgumentParser(description="Map your worldview concepts")
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_p = subparsers.add_parser("add", help="Add a concept")
    add_p.add_argument("name")
    add_p.add_argument("description", nargs="?", default="")

    link_p = subparsers.add_parser("link", help="Link cause and effect")
    link_p.add_argument("cause")
    link_p.add_argument("effect")

    subparsers.add_parser("show", help="Display worldview")

    args = parser.parse_args()

    wv = Worldview()

    if args.command == "add":
        wv.add_concept(args.name, args.description)
        wv.save()
    elif args.command == "link":
        try:
            wv.link(args.cause, args.effect)
        except ValueError as exc:
            parser.error(str(exc))
        else:
            wv.save()
    elif args.command == "show":
        wv.show()


if __name__ == "__main__":
    main()
