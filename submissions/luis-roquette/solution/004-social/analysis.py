"""Pure validation and decision-support engine for Challenge 004."""

from __future__ import annotations

import csv
import argparse
import hashlib
import html
import io
import json
import math
import os
import sys
import tempfile
import unicodedata
from collections.abc import Iterable
from datetime import timedelta
from pathlib import Path
from typing import Any

import pandas as pd


METHOD_VERSION = "1.0.0"
MAX_CSV_BYTES = 50 * 1024 * 1024
MAX_INT64 = 2**63 - 1
DATE_TIME_POLICY = "datas todas sem offset ou todas com o mesmo offset UTC explícito"
REQUIRED_COLUMNS = (
    "id",
    "platform",
    "content_id",
    "creator_id",
    "content_type",
    "content_category",
    "post_date",
    "views",
    "likes",
    "shares",
    "comments_count",
    "follower_count",
    "is_sponsored",
    "audience_age_distribution",
    "audience_gender_distribution",
    "audience_location",
)
OPTIONAL_COLUMNS = (
    "creator_name",
    "content_url",
    "language",
    "content_length",
    "content_description",
    "hashtags",
    "comments_text",
    "disclosure_type",
    "sponsor_name",
    "sponsor_category",
    "disclosure_location",
)
METRIC_COLUMNS = ("views", "likes", "shares", "comments_count", "follower_count")
CORE_KEYS = ("platform", "content_type", "content_category", "follower_band", "is_sponsored")
GROUP_KEYS = ("platform", "content_type", "content_category", "follower_band")
SPONSORSHIP_KEYS = (*GROUP_KEYS, "period_month")
AUDIENCE_KEYS = (
    "audience_age_distribution",
    "audience_gender_distribution",
    "audience_location",
)
DIMENSION_KEYS = {
    "platform": "platform",
    "content_type": "content_type",
    "content_category": "content_category",
    "creator_band": "follower_band",
    "audience_age": "audience_age_distribution",
    "audience_gender": "audience_gender_distribution",
    "audience_location": "audience_location",
    "month": "period_month",
}


def _error(row: int | None, column: str | None, problem: str, expected: str) -> dict[str, object]:
    return {"row": row, "column": column, "problem": problem, "expected": expected}


def load_csv(raw: bytes) -> tuple[pd.DataFrame | None, list[dict[str, object]]]:
    """Validate a complete CSV atomically and return normalized rows."""
    if not raw:
        return None, [_error(None, None, "empty_file", "CSV UTF-8 não vazio")]
    if len(raw) > MAX_CSV_BYTES:
        return None, [_error(None, None, "file_too_large", "até 50 MiB")]
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        return None, [_error(exc.start, None, "invalid_encoding", "UTF-8 ou UTF-8-BOM")]

    prior_field_limit = csv.field_size_limit()
    try:
        csv.field_size_limit(MAX_CSV_BYTES)
        try:
            reader = csv.reader(io.StringIO(text), strict=True)
            rows = []
            physical_lines = []
            while True:
                start_line = reader.line_num + 1
                record = next(reader, None)
                if record is None:
                    break
                rows.append(record)
                physical_lines.append(start_line)
        except csv.Error as exc:
            return None, [_error(None, None, "malformed_csv", str(exc))]
    finally:
        csv.field_size_limit(prior_field_limit)
    if not rows or not rows[0]:
        return None, [_error(None, None, "missing_header", "cabeçalho CSV")]
    header = rows[0]
    duplicates = sorted({name for name in header if header.count(name) > 1})
    if duplicates:
        return None, [_error(1, name, "duplicate_header", "nomes de colunas únicos") for name in duplicates]
    malformed_rows = [index for index, row in enumerate(rows[1:], start=1) if len(row) != len(header)]
    if malformed_rows:
        return None, [_error(physical_lines[index], None, "malformed_row", f"{len(header)} campos") for index in malformed_rows]

    missing = [name for name in REQUIRED_COLUMNS if name not in header]
    if missing:
        return None, [_error(1, name, "missing_required_column", "coluna obrigatória") for name in missing]

    try:
        frame = pd.read_csv(io.StringIO(text), dtype=str, keep_default_na=False)
    except (pd.errors.ParserError, UnicodeError, ValueError) as exc:
        return None, [_error(None, None, "malformed_csv", str(exc))]
    if frame.empty:
        return None, [_error(None, None, "empty_file", "ao menos uma linha de dados")]
    data_physical_lines = physical_lines[1:]

    def physical_line(index: object) -> int:
        return data_physical_lines[int(index)]

    errors: list[dict[str, object]] = []
    for column in REQUIRED_COLUMNS:
        empty = frame[column].astype(str).str.strip().eq("")
        errors.extend(
            _error(physical_line(index), column, "missing_value", "valor obrigatório")
            for index in frame.index[empty]
        )

    numeric_columns: dict[str, pd.Series] = {}
    for column in METRIC_COLUMNS:
        numeric = pd.to_numeric(frame[column], errors="coerce")
        numeric_columns[column] = numeric
        out_of_range = numeric.gt(MAX_INT64)
        invalid = numeric.isna() | ~numeric.map(math.isfinite) | numeric.lt(0) | numeric.mod(1).ne(0)
        errors.extend(
            _error(physical_line(index), column, "invalid_nonnegative_integer", "inteiro finito maior ou igual a zero")
            for index in frame.index[invalid & ~out_of_range]
        )
        errors.extend(
            _error(physical_line(index), column, "integer_out_of_range", f"inteiro entre 0 e {MAX_INT64}")
            for index in frame.index[out_of_range]
        )

    allowed_flags = {"TRUE": True, "FALSE": False, "true": True, "false": False}
    invalid_flags = ~frame["is_sponsored"].isin(allowed_flags)
    errors.extend(
        _error(physical_line(index), "is_sponsored", "invalid_boolean", "TRUE/FALSE ou true/false")
        for index in frame.index[invalid_flags]
    )

    timezone_flags = frame["post_date"].astype(str).str.contains(r"(?:[zZ]|[+-]\d{2}:?\d{2})$", regex=True)
    if timezone_flags.any() and not timezone_flags.all():
        errors.append(_error(None, "post_date", "mixed_timezone_semantics", DATE_TIME_POLICY))
    parsed_dates: list[pd.Timestamp | None] = []
    timezone_offsets: list[tuple[int, float]] = []
    for index, value in frame["post_date"].items():
        try:
            parsed = pd.Timestamp(value)
            if pd.isna(parsed):
                raise ValueError("NaT is not an analytical date")
            if parsed.tzinfo is not None:
                offset = parsed.utcoffset()
                if offset is None:
                    raise ValueError("timezone has no UTC offset")
                timezone_offsets.append((int(index), offset.total_seconds()))
            parsed_dates.append(parsed)
        except (ValueError, TypeError):
            parsed_dates.append(None)
            errors.append(_error(physical_line(index), "post_date", "invalid_date", "ISO-8601 ou %m/%d/%y %I:%M %p"))
    if timezone_offsets:
        expected_offset = timezone_offsets[0][1]
        errors.extend(
            _error(physical_line(index), "post_date", "incompatible_timezone_offset", DATE_TIME_POLICY)
            for index, offset in timezone_offsets[1:]
            if offset != expected_offset
        )

    duplicated_ids = frame["id"].duplicated(keep=False)
    errors.extend(
        _error(physical_line(index), "id", "duplicate_identity", "id único no arquivo")
        for index in frame.index[duplicated_ids]
    )
    duplicated_content = frame.duplicated(["platform", "content_id"], keep=False)
    errors.extend(
        _error(physical_line(index), "content_id", "duplicate_identity", "(platform, content_id) único no arquivo")
        for index in frame.index[duplicated_content]
    )
    if errors:
        errors.sort(key=lambda item: (item["row"] is None, item["row"] or 0, str(item["column"])))
        return None, errors

    source_hash = hashlib.sha256(raw).hexdigest()
    frame = frame.assign(
        **{column: numeric_columns[column].astype("int64") for column in METRIC_COLUMNS},
        is_sponsored=frame["is_sponsored"].map(allowed_flags).astype("bool"),
        post_date=pd.Series(parsed_dates, index=frame.index),
        source_hash=source_hash,
        source_row_id=source_hash + ":" + frame["id"].astype(str),
        source_line=physical_lines[1:],
    )
    return frame, []


