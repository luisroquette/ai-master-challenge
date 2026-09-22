from typing import Literal

import numpy as np
import pandas as pd

from .config import DEFAULT_WINDOWS, SCORING_CUTOFF
from .contracts import _coerce_table, _coerce_tables


def first_terminal_churn(churn_events: pd.DataFrame) -> pd.Series:
    churn = _coerce_table("churn_events", churn_events)
    terminal = churn.loc[~churn["is_reactivation"].fillna(False)]
    return terminal.groupby("account_id")["churn_date"].min().sort_index()


def mrr_lost_at_churn(subscriptions: pd.DataFrame, terminal_churn: pd.Series) -> pd.Series:
    parsed = _coerce_table("subscriptions", subscriptions)
    lost = {}
    for account_id, churn_date in terminal_churn.items():
        day_before = pd.Timestamp(churn_date) - pd.Timedelta(days=1)
        active = parsed.loc[
            parsed["account_id"].eq(account_id)
            & parsed["start_date"].le(day_before)
            & (parsed["end_date"].isna() | parsed["end_date"].gt(day_before))
        ]
        lost[account_id] = int(active["mrr_amount"].sum())
    return pd.Series(lost, name="mrr_lost", dtype="Int64")


def _single_or_mixed(values: pd.Series) -> object:
    unique = values.dropna().astype(str).unique()
    if len(unique) == 0:
        return pd.NA
    if len(unique) == 1:
        return unique[0]
    return "mixed"


def _next_anniversary(start: pd.Timestamp, cutoff: pd.Timestamp) -> pd.Timestamp:
    years = max(cutoff.year - start.year, 0)
    anniversary = start + pd.DateOffset(years=years)
    while anniversary <= cutoff:
        years += 1
        anniversary = start + pd.DateOffset(years=years)
    return anniversary


def _change(recent: float, recent_days: int, prior: float, prior_days: int) -> tuple[float, bool]:
    if prior <= 0:
        return np.nan, False
    return (recent / recent_days) / (prior / prior_days) - 1, True


def _events_between(
    events: pd.DataFrame, date_column: str, start: pd.Timestamp, end: pd.Timestamp
) -> pd.DataFrame:
    return events.loc[events[date_column].gt(start) & events[date_column].le(end)]


def _add_usage_window(
    row: dict[str, object],
    events: pd.DataFrame,
    subscriptions: pd.DataFrame,
    signup_date: pd.Timestamp,
    cutoff: pd.Timestamp,
    window: int,
) -> None:
    start = cutoff - pd.Timedelta(days=window)
    spans_window = subscriptions["start_date"].le(start) & (
        subscriptions["end_date"].isna() | subscriptions["end_date"].gt(cutoff)
    )
    covered = bool(signup_date <= start and spans_window.any())
    row[f"usage_coverage_{window}d"] = covered
    if not covered:
        for metric in (
            "usage_count",
            "usage_duration",
            "errors",
            "feature_breadth",
            "beta_share",
        ):
            row[f"{metric}_{window}d"] = np.nan
        return

    selected = _events_between(events, "usage_date", start, cutoff)
    row[f"usage_count_{window}d"] = int(selected["usage_count"].sum())
    row[f"usage_duration_{window}d"] = int(selected["usage_duration_secs"].sum())
    row[f"errors_{window}d"] = int(selected["error_count"].sum())
    row[f"feature_breadth_{window}d"] = int(selected["feature_name"].nunique())
    row[f"beta_share_{window}d"] = (
        float(selected["is_beta_feature"].mean()) if len(selected) else np.nan
    )


def _add_support_window(
    row: dict[str, object],
    events: pd.DataFrame,
    signup_date: pd.Timestamp,
    cutoff: pd.Timestamp,
    window: int,
) -> None:
    start = cutoff - pd.Timedelta(days=window)
    covered = bool(signup_date <= start)
    row[f"support_coverage_{window}d"] = covered
    if not covered:
        for metric in (
            "tickets",
            "escalations",
            "mean_first_response",
            "mean_resolution",
            "mean_satisfaction",
            "satisfaction_responses",
            "satisfaction_field_coverage",
        ):
            row[f"{metric}_{window}d"] = np.nan
        return

    selected = _events_between(events, "submitted_at", start, cutoff)
    ticket_count = len(selected)
    first_response_at = selected["submitted_at"] + pd.to_timedelta(
        selected["first_response_time_minutes"].astype("Float64"), unit="m"
    )
    responded = selected.loc[first_response_at.le(cutoff)]
    closed = selected.loc[selected["closed_at"].notna() & selected["closed_at"].le(cutoff)]
    satisfaction_count = int(closed["satisfaction_score"].notna().sum())
    row[f"tickets_{window}d"] = ticket_count
    row[f"escalations_{window}d"] = int(closed["escalation_flag"].fillna(False).sum())
    row[f"mean_first_response_{window}d"] = responded["first_response_time_minutes"].mean()
    row[f"mean_resolution_{window}d"] = closed["resolution_time_hours"].mean()
    row[f"mean_satisfaction_{window}d"] = closed["satisfaction_score"].mean()
    row[f"satisfaction_responses_{window}d"] = satisfaction_count
    row[f"satisfaction_field_coverage_{window}d"] = (
        satisfaction_count / ticket_count if ticket_count else np.nan
    )


