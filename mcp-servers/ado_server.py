import base64
import os
from typing import Any, Dict, Optional
from urllib.parse import quote

import requests

try:
    from mcp.server.fastmcp import FastMCP
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "Install dependencies first: pip install -r mcp-servers/requirements.txt"
    ) from exc


mcp = FastMCP("azure-devops")


def _env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def _headers() -> Dict[str, str]:
    token = _env("ADO_PAT")
    encoded = base64.b64encode(f":{token}".encode("utf-8")).decode("ascii")
    return {
        "Authorization": f"Basic {encoded}",
        "Content-Type": "application/json",
    }


def _base_url() -> str:
    org_url = _env("ADO_ORG_URL").rstrip("/")
    project = _env("ADO_PROJECT")
    return f"{org_url}/{project}/_apis"


def _get(path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    response = requests.get(
        f"{_base_url()}/{path.lstrip('/')}",
        headers=_headers(),
        params=params,
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def _get_text(path: str, params: Optional[Dict[str, Any]] = None) -> str:
    response = requests.get(
        f"{_base_url()}/{path.lstrip('/')}",
        headers=_headers(),
        params=params,
        timeout=30,
    )
    response.raise_for_status()
    return response.text


def _latest_iteration_id(repository: str, pull_request_id: int) -> int:
    data = _get(
        f"git/repositories/{repository}/pullRequests/{pull_request_id}/iterations",
        {"api-version": "7.1-preview.1"},
    )
    iteration_ids = [item.get("id") for item in data.get("value", []) if isinstance(item.get("id"), int)]
    if not iteration_ids:
        raise RuntimeError(f"No iterations found for pull request {pull_request_id} in repository {repository}.")
    return max(iteration_ids)


@mcp.tool()
def list_repositories() -> Dict[str, Any]:
    """List Azure DevOps repositories in the configured project."""
    data = _get("git/repositories", {"api-version": "7.1"})
    return {
        "count": data.get("count", 0),
        "repositories": [
            {"id": item.get("id"), "name": item.get("name"), "defaultBranch": item.get("defaultBranch")}
            for item in data.get("value", [])
        ],
    }


@mcp.tool()
def list_pull_requests(repository: str, status: str = "active", top: int = 10) -> Dict[str, Any]:
    """List pull requests for a repository. Use this before reviewing a PR in Copilot."""
    data = _get(
        f"git/repositories/{repository}/pullrequests",
        {
            "searchCriteria.status": status,
            "$top": max(1, min(top, 25)),
            "api-version": "7.1",
        },
    )
    return {
        "count": data.get("count", 0),
        "pullRequests": [
            {
                "pullRequestId": item.get("pullRequestId"),
                "title": item.get("title"),
                "status": item.get("status"),
                "sourceRefName": item.get("sourceRefName"),
                "targetRefName": item.get("targetRefName"),
                "createdBy": (item.get("createdBy") or {}).get("displayName"),
                "creationDate": item.get("creationDate"),
            }
            for item in data.get("value", [])
        ],
    }


@mcp.tool()
def get_pull_request(repository: str, pull_request_id: int) -> Dict[str, Any]:
    """Get pull request metadata for a specific Azure DevOps PR."""
    item = _get(
        f"git/repositories/{repository}/pullRequests/{pull_request_id}",
        {"api-version": "7.1"},
    )
    return {
        "pullRequestId": item.get("pullRequestId"),
        "title": item.get("title"),
        "description": item.get("description"),
        "status": item.get("status"),
        "sourceRefName": item.get("sourceRefName"),
        "targetRefName": item.get("targetRefName"),
        "reviewers": [
            {
                "displayName": reviewer.get("displayName"),
                "vote": reviewer.get("vote"),
                "isRequired": reviewer.get("isRequired"),
            }
            for reviewer in item.get("reviewers", [])
        ],
        "lastMergeSourceCommit": item.get("lastMergeSourceCommit"),
        "url": item.get("url"),
    }


@mcp.tool()
def list_pull_request_threads(repository: str, pull_request_id: int) -> Dict[str, Any]:
    """List review threads and comments for a PR so Copilot can summarize review feedback."""
    data = _get(
        f"git/repositories/{repository}/pullRequests/{pull_request_id}/threads",
        {"api-version": "7.1"},
    )
    return {
        "count": data.get("count", 0),
        "threads": [
            {
                "id": thread.get("id"),
                "status": thread.get("status"),
                "comments": [
                    {
                        "author": (comment.get("author") or {}).get("displayName"),
                        "content": comment.get("content"),
                        "commentType": comment.get("commentType"),
                        "isDeleted": comment.get("isDeleted"),
                    }
                    for comment in thread.get("comments", [])
                ],
            }
            for thread in data.get("value", [])
        ],
    }


@mcp.tool()
def list_pull_request_work_items(repository: str, pull_request_id: int) -> Dict[str, Any]:
    """List work items linked to a PR."""
    data = _get(
        f"git/repositories/{repository}/pullRequests/{pull_request_id}/workitems",
        {"api-version": "7.1"},
    )
    return {
        "count": data.get("count", 0),
        "workItems": data.get("value", []),
    }


@mcp.tool()
def list_pull_request_iterations(repository: str, pull_request_id: int) -> Dict[str, Any]:
    """List iterations for a PR so clients can fetch file-level changes by iteration."""
    data = _get(
        f"git/repositories/{repository}/pullRequests/{pull_request_id}/iterations",
        {"api-version": "7.1-preview.1"},
    )
    return {
        "count": data.get("count", 0),
        "iterations": [
            {
                "id": item.get("id"),
                "description": item.get("description"),
                "createdDate": item.get("createdDate"),
                "sourceRefCommit": (item.get("sourceRefCommit") or {}).get("commitId"),
                "targetRefCommit": (item.get("targetRefCommit") or {}).get("commitId"),
            }
            for item in data.get("value", [])
        ],
    }


@mcp.tool()
def list_pull_request_changes(
    repository: str,
    pull_request_id: int,
    iteration_id: Optional[int] = None,
    top: int = 2000,
) -> Dict[str, Any]:
    """List changed files for a PR iteration (defaults to latest iteration)."""
    selected_iteration = iteration_id if iteration_id is not None else _latest_iteration_id(repository, pull_request_id)
    data = _get(
        f"git/repositories/{repository}/pullRequests/{pull_request_id}/iterations/{selected_iteration}/changes",
        {
            "$top": max(1, min(top, 10000)),
            "api-version": "7.1-preview.1",
        },
    )
    entries = data.get("changeEntries", [])
    return {
        "pullRequestId": pull_request_id,
        "iterationId": selected_iteration,
        "count": len(entries),
        "changes": [
            {
                "changeType": item.get("changeType"),
                "path": (item.get("item") or {}).get("path"),
                "objectId": (item.get("item") or {}).get("objectId"),
                "gitObjectType": (item.get("item") or {}).get("gitObjectType"),
            }
            for item in entries
        ],
    }


@mcp.tool()
def get_item_content_at_commit(repository: str, path: str, commit_id: str) -> Dict[str, Any]:
    """Get file content for a repository path at a specific commit."""
    encoded_path = quote(path, safe="/")
    text = _get_text(
        f"git/repositories/{repository}/items",
        {
            "path": encoded_path,
            "includeContent": "true",
            "versionDescriptor.versionType": "commit",
            "versionDescriptor.version": commit_id,
            "$format": "json",
            "api-version": "7.1-preview.1",
        },
    )
    data = requests.models.complexjson.loads(text)
    return {
        "path": data.get("path"),
        "commitId": data.get("commitId"),
        "objectId": data.get("objectId"),
        "content": data.get("content", ""),
    }


if __name__ == "__main__":
    mcp.run()