def follower_band(followers: int) -> str:
    if followers < 10_000:
        return "0–9,999"
    if followers < 50_000:
        return "10,000–49,999"
    if followers < 100_000:
        return "50,000–99,999"
    if followers < 500_000:
        return "100,000–499,999"
    return "500,000+"


def derive_metrics(df: pd.DataFrame) -> pd.DataFrame:
    interactions = pd.Series(
        (
            int(likes) + int(shares) + int(comments)
            for likes, shares, comments in df[["likes", "shares", "comments_count"]].itertuples(index=False, name=None)
        ),
        index=df.index,
        dtype="object",
    )
    erv = pd.Series(
        (
            100.0 * int(interaction) / int(view) if int(view) > 0 else None
            for interaction, view in zip(interactions, df["views"], strict=True)
        ),
        index=df.index,
        dtype="float64",
    )
    erf = pd.Series(
        (
            100.0 * int(interaction) / int(followers) if int(followers) > 0 else None
            for interaction, followers in zip(interactions, df["follower_count"], strict=True)
        ),
        index=df.index,
        dtype="float64",
    )
    return df.assign(
        interactions=interactions,
        erv=erv,
        erf=erf,
        follower_band=df["follower_count"].map(lambda value: follower_band(int(value))),
        period_month=df["post_date"].dt.strftime("%Y-%m"),
    )


def _strength(rows: pd.DataFrame) -> tuple[float, dict[str, float]]:
    defined = rows.dropna(subset=["erv"])
    n_rate = len(defined)
    n_creators = int(defined["creator_id"].nunique())
    max_share = float(defined["creator_id"].value_counts(normalize=True).max()) if n_rate else 1.0
    factors = {
        "post_factor": min(n_rate / 100, 1),
        "creator_factor": min(n_creators / 20, 1),
        "concentration_factor": 1 - max_share,
    }
    return math.prod(factors.values()), factors


def _strength_label(value: float) -> str:
    if value < 0.40:
        return "limited"
    if value < 0.70:
        return "moderate"
    return "strong"


def _integer_sum(values: Iterable[object]) -> int:
    return sum(int(value) for value in values)


def _summary(rows: pd.DataFrame) -> dict[str, object]:
    rates = rows["erv"].dropna()
    eligible = rows.loc[rows["views"] > 0]
    views = _integer_sum(rows["views"])
    interactions = _integer_sum(rows["interactions"])
    creator_exposure = _integer_sum(rows.groupby("creator_id")["follower_count"].max()) if len(rows) else 0
    eligible_views = _integer_sum(eligible["views"])
    eligible_interactions = _integer_sum(eligible["interactions"])
    return {
        "posts": int(len(rows)),
        "creators": int(rows["creator_id"].nunique()),
        "views": views,
        "interactions": interactions,
        "creator_exposure": creator_exposure,
        "n_rate": int(len(rates)),
        "undefined_rates": int(rows["erv"].isna().sum()),
        "zero_interaction_share": float(rows["interactions"].eq(0).mean()) if len(rows) else None,
        "median_erv": float(rates.median()) if len(rates) else None,
        "q1_erv": float(rates.quantile(0.25)) if len(rates) else None,
        "q3_erv": float(rates.quantile(0.75)) if len(rates) else None,
        "weighted_erv": float(100.0 * eligible_interactions / eligible_views) if eligible_views else None,
    }


def _dimensions(rows: pd.DataFrame, source_hash: str) -> dict[str, list[dict[str, object]]]:
    dimensions: dict[str, list[dict[str, object]]] = {}
    for name, column in DIMENSION_KEYS.items():
        items: list[dict[str, object]] = []
        for value, group in rows.groupby(column, dropna=False, sort=True):
            items.append(
                {
                    "evidence_id": _stable_id("dimension", source_hash, {"dimension": name, "value": value}),
                    "dimension": name,
                    "value": str(value),
                    **_summary(group),
                    "source_row_ids": sorted(group["source_row_id"].astype(str)),
                }
            )
        dimensions[name] = items
    return dimensions


def _scope_dates(frame: pd.DataFrame, scope: dict[str, object]) -> tuple[pd.Timestamp, pd.Timestamp, pd.Timestamp]:
    dataset_timezone = frame["post_date"].dt.tz

    def align(value: object) -> pd.Timestamp:
        timestamp = pd.Timestamp(value)
        if dataset_timezone is None:
            return timestamp.tz_localize(None) if timestamp.tzinfo is not None else timestamp
        return timestamp.tz_localize(dataset_timezone) if timestamp.tzinfo is None else timestamp.tz_convert(dataset_timezone)

    reference = align(scope.get("reference_date") or max(frame["post_date"]))
    end = align(scope.get("target_end") or reference).normalize() + timedelta(days=1) - timedelta(microseconds=1)
    start = align(scope.get("target_start") or (reference - timedelta(days=6))).normalize()
    return start, end, reference


def _match(rows: pd.DataFrame, target: pd.Series, keys: Iterable[str]) -> pd.DataFrame:
    matched = rows
    for key in keys:
        matched = matched.loc[matched[key] == target[key]]
    return matched


def _benchmark(frame: pd.DataFrame, target: pd.Series, target_start: pd.Timestamp, strict: bool) -> dict[str, object]:
    levels = [
        ("core+age+gender+location/90d", 90, AUDIENCE_KEYS),
        ("core+age+gender+location/365d", 365, AUDIENCE_KEYS),
        ("core+age+gender/365d", 365, AUDIENCE_KEYS[:2]),
        ("core+age/365d", 365, AUDIENCE_KEYS[:1]),
        ("core/365d", 365, ()),
    ]
    if strict:
        levels = levels[:2]
    attempts: list[dict[str, object]] = []
    for name, days, audience in levels:
        candidates = frame.loc[
            (frame["post_date"] < target_start)
            & (frame["post_date"] >= target_start - timedelta(days=days))
            & (frame["creator_id"] != target["creator_id"])
        ]
        candidates = _match(candidates, target, (*CORE_KEYS, *audience)).dropna(subset=["erv"])
        n_rate = len(candidates)
        n_creators = int(candidates["creator_id"].nunique())
        attempt = {"level": name, "n_rate": n_rate, "n_creators": n_creators}
        attempts.append(attempt)
        if n_rate >= 30 and n_creators >= 5:
            rates = candidates["erv"]
            q1 = float(rates.quantile(0.25))
            q3 = float(rates.quantile(0.75))
            strength, factors = _strength(candidates)
            context = {key: target[key] for key in (*CORE_KEYS, *audience)}
            return {
                "eligible": True,
                "attempts": attempts,
                "effective_level": name,
                "effective_context": context,
                "removed_controls": [key for key in AUDIENCE_KEYS if key not in audience],
                "n_rate": n_rate,
                "n_creators": n_creators,
                "median": float(rates.median()),
                "q1": q1,
                "q3": q3,
                "iqr": q3 - q1,
                "strength": strength,
                "strength_factors": factors,
                "source_row_ids": sorted(candidates["source_row_id"].astype(str)),
                "abstention_reason": None,
            }
    return {
        "eligible": False,
        "attempts": attempts,
        "effective_level": None,
        "effective_context": None,
        "removed_controls": [],
        "n_rate": 0,
        "n_creators": 0,
        "strength": 0.0,
        "strength_factors": {"post_factor": 0.0, "creator_factor": 0.0, "concentration_factor": 0.0},
        "source_row_ids": [],
        "abstention_reason": "fewer_than_30_rates_or_5_creators",
    }


