"""The layered configuration, read and checked by the engine's own reader.

The reader runs in a throwaway container of the engine image (no systemd, no
engine): the layers are put in a temporary directory and mounted read only.
"""

import json
import subprocess
from pathlib import Path

from conftest import ROOT, engine_image


def run_reader(
    tmp_path: Path, base: str | None = None, profile: str | None = None, extra=()
):
    """Run /usr/libexec/anima/config on the given layers; returns (code, messages, files)."""
    config = tmp_path / "config"
    out = tmp_path / "out"
    config.mkdir(parents=True, exist_ok=True)
    out.mkdir(parents=True, exist_ok=True)
    if base is not None:
        (config / "mail").mkdir(exist_ok=True)
        (config / "mail" / "mail.toml").write_text(base)
    if profile is not None:
        (config / "profiles" / "p" / "mail").mkdir(parents=True, exist_ok=True)
        (config / "profiles" / "p" / "mail" / "mail.toml").write_text(profile)
    result = subprocess.run(
        [
            "podman",
            "run",
            "--rm",
            "--network=none",
            f"--volume={config}:/cfg:ro",
            f"--volume={out}:/out",
            "--env=ANIMA_CONFIG_DIR=/cfg",
            "--env=ANIMA_CONFIG_RUN_DIR=/out",
            "--env=ANIMA_PROFILE=p",
            *extra,
            "--entrypoint=/usr/libexec/anima/config",
            engine_image(),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    files = sorted(p.name for p in out.iterdir())
    return result.returncode, result.stdout + result.stderr, files, out


def test_R95_absent_setting_takes_production_default(tmp_path):
    """A setting the configuration does not write is the engine's default."""
    code, out, files, run = run_reader(
        tmp_path, base='[smtp]\nhost = "smtp.example.org"\n'
    )
    assert code == 0, out
    mail = json.loads((run / "effective.json").read_text())["mail"]
    assert mail["smtp"]["host"] == "smtp.example.org"  # written
    assert mail["smtp"]["port"] == 587  # absent: the default
    assert mail["driver"] == "smtp" and mail["smtp"]["starttls"] is True
    assert "mail.smtp.active" in files
    # Nothing written at all: every setting takes its default.
    code, out, _, run = run_reader(tmp_path / "empty")
    assert code == 0, out
    assert (
        json.loads((run / "effective.json").read_text())["mail"]["smtp"]["port"] == 587
    )
    # The profile overrides the base, and the base the defaults, in that order.
    code, out, files, run = run_reader(
        tmp_path / "layers",
        base='driver = "smtp"\n[smtp]\nport = 2525\n',
        profile='driver = "catcher"\n',
    )
    assert code == 0, out
    mail = json.loads((run / "effective.json").read_text())["mail"]
    assert (mail["driver"], mail["smtp"]["port"]) == ("catcher", 2525)
    assert "mail.catcher.active" in files and "mail.smtp.active" not in files


def test_R48_configuration_validated_before_ready(tmp_path):
    """An unknown, a forbidden or a secret setting is refused, naming it, and
    nothing is written."""
    cases = {
        "mail.smtp.hostt": '[smtp]\nhostt = "x"\n',
        "mail.catcher.address": '[catcher]\naddress = "0.0.0.0:25"\n',
        "mail.smtp.password": '[smtp]\npassword = "hunter2"\n',
        "mail.smtp.port": '[smtp]\nport = "587"\n',
        "mail.driver": 'driver = "carrier-pigeon"\n',
    }
    for number, (setting, base) in enumerate(cases.items()):
        code, out, files, _ = run_reader(tmp_path / str(number), base=base)
        assert code == 1, (setting, out)
        assert setting in out, (setting, out)
        assert files == [], (setting, files)
    # The secret is refused before any value is read, and the message says what to do.
    _, out, _, _ = run_reader(tmp_path / "secret", base='[smtp]\ntoken = "abc"\n')
    assert "password_file" not in out and "token_file" in out, out
    assert "abc" not in out


def test_R103_adopter_secrets_arrive_as_files(tmp_path):
    """One end-to-end example: a setting names the file that holds a secret; the
    effective configuration holds the path and never the value."""
    secret = tmp_path / "smtp-password"
    value = "not-a-real-secret-value"
    secret.write_text(value)
    base = '[smtp]\npassword_file = "/run/secrets/smtp-password"\n'
    # The file is missing: refused, naming the setting.
    code, out, files, _ = run_reader(tmp_path / "missing", base=base)
    assert code == 1 and "mail.smtp.password_file" in out and files == [], out
    # The host mounts it: accepted.
    code, out, files, run = run_reader(
        tmp_path / "present",
        base=base,
        extra=[f"--volume={secret}:/run/secrets/smtp-password:ro"],
    )
    assert code == 0, out
    effective = (run / "effective.json").read_text()
    assert "/run/secrets/smtp-password" in effective and value not in effective
    # No file of the configuration holds a value of that kind.
    for path in (ROOT / "config").rglob("*.toml"):
        text = path.read_text().lower()
        assert "password =" not in text and "token =" not in text, path
