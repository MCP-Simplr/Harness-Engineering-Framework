"""PreToolUse hook: block Write/Edit content that contains a real-looking secret.

Short fake fixtures (e.g. `sk_test_production`) pass; patterns require key-length values.
Exit 2 blocks the tool call and shows stderr to the model.
"""

import json
import re
import sys

# Each pattern matches the shape of a real credential, not just its prefix.
SECRET_PATTERNS = {
    "Stripe secret/restricted key": r"\b[rs]k_(?:live|test)_[A-Za-z0-9]{24,}",
    "Stripe webhook secret": r"\bwhsec_[A-Za-z0-9]{24,}",
    "AWS access key id": r"\bAKIA[0-9A-Z]{16}\b",
    "Google API key": r"\bAIza[0-9A-Za-z_\-]{35}\b",
    "GitHub token": r"\bgh[pousr]_[A-Za-z0-9]{36,}\b",
    "Slack token": r"\bxox[abprs]-[A-Za-z0-9-]{10,}",
    "Private key block": r"-----BEGIN (?:[A-Z]+ )?PRIVATE KEY-----",
}


class SecretScanner:
    """Finds credential-shaped strings in the text a Write/Edit is about to save."""

    @staticmethod
    def written_text(tool_input: dict) -> str:
        # Write sends `content`; Edit sends `new_string`; MultiEdit sends a list of edits.
        parts = [tool_input.get("content", ""), tool_input.get("new_string", "")]
        parts += [edit.get("new_string", "") for edit in tool_input.get("edits", [])]
        return "\n".join(part for part in parts if isinstance(part, str))

    @staticmethod
    def find(text: str) -> list[str]:
        return [name for name, pattern in SECRET_PATTERNS.items() if re.search(pattern, text)]


def main() -> int:
    payload = json.load(sys.stdin)
    tool_input = payload.get("tool_input", {})
    found = SecretScanner.find(SecretScanner.written_text(tool_input))
    if not found:
        return 0
    path = tool_input.get("file_path", "<unknown file>")
    print(
        f"Blocked: {path} would contain what looks like a real secret ({', '.join(found)}). "
        "Secrets belong in your secret manager / .env, never in tracked files. "
        "Use a short fake value in tests.",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
