"""Builds grounded explanations from analytical results."""

from __future__ import annotations

from earth_twin_engine.application.modules.regional_comparison import RegionalComparisonResult
from earth_twin_engine.application.modules.statistical_testing import StatisticalTestResult
from earth_twin_engine.application.modules.trend_analysis import TrendAnalysisCompletedEvent
from earth_twin_engine.application.modules.trend_analysis.trend_analysis_result import (
    TrendAnalysisResult,
)

from .errors import ScientificInterpretationDataError
from .scientific_interpretation_models import ScientificInterpretation


class ScientificInterpretationService:
    """Translate analytical outputs into explainable scientific summaries."""

    def build_interpretation_from_event(self, event) -> ScientificInterpretation:
        """Create a scientific interpretation from a completed module event."""

        event_type = type(event).__name__

        if hasattr(event, "result"):
            result = event.result

            if isinstance(result, TrendAnalysisResult):
                direction = result.direction.value.replace("_", " ")
                slope = result.sen_slope_per_day
                slope_text = (
                    f"The estimated Sen's slope is {slope:.6f} per day."
                    if slope is not None
                    else "The trend magnitude could not be estimated from the available data."
                )
                p_value_text = (
                    "The statistical test indicates a significant trend."
                    if result.p_value is not None and result.p_value < result.significance_level
                    else "The trend is not statistically significant at the selected significance level."
                )
                return ScientificInterpretation(
                    variable_id=result.variable_id,
                    summary=f"The analyzed variable shows a {direction} trend over the selected period.",
                    observed_pattern=f"The observed signal is {direction} during the selected observation window.",
                    trend_magnitude=slope_text,
                    statistical_evidence=p_value_text,
                    confidence_and_uncertainty="This interpretation is grounded in the calculated trend and significance test results.",
                    data_limitations=(
                        "Insufficient or missing observations reduce confidence when only sparse data are available."
                        if result.missing_observation_count
                        else "The available data appear sufficient for the reported interpretation."
                    ),
                    methodological_notes=f"Methodology: trend direction and magnitude were derived from the observed series, with p-value threshold {result.significance_level:.3f}.",
                    metadata={
                        "source_event_type": event_type,
                        "direction": result.direction.value,
                        "significance_level": result.significance_level,
                        "missing_observation_count": result.missing_observation_count,
                    },
                )

            if isinstance(result, StatisticalTestResult):
                significance = "significant" if result.significant else "not significant"
                return ScientificInterpretation(
                    variable_id=result.variable_id,
                    summary=f"The statistical test result is {significance} at the selected significance threshold.",
                    observed_pattern="The observed pattern is evaluated against the null hypothesis defined by the selected test.",
                    trend_magnitude="Magnitude is represented through the reported effect size and test statistic.",
                    statistical_evidence=f"The p-value is {result.p_value} and the confidence interval is {result.confidence_interval}.",
                    confidence_and_uncertainty="Confidence depends on the selected method, the data quality, and any assumptions underlying the test.",
                    data_limitations="Missing observations and sample limitations can weaken the precision of the inference.",
                    methodological_notes=f"Method: {result.method.name if hasattr(result, 'method') else result.method}.",
                    metadata={"source_event_type": event_type, "p_value": result.p_value},
                )

            if isinstance(result, RegionalComparisonResult):
                ranking = ", ".join(result.ranking)
                return ScientificInterpretation(
                    variable_id=result.variable_id,
                    summary=f"Regional comparison shows the strongest change in the order: {ranking}.",
                    observed_pattern="Regional differences are interpreted as patterns in the compared regions rather than proof of causation.",
                    trend_magnitude="Trend magnitude varies across regions and is reported in the comparison ordering and regional summaries.",
                    statistical_evidence="Regional findings should be interpreted together with their significance and uncertainty information.",
                    regional_comparison=f"Compared regions are ranked as follows: {ranking}.",
                    confidence_and_uncertainty="Confidence differs by region depending on the available observations and statistical support.",
                    data_limitations="Regional conclusions remain limited by uneven sampling, missing data, and methodological assumptions.",
                    methodological_notes="The comparison is descriptive and should not be mistaken for a causal explanation.",
                    metadata={"source_event_type": event_type, "ranking": result.ranking},
                )

        raise ScientificInterpretationDataError(
            f"Unsupported scientific interpretation event type: {event_type}"
        )
