#!/usr/bin/env python3
"""Run and archive the complete Mission 4 verification suite."""

from __future__ import annotations

from datetime import datetime, timezone
import json
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data/exports/atlas_second_edition/verification_summary.json"
PUBLICATION_MANIFEST = ROOT / "data/exports/atlas_second_edition/publication_manifest.json"
LOG_DIR = ROOT / "evidence/lhdrs/verification"


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=path.parent, delete=False
    ) as stream:
        stream.write(value)
        temporary = Path(stream.name)
    os.replace(temporary, path)


def refresh_verification_manifest_entry() -> None:
    """Keep the publication checksum stable after this verifier rewrites its summary."""
    if not PUBLICATION_MANIFEST.exists():
        return
    manifest = json.loads(PUBLICATION_MANIFEST.read_text(encoding="utf-8"))
    relative = str(OUTPUT.relative_to(ROOT))
    for item in manifest.get("files", []):
        if item.get("path") == relative:
            item["bytes"] = OUTPUT.stat().st_size
            item["sha256"] = hashlib.sha256(OUTPUT.read_bytes()).hexdigest()
            break
    write_text(PUBLICATION_MANIFEST, json.dumps(manifest, indent=2, sort_keys=True) + "\n")


def run_check(identifier: str, command: list[str], cwd: Path, timeout: int, env: dict[str, str] | None = None) -> dict[str, object]:
    started = time.monotonic()
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout,
            check=False,
        )
        status = "passed" if result.returncode == 0 else "failed"
        output = result.stdout
        return_code: int | None = result.returncode
    except subprocess.TimeoutExpired as error:
        status = "timed_out"
        partial = error.stdout or ""
        output = partial.decode() if isinstance(partial, bytes) else partial
        output += f"\nTimed out after {timeout} seconds."
        return_code = None
    duration = round(time.monotonic() - started, 2)
    log_path = LOG_DIR / f"{identifier}.log"
    write_text(log_path, output.replace(str(ROOT), "."))
    try:
        working_directory = str(cwd.relative_to(ROOT)) or "."
    except ValueError:
        working_directory = "apps/web (temporary local build mirror)"
    return {
        "id": identifier,
        "status": status,
        "command": " ".join(command),
        "workingDirectory": working_directory,
        "returnCode": return_code,
        "durationSeconds": duration,
        "logPath": str(log_path.relative_to(ROOT)),
        "outputTail": "\n".join(output.replace(str(ROOT), ".").splitlines()[-20:]),
    }


def main() -> int:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    python = os.environ.get("LHDRS_PYTHON", os.environ.get("PYTHON", "python3"))
    npm_env = os.environ.copy()
    npm_env.setdefault("NEXT_TELEMETRY_DISABLED", "1")
    npm_env.setdefault("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/lhdrs")
    started = datetime.now(timezone.utc).isoformat()
    results = [
        run_check("data_integrity", [python, "tests/test_data_integrity.py"], ROOT, 120),
        run_check("lhdrs_integrity", [python, "tests/test_lhdrs_integrity.py"], ROOT, 120),
    ]
    with tempfile.TemporaryDirectory(prefix="lhdrs-mission4-build-") as temporary:
        mirror = Path(temporary) / "repo"
        for directory in ["apps/web", "research", "data", "docs", "packages"]:
            target = mirror / directory
            if directory != "apps/web":
                target.parent.mkdir(parents=True, exist_ok=True)
                target.symlink_to(ROOT / directory, target_is_directory=True)
                continue
            target.mkdir(parents=True, exist_ok=True)
            command = ["rsync", "-a"]
            command.extend(["--exclude=.next", "--exclude=node_modules"])
            command.extend([str(ROOT / directory) + "/", str(target) + "/"])
            subprocess.run(command, check=True, stdout=subprocess.DEVNULL)
        for filename in ["project_state.json", "LHDRS_MASTER_PRD.md"]:
            source = ROOT / filename
            if source.exists():
                (mirror / filename).parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, mirror / filename)
        web = mirror / "apps/web"
        install = run_check("clean_install", ["npm", "ci"], web, 600, npm_env)
        results.append(install)
        mirror_checks = [
            ("typescript", ["./node_modules/.bin/tsc", "--noEmit"], web, 300, npm_env),
            ("prisma_validate", ["./node_modules/.bin/prisma", "validate", "--schema", "../../packages/database/schema.prisma"], web, 300, npm_env),
            ("npm_audit", ["npm", "audit", "--audit-level=high"], web, 300, npm_env),
            ("production_build", ["npm", "run", "build"], web, 900, npm_env),
        ]
        if install["status"] == "passed":
            results.extend(run_check(*check) for check in mirror_checks)
        else:
            for identifier, command, _, _, _ in mirror_checks:
                results.append(
                    {
                        "id": identifier,
                        "status": "skipped",
                        "command": " ".join(command),
                        "workingDirectory": "apps/web (temporary local build mirror)",
                        "returnCode": None,
                        "durationSeconds": 0,
                        "logPath": "",
                        "outputTail": "Skipped because clean npm install failed.",
                    }
                )
    finished = datetime.now(timezone.utc).isoformat()
    payload = {
        "startedAt": started,
        "finishedAt": finished,
        "status": "passed" if all(result["status"] == "passed" for result in results) else "failed",
        "passedCount": sum(result["status"] == "passed" for result in results),
        "checkCount": len(results),
        "buildWorkspace": "temporary local mirror of the exact repository app, lockfile, schema, research, and generated data",
        "checks": results,
    }
    write_text(OUTPUT, json.dumps(payload, indent=2, sort_keys=True) + "\n")
    refresh_verification_manifest_entry()
    for result in results:
        print(f"{str(result['status']).upper():10} {result['id']} ({result['durationSeconds']}s)")
    print(f"SUMMARY    {payload['passedCount']}/{payload['checkCount']} checks passed")
    return 0 if payload["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
