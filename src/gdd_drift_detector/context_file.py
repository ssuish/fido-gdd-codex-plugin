"""Delimited game design context block updates for agent memory files."""

from __future__ import annotations

from pathlib import Path

_START = "<!-- fido:context:start -->"
_END = "<!-- fido:context:end -->"
_START_BYTES = _START.encode()
_END_BYTES = _END.encode()


def write_context_block(path: Path, block: str, *, update_only: bool) -> bool:
    """Create, append, or replace Fido's delimited context block."""
    if not path.exists():
        if update_only:
            return False
        path.write_bytes(block.encode())
        return True

    content = path.read_bytes()
    newline = _newline(content)
    encoded_block = block.encode().replace(b"\n", newline)
    start = content.find(_START_BYTES)
    end = content.find(_END_BYTES, start)
    if start != -1 and end != -1:
        replacement_end = end + len(_END_BYTES)
        suffix = content[replacement_end:]
        replacement = (
            encoded_block.rstrip(b"\r\n")
            if suffix.startswith(newline)
            else encoded_block
        )
        path.write_bytes(content[:start] + replacement + suffix)
        return True
    if update_only:
        return False

    separator = b"" if not content or content.endswith(newline * 2) else newline
    path.write_bytes(content + separator + encoded_block)
    return True


def _newline(content: bytes) -> bytes:
    return b"\r\n" if b"\r\n" in content else b"\n"
