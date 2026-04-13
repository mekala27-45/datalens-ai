from __future__ import annotations

from datalens_ai.core.models import DataProfile, QualityIssue


def score_quality(profile: DataProfile) -> tuple[float, list[QualityIssue]]:
    """Score data quality (0-100) and generate issues.

    The score is composed of four equally-weighted dimensions, each
    contributing up to 25 points:

    * **Completeness** -- penalises missing / null values.
    * **Uniqueness** -- penalises unexpected duplicates in ID-like columns.
    * **Consistency** -- flags columns whose type may be mis-detected.
    * **Validity** -- flags outliers and suspicious value ranges.
    """
    issues: list[QualityIssue] = []

    # Completeness (25 points)
    completeness = _score_completeness(profile, issues)

    # Uniqueness (25 points)
    uniqueness = _score_uniqueness(profile, issues)

    # Consistency (25 points)
    consistency = _score_consistency(profile, issues)

    # Validity (25 points)
    validity = _score_validity(profile, issues)

    total = completeness + uniqueness + consistency + validity
    return round(total, 1), issues


# ------------------------------------------------------------------
# Dimension scorers
# ------------------------------------------------------------------

def _score_completeness(
    profile: DataProfile, issues: list[QualityIssue]
) -> float:
    """Score based on missing values (0-25)."""
    if not profile.columns:
        return 25.0

    avg_null_pct = sum(c.null_pct for c in profile.columns) / len(profile.columns)
    score = (1 - avg_null_pct) * 25

    for col in profile.columns:
        if col.null_pct > 0.5:
            issues.append(
                QualityIssue(
                    severity="critical",
                    column=col.name,
                    issue_type="missing_values",
                    description=(
                        f"Column '{col.name}' has {col.null_pct:.0%} missing values"
                    ),
                    recommendation=(
                        f"Consider imputing or dropping column '{col.name}'"
                    ),
                )
            )
        elif col.null_pct > 0.1:
            issues.append(
                QualityIssue(
                    severity="warning",
                    column=col.name,
                    issue_type="missing_values",
                    description=(
                        f"Column '{col.name}' has {col.null_pct:.0%} missing values"
                    ),
                    recommendation=(
                        f"Review missing values in '{col.name}' -- impute or filter"
                    ),
                )
            )

    return max(0, score)


def _score_uniqueness(
    profile: DataProfile, issues: list[QualityIssue]
) -> float:
    """Score based on unexpected duplicates (0-25)."""
    score = 25.0

    # Check for ID-like columns with duplicates
    for col in profile.columns:
        if col.cardinality == "id" and col.unique_count < profile.row_count:
            dup_pct = 1 - (col.unique_count / max(profile.row_count, 1))
            score -= dup_pct * 10
            issues.append(
                QualityIssue(
                    severity="warning",
                    column=col.name,
                    issue_type="duplicate_ids",
                    description=(
                        f"ID column '{col.name}' has {dup_pct:.1%} duplicates"
                    ),
                    recommendation=(
                        f"Check for duplicate records in '{col.name}'"
                    ),
                )
            )

    return max(0, score)


def _score_consistency(
    profile: DataProfile, issues: list[QualityIssue]
) -> float:
    """Score based on type consistency (0-25)."""
    score = 25.0

    for col in profile.columns:
        # Check for mixed types in categorical columns
        if col.dtype == "text" and col.unique_count < profile.row_count * 0.1:
            score -= 2
            issues.append(
                QualityIssue(
                    severity="info",
                    column=col.name,
                    issue_type="possible_categorical",
                    description=(
                        f"Column '{col.name}' looks categorical "
                        f"({col.unique_count} unique values)"
                    ),
                    recommendation=(
                        f"Consider treating '{col.name}' as a categorical column"
                    ),
                )
            )

    return max(0, score)


def _score_validity(
    profile: DataProfile, issues: list[QualityIssue]
) -> float:
    """Score based on value validity (0-25)."""
    score = 25.0

    for col in profile.columns:
        if col.dtype == "numeric":
            # Check for suspicious ranges
            min_val = col.stats.get("min", 0)
            max_val = col.stats.get("max", 0)
            mean_val = col.stats.get("mean", 0)
            std_val = col.stats.get("std", 0)

            if std_val > 0 and max_val > mean_val + 5 * std_val:
                score -= 2
                issues.append(
                    QualityIssue(
                        severity="warning",
                        column=col.name,
                        issue_type="outliers",
                        description=(
                            f"Column '{col.name}' has extreme outliers "
                            f"(max={max_val:.2f}, mean={mean_val:.2f})"
                        ),
                        recommendation=(
                            f"Review outliers in '{col.name}' -- "
                            f"may need capping or filtering"
                        ),
                    )
                )

            # Check for negative values in likely-positive columns
            if col.semantic_type in ("currency", "percentage") and min_val < 0:
                issues.append(
                    QualityIssue(
                        severity="info",
                        column=col.name,
                        issue_type="unexpected_negatives",
                        description=(
                            f"Column '{col.name}' ({col.semantic_type}) "
                            f"has negative values"
                        ),
                        recommendation=(
                            f"Verify that negative values in '{col.name}' "
                            f"are intentional"
                        ),
                    )
                )

    return max(0, score)