def _stable_id(kind: str, source_hash: str, payload: object) -> str:
    encoded = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str, separators=(",", ":"))
    return f"{kind}-{hashlib.sha256(f'{METHOD_VERSION}|{source_hash}|{encoded}'.encode()).hexdigest()[:16]}"


def _sponsorship(targets: pd.DataFrame, source_hash: str) -> dict[str, object]:
    strata: list[dict[str, object]] = []
    uncovered: list[dict[str, object]] = []
    comparable_posts = 0
    for key, group in targets.groupby(list(SPONSORSHIP_KEYS), dropna=False, sort=True):
        context = dict(zip(SPONSORSHIP_KEYS, key, strict=True))
        arms = {flag: group.loc[group["is_sponsored"] == flag].dropna(subset=["erv"]) for flag in (False, True)}
        eligible = all(len(arm) >= 30 and arm["creator_id"].nunique() >= 5 for arm in arms.values())
        if not eligible:
            uncovered.append(
                {
                    **context,
                    "posts": int(len(group)),
                    "organic_posts": int((~group["is_sponsored"]).sum()),
                    "sponsored_posts": int(group["is_sponsored"].sum()),
                    "organic_defined_rates": int(len(arms[False])),
                    "sponsored_defined_rates": int(len(arms[True])),
                    "organic_creators": int(arms[False]["creator_id"].nunique()),
                    "sponsored_creators": int(arms[True]["creator_id"].nunique()),
                    "reason": "missing_or_insufficient_contemporaneous_arm",
                }
            )
            continue
        creator_medians = {
            flag: arms[flag].groupby("creator_id")["erv"].median() for flag in (False, True)
        }
        organic = float(creator_medians[False].median())
        sponsored = float(creator_medians[True].median())
        strength_org, factors_org = _strength(arms[False])
        strength_spon, factors_spon = _strength(arms[True])
        delta = sponsored - organic
        comparable_posts += len(group)
        strata.append(
            {
                "evidence_id": _stable_id("sponsorship", source_hash, context),
                "context": context,
                "organic": {**_summary(arms[False]), "creator_median_erv": organic, "strength_factors": factors_org},
                "sponsored": {**_summary(arms[True]), "creator_median_erv": sponsored, "strength_factors": factors_spon},
                "delta_erv_pp": delta,
                "relative_difference_pct": (100 * delta / organic) if organic > 0 else None,
                "strength": min(strength_org, strength_spon),
                "creator_overlap": int(len(set(creator_medians[False].index) & set(creator_medians[True].index))),
                "representative_date": arms[True]["post_date"].median(),
                "source_row_ids": sorted(group["source_row_id"].astype(str)),
                "claim": "observational_association_not_causal_or_financial_roi",
            }
        )
    return {
        "evidence_id": _stable_id("sponsorship-overview", source_hash, {"posts": len(targets), "strata": len(strata), "uncovered": len(uncovered)}),
        "posts": int(len(targets)),
        "eligible_strata": len(strata),
        "uncovered_count": len(uncovered),
        "strata": strata,
        "uncovered_strata": uncovered,
        "coverage": comparable_posts / len(targets) if len(targets) else 0.0,
        "period_granularity": "calendar_month",
        "required_financial_data": ["investment", "production_cost", "revenue_or_conversion_value"],
        "source_row_ids": sorted(targets["source_row_id"].astype(str)),
    }


def _p95(values: pd.Series) -> float:
    if values.empty:
        return 0.0
    value = float(values.quantile(0.95))
    if value > 0:
        return value
    positives = values.loc[values > 0]
    return float(positives.max()) if len(positives) else 0.0


def _aggregate_normalization(targets: pd.DataFrame) -> dict[tuple[str, str], dict[str, float]]:
    pools: dict[tuple[str, str], list[dict[str, float]]] = {}
    specifications = (
        ("editorial", targets.loc[~targets["is_sponsored"]], (*GROUP_KEYS, *AUDIENCE_KEYS)),
        ("sponsorship", targets.loc[targets["is_sponsored"]], SPONSORSHIP_KEYS),
    )
    for kind, rows, keys in specifications:
        for _, group in rows.groupby(list(keys), dropna=False, sort=True):
            platform = str(group.iloc[0]["platform"])
            pools.setdefault((kind, platform), []).append(
                {
                    "views": float(_integer_sum(group["views"])),
                    "interactions": float(_integer_sum(group["interactions"])),
                    "followers": float(_integer_sum(group.groupby("creator_id")["follower_count"].max())),
                }
            )
    return {
        key: {
            name: _p95(pd.Series([values[name] for values in groups]))
            for name in ("views", "interactions", "followers")
        }
        for key, groups in pools.items()
    }


def _priority(values: dict[str, float], denominators: dict[str, float], strength: float, date: pd.Timestamp, reference: pd.Timestamp) -> tuple[float, dict[str, float]]:
    normalized = [min(values[name] / denominators[name], 1.0) if denominators[name] else 0.0 for name in ("views", "interactions", "followers")]
    impact = sum(normalized) / 3
    age = max((reference.normalize() - date.normalize()).days, 0)
    recency = 2 ** (-age / 7)
    score = 100 * impact * strength * recency
    return score, {"impact": impact, "strength": strength, "recency": recency}


def _frequency_hypothesis(
    rows: pd.DataFrame,
    coverage_start: pd.Timestamp,
    coverage_end: pd.Timestamp,
    period_month: object | None = None,
) -> dict[str, object]:
    if period_month is not None:
        month_start = pd.Timestamp(f"{period_month}-01")
        if coverage_start.tzinfo is not None:
            month_start = month_start.tz_localize(coverage_start.tzinfo)
        next_month = month_start + pd.offsets.MonthBegin(1)
        coverage_start = max(coverage_start, month_start)
        coverage_end = min(coverage_end, next_month - timedelta(days=1))

    first_monday = coverage_start.normalize() + timedelta(days=(-coverage_start.weekday()) % 7)
    last_sunday = coverage_end.normalize() - timedelta(days=(coverage_end.weekday() + 1) % 7)
    week_starts: list[pd.Timestamp] = []
    cursor = first_monday
    while cursor + timedelta(days=6) <= last_sunday:
        week_starts.append(cursor)
        cursor += timedelta(days=7)

    observed = rows.assign(
        week_start=rows["post_date"].map(
            lambda value: value.normalize() - timedelta(days=value.weekday())
        )
    )
    observed = observed.loc[observed["week_start"].isin(week_starts)]
    counts = observed.groupby(["creator_id", "week_start"], sort=True).size()
    observed_weeks = int(observed["week_start"].nunique())
    sufficient = observed_weeks >= 2
    return {
        "status": "test" if sufficient else "collect",
        "value": float(counts.median()) if sufficient else None,
        "unit": "posts_per_creator_per_complete_iso_week",
        "method": "median_observed_posts_per_creator_week",
        "coverage_rule": (
            "complete_iso_weeks_within_calendar_month_and_scope"
            if period_month is not None
            else "complete_iso_weeks_within_scope"
        ),
        "period_month": str(period_month) if period_month is not None else None,
        "sample_creator_weeks": int(len(counts)),
        "sample_creators": int(observed["creator_id"].nunique()),
        "complete_weeks_available": len(week_starts),
        "observed_complete_weeks": observed_weeks,
        "window_start": week_starts[0].isoformat() if week_starts else None,
        "window_end": (week_starts[-1] + timedelta(days=6)).isoformat() if week_starts else None,
        "action_type": "test_observed_cadence" if sufficient else "collect_two_complete_weeks",
        "collection_requirement_weeks": 2,
        "limitation": "frequência observada é hipótese de teste, não efeito causal",
    }


