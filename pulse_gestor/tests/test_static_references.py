# Copyright (c) 2026, StillPulse Tecnologia LTDA and contributors
# For license information, please see license.txt

"""Pure static checks (no bench needed) that catch orphan references after renames.

- `self.x()` calls must resolve to a method/attribute of the class (or of a known base).
- Dotted `pulse_gestor.<module>.<name>` strings (hooks, Number Card JSON, JS `frappe.call`/`xcall`) must point to a
  function/class that exists.
- Keyword arguments used when calling an in-repo function imported by name must exist in its signature.
"""

import ast
import re
import unittest
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent.parent
REPO = PACKAGE.parent
SKIP_PARTS = ("__pycache__", "node_modules")


def _python_files():
	for path in PACKAGE.rglob("*.py"):
		if not any(part in path.parts for part in SKIP_PARTS):
			yield path


def _defined_names(tree):
	names = set()
	for node in tree.body:
		if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef):
			names.add(node.name)
		elif isinstance(node, ast.Assign):
			names.update(t.id for t in node.targets if isinstance(t, ast.Name))
		elif isinstance(node, ast.Import | ast.ImportFrom):
			names.update((a.asname or a.name).split(".")[0] for a in node.names)
		elif isinstance(node, ast.If | ast.Try):
			for sub in ast.walk(node):
				if isinstance(sub, ast.FunctionDef | ast.ClassDef):
					names.add(sub.name)
				elif isinstance(sub, ast.Assign):
					names.update(t.id for t in sub.targets if isinstance(t, ast.Name))
	return names


def _class_members(cls):
	members = set()
	for node in ast.walk(cls):
		if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
			members.add(node.name)
		elif isinstance(node, ast.Assign):
			members.update(t.id for t in node.targets if isinstance(t, ast.Name))
		elif isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id == "self":
			if isinstance(node.ctx, ast.Store):
				members.add(node.attr)
	return members


class TestStaticReferences(unittest.TestCase):
	def test_self_calls_resolve_to_class_members(self):
		try:
			from frappe.model.document import Document

			frappe_members = set(dir(Document))
		except ImportError:
			frappe_members = None
		problems = []
		for path in _python_files():
			tree = ast.parse(path.read_text(encoding="utf-8"))
			for cls in [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]:
				if cls.name.startswith("Test"):
					continue  # unittest/FrappeTestCase helpers come from the framework
				members = _class_members(cls)
				bases = {b.id for b in cls.bases if isinstance(b, ast.Name)}
				for node in ast.walk(cls):
					if not (
						isinstance(node, ast.Call)
						and isinstance(node.func, ast.Attribute)
						and isinstance(node.func.value, ast.Name)
						and node.func.value.id == "self"
					):
						continue
					name = node.func.attr
					if name in members or name.startswith("__"):
						continue
					if "Document" in bases and frappe_members is not None and name in frappe_members:
						continue
					# Unknown external bases (e.g. the optional signature engine) only allow public inherited names.
					if (
						bases
						and not name.startswith("_")
						and (frappe_members is None or "Document" not in bases)
					):
						continue
					if "Document" in bases and frappe_members is None and not name.startswith("_"):
						continue
					problems.append(f"{path.relative_to(REPO)}:{node.lineno} self.{name}()")
		self.assertEqual(problems, [])

	def test_dotted_paths_resolve(self):
		pattern = re.compile(r"pulse_gestor(?:\.\w+)+")
		problems = []
		files = [p for p in REPO.rglob("*") if p.suffix in (".py", ".js", ".json") and p.is_file()]
		for path in files:
			if any(part in path.parts for part in (*SKIP_PARTS, ".git")) or "patches" in path.parts:
				continue
			text = path.read_text(encoding="utf-8", errors="ignore")
			for match in pattern.finditer(text):
				parts = match.group(0).split(".")
				for i in range(len(parts), 1, -1):
					module = REPO.joinpath(*parts[:i]).with_suffix(".py")
					if module.exists():
						if i < len(parts):
							tree = ast.parse(module.read_text(encoding="utf-8"))
							if parts[i] not in _defined_names(tree):
								problems.append(f"{path.relative_to(REPO)}: {match.group(0)}")
						break
		self.assertEqual(problems, [])

	def test_keyword_arguments_match_in_repo_signatures(self):
		signatures = {}
		trees = {}
		for path in _python_files():
			trees[path] = ast.parse(path.read_text(encoding="utf-8"))
			module = ".".join(path.relative_to(REPO).with_suffix("").parts)
			for node in trees[path].body:
				if isinstance(node, ast.FunctionDef):
					args = node.args
					names = {a.arg for a in args.args + args.kwonlyargs}
					signatures[(module, node.name)] = (names, args.kwarg is not None)
		problems = []
		for path, tree in trees.items():
			imported = {}
			for node in ast.walk(tree):
				if (
					isinstance(node, ast.ImportFrom)
					and node.module
					and node.module.startswith("pulse_gestor")
				):
					for alias in node.names:
						imported[alias.asname or alias.name] = (node.module, alias.name)
			for node in ast.walk(tree):
				if (
					isinstance(node, ast.Call)
					and isinstance(node.func, ast.Name)
					and node.func.id in imported
				):
					signature = signatures.get(imported[node.func.id])
					if not signature:
						continue
					names, has_kwargs = signature
					for keyword in node.keywords:
						if keyword.arg and not has_kwargs and keyword.arg not in names:
							problems.append(
								f"{path.relative_to(REPO)}:{node.lineno} {node.func.id}({keyword.arg}=)"
							)
		self.assertEqual(problems, [])


if __name__ == "__main__":
	unittest.main()
