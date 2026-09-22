from __future__ import annotations

import io
import zipfile

import deploy_app


def test_download_csv_extracts_expected_member_atomically(tmp_path, monkeypatch):
    payload = io.BytesIO()
    with zipfile.ZipFile(payload, "w") as archive:
        archive.writestr("nested/customer.csv", "ticket,status\n1,Open\n")
        archive.writestr("nested/ignored.csv", "ignored\n")

    monkeypatch.setattr(
        deploy_app.urllib.request,
        "urlopen",
        lambda *_args, **_kwargs: io.BytesIO(payload.getvalue()),
    )
    destination = tmp_path / "customer.csv"

    deploy_app._download_csv("https://example.test/dataset", destination)

    assert destination.read_text() == "ticket,status\n1,Open\n"
    assert not destination.with_suffix(".csv.tmp").exists()
