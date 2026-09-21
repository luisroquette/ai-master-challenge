"""Verified CRM snapshots and cardinality-preserving normalization (no scoring)."""
from __future__ import annotations

import csv
import hashlib
import io
import json
import math
from dataclasses import asdict, dataclass, is_dataclass
from datetime import date
from pathlib import Path
from typing import Mapping

import pandas as pd

ROOT = Path(__file__).resolve().parent
SCHEMA = {
    "accounts.csv": ("account", "year_established"),
    "products.csv": ("product", "series", "sales_price"),
    "sales_teams.csv": ("sales_agent", "manager", "regional_office"),
    "sales_pipeline.csv": ("opportunity_id", "sales_agent", "product", "account",
                           "deal_stage", "engage_date", "close_date", "close_value"),
}
KEYS = {name: fields[0] for name, fields in SCHEMA.items()}
ACTIVE = frozenset(("Engaging", "Prospecting"))
CLOSED = frozenset(("Won", "Lost"))


@dataclass(frozen=True)
class Diagnostic:
    code: str
    scope: str
    file: str | None
    opportunity_id: str | None
    field: str | None
    reason: str
    correction: str


class DataValidationError(ValueError):
    def __init__(self, diagnostics):
        self.diagnostics = tuple(diagnostics)
        super().__init__("; ".join(f"{d.file}: {d.reason}. {d.correction}"
                                   for d in self.diagnostics))


@dataclass(frozen=True)
class Snapshot:
    """Immutable bytes are shared by verification, parsing and cache hashing."""
    files: tuple[tuple[str, bytes], ...]
    manifest_json: str
    dependency_digest: str


@dataclass(frozen=True)
class Dataset:
    """Frames are owned by this result; consumers must not mutate cached frames."""
    opportunities: pd.DataFrame
    accounts: pd.DataFrame
    products: pd.DataFrame
    sales_teams: pd.DataFrame
    diagnostics: tuple[Diagnostic, ...]
    counts: Mapping[str, int]
    data_fingerprint: str


def _block(code, filename, field, reason, correction):
    raise DataValidationError((Diagnostic(code, "global", filename, None, field,
                                          reason, correction),))


def _canonical(value):
    if is_dataclass(value):
        value = asdict(value)
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False)


def read_snapshot(raw_dir, manifest_path, verify_checksums=True):
    raw_dir, manifest_path = Path(raw_dir), Path(manifest_path)
    marker = raw_dir.parent / ".recovery.lock"
    def check_marker():
        if marker.exists():
            _block("recovery_in_progress", str(marker), None,
                   "Recuperação em andamento ou interrompida",
                   "Conclua a recuperação explícita antes de abrir o aplicativo")
    check_marker()
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        entries = manifest["files"]
        if not isinstance(entries, dict) or manifest["schema_version"] != 1 or set(entries) != set(SCHEMA):
            raise ValueError("schema_version/files")
        for name, entry in entries.items():
            if not isinstance(entry, dict) or not isinstance(entry.get("headers"), list):
                raise ValueError(name)
            if not all(isinstance(column, str) for column in entry["headers"]) or not all(
                isinstance(entry.get(key), str) and entry[key]
                for key in ("sha256", "source_url", "license", "download_url")):
                raise ValueError(name)
            if len(entry["sha256"]) != 64 or any(c not in "0123456789abcdef" for c in entry["sha256"]):
                raise ValueError(name)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        _block("manifest_invalid", str(manifest_path), None,
               f"Manifesto ausente ou inválido ({exc})", "Restaure o manifesto versionado")
    buffers = []
    for name in sorted(SCHEMA):
        try:
            content = (raw_dir / name).read_bytes()
        except OSError as exc:
            _block("missing_file", name, None, f"Arquivo indisponível ({exc})",
                   "Restaure os quatro CSVs da versão registrada")
        if verify_checksums and hashlib.sha256(content).hexdigest() != entries[name]["sha256"]:
            _block("checksum_mismatch", name, None, "SHA-256 diverge do manifesto",
                   "Restaure o arquivo original; não atualize o checksum automaticamente")
        buffers.append((name, content))
    check_marker()
    try:
        dependency_digest = hashlib.sha256((ROOT / "requirements.txt").read_bytes()).hexdigest()
    except OSError:
        _block("dependencies_missing", "requirements.txt", None,
               "Lock de dependências ausente", "Restaure requirements.txt")
    return Snapshot(tuple(buffers), _canonical(manifest), dependency_digest)