def _add_trends(
    row: dict[str, object],
    usage: pd.DataFrame,
    tickets: pd.DataFrame,
    cutoff: pd.Timestamp,
) -> None:
    usage_7 = _events_between(usage, "usage_date", cutoff - pd.Timedelta(days=7), cutoff)[
        "usage_count"
    ].sum()
    usage_prior_23 = _events_between(
        usage,
        "usage_date",
        cutoff - pd.Timedelta(days=30),
        cutoff - pd.Timedelta(days=7),
    )["usage_count"].sum()
    usage_30 = row["usage_count_30d"]
    usage_90 = row["usage_count_90d"]
    if row["usage_coverage_30d"]:
        row["usage_change_7_vs_30"], row["usage_change_7_vs_30_available"] = _change(
            float(usage_7), 7, float(usage_prior_23), 23
        )
    else:
        row["usage_change_7_vs_30"] = np.nan
        row["usage_change_7_vs_30_available"] = False

    if row["usage_coverage_90d"] and pd.notna(usage_30) and pd.notna(usage_90):
        prior_60 = float(usage_90) - float(usage_30)
        row["usage_change_30_vs_90"], row["usage_change_30_vs_90_available"] = _change(
            float(usage_30), 30, prior_60, 60
        )
    else:
        row["usage_change_30_vs_90"] = np.nan
        row["usage_change_30_vs_90_available"] = False

    if row["usage_coverage_30d"] and pd.notna(usage_30) and float(usage_30) > 0:
        row["error_rate_30d"] = float(row["errors_30d"]) / float(usage_30)
        row["error_rate_30d_available"] = True
    else:
        row["error_rate_30d"] = np.nan
        row["error_rate_30d_available"] = False

    tickets_30 = row["tickets_30d"]
    tickets_90 = row["tickets_90d"]
    if row["support_coverage_90d"] and pd.notna(tickets_30) and pd.notna(tickets_90):
        prior_60 = float(tickets_90) - float(tickets_30)
        row["ticket_change_30_vs_90"], row["ticket_change_30_vs_90_available"] = _change(
            float(tickets_30), 30, prior_60, 60
        )
    else:
        row["ticket_change_30_vs_90"] = np.nan
        row["ticket_change_30_vs_90_available"] = False