def _context_rows(rows: pd.DataFrame, context: dict[str, object], sponsored: bool | None = None) -> pd.DataFrame:
    selected = rows
    for key, value in context.items():
        if key in selected.columns:
            selected = selected.loc[selected[key] == value]
    if sponsored is not None:
        selected = selected.loc[selected["is_sponsored"] == sponsored]
    return selected


def _editorial(frame: pd.DataFrame, start: pd.Timestamp, end: pd.Timestamp, source_hash: str) -> list[dict[str, object]]:
    duration = int((end.normalize() - start.normalize()).days) + 1
    previous_end = start - timedelta(microseconds=1)
    previous_start = start.normalize() - timedelta(days=duration)
    current = frame.loc[(frame["post_date"] >= start) & (frame["post_date"] <= end) & ~frame["is_sponsored"]]
    previous = frame.loc[(frame["post_date"] >= previous_start) & (frame["post_date"] <= previous_end) & ~frame["is_sponsored"]]
    evidence: list[dict[str, object]] = []
    keys = [*GROUP_KEYS, *AUDIENCE_KEYS]
    for key, now in current.groupby(keys, dropna=False, sort=True):
        context = dict(zip(keys, key, strict=True))
        before = previous
        for name, value in context.items():
            before = before.loc[before[name] == value]
        now_defined = now.dropna(subset=["erv"])
        before_defined = before.dropna(subset=["erv"])
        if min(len(now_defined), len(before_defined)) < 30 or min(now_defined["creator_id"].nunique(), before_defined["creator_id"].nunique()) < 5:
            continue
        current_strength, _ = _strength(now_defined)
        previous_strength, _ = _strength(before_defined)
        delta_erv = float(now_defined["erv"].median() - before_defined["erv"].median())
        delta_views = float(now["views"].median() - before["views"].median())
        delta_interactions = float(now["interactions"].median() - before["interactions"].median())
        evidence.append(
            {
                "evidence_id": _stable_id("editorial", source_hash, {**context, "start": start, "end": end}),
                "context": context,
                "current": _summary(now),
                "previous": _summary(before),
                "delta_erv_pp": delta_erv,
                "delta_views_per_post": delta_views,
                "delta_interactions_per_post": delta_interactions,
                "strength": min(current_strength, previous_strength),
                "representative_date": now["post_date"].sort_values().iloc[len(now) // 2],
                "source_row_ids": sorted(now["source_row_id"].astype(str)),
                "creator_overlap": int(len(set(now["creator_id"]) & set(before["creator_id"]))),
            }
        )
    return evidence


def analyze(df: pd.DataFrame, scope: dict[str, object], source_hash: str) -> dict[str, object]:
    frame = derive_metrics(df)
    start, end, reference = _scope_dates(frame, scope)
    filters = dict(scope.get("filters") or {})
    targets = frame.loc[(frame["post_date"] >= start) & (frame["post_date"] <= end)]
    for key, value in filters.items():
        if key in targets.columns and value not in (None, "", []):
            accepted = value if isinstance(value, (list, tuple, set)) else [value]
            targets = targets.loc[targets[key].isin(accepted)]
    frequency_coverage_start = max(start.normalize(), min(frame["post_date"]).normalize())
    frequency_coverage_end = min(end.normalize(), max(frame["post_date"]).normalize())

    alerts: list[dict[str, object]] = []
    alert_targets = targets if bool(scope.get("include_post_alerts", True)) else targets.iloc[0:0]
    for _, target in alert_targets.sort_values(["post_date", "id"]).iterrows():
        if pd.isna(target["erv"]):
            continue
        benchmark = _benchmark(frame, target, start, bool(scope.get("strict_audience", False)))
        if not benchmark["eligible"]:
            continue
        iqr = float(benchmark["iqr"])
        rate = float(target["erv"])
        q1 = float(benchmark["q1"])
        q3 = float(benchmark["q3"])
        median = float(benchmark["median"])
        direction = "high" if rate > q3 + 1.5 * iqr else "low" if rate < q1 - 1.5 * iqr else "within"
        is_outlier = iqr > 0 and direction != "within"
        context = {key: target[key] for key in (*CORE_KEYS, *AUDIENCE_KEYS)}
        alerts.append(
            {
                "evidence_id": _stable_id("post", source_hash, {"id": target["id"], "context": context, "scope": scope}),
                "evidence_type": "post",
                "source_id": str(target["id"]),
                "source_row_id": str(target["source_row_id"]),
                "context": context,
                "post_date": target["post_date"].isoformat(),
                "erv": rate,
                "delta_erv_pp": rate - median,
                "relative_difference_pct": (100 * (rate - median) / median) if median > 0 else None,
                "direction": direction,
                "is_outlier": is_outlier,
                "strength": float(benchmark["strength"]),
                "strength_label": _strength_label(float(benchmark["strength"])) if iqr > 0 else "limited",
                "benchmark": benchmark,
                "values": {"views": int(target["views"]), "interactions": int(target["interactions"]), "followers": int(target["follower_count"])},
            }
        )

    sponsorship = _sponsorship(targets, source_hash)
    editorial = _editorial(frame, start, end, source_hash)
    candidates: list[dict[str, object]] = []

    platform_denominators: dict[str, dict[str, float]] = {}
    for platform, rows in targets.groupby("platform"):
        platform_denominators[str(platform)] = {
            "views": _p95(rows["views"].astype(float)),
            "interactions": _p95(rows["interactions"].astype(float)),
            "followers": _p95(rows["follower_count"].astype(float)),
        }
    for alert in alerts:
        if not alert["is_outlier"]:
            continue
        platform = str(alert["context"]["platform"])
        score, components = _priority(alert["values"], platform_denominators[platform], float(alert["strength"]), pd.Timestamp(alert["post_date"]), reference)
        action_type = "test" if alert["direction"] == "high" else "review"
        candidates.append(
            {
                "recommendation_key": alert["evidence_id"],
                "evidence_id": alert["evidence_id"],
                "evidence_type": "post",
                "topic": "quick_win" if alert["direction"] == "high" else "stop",
                "action_type": action_type,
                "action": "Testar repetição controlada do padrão" if alert["direction"] == "high" else "Revisar o criativo e evitar repetir o padrão até novo teste",
                "owner": "Gestor de Social Media",
                "execution_window": "próximos 7 dias",
                "review_window": "7 dias após o teste",
                "metric": "ERv e volume por post",
                "priority": score,
                "priority_components": components,
                "priority_values": alert["values"],
                "normalization": platform_denominators[platform],
                "delta_erv_pp": alert["delta_erv_pp"],
                "representative_date": alert["post_date"],
                "context": alert["context"],
                "supporting_topics": ["audience", "creator", "frequency"],
                "frequency_hypothesis": _frequency_hypothesis(
                    _context_rows(targets, alert["context"]),
                    frequency_coverage_start,
                    frequency_coverage_end,
                    alert["context"].get("period_month"),
                ),
            }
        )

    aggregate_items: list[tuple[str, dict[str, object], dict[str, float], str, str]] = []
    for item in editorial:
        current = item["current"]
        values = {"views": float(current["views"]), "interactions": float(current["interactions"]), "followers": float(current["creator_exposure"])}
        delta = float(item["delta_erv_pp"])
        aligned_up = delta > 0 and item["delta_views_per_post"] >= 0 and item["delta_interactions_per_post"] >= 0
        aligned_down = delta < 0 and item["delta_views_per_post"] <= 0 and item["delta_interactions_per_post"] <= 0
        if float(item["strength"]) >= 0.70 and aligned_up:
            action_type, topic = "scale_test", "effort"
        elif float(item["strength"]) >= 0.70 and aligned_down:
            action_type, topic = "review_stop", "stop"
        else:
            action_type, topic = "test", "effort"
        aggregate_items.append(("editorial", item, values, action_type, topic))
    for item in sponsorship["strata"]:
        arm = item["sponsored"]
        values = {"views": float(arm["views"]), "interactions": float(arm["interactions"]), "followers": float(arm["creator_exposure"])}
        delta = float(item["delta_erv_pp"])
        delta_views = float(arm["views"]) / arm["posts"] - float(item["organic"]["views"]) / item["organic"]["posts"]
        delta_interactions = float(arm["interactions"]) / arm["posts"] - float(item["organic"]["interactions"]) / item["organic"]["posts"]
        if float(item["strength"]) >= 0.40 and delta > 0 and delta_views >= 0 and delta_interactions >= 0:
            action_type = "sponsorship_test_after_costs"
        elif float(item["strength"]) >= 0.70 and delta < 0 and delta_views <= 0 and delta_interactions <= 0:
            action_type = "review_renewal"
        else:
            action_type = "test"
        aggregate_items.append(("sponsorship", item, values, action_type, "sponsorship"))

    aggregate_denominators = _aggregate_normalization(targets)
    for kind, item, values, action_type, topic in aggregate_items:
        platform = str(item["context"]["platform"])
        representative = pd.Timestamp(item["representative_date"])
        score, components = _priority(values, aggregate_denominators[(kind, platform)], float(item["strength"]), representative, reference)
        candidates.append(
            {
                "recommendation_key": item["evidence_id"],
                "evidence_id": item["evidence_id"],
                "evidence_type": "aggregate",
                "topic": topic,
                "action_type": action_type,
                "action": "Executar teste controlado e reavaliar; patrocínio depende de custos reais" if kind == "sponsorship" else "Testar o padrão editorial e reavaliar sinais de taxa e volume",
                "owner": "Gestor de Social Media",
                "execution_window": "próximos 7 dias",
                "review_window": "7 dias após o teste",
                "metric": "ERv, views e interações por post",
                "priority": score,
                "priority_components": components,
                "priority_values": values,
                "normalization": aggregate_denominators[(kind, platform)],
                "delta_erv_pp": item["delta_erv_pp"],
                "representative_date": representative.isoformat(),
                "context": item["context"],
                "supporting_topics": ["audience", "creator", "frequency", "quick_win"],
                "frequency_hypothesis": _frequency_hypothesis(
                    _context_rows(
                        targets,
                        item["context"],
                        sponsored=False if kind == "editorial" else True,
                    ),
                    frequency_coverage_start,
                    frequency_coverage_end,
                    item["context"].get("period_month"),
                ),
            }
        )

    candidates.sort(key=lambda item: (-float(item["priority"]), -abs(float(item["delta_erv_pp"])), -pd.Timestamp(item["representative_date"]).value, str(item["evidence_id"])))
    recommendations: list[dict[str, object]] = []
    seen: set[tuple[object, ...]] = set()
    for item in candidates:
        context = item["context"]
        key = tuple(context.get(name) for name in (*GROUP_KEYS, *AUDIENCE_KEYS)) + (start.isoformat(), end.isoformat())
        if key in seen:
            continue
        seen.add(key)
        recommendations.append(item)
        if len(recommendations) == 3:
            break

    attempted = sum(len(alert.get("benchmark", {}).get("attempts", [])) for alert in alerts)
    pending = [] if recommendations else [{"evidence_id": _stable_id("pending", source_hash, scope), "action_type": "collect", "reason": "no_eligible_performance_evidence"}]
    return {
        "source": {
            "source_hash": source_hash,
            "rows": int(len(frame)),
            "period_start": min(frame["post_date"]).isoformat(),
            "period_end": max(frame["post_date"]).isoformat(),
            "platforms": sorted(frame["platform"].unique().tolist()),
        },
        "scope": {**scope, "target_start": start.isoformat(), "target_end": end.isoformat(), "reference_date": reference.isoformat(), "method_version": METHOD_VERSION},
        "quality": {
            "optional_columns_missing": sorted(set(OPTIONAL_COLUMNS) - set(frame.columns)),
            "ignored_source_engagement_rate": "engagement_rate" in frame.columns,
            "benchmark_levels_attempted": attempted,
        },
        "metrics": _summary(targets),
        "dimensions": _dimensions(targets, source_hash),
        "cohorts": {"editorial": editorial},
        "alerts": alerts,
        "sponsorship": sponsorship,
        "recommendations": recommendations,
        "pending": pending,
        "row_references": {str(row["source_row_id"]): int(row["source_line"]) for _, row in frame.iterrows()},
    }


EXPORT_COLUMNS = (
    "record_type", "evidence_id", "source_hash", "method_version", "text",
    "metric_name", "metric_value", "unit", "context", "scope",
    "formula",
    "source_row_id", "source_line", "decision_id", "status", "owner",
    "execution_window", "review_window",
    "rank", "recommendation_key", "priority", "impact", "strength", "recency",
    "priority_values", "normalization", "delta_erv_pp", "representative_date",
    "action", "action_type", "topic", "metric", "frequency_hypothesis",
    "reference_chunk", "reference_index",
)

# History columns are appended only when history exists, preserving the static
# analytical export contract (and its byte identity) for empty local logs.
HISTORY_EXPORT_COLUMNS = (
    "event_id", "revision_of", "decided_at", "baseline", "original_text",
    "edited_text", "effective_text", "outcome_id", "recorded_at",
    "decision_source_hash", "decision_scope", "decision_method_version",
    "execution_status", "execution_date", "observed", "comparison", "reason",
    "period_start", "period_end", "coverage_days", "baseline_coverage_days",
    "coverage_equal", "comparable", "baseline_median", "observed_median",
    "median_delta", "baseline_volume_per_day", "observed_volume_per_day",
    "non_causal", "field_name", "field_chunk", "field_value",
)


def _cell(value: object) -> str | int | float:
    if value is None:
        return ""
    if isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, (int, float)):
        return value
    text = json.dumps(value, ensure_ascii=False, sort_keys=True, default=str) if isinstance(value, (dict, list, tuple)) else str(value)
    for char in text:
        if unicodedata.category(char) in ("Cc", "Cf") or char in ("=", "+", "-", "@"):
            return f"'{text}"
        if not char.isspace():
            break
    return text


