import json
import math

from langchain.tools import ToolRuntime, tool
from pydantic import BaseModel, ConfigDict, Field

from ...utils import logger
from .tool_descriptions import ASSESS_RISKS_DESCRIPTION

ALLOWED_STAGES = ("Demand", "Sourcing", "Manufacturing", "Delivery")


def _clamp(value: int, lo: int = 1, hi: int = 10) -> int:
    return max(lo, min(hi, value))


def _risk_band(score: int) -> str:
    if score <= 3:
        return "Low"
    if score <= 6:
        return "Moderate"
    if score <= 8:
        return "High"
    return "Critical"


def _risk_score(severity: int, exposure: int, fragility: int) -> int:
    raw = (severity * exposure * fragility) / 12.5
    return _clamp(round(raw))


class RiskItemInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    risk_id: str = Field(description="Stable ID for the risk, e.g. R1, R2")
    product: str = Field(description="Product that is at risk")
    stage: str = Field(
        description="Supply-chain stage: Demand, Sourcing, Manufacturing, or Delivery"
    )
    dimension: str = Field(
        description="The part of the chain affected, e.g. material, plant, warehouse, location, policy, labor, logistics"
    )
    severity: int = Field(
        ge=1, le=5, description="Severity (S) on a 1-5 scale derived from evidence"
    )
    exposure: int = Field(
        ge=1, le=5, description="Exposure (E) on a 1-5 scale derived from evidence"
    )
    fragility: int = Field(
        ge=1, le=5, description="Fragility (F) on a 1-5 scale derived from evidence"
    )


class AssessRisksInput(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    risks: list[RiskItemInput] = Field(
        description="List of ALL distinct risks to score, one item per risk"
    )
    runtime: ToolRuntime


@tool(description=ASSESS_RISKS_DESCRIPTION, parse_docstring=True, args_schema=AssessRisksInput)
def assess_risks(risks: list[RiskItemInput], runtime: ToolRuntime) -> str:
    """Calculate each risk's score from S/E/F factors and the cumulative risk across all risks.

    Args:
        risks: All distinct risks to evaluate, one item per risk.

    Returns:
        Deterministic markdown report with per-risk scores/bands and the cumulative risk.
    """
    try:
        if not risks:
            return (
                "No risks were provided to evaluate. "
                "Pass at least one risk item with severity, exposure, and fragility factors."
            )

        rows: list[dict] = []
        for item in risks:
            score = _risk_score(item.severity, item.exposure, item.fragility)
            rows.append(
                {
                    "risk_id": item.risk_id,
                    "product": item.product,
                    "stage": item.stage,
                    "dimension": item.dimension,
                    "s": item.severity,
                    "e": item.exposure,
                    "f": item.fragility,
                    "score": score,
                    "band": _risk_band(score),
                }
            )

        scores = [row["score"] for row in rows]
        highest = max(scores)
        average = round(sum(scores) / len(scores))
        rms_raw = math.sqrt(sum(s ** 2 for s in scores) / len(scores))
        cumulative = _clamp(round(rms_raw))
        cumulative_band = _risk_band(cumulative)

        payload = {
            "risks": rows,
            "cumulative": {
                "count": len(scores),
                "highest": highest,
                "highest_band": _risk_band(highest),
                "average": average,
                "average_band": _risk_band(average),
                "score": cumulative,
                "band": cumulative_band,
                "method": "root mean square (RMS)",
                "formula": "cumulative = round(sqrt(sum(score^2 for all risks) / count)), clamped to 1-10",
            },
        }

        lines = [
            "# Risk Score Calculation",
            "",
            "| Risk ID | Product | Stage | Dimension | S | E | F | Score | Band |",
            "|---|---|---|---|---|---|---|---|---|",
        ]
        for row in rows:
            lines.append(
                "| {risk_id} | {product} | {stage} | {dimension} | {s} | {e} | {f} | {score} | {band} |".format(
                    **row
                )
            )
        lines += [
            "",
            "## Cumulative risk",
            f"- Risks scored: {len(scores)}",
            f"- Highest individual risk: {highest}/10 ({_risk_band(highest)})",
            f"- Average risk: {average}/10 ({_risk_band(average)})",
            f"- Cumulative risk score: {cumulative}/10 ({cumulative_band})",
            "",
            "- The cumulative score is the root mean square (RMS) of all individual scores, so higher risks weigh more while every risk still contributes.",
            "",
            "```json",
            json.dumps(payload, indent=2),
            "```",
        ]
        return "\n".join(lines)
    except Exception as exc:
        logger.error("Error evaluating risks: %s", exc)
        return f"Error evaluating risks: {exc}"