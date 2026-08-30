from langchain.tools import ToolRuntime, tool
from langchain_core.messages import ToolMessage
from langgraph.config import get_stream_writer
from langgraph.types import Command
from pydantic import BaseModel, ConfigDict, Field

from ...utils import logger
from .tool_descriptions import (
    PRESENT_REPORT_DESCRIPTION,
    READ_REPORT_DESCRIPTION,
    SAVE_REPORT_DESCRIPTION,
)


def _report_tool_response(
    runtime: ToolRuntime,
    feedback: str,
    *,
    is_error: bool = False,
    reports: list[dict[str, str]] | None = None,
    presented_files: list[dict[str, str]] | None = None,
) -> Command:
    update: dict = {
        "messages": [
            ToolMessage(
                feedback,
                tool_call_id=runtime.tool_call_id,
                status="error" if is_error else "success",
            )
        ],
    }
    if reports is not None:
        update["reports"] = reports
    if presented_files is not None:
        update["presented_files"] = presented_files
    return Command(update=update)


def _upsert_by_name(
    items: list[dict[str, str]],
    name: str,
    content: str,
) -> list[dict[str, str]]:
    updated = [item for item in items if item.get("name") != name]
    updated.append({"name": name, "content": content})
    return updated


def _find_report(reports: list[dict[str, str]], name: str) -> dict[str, str] | None:
    for report in reports:
        if report.get("name") == name:
            return report
    return None


class SaveReportInput(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    name: str = Field(description="Canonical report name, e.g. product_dossier")
    content: str = Field(description="Full report body to persist")
    runtime: ToolRuntime


class ReadReportInput(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    name: str | None = Field(
        default=None,
        description="Optional report name. Omit to list all saved reports.",
    )
    runtime: ToolRuntime


class PresentReportInput(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    name: str = Field(description="Name of a saved report to present to the user")
    runtime: ToolRuntime


@tool(description=SAVE_REPORT_DESCRIPTION, parse_docstring=True, args_schema=SaveReportInput)
def save_report(name: str, content: str, runtime: ToolRuntime) -> Command:
    """Save or replace a named report in agent state.

    Args:
        name: Canonical report name
        content: Full report body to persist

    Returns:
        Command updating state.reports
    """
    try:
        reports = list(runtime.state.get("reports") or [])
        reports = _upsert_by_name(reports, name, content)
        return _report_tool_response(
            runtime,
            f"Saved report '{name}' ({len(content)} characters).",
            reports=reports,
        )
    except Exception as exc:
        logger.error("Error saving report: %s", exc)
        return _report_tool_response(runtime, f"Error: {exc}", is_error=True)


@tool(description=READ_REPORT_DESCRIPTION, parse_docstring=True, args_schema=ReadReportInput)
def read_report(runtime: ToolRuntime, name: str | None = None) -> Command:
    """Read a saved report by name, or list all saved reports.

    Args:
        name: Optional report name. Omit to list all saved reports.

    Returns:
        Command with report content or a listing in the tool message
    """
    try:
        reports = list(runtime.state.get("reports") or [])
        if not reports:
            return _report_tool_response(runtime, "No reports currently saved.")

        if not name:
            listing = ["Saved reports:"]
            for report in reports:
                preview = (report.get("content") or "")[:200]
                listing.append(
                    f"- {report.get('name', '(unnamed)')} "
                    f"({len(report.get('content') or '')} chars): {preview}..."
                )
            return _report_tool_response(runtime, "\n".join(listing))

        found = _find_report(reports, name)
        if found is None:
            names = [r.get("name", "(unnamed)") for r in reports]
            return _report_tool_response(
                runtime,
                f"Report '{name}' not found. Available: {names}",
                is_error=True,
            )
        return _report_tool_response(
            runtime,
            f"Report '{name}':\n\n{found.get('content', '')}",
        )
    except Exception as exc:
        logger.error("Error reading report: %s", exc)
        return _report_tool_response(runtime, f"Error: {exc}", is_error=True)


@tool(
    description=PRESENT_REPORT_DESCRIPTION,
    parse_docstring=True,
    args_schema=PresentReportInput,
)
def present_report(name: str, runtime: ToolRuntime) -> Command:
    """Present a saved report to the user by copying it into presented_files.

    Args:
        name: Name of a saved report to present

    Returns:
        Command updating presented_files
    """
    try:
        reports = list(runtime.state.get("reports") or [])
        found = _find_report(reports, name)
        if found is None:
            names = [r.get("name", "(unnamed)") for r in reports]
            return _report_tool_response(
                runtime,
                f"Cannot present '{name}': report not found. Available: {names}",
                is_error=True,
            )

        report_name = found["name"]
        report_content = found.get("content", "")
        presented = list(runtime.state.get("presented_files") or [])
        presented = _upsert_by_name(presented, report_name, report_content)

        try:
            writer = get_stream_writer()
            writer(
                {
                    "kind": "report.presented",
                    "name": report_name,
                    "content": report_content,
                }
            )
        except Exception as stream_exc:
            logger.warning(
                "Could not stream report.presented for '%s': %s",
                report_name,
                stream_exc,
            )

        return _report_tool_response(
            runtime,
            f"Presented report '{name}' to the user.",
            presented_files=presented,
        )
    except Exception as exc:
        logger.error("Error presenting report: %s", exc)
        return _report_tool_response(runtime, f"Error: {exc}", is_error=True)