def _reference_chunks(source_ids: list[str], lines: dict[str, int]) -> Iterable[dict[str, object]]:
    chunk = 1
    ids, indices, physical = [], [], []
    size = 2
    for index, source_id in enumerate(source_ids):
        opaque_id = str(source_id).split(":", 1)[-1]
        # Bound even a single unusually long ID; repeated indices join its fragments.
        for offset in range(0, len(opaque_id), 4096):
            fragment = opaque_id[offset:offset + 4096]
            length = len(json.dumps(fragment, ensure_ascii=False)) + 2
            if ids and (size + length > 32_768 or len(ids) == 500):
                yield {"reference_chunk": chunk, "reference_index": indices, "source_row_id": ids, "source_line": physical}
                chunk += 1
                ids, indices, physical, size = [], [], [], 2
            ids.append(fragment)
            indices.append(index)
            physical.append(lines[str(source_id)])
            size += length
    if ids:
        yield {"reference_chunk": chunk, "reference_index": indices, "source_row_id": ids, "source_line": physical}


def iter_export_rows(result: dict[str, object], decisions: list[dict[str, object]]) -> Iterable[dict[str, object]]:
    source = result.get("source", {})
    scope = result.get("scope", {})
    source_hash = source.get("source_hash", "")
    method = scope.get("method_version", METHOD_VERSION)
    columns = EXPORT_COLUMNS + (HISTORY_EXPORT_COLUMNS if decisions else ())

    def row(record_type: str, evidence_id: str = "", **values: object) -> dict[str, object]:
        return {name: _cell({"record_type": record_type, "evidence_id": evidence_id, "source_hash": source_hash, "method_version": method, "scope": scope, **values}.get(name, "")) for name in columns}

    def history_row(record_type: str, evidence_id: str, **values: object) -> Iterable[dict[str, object]]:
        # Never infer historical provenance from the currently active analysis.
        values = {"source_hash": "", "scope": None, "method_version": "", **values}
        exported = row(record_type, evidence_id, **values)
        chunks = []
        for name, value in exported.items():
            if isinstance(value, str) and len(value) > 32_768:
                exported[name] = ""
                for offset in range(0, len(value), 4096):
                    chunks.append(row(
                        "history_field", evidence_id,
                        **{key: values.get(key, "") for key in ("source_hash", "method_version", "decision_id", "outcome_id", "event_id")},
                        scope=None, field_name=name, field_chunk=offset // 4096 + 1,
                        field_value=json.dumps(value[offset:offset + 4096], ensure_ascii=False),
                    ))
        yield exported
        yield from chunks

    yield row("summary", metric_name="posts", metric_value=result.get("metrics", {}).get("posts"), unit="posts", text="Escopo analisado")
    summary_id = _stable_id("summary", str(source_hash), scope)
    evidence: list[dict[str, object]] = [{
        "evidence_id": summary_id,
        "dimension": "overall",
        "value": "Escopo completo",
        **result.get("metrics", {}),
        "source_row_ids": list(result.get("row_references", {})),
    }]
    for items in result.get("dimensions", {}).values():
        evidence.extend(items)
    evidence.extend(result.get("alerts", []))
    evidence.extend(result.get("cohorts", {}).get("editorial", []))
    if result.get("sponsorship", {}).get("evidence_id"):
        evidence.append(result["sponsorship"])
    evidence.extend(result.get("sponsorship", {}).get("strata", []))
    evidence.extend(result.get("pending", []))

    emitted: set[str] = set()
    for item in evidence:
        evidence_id = str(item.get("evidence_id", ""))
        if not evidence_id or evidence_id in emitted:
            continue
        emitted.add(evidence_id)
        metric_name = "metric_value" if item.get("metric_value") is not None else "median_erv" if "median_erv" in item else "delta_erv_pp" if item.get("delta_erv_pp") is not None else "coverage" if item.get("coverage") is not None else "posts"
        metric_value = item.get(metric_name, item.get("metric_value", item.get("posts", "")))
        text = item.get("value", item.get("action", item.get("reason", item.get("claim", item.get("direction", item.get("dimension", "evidence"))))))
        context = dict(item.get("context") or {"dimension": item.get("dimension"), "value": item.get("value")})
        context.update({name: item[name] for name in ("posts", "creators", "n_rate", "views", "interactions", "creator_exposure", "undefined_rates", "zero_interaction_share", "weighted_erv", "q1_erv", "q3_erv", "strength", "organic", "sponsored", "creator_overlap", "eligible_strata", "uncovered_count", "coverage", "period_granularity", "required_financial_data") if name in item})
        formula = "eligible controlled posts / scoped posts" if evidence_id.startswith("sponsorship-overview-") else "median_by_creator(sponsored ERv) - median_by_creator(organic ERv)" if evidence_id.startswith("sponsorship-") else "median(100 * (likes + shares + comments_count) / views)" if evidence_id.startswith(("dimension-", "summary-")) else "method_version contract"
        yield row("evidence", evidence_id, text=text, metric_name=metric_name, metric_value=metric_value, unit="ratio" if metric_name == "coverage" else "percentage_points" if metric_name == "delta_erv_pp" else "percent" if "erv" in metric_name else "count", context=context, formula=formula)
        source_row_ids = item.get("source_row_ids", [])
        for chunk in _reference_chunks(source_row_ids, result.get("row_references", {})):
            yield row("source_ref", evidence_id, **chunk)

    for rank, item in enumerate(result.get("recommendations", []), start=1):
        yield row("recommendation", str(item["evidence_id"]), rank=rank,
                  **{name: item.get(name) for name in ("recommendation_key", "priority", "priority_values", "normalization", "delta_erv_pp", "representative_date", "context", "action", "action_type", "topic", "metric", "owner", "execution_window", "review_window", "frequency_hypothesis")},
                  **item.get("priority_components", {}),
                  formula="100 * mean(min(V/P95_V,1), min(I/P95_I,1), min(F/P95_F,1)) * strength * 2**(-age_days/7)")

    for decision in decisions:
        baseline = decision.get("baseline", {})
        evidence_id = str(baseline.get("evidence_id") or decision.get("evidence_id") or decision.get("recommendation_key", ""))
        effective = (decision.get("edited_text", "") if decision.get("status") == "edited" else decision.get("original_text", decision.get("text", decision.get("action", ""))))
        decision_values = {key: decision.get(key, "") for key in (
            "decision_id", "event_id", "revision_of", "decided_at", "recommendation_key",
            "source_hash", "scope", "method_version", "status", "original_text", "edited_text",
            "owner", "execution_window", "review_window",
        )}
        yield from history_row("decision", evidence_id, **decision_values, baseline=baseline, text=effective, effective_text=effective)
        for outcome in decision.get("outcomes", []):
            observed = outcome.get("observed", {})
            comparison = outcome.get("comparison", {})
            yield from history_row(
                "outcome", evidence_id,
                **{key: outcome.get(key, "") for key in ("outcome_id", "event_id", "source_hash", "method_version", "recorded_at", "execution_status", "execution_date", "status", "reason")},
                scope=outcome.get("scope", observed.get("scope")),
                decision_id=decision.get("decision_id", ""), revision_of=decision.get("revision_of"),
                decided_at=decision.get("decided_at", ""),
                decision_source_hash=decision.get("source_hash", ""),
                decision_scope=decision.get("scope"), decision_method_version=decision.get("method_version", ""),
                observed=observed, comparison=comparison,
                metric_name=observed.get("metric", outcome.get("metric_name", "")),
                metric_value=observed.get("median", outcome.get("metric_value")),
                unit="percent" if observed.get("metric") == "erv" else outcome.get("unit", ""),
                **{key: observed.get(key) for key in ("period_start", "period_end", "coverage_days")},
                baseline_coverage_days=baseline.get("coverage_days"),
                **{key: comparison.get(key) for key in ("coverage_equal", "baseline_median", "observed_median", "median_delta", "baseline_volume_per_day", "observed_volume_per_day")},
                comparable=outcome.get("status") == "observed", non_causal=True,
                text="Associação observacional; não demonstra causalidade ou ROI financeiro.",
            )


