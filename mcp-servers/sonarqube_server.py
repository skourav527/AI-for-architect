import base64
import os
from typing import Any, Dict, Optional

import requests

try:
    from mcp.server.fastmcp import FastMCP
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "Install dependencies first: pip install -r mcp-servers/requirements.txt"
    ) from exc


mcp = FastMCP("sonarqube")


def _env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def _headers() -> Dict[str, str]:
    token = _env("SONARQUBE_TOKEN")
    encoded = base64.b64encode(f"{token}:".encode("utf-8")).decode("ascii")
    return {
        "Authorization": f"Basic {encoded}",
        "Content-Type": "application/json",
    }


def _base_url() -> str:
    return _env("SONARQUBE_URL").rstrip("/")


def _get(path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    response = requests.get(
        f"{_base_url()}/{path.lstrip('/')}",
        headers=_headers(),
        params=params,
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


@mcp.tool()
def project_quality_gate(project_key: str) -> Dict[str, Any]:
    """Get the SonarQube quality gate status for a project."""
    data = _get("api/qualitygates/project_status", {"projectKey": project_key})
    return data.get("projectStatus", {})


@mcp.tool()
def get_project_measures(
    project_key: str,
    metrics: str = "bugs,vulnerabilities,code_smells,coverage,duplicated_lines_density"
) -> Dict[str, Any]:
    """Get SonarQube measures used to prioritize fixes in Copilot."""
    data = _get(
        "api/measures/component",
        {
            "component": project_key,
            "metricKeys": metrics,
        },
    )
    component = data.get("component", {})
    return {
        "project": component.get("key"),
        "name": component.get("name"),
        "measures": component.get("measures", []),
    }


@mcp.tool()
def list_project_issues(
    project_key: str,
    severities: str = "BLOCKER,CRITICAL,MAJOR",
    statuses: str = "OPEN,CONFIRMED,REOPENED",
    page_size: int = 20,
) -> Dict[str, Any]:
    """List open issues so Copilot can map SonarQube findings to local files."""
    data = _get(
        "api/issues/search",
        {
            "componentKeys": project_key,
            "severities": severities,
            "statuses": statuses,
            "ps": max(1, min(page_size, 100)),
        },
    )
    return {
        "total": data.get("total", 0),
        "issues": [
            {
                "key": issue.get("key"),
                "rule": issue.get("rule"),
                "severity": issue.get("severity"),
                "message": issue.get("message"),
                "component": issue.get("component"),
                "line": issue.get("line"),
                "status": issue.get("status"),
                "type": issue.get("type"),
            }
            for issue in data.get("issues", [])
        ],
    }


@mcp.tool()
def get_issue(issue_key: str) -> Dict[str, Any]:
    """Get details for a specific SonarQube issue."""
    data = _get("api/issues/search", {"issues": issue_key, "ps": 1})
    issues = data.get("issues", [])
    if not issues:
        return {"error": f"Issue not found: {issue_key}"}
    return issues[0]


if __name__ == "__main__":
    mcp.run()