def build_account_panel(
    tables: dict[str, pd.DataFrame],
    cutoffs: pd.DatetimeIndex,
    chronology: Literal["observed", "strict"],
) -> pd.DataFrame:
    if chronology not in {"observed", "strict"}:
        raise ValueError("chronology must be 'observed' or 'strict'")

    parsed = _coerce_tables(tables)
    accounts = parsed["accounts"].copy()
    subscriptions = parsed["subscriptions"].copy()
    usage = (
        parsed["feature_usage"]
        .merge(
            subscriptions[["subscription_id", "account_id", "start_date", "end_date"]],
            on="subscription_id",
            how="left",
            validate="many_to_one",
        )
        .merge(
            accounts[["account_id", "signup_date"]],
            on="account_id",
            how="left",
            validate="many_to_one",
        )
    )
    tickets = parsed["support_tickets"].merge(
        accounts[["account_id", "signup_date"]],
        on="account_id",
        how="left",
        validate="many_to_one",
    )
    if chronology == "strict":
        usage = usage.loc[
            usage["usage_date"].ge(usage["signup_date"])
            & usage["usage_date"].ge(usage["start_date"])
            & (usage["end_date"].isna() | usage["usage_date"].le(usage["end_date"]))
        ]
        tickets = tickets.loc[tickets["submitted_at"].ge(tickets["signup_date"])]

    terminal = first_terminal_churn(parsed["churn_events"])
    lost_at_churn = mrr_lost_at_churn(subscriptions, terminal)
    usage_by_account = {key: value for key, value in usage.groupby("account_id")}
    tickets_by_account = {key: value for key, value in tickets.groupby("account_id")}
    subscriptions_by_account = {key: value for key, value in subscriptions.groupby("account_id")}
    rows: list[dict[str, object]] = []

    for raw_cutoff in pd.DatetimeIndex(cutoffs):
        cutoff = pd.Timestamp(raw_cutoff)
        eligible = accounts.loc[accounts["signup_date"].le(cutoff)].copy()
        eligible_terminal = eligible["account_id"].map(terminal)
        eligible = eligible.loc[eligible_terminal.isna() | eligible_terminal.gt(cutoff)]

        for account in eligible.sort_values("account_id").itertuples(index=False):
            account_id = account.account_id
            account_subscriptions = subscriptions_by_account.get(
                account_id, subscriptions.iloc[0:0]
            )
            active = account_subscriptions.loc[
                account_subscriptions["start_date"].le(cutoff)
                & (
                    account_subscriptions["end_date"].isna()
                    | account_subscriptions["end_date"].gt(cutoff)
                )
            ]
            annual = active.loc[active["billing_frequency"].eq("annual")]
            renewals = [_next_anniversary(start, cutoff) for start in annual["start_date"].dropna()]
            next_renewal = min(renewals) if renewals else pd.NaT
            terminal_date = terminal.get(account_id, pd.NaT)
            usage_events = usage_by_account.get(account_id, usage.iloc[0:0])
            ticket_events = tickets_by_account.get(account_id, tickets.iloc[0:0])

            row: dict[str, object] = {
                "account_id": account_id,
                "cutoff": cutoff,
                "chronology": chronology,
                "account_name": account.account_name,
                "industry": account.industry,
                "country": account.country,
                "signup_date": account.signup_date,
                "referral_source": account.referral_source,
                "is_trial": account.is_trial,
                "account_churn_flag": account.churn_flag,
                "first_terminal_churn_date": terminal_date,
                "has_active_subscription": bool(len(active)),
                "mrr_active": int(active["mrr_amount"].sum()),
                "seats": int(active["seats"].sum()),
                "plan_tier": _single_or_mixed(active["plan_tier"]),
                "billing_frequency": _single_or_mixed(active["billing_frequency"]),
                "next_annual_renewal": next_renewal,
                "days_to_annual_renewal": (
                    int((next_renewal - cutoff).days) if pd.notna(next_renewal) else np.nan
                ),
                "tenure_days": int((cutoff - account.signup_date).days),
                "auto_renew_off": bool(
                    len(annual) and (~annual["auto_renew_flag"].fillna(False)).any()
                ),
            }

            for window in DEFAULT_WINDOWS:
                _add_usage_window(
                    row,
                    usage_events,
                    account_subscriptions,
                    account.signup_date,
                    cutoff,
                    window,
                )
                _add_support_window(row, ticket_events, account.signup_date, cutoff, window)

            recent_subscriptions = _events_between(
                account_subscriptions,
                "start_date",
                cutoff - pd.Timedelta(days=90),
                cutoff,
            )
            row["downgrade_90d"] = bool(recent_subscriptions["downgrade_flag"].fillna(False).any())
            row["upgrade_90d"] = bool(recent_subscriptions["upgrade_flag"].fillna(False).any())
            _add_trends(row, usage_events, ticket_events, cutoff)

            row["is_scoring_row"] = bool(cutoff == SCORING_CUTOFF)
            if row["is_scoring_row"]:
                row["churn_next_30d"] = pd.NA
                row["mrr_lost_next_30d"] = pd.NA
            else:
                row["churn_next_30d"] = int(
                    pd.notna(terminal_date)
                    and terminal_date > cutoff
                    and terminal_date <= cutoff + pd.Timedelta(days=30)
                )
                row["mrr_lost_next_30d"] = (
                    int(lost_at_churn.get(account_id, 0)) if row["churn_next_30d"] else 0
                )
            rows.append(row)

    panel = pd.DataFrame(rows).sort_values(["cutoff", "account_id"]).reset_index(drop=True)
    if panel.duplicated(["account_id", "cutoff", "chronology"]).any():
        raise ValueError("duplicate account/cutoff/chronology rows")
    return panel