def export_evidence(result: dict[str, object], decisions: list[dict[str, object]]) -> bytes:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=EXPORT_COLUMNS + (HISTORY_EXPORT_COLUMNS if decisions else ()), lineterminator="\n")
    writer.writeheader()
    writer.writerows(iter_export_rows(result, decisions))
    return output.getvalue().encode("utf-8")


RECENCY_NOTE = (
    "Atualidade = 2^(−idade em dias/7), ancorada na data de referência do dataset. "
    "Em grupos agregados, a data representativa é a mediana das datas do grupo-alvo "
    "(posts patrocinados na comparação de patrocínio). Um escopo de dois anos pode "
    "produzir scores muito pequenos: isso preserva a regra de recência e não demonstra "
    "uma oportunidade atual. A ordem é prioridade decrescente, |ΔERv| decrescente, "
    "data representativa decrescente e evidence_id crescente, após deduplicação contextual."
)


def _recommendation_text(item: dict[str, object]) -> str:
    context = " / ".join(str(value) for value in item.get("context", {}).values())
    components = item.get("priority_components", {})
    frequency = item.get("frequency_hypothesis")
    frequency_text = ""
    if frequency:
        cadence = (f"Testar {frequency['value']:g} posts por creator por semana ISO completa"
                   if frequency["value"] is not None else "Coletar antes de sugerir cadência; valor não definido")
        frequency_text = (
            f". Frequência: {cadence}; status {frequency['status']}; unidade {frequency['unit']}; "
            f"mês {frequency.get('period_month') or 'não fixado'}; regra {frequency['coverage_rule']}; "
            f"método {frequency['method']}; {frequency['sample_creator_weeks']} creator-semanas, "
            f"{frequency['sample_creators']} creators; {frequency['complete_weeks_available']} semanas completas disponíveis, "
            f"{frequency['observed_complete_weeks']} semanas observadas; janela {frequency['window_start'] or 'não definida'} a {frequency['window_end'] or 'não definida'}; "
            f"ação {frequency['action_type']}; mínimo de {frequency['collection_requirement_weeks']} semanas completas observadas. "
            f"Limite: {frequency['limitation']}; ausência de linha não equivale a zero."
        )
    return (
        f"{context}: {item.get('action', item.get('reason', 'Coletar evidência'))}. "
        f"Prioridade {item.get('priority', 0):.6g}; impacto {components.get('impact', 0):.6g}; "
        f"força {components.get('strength', 0):.6g}; atualidade {components.get('recency', 0):.6g}; "
        f"ΔERv {item.get('delta_erv_pp', 0):+.6g} p.p.; data representativa {item.get('representative_date', 'não definida')}. "
        f"Responsável: {item.get('owner', 'Gestor de Social Media')}; execução: {item.get('execution_window', 'coletar primeiro')}; "
        f"revisão: {item.get('review_window', 'após coleta')}; métrica: {item.get('metric', 'amostra comparável')}. "
        f"Evidência: {item.get('evidence_id', '')}{frequency_text}"
    )