def fingerprint(snapshot, config):
    identity = {
        "files": {name: hashlib.sha256(content).hexdigest() for name, content in snapshot.files},
        "manifest": json.loads(snapshot.manifest_json),
        "config": asdict(config) if is_dataclass(config) else config,
        "dependencies": snapshot.dependency_digest,
    }
    return hashlib.sha256(_canonical(identity).encode("utf-8")).hexdigest()


def _number(value):
    try:
        parsed = float(value)
        return parsed if math.isfinite(parsed) else None
    except (ValueError, TypeError):
        return None


def _iso_date(value):
    if value is None:
        return None
    try:
        parsed = date.fromisoformat(value)
        return parsed if parsed.isoformat() == value else None
    except (ValueError, TypeError):
        return None


def load_dataset(snapshot):
    manifest = json.loads(snapshot.manifest_json)
    tables = {}
    for name, content in snapshot.files:
        try:
            text = content.decode("utf-8-sig")
            rows = list(csv.reader(io.StringIO(text), strict=True))
            header = rows[0]
            if len(header) != len(set(header)) or any(len(row) != len(header) for row in rows[1:]):
                raise ValueError("colunas duplicadas ou quantidade de células irregular")
            if header != manifest["files"][name]["headers"]:
                _block("manifest_schema_mismatch", name, None,
                       "Cabeçalhos divergem do manifesto", "Restaure o esquema registrado")
            missing = set(SCHEMA[name]) - set(header)
            if missing:
                _block("missing_columns", name, ",".join(sorted(missing)),
                       f"Colunas obrigatórias ausentes: {sorted(missing)}", "Corrija o cabeçalho")
            frame = pd.read_csv(io.StringIO(text), dtype=str, keep_default_na=False)
        except DataValidationError:
            raise
        except (UnicodeError, ValueError, csv.Error, IndexError, pd.errors.ParserError) as exc:
            _block("unreadable_csv", name, None, f"CSV inválido ({exc})", "Restaure o CSV original")
        for column in frame:
            frame[column] = frame[column].map(lambda v: v.strip() or None)
        if "product" in frame:
            frame["product"] = frame["product"].replace({"GTXPro": "GTX Pro"})
        key = KEYS[name]
        if frame[key].isna().any() or frame[key].duplicated().any():
            _block("invalid_primary_key", name, key,
                   "Chave primária vazia ou duplicada após normalização",
                   f"Preencha e torne {key} único")
        tables[name] = frame
    if set(tables) != set(SCHEMA):
        _block("missing_file", None, None, "Snapshot incompleto", "Forneça os quatro CSVs")
    opportunities = tables["sales_pipeline.csv"]
    count = len(opportunities)
    for name, key, indicator in (("products.csv", "product", "product_match"),
                                  ("accounts.csv", "account", "account_match"),
                                  ("sales_teams.csv", "sales_agent", "seller_match")):
        opportunities = opportunities.merge(tables[name], on=key, how="left",
                                              validate="many_to_one", indicator=indicator)
        assert len(opportunities) == count, "A junção alterou a quantidade de oportunidades"
    diagnostics = []
    normalized = []
    for record in opportunities.to_dict("records"):
        oid, stage = record["opportunity_id"], record["deal_stage"]
        supported = True
        def issue(code, field, reason, correction, blocking=True):
            nonlocal supported
            diagnostics.append(Diagnostic(code, "row", "sales_pipeline.csv", oid,
                                          field, reason, correction))
            if blocking:
                supported = False
        if stage not in ACTIVE | CLOSED:
            issue("invalid_stage", "deal_stage", "Estágio desconhecido",
                  "Use Prospecting, Engaging, Won ou Lost")
        for field, indicator in (("product", "product_match"), ("sales_agent", "seller_match")):
            if record[indicator] != "both":
                issue("unknown_key", field, f"{field} ausente ou sem correspondência",
                      f"Corrija {field} usando uma chave do cadastro")
        price = _number(record.get("sales_price"))
        if price is None or price <= 0:
            issue("invalid_price", "sales_price", "Preço de catálogo não é finito e positivo",
                  "Corrija sales_price no catálogo para um número maior que zero")
        if pd.isna(record.get("series")):
            issue("missing_series", "series", "Série do produto ausente", "Preencha series no catálogo")
        for field in ("manager", "regional_office"):
            if pd.isna(record.get(field)):
                issue("missing_team_field", field, f"{field} ausente",
                      f"Preencha {field} no cadastro do vendedor")
        year = _number(record.get("year_established"))
        full = record["account_match"] == "both" and year is not None and year > 0 and year.is_integer()
        if not full:
            issue("account_fallback", "year_established" if record["account_match"] == "both" else "account",
                  "Conta ausente, não cadastrada ou ano de fundação inválido; rota sem conta",
                  "Confira account e um year_established inteiro positivo", blocking=False)
        record["year_established"] = int(year) if full else None
        record["sales_price"] = price
        record["route"] = "full" if full else "fallback"
        for field in ("engage_date", "close_date"):
            raw = record[field]
            parsed = _iso_date(raw)
            required = stage in CLOSED or (stage == "Engaging" and field == "engage_date")
            if (not pd.isna(raw) and parsed is None) or (required and parsed is None):
                issue("invalid_date", field, f"{field} ausente ou fora do formato ISO YYYY-MM-DD",
                      f"Corrija {field} para uma data válida", blocking=stage in CLOSED or field == "engage_date")
            record[field] = parsed
        if stage in CLOSED and record["close_date"] and record["engage_date"] and record["close_date"] < record["engage_date"]:
            issue("date_order", "close_date", "Fechamento anterior ao engajamento",
                  "Corrija a sequência engage_date <= close_date")
        value = _number(record["close_value"])
        financial = stage in CLOSED and value is not None and ((stage == "Won" and value >= 0) or (stage == "Lost" and value == 0))
        if stage in CLOSED and not financial:
            issue("invalid_financial_label", "close_value",
                  "Valor de fechamento inválido; excluído apenas da avaliação financeira",
                  "Won requer valor finito não negativo; Lost requer zero", blocking=False)
        record["close_value"] = value
        record["eligible_history"] = supported and stage in CLOSED
        record["eligible_active"] = supported and stage in ACTIVE
        record["financial_eligible"] = financial and record["eligible_history"]
        record["input_status"] = ("supported_active" if record["eligible_active"] else
                                  "supported_history" if record["eligible_history"] else
                                  "unsupported_active" if stage in ACTIVE else "excluded_history_or_stage")
        normalized.append(record)
    frame = pd.DataFrame(normalized, columns=list(opportunities.columns) + [
        "route", "eligible_history", "eligible_active", "financial_eligible", "input_status"])
    if frame.empty or not frame["eligible_history"].any():
        diagnostics.append(Diagnostic("no_usable_history", "global", "sales_pipeline.csv", None,
                                      "deal_stage", "Nenhum histórico fechado utilizável",
                                      "Forneça oportunidades Won/Lost com chaves e datas válidas"))
        raise DataValidationError(diagnostics)
    counts = {name: len(table) for name, table in tables.items()}
    counts.update({str(status): int(n) for status, n in frame["input_status"].value_counts().items()})
    counts["financial_eligible"] = int(frame["financial_eligible"].sum())
    return Dataset(frame, tables["accounts.csv"], tables["products.csv"], tables["sales_teams.csv"],
                   tuple(diagnostics), counts, fingerprint(snapshot, {}))
