"""GDScript parse via tree-sitter: code entities and containment relationships."""

from __future__ import annotations

from pathlib import Path

from tree_sitter import Node, Parser
from tree_sitter_language_pack import get_language

from .models import CodeEntity, Relationship, ScanFailure
from .names import normalize_name


def parse_gdscript(
    root: Path, relative_path: Path
) -> tuple[list[CodeEntity], list[Relationship]]:
    path = root / relative_path
    try:
        source = path.read_bytes()
    except OSError as error:
        raise ScanFailure(
            "UNREADABLE_INPUT", "could not read configured input", path
        ) from error
    tree = Parser(get_language("gdscript")).parse(source)
    if tree.root_node.has_error:
        raise ScanFailure("UNSUPPORTED_SOURCE", "could not parse GDScript input", path)
    entities: list[CodeEntity] = []
    relationships: list[Relationship] = []
    extends = next(
        (
            child
            for child in tree.root_node.children
            if child.type == "extends_statement"
        ),
        None,
    )
    script_name = relative_path.stem
    script_entity = _make_code_entity(
        relative_path,
        name=script_name,
        kind="script",
        line=extends.start_point.row + 1 if extends else 1,
        parent=None,
    )
    entities.append(script_entity)

    class_entity = next(
        (
            _make_code_entity(
                relative_path,
                name=_node_name(source, node),
                kind="class",
                line=_node_line(node),
                parent=None,
            )
            for node in tree.root_node.children
            if node.type == "class_name_statement"
            and node.child_by_field_name("name") is not None
        ),
        None,
    )
    if class_entity is not None:
        entities.append(class_entity)
    default_parent = class_entity or script_entity

    def visit(
        node: Node, parent: CodeEntity | None, exported_variable: bool = False
    ) -> None:
        if node.type in {"class_name_statement", "extends_statement"}:
            return
        current_parent = parent
        if node.type == "class_definition":
            name_node = node.child_by_field_name("name")
            if name_node is not None:
                class_entity_for_node = _make_code_entity(
                    relative_path,
                    name=_node_name(source, node),
                    kind="class",
                    line=name_node.start_point.row + 1,
                    parent=parent,
                )
                entities.append(class_entity_for_node)
                _add_relationship(relationships, parent, class_entity_for_node)
                current_parent = class_entity_for_node
        elif node.type == "function_definition":
            name_node = node.child_by_field_name("name")
            if name_node is not None:
                function_entity = _make_code_entity(
                    relative_path,
                    name=_node_name(source, node),
                    kind="function",
                    line=name_node.start_point.row + 1,
                    parent=parent,
                )
                entities.append(function_entity)
                _add_relationship(relationships, parent, function_entity)
                current_parent = function_entity
        elif node.type == "signal_statement":
            signal_entity = _make_code_entity(
                relative_path,
                name=_node_name(source, node),
                kind="signal",
                line=_node_line(node),
                parent=parent,
            )
            entities.append(signal_entity)
            _add_relationship(relationships, parent, signal_entity)
        elif node.type == "variable_statement" and (
            exported_variable or _is_exported(node)
        ):
            variable_entity = _make_code_entity(
                relative_path,
                name=_node_name(source, node),
                kind="exported_variable",
                line=_node_line(node),
                parent=parent,
            )
            entities.append(variable_entity)
            _add_relationship(relationships, parent, variable_entity)
        for index, child in enumerate(node.children):
            previous = node.children[index - 1] if index else None
            visit(
                child,
                current_parent,
                exported_variable=(
                    child.type == "variable_statement"
                    and previous is not None
                    and _is_export_annotation(previous)
                ),
            )

    for index, child in enumerate(tree.root_node.children):
        previous = tree.root_node.children[index - 1] if index else None
        visit(
            child,
            default_parent if child.type != "class_definition" else None,
            exported_variable=(
                child.type == "variable_statement"
                and previous is not None
                and _is_export_annotation(previous)
            ),
        )
    return entities, relationships


def _node_name(source: bytes, node: Node) -> str:
    name_node = node.child_by_field_name("name")
    if name_node is None:
        return ""
    return source[name_node.start_byte : name_node.end_byte].decode("utf-8")


def _node_line(node: Node) -> int:
    name_node = node.child_by_field_name("name")
    if name_node is None:
        raise ScanFailure(
            "UNSUPPORTED_SOURCE",
            "GDScript node is missing a name field",
        )
    return name_node.start_point.row + 1


def _is_exported(node: Node) -> bool:
    return "@export" in (node.text or b"").decode("utf-8").split(" var ", maxsplit=1)[0]


def _is_export_annotation(node: Node) -> bool:
    return (
        node.type == "annotation"
        and (node.text or b"").decode("utf-8").strip() == "@export"
    )


def _make_code_entity(
    relative_path: Path,
    *,
    name: str,
    kind: str,
    line: int,
    parent: CodeEntity | None,
) -> CodeEntity:
    symbol_path = f"{parent.symbol_path}.{name}" if parent else name
    entity_id = f"{relative_path.as_posix()}::{kind}:{symbol_path}"
    return CodeEntity(
        name=name,
        normalized_name=normalize_name(name),
        kind=kind,
        path=str(relative_path),
        line=line,
        entity_id=entity_id,
        symbol_path=symbol_path,
        parent_id=parent.entity_id if parent else None,
    )


def _add_relationship(
    relationships: list[Relationship],
    parent: CodeEntity | None,
    child: CodeEntity,
) -> None:
    if parent is not None:
        relationships.append(
            Relationship(source_id=parent.entity_id, target_id=child.entity_id)
        )
