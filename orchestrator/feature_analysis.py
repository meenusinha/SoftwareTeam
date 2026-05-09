"""Generates a Feature Analysis Document from cross-repo knowledge."""
from datetime import datetime


def generate_feature_analysis(
    requesting_repo: str,
    feature_request: str,
    own_knowledge: str,
    peer_responses: dict[str, str],
    llm=None,
    repo_display: dict[str, str] | None = None,
) -> str:
    """
    Combine own RAG knowledge and peer responses into a Feature Analysis Document.

    Returns a markdown string with two sections:
      1. Current State — what each repo already has relevant to the feature
      2. Solution Design — cross-repo implementation recommendation
    """
    display = repo_display or {}

    def _display(name: str) -> str:
        return display.get(name, name)

    lines = [
        f"# Feature Analysis: {feature_request}",
        "",
        f"**Requesting Repo**: {_display(requesting_repo)}",
        f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "---",
        "",
        "## Current State",
        "",
        f"### {_display(requesting_repo)} (own knowledge)",
        "",
        own_knowledge if own_knowledge.strip() else "(no relevant knowledge found in own repo)",
        "",
    ]

    for repo_name, response in peer_responses.items():
        lines += [
            f"### {_display(repo_name)}",
            "",
            response if response.strip() else "(no relevant knowledge found)",
            "",
        ]

    lines += ["---", "", "## Solution Design", ""]

    if llm is not None:
        peer_section = "\n\n".join(
            f"[From {_display(r)}]\n{resp}" for r, resp in peer_responses.items()
        )
        prompt = (
            f"You are a senior software architect for a lithography scanner system.\n\n"
            f"The '{_display(requesting_repo)}' team has a feature request:\n"
            f'"{feature_request}"\n\n'
            f"Own repo knowledge:\n{own_knowledge}\n\n"
            f"Knowledge from peer repos:\n{peer_section}\n\n"
            f"Write a concise Solution Design with two sub-sections:\n"
            f"1. Overview — one paragraph describing the cross-repo approach.\n"
            f"2. Changes Required per Repo — bullet points per repo naming which "
            f"component/interface/file changes and what changes.\n\n"
            f"Be concrete. Reference actual component and interface names."
        )
        response = llm.invoke(prompt)
        lines.append(response.content)
    else:
        lines += [
            "*(LLM synthesis unavailable — set GITHUB_TOKEN in .env for AI-generated design)*",
            "",
            "### Overview",
            "",
            f"To implement **{feature_request}**, the following repos are involved "
            f"based on their relevant components and interfaces:",
            "",
            f"- **{_display(requesting_repo)}** (requesting) — owns the feature and "
            f"will coordinate the change",
        ]
        for repo_name in peer_responses:
            lines.append(f"- **{_display(repo_name)}** — provides supporting interfaces/components")

        lines += [
            "",
            "### Changes Required per Repo",
            "",
            f"#### {_display(requesting_repo)}",
            "- Review own components and interfaces identified in the Current State section above",
            "- Implement the feature using the interfaces provided by peer repos",
            "",
        ]
        for repo_name, response in peer_responses.items():
            lines += [
                f"#### {_display(repo_name)}",
                "- Review the relevant components and interfaces identified in Current State",
                "- Assess whether interface changes are required to support the feature",
                "",
            ]

        lines += [
            "### Cross-Repo Interface Touch Points",
            "",
            "Refer to the Current State section above for specific interface names and files.",
            "Coordinate interface changes across repos before implementation begins.",
        ]

    return "\n".join(lines)
