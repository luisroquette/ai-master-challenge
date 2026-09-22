"""Frozen temporal evidence and stage-specific presentation contracts.

Input records are injected: this module imports neither data nor the UI. Estimators
are fitted once on training history, calibrated later, and never refitted on test.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, fields, is_dataclass
from datetime import date
import hashlib
import json
import math
from types import MappingProxyType
from typing import Any, Mapping
import warnings


def serialize(value):
    """JSON-safe copy, including immutable mappings and explicit score variants."""
    if isinstance(value, ScoreResult):
        return value.to_dict()
    if is_dataclass(value):
        return {field.name: serialize(getattr(value, field.name)) for field in fields(value)}
    if isinstance(value, Mapping):
        return {str(key): serialize(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [serialize(item) for item in value]
    if isinstance(value, date):
        return value.isoformat()
    return value


def digest(value):
    return hashlib.sha256(json.dumps(serialize(value), sort_keys=True,
        separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode()).hexdigest()


def diagnostic(code, reason, correction, *, field=None, opportunity_id=None, scope="route"):
    return MappingProxyType(dict(code=code, scope=scope, file=None,
        opportunity_id=opportunity_id, field=field, reason=reason, correction=correction))


class ScoringValidationError(ValueError):
    def __init__(self, code, reason):
        self.diagnostics = (diagnostic(code, reason,
            "Forneça histórico fechado com três períodos cronológicos utilizáveis", scope="global"),)
        super().__init__(f"{code}: {reason}")


@dataclass(frozen=True)
class ScoringConfig:
    version: str = "temporal-v1"
    feature_version: str = "product-series-founded-v1"
    playbook_version: str = "v1"
    dependency_digest: str = "43a420f22b5e31ceadf0946434689dca39359c7a69d358e4636ee6c0fb344843"
    fallback_features: tuple[str, ...] = ("product", "series")
    full_features: tuple[str, ...] = ("product", "series", "year_established")
    train_fraction: float = .60
    calibration_fraction: float = .80
    min_train: int = 200
    min_calibration: int = 100
    min_test: int = 100
    min_class: int = 20
    band_edges: tuple[float, float] = (.40, .70)
    min_band: int = 30
    band_tolerance: float = .10
    min_populated_bands: int = 2
    comparison_epsilon: float = 1e-12
    log_clip: float = 1e-15
    top_fractions: tuple[float, float] = (.10, .20)
    seed: int = 42
    logistic_c: float = 1.
    logistic_max_iter: int = 1000
    boosting_estimators: int = 100
    boosting_learning_rate: float = .05
    boosting_depth: int = 2
    boosting_min_leaf: int = 20
    prior_strength: float = 20.
    min_group: int = 20
    relative_delta: float = .05
    margin_quantiles: tuple[float, float] = (1/3, 2/3)
    explanation_tolerance: float = 1e-8

    def __post_init__(self):
        # Only the declared provenance allowlist may become prediction inputs.
        if self.fallback_features != ("product", "series") or self.full_features != (
                "product", "series", "year_established"):
            raise ValueError("feature_provenance: prediction allowlists cannot include other fields")
        if not 0 < self.train_fraction < self.calibration_fraction < 1:
            raise ValueError("Invalid chronological fractions")
        if not 0 < self.band_edges[0] < self.band_edges[1] < 1:
            raise ValueError("Invalid probability bands")
        if self.prior_strength <= 0 or self.min_group < 1:
            raise ValueError("Positive smoothing support required")

    @property
    def fingerprint(self):
        return digest(self)


DEFAULT_CONFIG = ScoringConfig()
FEATURE_PROVENANCE = MappingProxyType({
    "product": ("product",), "series": ("series",),
    "year_established": ("year_established",),
})
LIMITATIONS = (
    "Estimativa de Won versus Lost entre oportunidades engajadas que se resolveram; sem horizonte de fechamento.",
    "Aplicação a oportunidades abertas pressupõe transportabilidade; há censura e metadados estáticos.",
    "Seleção fixa entre candidatos no teste final gera otimismo pós-seleção; requer evidência prospectiva nova.",
    "Reutilizar o teste após mudar a política é exploratório, não validação em novo holdout.",
)


@dataclass(frozen=True)
class Factor:
    field: str
    observed_value: str | int | float | None
    contribution: float
    direction: str
    reference: str
    actionable: bool


@dataclass(frozen=True)
class ScoreResult:
    opportunity_id: str
    stage: str
    sales_agent: str | None = None
    manager: str | None = None
    regional_office: str | None = None
    product: str | None = None
    account: str | None = None
    state: str = "insufficient_data"
    route: str | None = None
    origin: str | None = None
    band: str | None = None
    band_kind: str | None = None
    potential_revenue: float | None = None
    probability: float | None = None
    expected_revenue: float | None = None
    relative_index: float | None = None
    evaluation_id: str | None = None
    fingerprint: str = ""
    observed_n: int = 0
    prior_strength: float = 0.
    effective_support: float = 0.
    evidence_strength: str = "indisponivel"
    backoff_path: tuple[str, ...] = ()
    diagnostics: tuple = ()
    explanation_scale: str | None = None
    base_value: float | None = None
    factors: tuple[Factor, ...] = ()
    next_action: str = "Sem ação recomendada com os dados atuais"

    def __post_init__(self):
        if self.stage not in ("Engaging", "Prospecting") or not self.opportunity_id:
            raise ValueError("Invalid active identity/stage")
        if self.observed_n < 0 or self.prior_strength < 0 or self.effective_support < 0:
            raise ValueError("Negative support")
        if self.potential_revenue is not None and not (
                math.isfinite(self.potential_revenue) and self.potential_revenue > 0):
            raise ValueError("Invalid potential revenue")
        if self.state == "calibrated":
            if self.stage != "Engaging" or self.route not in ("full", "fallback"):
                raise ValueError("Only Engaging model routes support probabilities")
            validate_probabilities((self.probability,))
            if self.potential_revenue is None or self.expected_revenue is None or not math.isclose(
                    self.expected_revenue, self.probability * self.potential_revenue,
                    rel_tol=1e-12, abs_tol=1e-12):
                raise ValueError("Expected revenue must equal probability times catalog price")
            if self.band_kind != "probability" or self.band not in ("baixa", "media", "alta") or not self.evaluation_id:
                raise ValueError("Calibrated score needs probability-band evaluation provenance")
            if self.relative_index is not None:
                raise ValueError("Calibrated score cannot own a relative index")
        elif self.state in ("relative", "insufficient_data"):
            if self.probability is not None or self.expected_revenue is not None:
                raise ValueError("Unvalidated states cannot own probabilistic values")
            if self.state == "relative":
                if self.relative_index is None or not math.isfinite(self.relative_index):
                    raise ValueError("Relative state needs a finite index")
                if self.band_kind != "relative" or self.band not in ("baixa", "media", "alta"):
                    raise ValueError("Relative state needs its own band")
            elif any(item is not None for item in (self.band, self.band_kind, self.relative_index, self.base_value)) or self.factors:
                raise ValueError("Insufficient state cannot invent a score or factors")
        else:
            raise ValueError("Unknown score state")

    def to_dict(self):
        result = {field.name: serialize(getattr(self, field.name)) for field in fields(self)}
        if self.state != "calibrated":
            result.pop("probability")
            result.pop("expected_revenue")
        if self.state != "relative":
            result.pop("relative_index")
        return result


@dataclass(frozen=True)
class PeriodEvidence:
    period: str
    ids: tuple[str, ...]
    wins: int
    losses: int
    global_count: int
    excluded: tuple[tuple[str, tuple[str, ...]], ...]

    @property
    def count(self):
        return len(self.ids)


@dataclass(frozen=True)
class BandEvidence:
    band: str
    count: int
    mean_probability: float | None
    observed_rate: float | None
    supported: bool
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class TopKMetric:
    fraction: float
    k: int
    precision: float
    realized_value_share: float | None
    financial_unavailable_reason: str | None


@dataclass(frozen=True)
class SegmentEvidence:
    field: str
    value: str
    count: int
    observed_rate: float
    mean_probability: float
    brier: float
    log_loss: float


@dataclass(frozen=True)
class CandidateEvaluation:
    evaluation_id: str
    candidate: str
    route: str
    status: str
    config_fingerprint: str
    split_fingerprint: str
    feature_fingerprint: str
    feature_names: tuple[str, ...]
    periods: tuple[PeriodEvidence, ...]
    train_boundary: str
    calibration_boundary: str
    baseline_rate: float | None
    brier: float | None
    log_loss: float | None
    baseline_brier: float | None
    baseline_log_loss: float | None
    bands: tuple[BandEvidence, ...]
    top_k: tuple[TopKMetric, ...]
    segments: tuple[SegmentEvidence, ...]
    reasons: tuple[str, ...]
    unavailable_reasons: tuple[str, ...]
    natural_missing_account_count: int
    financial_valid_count: int
    limitations: tuple[str, ...] = LIMITATIONS

    @property
    def test_ids(self):
        return self.periods[2].ids


@dataclass(frozen=True)
class RouteSelection:
    route: str
    candidate: str | None
    evaluation_id: str | None
    reason: str


@dataclass(frozen=True)
class ScoringBundle:
    fingerprint: str
    config_version: str
    candidate_evaluations: tuple[CandidateEvaluation, ...]
    selected_routes: tuple[RouteSelection, ...]
    scores: tuple[ScoreResult, ...]
    input_diagnostics: tuple
    source_identity: Mapping

    def __post_init__(self):
        expected = {(candidate, route) for candidate in ("logistic", "boosting") for route in ("full", "fallback")}
        if len(self.candidate_evaluations) != 4 or {
                (item.candidate, item.route) for item in self.candidate_evaluations} != expected:
            raise ValueError("Bundle publication requires all four route outcomes")
        object.__setattr__(self, "source_identity", MappingProxyType(dict(self.source_identity)))

    def to_dict(self):
        return serialize(self)


@dataclass(frozen=True)
class TemporalSplit:
    train: tuple[Mapping, ...]
    calibration: tuple[Mapping, ...]
    test: tuple[Mapping, ...]
    train_boundary: date
    calibration_boundary: date

    @property
    def fingerprint(self):
        return digest({"boundaries": (self.train_boundary, self.calibration_boundary),
            "ids": tuple(tuple(row["opportunity_id"] for row in period)
                for period in (self.train, self.calibration, self.test))})


@dataclass(frozen=True)
class FeatureSupport:
    route: str
    products: tuple[str, ...]
    series: tuple[str, ...]
    year_min: int | None
    year_max: int | None


@dataclass(frozen=True)
class CandidateFit:
    candidate: str
    route: str
    support: FeatureSupport
    periods: tuple[tuple[Mapping, ...], ...]
    evidence: tuple[PeriodEvidence, ...]
    pipeline: Any
    calibrated: Any
    feature_names: tuple[str, ...]
    fit_reasons: tuple[str, ...]
    failed: bool
    config_fingerprint: str


def _records(records):
    return records.to_dict("records") if hasattr(records, "to_dict") else records


def split_closed_history(records, config=DEFAULT_CONFIG):
    history = [dict(row) for row in _records(records)
        if row.get("eligible_history") and row.get("deal_stage") in ("Won", "Lost")]
    for row in history:
        value = row.get("close_date")
        if not isinstance(value, date):
            raise ScoringValidationError("invalid_history_date", "Histórico elegível contém close_date inválido")
    history.sort(key=lambda row: (row["close_date"], row["opportunity_id"]))
    if len({row["opportunity_id"] for row in history}) != len(history):
        raise ScoringValidationError("duplicate_history_id", "Histórico contém oportunidade duplicada")
    counts = {}
    for row in history:
        counts[row["close_date"]] = counts.get(row["close_date"], 0) + 1
    cumulative, first, second = 0, None, None
    for day, count in counts.items():
        cumulative += count
        if first is None and cumulative >= math.ceil(config.train_fraction * len(history)):
            first = day
        elif first is not None and second is None and cumulative >= math.ceil(config.calibration_fraction * len(history)):
            second = day
    if first is None or second is None:
        raise ScoringValidationError("insufficient_temporal_periods", "Não há três períodos cronológicos")
    periods = tuple(tuple(MappingProxyType(row) for row in history if predicate(row["close_date"]))
        for predicate in (lambda day: day <= first, lambda day: first < day <= second, lambda day: day > second))
    if not all(periods):
        raise ScoringValidationError("insufficient_temporal_periods", "Uma divisão cronológica está vazia")
    return TemporalSplit(*periods, first, second)


def feature_record(row, route, config=DEFAULT_CONFIG):
    if route not in ("full", "fallback"):
        raise ValueError("Unknown account route")
    names = config.full_features if route == "full" else config.fallback_features
    return {name: row.get(name) for name in names}


def support_reasons(row, route, support=None):
    reasons = []
    if not row.get("product") or not row.get("series"):
        reasons.append("missing_product_or_series")
    price = row.get("sales_price")
    if not isinstance(price, (int, float)) or not math.isfinite(price) or price <= 0:
        reasons.append("invalid_price")
    if row.get("product_match") != "both":
        reasons.append("unmatched_product")
    if row.get("seller_match") != "both":
        reasons.append("unmatched_seller")
    if route == "full":
        year = row.get("year_established")
        if row.get("account_match") != "both" or not isinstance(year, (int, float)) or not math.isfinite(year) or year <= 0 or int(year) != year:
            reasons.append("unsupported_account_year")
        elif support and (support.year_min is None or not support.year_min <= year <= support.year_max):
            reasons.append("year_outside_training_support")
    if support:
        if row.get("product") not in support.products:
            reasons.append("unseen_product")
        if row.get("series") not in support.series:
            reasons.append("unseen_series")
    return tuple(reasons)


def _route_periods(split, route):
    train = [row for row in split.train if not support_reasons(row, route)]
    years = [row["year_established"] for row in train] if route == "full" else []
    support = FeatureSupport(route, tuple(sorted({row["product"] for row in train})),
        tuple(sorted({row["series"] for row in train})), min(years) if years else None,
        max(years) if years else None)
    periods, evidence = [], []
    for name, rows in zip(("train", "calibration", "test"), (split.train, split.calibration, split.test)):
        eligible, excluded = [], []
        for row in rows:
            reasons = support_reasons(row, route, support)
            if reasons:
                excluded.append((row["opportunity_id"], reasons))
            else:
                eligible.append(row)
        periods.append(tuple(eligible))
        wins = sum(row["deal_stage"] == "Won" for row in eligible)
        evidence.append(PeriodEvidence(name, tuple(row["opportunity_id"] for row in eligible),
            wins, len(eligible)-wins, len(rows), tuple(excluded)))
    return support, tuple(periods), tuple(evidence)


def feature_frame(records, route, config=DEFAULT_CONFIG):
    import pandas as pd
    columns = config.full_features if route == "full" else config.fallback_features
    return pd.DataFrame([feature_record(row, route, config) for row in records], columns=columns,
        index=[row["opportunity_id"] for row in records])


def fit_candidate(split, candidate, route, config=DEFAULT_CONFIG):
    from sklearn.calibration import CalibratedClassifierCV
    from sklearn.compose import ColumnTransformer
    from sklearn.ensemble import GradientBoostingClassifier
    from sklearn.exceptions import ConvergenceWarning
    from sklearn.frozen import FrozenEstimator
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import OneHotEncoder, StandardScaler

    if candidate not in ("logistic", "boosting") or route not in ("full", "fallback"):
        raise ValueError("Unknown candidate or route")
    support, periods, evidence = _route_periods(split, route)
    pipeline = calibrated = None
    reasons, names, failed = [], (), False
    train, calibration, _ = periods
    if not train or len({row["deal_stage"] for row in train}) != 2:
        reasons.append("training_requires_both_classes")
    else:
        transforms = [("categorical", OneHotEncoder(drop=None, sparse_output=False,
            handle_unknown="error"), ["product", "series"])]
        if route == "full":
            transforms.append(("numeric", StandardScaler(), ["year_established"]))
        estimator = (LogisticRegression(l1_ratio=0, C=config.logistic_c, solver="lbfgs",
            max_iter=config.logistic_max_iter, random_state=config.seed) if candidate == "logistic"
            else GradientBoostingClassifier(loss="log_loss", n_estimators=config.boosting_estimators,
                learning_rate=config.boosting_learning_rate, max_depth=config.boosting_depth,
                min_samples_leaf=config.boosting_min_leaf, subsample=1., random_state=config.seed,
                n_iter_no_change=None))
        training_complete = False
        try:
            pipeline = Pipeline((("preprocessor", ColumnTransformer(transforms)), ("estimator", estimator)))
            with warnings.catch_warnings():
                warnings.simplefilter("error", ConvergenceWarning)
                pipeline.fit(feature_frame(train, route, config), [int(row["deal_stage"] == "Won") for row in train])
            training_complete = True
            names = tuple(pipeline.named_steps["preprocessor"].get_feature_names_out())
            if not calibration or len({row["deal_stage"] for row in calibration}) != 2:
                reasons.append("calibration_requires_both_classes")
            else:
                calibrated = CalibratedClassifierCV(FrozenEstimator(pipeline), method="sigmoid", ensemble=False)
                with warnings.catch_warnings():
                    warnings.simplefilter("error", ConvergenceWarning)
                    calibrated.fit(feature_frame(calibration, route, config),
                        [int(row["deal_stage"] == "Won") for row in calibration])
        except (ValueError, RuntimeError, FloatingPointError, ConvergenceWarning) as exc:
            # A failed calibrator may leave a fitted raw model for later relative use.
            failed = True
            calibrated = None
            if not training_complete:
                pipeline = None
            reasons.append(f"fit_failed:{type(exc).__name__}:{exc}")
    return CandidateFit(candidate, route, support, periods, evidence, pipeline,
        calibrated, names, tuple(reasons), failed, config.fingerprint)


def validate_probabilities(probabilities):
    if any(not isinstance(value, (int, float)) or not math.isfinite(value) or not 0 <= value <= 1
           for value in probabilities):
        raise ValueError("invalid_probability: values must be finite in [0,1]")


def probability_band(probability, config=DEFAULT_CONFIG):
    validate_probabilities((probability,))
    return "baixa" if probability < config.band_edges[0] else "media" if probability < config.band_edges[1] else "alta"


def probability_losses(labels, probabilities, config=DEFAULT_CONFIG):
    if not labels or len(labels) != len(probabilities) or any(label not in (0, 1) for label in labels):
        raise ValueError("Invalid probability evaluation cohort")
    validate_probabilities(probabilities)
    brier = sum((probability-label)**2 for label, probability in zip(labels, probabilities)) / len(labels)
    loss = -sum(label*math.log(max(config.log_clip, min(1-config.log_clip, probability)))
        + (1-label)*math.log(1-max(config.log_clip, min(1-config.log_clip, probability)))
        for label, probability in zip(labels, probabilities)) / len(labels)
    return brier, loss


def band_evidence(labels, probabilities, config=DEFAULT_CONFIG):
    if len(labels) != len(probabilities):
        raise ValueError("Band cohort mismatch")
    validate_probabilities(probabilities)
    output = []
    for band in ("baixa", "media", "alta"):
        pairs = [(label, probability) for label, probability in zip(labels, probabilities)
            if probability_band(probability, config) == band]
        if not pairs:
            output.append(BandEvidence(band, 0, None, None, False, ("empty_band",)))
            continue
        predicted = sum(pair[1] for pair in pairs) / len(pairs)
        observed = sum(pair[0] for pair in pairs) / len(pairs)
        reasons = []
        if len(pairs) < config.min_band:
            reasons.append("insufficient_band_support")
        # isclose absorbs representation of the fixed boundary, not a policy tolerance.
        difference = abs(predicted-observed)
        if difference > config.band_tolerance and not math.isclose(difference, config.band_tolerance, rel_tol=0, abs_tol=1e-15):
            reasons.append("incoherent_band")
        output.append(BandEvidence(band, len(pairs), predicted, observed, not reasons, tuple(reasons)))
    return tuple(output)


def publication_reasons(periods, brier, loss, baseline_brier, baseline_loss, bands, config=DEFAULT_CONFIG):
    reasons = []
    for period, minimum in zip(periods, (config.min_train, config.min_calibration, config.min_test)):
        if period.count < minimum:
            reasons.append(f"{period.period}_support_below_{minimum}")
        if min(period.wins, period.losses) < config.min_class:
            reasons.append(f"{period.period}_class_support_below_{config.min_class}")
    if not baseline_brier-brier > config.comparison_epsilon:
        reasons.append("brier_not_strictly_better")
    if not baseline_loss-loss > config.comparison_epsilon:
        reasons.append("log_loss_not_strictly_better")
    populated = [band for band in bands if band.count]
    if any(not band.supported for band in populated):
        reasons.append("populated_band_failed")
    if sum(band.supported for band in populated) < config.min_populated_bands:
        reasons.append("fewer_than_two_supported_bands")
    if any(left.observed_rate > right.observed_rate for left, right in zip(populated, populated[1:])):
        reasons.append("nonmonotonic_observed_bands")
    return tuple(reasons)


def ranking_metrics(rows, probabilities, config=DEFAULT_CONFIG):
    if not rows or len(rows) != len(probabilities):
        raise ValueError("Invalid ranking cohort")
    validate_probabilities(probabilities)
    band_rank = {"baixa": 0, "media": 1, "alta": 2}
    ranked = sorted(zip(rows, probabilities), key=lambda pair: (
        -band_rank[probability_band(pair[1], config)], -pair[1]*pair[0]["sales_price"], pair[0]["opportunity_id"]))
    valid_financial = all(row.get("financial_eligible") and isinstance(row.get("close_value"), (int, float))
        and math.isfinite(row["close_value"]) and row["close_value"] >= 0
        and (row["deal_stage"] == "Won" or row["close_value"] == 0) for row in rows)
    total = sum(row["close_value"] for row in rows if row["deal_stage"] == "Won") if valid_financial else None
    unavailable = "incomplete_financial_labels" if not valid_financial else "no_positive_realized_total" if total <= 0 else None
    result = []
    for fraction in config.top_fractions:
        k = math.ceil(fraction*len(rows))
        top = [pair[0] for pair in ranked[:k]]
        precision = sum(row["deal_stage"] == "Won" for row in top) / k
        share = None if unavailable else sum(row["close_value"] for row in top if row["deal_stage"] == "Won") / total
        result.append(TopKMetric(fraction, k, precision, share, unavailable))
    return tuple(result)


def _segments(rows, probabilities, config):
    result = []
    for field in ("sales_agent", "manager", "regional_office"):
        groups = {}
        for row, probability in zip(rows, probabilities):
            groups.setdefault(str(row.get(field) or "Não informado"), []).append((int(row["deal_stage"] == "Won"), probability))
        for value, pairs in sorted(groups.items()):
            labels, predicted = zip(*pairs)
            brier, loss = probability_losses(labels, predicted, config)
            result.append(SegmentEvidence(field, value, len(pairs), sum(labels)/len(pairs),
                sum(predicted)/len(pairs), brier, loss))
    return tuple(result)


def evaluate_candidate(fitted, split, config=DEFAULT_CONFIG):
    if fitted.config_fingerprint != config.fingerprint:
        raise ValueError("Policy changed between fit and evaluation")
    train, _, test = fitted.periods
    baseline = sum(row["deal_stage"] == "Won" for row in train)/len(train) if train else None
    reasons = list(fitted.fit_reasons)
    unavailable = []
    brier = loss = base_brier = base_loss = None
    bands, top, segments = (), (), ()
    failed = fitted.failed
    if fitted.calibrated is None or not test:
        unavailable.append("probability_metrics_unavailable:unfitted_calibrator_or_empty_test")
        reasons.extend(publication_reasons(fitted.evidence, 0, 0, 1, 1, (), config))
    else:
        try:
            probabilities = tuple(float(value) for value in fitted.calibrated.predict_proba(feature_frame(test, fitted.route, config))[:, 1])
            labels = tuple(int(row["deal_stage"] == "Won") for row in test)
            brier, loss = probability_losses(labels, probabilities, config)
            base_brier, base_loss = probability_losses(labels, (baseline,)*len(test), config)
            bands = band_evidence(labels, probabilities, config)
            reasons.extend(publication_reasons(fitted.evidence, brier, loss, base_brier, base_loss, bands, config))
            top = ranking_metrics(test, probabilities, config)
            segments = _segments(test, probabilities, config)
            unavailable.extend(sorted({item.financial_unavailable_reason for item in top if item.financial_unavailable_reason}))
        except (ValueError, RuntimeError, FloatingPointError) as exc:
            failed = True
            reasons.append(f"evaluation_failed:{type(exc).__name__}:{exc}")
            unavailable.append("probability_metrics_unavailable:invalid_prediction")
            brier = loss = base_brier = base_loss = None
            bands, top, segments = (), (), ()
    feature_identity = digest({"names": fitted.feature_names, "support": fitted.support,
        "provenance": FEATURE_PROVENANCE, "policy": config.feature_version})
    consumed_history = tuple(tuple({"features": feature_record(row, fitted.route, config),
        **{key: row.get(key) for key in ("opportunity_id", "deal_stage", "close_date", "close_value",
            "financial_eligible", "sales_price", "sales_agent", "manager", "regional_office")}}
        for row in period) for period in fitted.periods)
    evaluation_id = digest((config.fingerprint, split.fingerprint, feature_identity,
        fitted.candidate, fitted.route, consumed_history))
    natural_missing = sum(row.get("account_match") != "both" for period in (split.train, split.calibration, split.test) for row in period)
    limitations = LIMITATIONS + (("Nenhuma conta naturalmente ausente no histórico fechado: fallback validado por remoção intencional de atributos.",) if not natural_missing else ())
    return CandidateEvaluation(evaluation_id, fitted.candidate, fitted.route,
        "failed" if failed else "rejected" if reasons else "passed", config.fingerprint,
        split.fingerprint, feature_identity, fitted.feature_names, fitted.evidence,
        split.train_boundary.isoformat(), split.calibration_boundary.isoformat(), baseline,
        brier, loss, base_brier, base_loss, bands, top, segments,
        tuple(dict.fromkeys(reasons)), tuple(unavailable), natural_missing,
        sum(bool(row.get("financial_eligible")) for row in test), limitations)


def select_route(evaluations, route, config=DEFAULT_CONFIG):
    candidates = {item.candidate: item for item in evaluations if item.route == route}
    if set(candidates) != {"logistic", "boosting"}:
        raise ValueError("Selection requires both route candidates")
    passed = {name: item for name, item in candidates.items() if item.status == "passed"}
    if not passed:
        return RouteSelection(route, None, None, "no_validated_candidate")
    if len(passed) == 1:
        winner = next(iter(passed.values()))
        return RouteSelection(route, winner.candidate, winner.evaluation_id, "only_validated_candidate")
    logistic, boosting = passed["logistic"], passed["boosting"]
    winner, reason = logistic, "logistic_default_inconsistent_gains"
    if logistic.test_ids != boosting.test_ids or logistic.split_fingerprint != boosting.split_fingerprint:
        reason = "incomparable_test_cohorts"
    elif any(item.financial_unavailable_reason for candidate in (logistic, boosting) for item in candidate.top_k):
        reason = "financial_comparison_unavailable"
    elif (tuple(item.fraction for item in logistic.top_k) != config.top_fractions or
          tuple(item.fraction for item in boosting.top_k) != config.top_fractions or
          any(a.k != b.k or a.k != math.ceil(a.fraction*len(logistic.test_ids))
              for a, b in zip(logistic.top_k, boosting.top_k))):
        reason = "incomparable_top_k"
    elif all(value is not None and math.isfinite(value) for candidate in (logistic, boosting)
             for value in (candidate.brier, candidate.log_loss)) and all(
             b.precision-a.precision > config.comparison_epsilon and
             a.realized_value_share is not None and b.realized_value_share is not None and
             b.realized_value_share-a.realized_value_share > config.comparison_epsilon
             for a, b in zip(logistic.top_k, boosting.top_k)) and (
             boosting.brier-logistic.brier <= config.comparison_epsilon and
             boosting.log_loss-logistic.log_loss <= config.comparison_epsilon):
        winner, reason = boosting, "consistent_boosting_gains"
    return RouteSelection(route, winner.candidate, winner.evaluation_id, reason)


def evaluate_history(records, config=DEFAULT_CONFIG):
    """One fixed pass yields all four outcomes, including controlled rejections."""
    split = split_closed_history(records, config)
    fitted = tuple(fit_candidate(split, candidate, route, config)
        for candidate in ("logistic", "boosting") for route in ("full", "fallback"))
    evaluations = tuple(evaluate_candidate(model, split, config) for model in fitted)
    selections = tuple(select_route(evaluations, route, config) for route in ("full", "fallback"))
    return split, fitted, evaluations, selections


def build_scoring_bundle(dataset, config=DEFAULT_CONFIG):
    """Contract reserved for Phase 2 composition; evaluation itself is callable now.

    Deliberately fails rather than publishing an empty/fabricated active portfolio.
    Phase 2 composes evaluate_history with score_active and source identity here.
    """
    raise NotImplementedError("Active score composition belongs to validated SDD step 03a")
