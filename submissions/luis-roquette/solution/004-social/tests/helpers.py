from __future__ import annotations

import csv
import io
from datetime import datetime, timedelta

import pandas as pd


def make_post(**overrides: object) -> dict[str, object]:
    row: dict[str, object] = {
        "id": "1",
        "platform": "Instagram",
        "content_id": "content-1",
        "creator_id": "creator-1",
        "content_type": "video",
        "content_category": "tech",
        "post_date": "2025-01-15T12:00:00",
        "views": 100,
        "likes": 5,
        "shares": 2,
        "comments_count": 1,
        "follower_count": 20_000,
        "is_sponsored": "FALSE",
        "audience_age_distribution": "19-25",
        "audience_gender_distribution": "female",
        "audience_location": "BR",
    }
    row.update(overrides)
    return row


def csv_bytes(rows: list[dict[str, object]]) -> bytes:
    if not rows:
        return b""
    fields = list(rows[0])
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue().encode("utf-8")


def frame_from_rows(rows: list[dict[str, object]]) -> pd.DataFrame:
    from analysis import load_csv

    frame, errors = load_csv(csv_bytes(rows))
    if errors:
        raise AssertionError(errors)
    assert frame is not None
    return frame


def make_cohort(
    creators: int = 5,
    posts_per_creator: int = 6,
    erv_values: list[float] | None = None,
    *,
    start: str = "2024-11-01T12:00:00",
    sponsored: bool = False,
    **overrides: object,
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    started = datetime.fromisoformat(start)
    values = erv_values or [4.0] * (creators * posts_per_creator)
    for index in range(creators * posts_per_creator):
        creator = index // posts_per_creator
        erv = values[index % len(values)]
        views = 100
        interactions = int(round(erv))
        rows.append(
            make_post(
                id=f"r-{index}",
                content_id=f"c-{index}",
                creator_id=f"creator-{creator}",
                post_date=(started + timedelta(days=index % 30)).isoformat(),
                views=views,
                likes=interactions,
                shares=0,
                comments_count=0,
                is_sponsored=str(sponsored).upper(),
                **overrides,
            )
        )
    return frame_from_rows(rows)


def frame_with_target(frame: pd.DataFrame, erv: float, **overrides: object) -> pd.DataFrame:
    values: dict[str, object] = {
        "id": "target",
        "content_id": "target-content",
        "creator_id": "target-creator",
        "post_date": "2025-01-15T12:00:00",
        "views": 100,
        "likes": int(erv),
        "shares": 0,
        "comments_count": 0,
    }
    values.update(overrides)
    row = make_post(**values)
    target = frame_from_rows([row])
    return pd.concat([frame, target], ignore_index=True)


def default_scope(**overrides: object) -> dict[str, object]:
    scope: dict[str, object] = {
        "target_start": "2025-01-15",
        "target_end": "2025-01-15",
        "reference_date": "2025-01-15",
        "filters": {},
        "strict_audience": False,
        "method_version": "1.0.0",
    }
    scope.update(overrides)
    return scope


def alert_for_target(result: dict[str, object]) -> dict[str, object]:
    return next(item for item in result["alerts"] if item["source_id"] == "target")  # type: ignore[index]


def sponsorship_rows() -> pd.DataFrame:
    frames = [
        make_cohort(5, 6, [4], sponsored=False, start="2025-01-01T12:00:00"),
        make_cohort(5, 6, [8], sponsored=True, start="2025-01-01T12:00:00"),
        make_cohort(5, 6, [6], sponsored=False, start="2025-01-01T12:00:00", content_type="image"),
    ]
    frame = pd.concat(frames, ignore_index=True)
    frame["id"] = [f"s-{i}" for i in range(len(frame))]
    frame["content_id"] = [f"sc-{i}" for i in range(len(frame))]
    frame["source_row_id"] = [f"hash:s-{i}" for i in range(len(frame))]
    return frame