def executive_summary(result: dict[str, object], decisions: list[dict[str, object]]) -> str:
    source = result.get("source", {})
    metrics = result.get("metrics", {})
    recommendations = result.get("recommendations", [])
    dimensions = [item for items in result.get("dimensions", {}).values() for item in items]
    priority_items = recommendations or result.get("pending", [])
    priorities = "".join(
        f"<li>{html.escape(_recommendation_text(item))}</li>"
        for item in priority_items[:3]
    )
    findings = "".join(
        f"<li>{html.escape(str(item.get('dimension', 'segmento')))} = {html.escape(str(item.get('value', '')))}: {int(item.get('posts', 0))} posts; mediana ERv {format(float(item['median_erv']), '.2f') + '%' if item.get('median_erv') is not None else 'não definida (views=0: sem denominador para ERv)'} <small>{html.escape(str(item.get('evidence_id', '')))}</small></li>"
        for item in sorted(dimensions, key=lambda value: (-int(value.get("posts", 0)), str(value.get("evidence_id", ""))))[:5]
    )
    decisions_html = "".join(f"<li>{html.escape(str(item.get('status', '')))} — {html.escape(str(item.get('text', item.get('action', ''))))}</li>" for item in decisions[:5]) or "<li>Nenhuma decisão registrada.</li>"
    return f"""<!doctype html><html lang=\"pt-BR\"><head><meta charset=\"utf-8\"><title>Resumo executivo social</title><style>@page{{size:A4;margin:12mm}}body{{font:14px system-ui;max-width:900px;margin:auto;color:#17202a}}h1,h2{{margin:.5em 0}}small{{color:#566}}.kpi{{display:flex;gap:2rem}}@media print{{body{{font-size:11px}}}}</style></head><body><h1>Resumo executivo social</h1><p>Fonte {html.escape(str(source.get('source_hash', '')))} · {int(source.get('rows', 0))} linhas · {html.escape(str(source.get('period_start', '')))} a {html.escape(str(source.get('period_end', '')))}</p><div class=\"kpi\"><b>{int(metrics.get('posts', 0))} posts</b><b>{int(metrics.get('views', 0))} views</b><b>{int(metrics.get('interactions', 0))} interações</b></div><h2>Prioridades</h2><ol>{priorities}</ol><p><small>{html.escape(RECENCY_NOTE)}</small></p><h2>Evidências</h2><ul>{findings}</ul><h2>Decisões</h2><ul>{decisions_html}</ul><p><b>Limite:</b> associação observacional; sem investimento, receita ou conversão não há ROI financeiro nem causalidade.</p></body></html>"""


def analysis_report(result: dict[str, object]) -> str:
    """Render the standalone strategy from the same evidence and queue as HTML/CSV."""
    source, scope, metrics = result["source"], result["scope"], result["metrics"]
    summary_id = _stable_id("summary", str(source["source_hash"]), scope)
    sponsorship = result.get("sponsorship", {})
    overview_id = sponsorship.get("evidence_id", "")

    def text(value: object) -> str:
        return html.escape(str(value)).replace("|", "\\|").replace("\n", " ").replace("\r", " ")

    def number(value: object) -> str:
        return "não definida" if value is None else f"{float(value):.6g}"

    lines = ["# Estratégia Social Media — Challenge 004", "", "## Decisão para segunda-feira", "",
             "Fila única: as recomendações abaixo vêm de `result[recommendations]`, na mesma ordem do HTML e do CSV. "
             "São propostas para decisão humana; não executam gasto, publicação ou interrupção.", ""]
    for rank, item in enumerate(result.get("recommendations") or result.get("pending", []), 1):
        lines.append(f"{rank}. {text(_recommendation_text(item))}")
    lines += ["", RECENCY_NOTE, "",
              "Força limitada (<0,40) exige coleta/teste, sem ampliação de investimento. "
              "As janelas de execução/revisão são propostas futuras, não datas de performance observada.", "",
              "## O que os dados permitem afirmar", "",
              f"Escopo: {text(scope.get('target_start'))} a {text(scope.get('target_end'))}; "
              f"referência: {text(scope.get('reference_date'))}; filtros: `{text(json.dumps(scope.get('filters', {}), ensure_ascii=False, sort_keys=True))}`.", "",
              f"{metrics.get('posts', 0)} posts; {metrics.get('creators', 0)} creators; "
              f"{metrics.get('views', 0)} views; {metrics.get('interactions', 0)} interações. "
              f"Mediana ERv: {number(metrics.get('median_erv'))}{'%' if metrics.get('median_erv') is not None else ''}; "
              f"ERv ponderado: {number(metrics.get('weighted_erv'))}{'%' if metrics.get('weighted_erv') is not None else ''}. "
              f"Proporção de posts com zero interação: {number(metrics.get('zero_interaction_share'))}; "
              f"taxas indefinidas: {metrics.get('undefined_rates', 0)}. Evidência: `{summary_id}`.", "",
              "ERv = 100 × (likes + shares + comments_count) / views; views=0 deixa a taxa indefinida e preserva volume. "
              "A mediana usa taxas por post; a taxa ponderada usa totais apenas onde views>0. "
              "Views não são alcance único; interações não são pessoas únicas.", "",
              "## Plataforma, conteúdo, categoria, creators, audiência e tempo", "",
              "As tabelas descrevem cada recorte; não criam uma segunda fila de prioridades. "
              "Diferenças pequenas de taxa, sem comparação controlada, não justificam redistribuir o mix. "
              "Idade, gênero e localização são rótulos de posts, não percentuais ou personas. "
              "Estas marginais não identificam qual público vence dentro de cada combinação plataforma/formato/categoria: "
              "essa pergunta exige filtros comparáveis e amostra suficiente no motor. "
              "Bilibili e RedNote permanecem no escopo junto a Instagram, TikTok e YouTube.", ""]
    labels = {"platform": "Plataforma", "content_type": "Formato", "content_category": "Categoria",
              "creator_band": "Faixa de seguidores", "audience_age": "Idade", "audience_gender": "Gênero",
              "audience_location": "Localização", "month": "Mês"}
    for dimension, items in result.get("dimensions", {}).items():
        lines += [f"### {labels.get(dimension, dimension)}", "",
                  "| Recorte | Posts | Creators | Views | Interações | Mediana ERv (%) | Evidência |",
                  "|---|---:|---:|---:|---:|---:|---|"]
        for item in items:
            lines.append(f"| {text(item['value'])} | {item.get('posts', 0)} | {item.get('creators', 0)} | "
                         f"{item.get('views', 0)} | {item.get('interactions', 0)} | "
                         f"{number(item.get('median_erv'))} | `{item['evidence_id']}` |")
        lines.append("")
    lines += ["## Patrocínio e o que não funciona", "",
              f"{sponsorship.get('eligible_strata', 0)} estratos elegíveis; {sponsorship.get('uncovered_count', 0)} "
              f"sem amostra/contraparte suficiente; cobertura de {100 * sponsorship.get('coverage', 0):.6g}% dos posts. "
              f"Evidência: `{overview_id}`.", "",
              "Controle: mesma plataforma, formato, categoria, faixa de creator e mês-calendário. "
              "Cada mês exige contrapartes contemporâneas; orgânicos de um mês não são comparados a patrocinados de outro. "
              "Cada braço exige 30 taxas definidas e cinco creators; o efeito é a diferença entre "
              "medianas das medianas de ERv por creator. Cobertura baixa restringe as conclusões aos meses/contextos elegíveis; "
              "não sustenta uma política geral de patrocínio. Patrocínio é associação observacional, não causalidade. "
              "Custo implícito e retorno financeiro não podem ser calculados: faltam investimento, "
              "custo de produção, receita/conversão. Nenhum threshold de seguidores justifica desembolso sozinho.", ""]
    strata = sponsorship.get("strata", [])
    if strata:
        for label, item in (("Menor associação de ERv", min(strata, key=lambda item: item["delta_erv_pp"])),
                            ("Maior associação de ERv", max(strata, key=lambda item: item["delta_erv_pp"]))):
            organic, sponsored = item["organic"], item["sponsored"]
            lines += [f"{label}: {text(' / '.join(str(value) for value in item['context'].values()))}; "
                      f"ΔERv {item['delta_erv_pp']:+.6g} p.p.; força {item['strength']:.6g}; "
                      f"orgânicos/patrocinados: {organic['posts']}/{sponsored['posts']} posts, "
                      f"{organic['views']}/{sponsored['views']} views, "
                      f"{organic['interactions']}/{sponsored['interactions']} interações. "
                      f"Evidência: `{item['evidence_id']}`.", ""]
    lines += ["Esses extremos são achados descritivos, não prioridades adicionais nem ordens para suspender renovação. "
              "Sinal negativo isolado ou força insuficiente exige investigação; interromper investimento requer "
              "sinais concordantes, evidência forte e decisão humana. Ausência de zeros observados, quando indicada "
              "acima, limita a avaliação do fracasso: não prova inexistência de posts sem engajamento.", "",
              "## Estratégia operacional e quick wins", "",
              "Responsável sugerido: Gestor de Social Media. Executar nos próximos 7 dias; revisar 7 dias "
              "após cada teste. A estratégia abaixo aplica a fila inicial, sem reordená-la.", "",
              "| Tema | Ação | Critério de revisão |", "|---|---|---|",
              "| Esforço e quick win | Preparar briefs dos contextos da fila na ordem exibida; anexar a evidência e registrar aceitar/rejeitar/editar. | Rever ERv, views e interações por post no mesmo contexto. |",
              "| Público e creators | Preservar rótulos de audiência e faixa de creator do contexto; coletar se faltarem controles. Não inferir uma persona ou threshold de contratação. | Pelo menos 30 taxas e cinco creators por braço; declarar composição e concentração. |",
              "| Frequência | Testar a mediana observada de posts/creator/semana completa indicada em cada prioridade; estado collect pede coleta antes de propor cadência. | Comparar janelas equivalentes; hipótese observacional, não frequência ótima ou efeito causal. Ausência de linha não equivale a zero. |",
              "| Patrocínio | Obter custos reais antes de avaliar desembolso; força limitada pede coleta/teste. | ERv e volume concordantes, grupo comparável e dados financeiros. |",
              "| Parar/revisar | Revisar repetição de padrões negativos; não parar por média global ou sinal isolado. | Interrupção exige a guarda do motor e decisão humana; sem base, coletar. |", "",
              "## Auditabilidade e limites", "",
              f"Fonte SHA-256: `{source['source_hash']}`; método `{scope.get('method_version', METHOD_VERSION)}`. "
              "Cada evidência está em [evidence.csv](./evidence.csv), com escopo, fórmula e referências.", "",
              "Regeração conjunta: `python3 analysis.py /caminho/social_media_dataset.csv --evidence evidence.csv "
              "--summary summary.html --report analysis.md`.", "",
              "Linhas `recommendation` preservam `rank`, score, impacto, força, atualidade, valores originais "
              "V/I/F, denominadores P95, diferença, data representativa, ação, responsável e janelas. "
              "Impacto = média de min(V/P95_V,1), min(I/P95_I,1), min(F/P95_F,1); "
              "prioridade = 100 × impacto × força × atualidade. Scores são relativos à plataforma/tipo/unidade, "
              "não monetários. P95=0 usa máximo positivo ou zero se inexistente.", "",
              "A coluna JSON `frequency_hypothesis` preserva status, valor/unidade, método, amostra de creator-semanas/creators, "
              "mês (`period_month`), regra (`coverage_rule`), semanas completas disponíveis/observadas, janela, ação, mínimo de semanas para coleta e limitação. "
              "No patrocínio mensal, entram apenas semanas ISO completas inteiramente dentro do mês e do escopo; "
              "semanas que atravessam a fronteira mensal ficam fora. Sem mês fixo, vale a cobertura completa do escopo. "
              "O valor é uma hipótese de teste no mesmo contexto da recomendação, não promessa de desempenho.", "",
              "Em `source_ref`, ordenar as linhas de cada evidência por `reference_chunk` (base 1). "
              "`source_row_id`, `source_line` e `reference_index` são arrays JSON paralelos, em blocos de até 500 entradas "
              "e 32.768 caracteres no campo de IDs, legíveis pelo limite padrão do csv.reader. "
              "O índice identifica o registro dentro da evidência (base 0); concatenar fragmentos de ID com o mesmo "
              "`reference_index`, conservando a linha física inicial (base 1). IDs acima de 4.096 caracteres "
              "são fragmentados sem perder conteúdo. Reconstituir a chave completa com `source_hash + ':' + ID`. "
              "Campos multilinha contam todas as linhas físicas; células de texto neutralizam fórmulas de planilha.", "",
              "A CLI publica todo o histórico, sem alertas post a post. Ausência de período anterior igualmente "
              "longo pode impedir comparações editoriais; não se inventa tendência. O monitoramento recente "
              "pode produzir outra fila porque tem outro escopo. Não há unidade confirmada de content_length, "
              "causalidade, ROI ou resultados futuros inferidos.", ""]
    return "\n".join(lines)


def _atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(payload)
        Path(temporary).replace(path)
    except BaseException:
        Path(temporary).unlink(missing_ok=True)
        raise


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Gera evidências sociais reproduzíveis")
    parser.add_argument("input", type=Path)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--report", type=Path, help="Relatório Markdown da mesma análise")
    args = parser.parse_args(argv)
    try:
        raw = args.input.read_bytes()
    except OSError as exc:
        print(f"input_error: {exc}", file=sys.stderr)
        return 2
    frame, errors = load_csv(raw)
    if errors or frame is None:
        print(json.dumps(errors, ensure_ascii=False), file=sys.stderr)
        return 2
    source_hash = hashlib.sha256(raw).hexdigest()
    result = analyze(frame, {"target_start": min(frame["post_date"]).isoformat(), "target_end": max(frame["post_date"]).isoformat(), "reference_date": max(frame["post_date"]).isoformat(), "filters": {}, "strict_audience": False, "include_post_alerts": False, "method_version": METHOD_VERSION}, source_hash)
    _atomic_write(args.evidence, export_evidence(result, []))
    _atomic_write(args.summary, executive_summary(result, []).encode("utf-8"))
    if args.report:
        _atomic_write(args.report, analysis_report(result).encode("utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
