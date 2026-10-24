"""Cross-platform commands and smoke tests for the local Docker Compose platform."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[2]
COMPOSE_FILE = ROOT / "infrastructure" / "docker" / "compose.yaml"
SERVICES = (
    "postgres",
    "redis",
    "dynamodb-local",
    "jaeger",
    "prometheus",
    "grafana",
    "mailpit",
    "otel-collector",
)
HTTP_CHECKS = (
    ("Jaeger", "http://127.0.0.1:16686/"),
    ("OpenTelemetry Collector", "http://127.0.0.1:13133/"),
    ("Prometheus", "http://127.0.0.1:9090/-/healthy"),
    ("Grafana", "http://127.0.0.1:3000/api/health"),
    ("Mailpit", "http://127.0.0.1:8025/api/v1/info"),
)


def run(command: list[str], *, capture_output: bool = False) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            command,
            cwd=ROOT,
            check=False,
            capture_output=capture_output,
            text=True,
        )
    except FileNotFoundError as error:
        message = f"Comando não encontrado: {command[0]}. Instale o Docker e o Docker Compose."
        print(message, file=sys.stderr, flush=True)
        raise SystemExit(1) from error


def compose(*arguments: str, capture_output: bool = False) -> subprocess.CompletedProcess[str]:
    return run(
        ["docker", "compose", "-f", str(COMPOSE_FILE), *arguments],
        capture_output=capture_output,
    )


def health_check() -> bool:
    all_healthy = True
    for service in SERVICES:
        container_result = compose("ps", "-q", service, capture_output=True)
        if container_result.returncode != 0:
            print(f"FAIL {service}: não foi possível consultar o Docker Compose.", flush=True)
            if container_result.stderr:
                print(container_result.stderr.strip(), file=sys.stderr)
            all_healthy = False
            continue

        container_ids = container_result.stdout.splitlines()
        if len(container_ids) != 1:
            count = len(container_ids)
            print(
                f"FAIL {service}: esperado 1 container em execução; encontrados {count}.",
                flush=True,
            )
            all_healthy = False
            continue

        inspect_result = run(
            ["docker", "inspect", "--format={{.State.Health.Status}}", container_ids[0]],
            capture_output=True,
        )
        status = inspect_result.stdout.strip()
        healthy = inspect_result.returncode == 0 and status == "healthy"
        print(
            f"{'PASS' if healthy else 'FAIL'} {service}: {status or 'sem estado de saúde'}",
            flush=True,
        )
        all_healthy = all_healthy and healthy

    return all_healthy


def http_check(name: str, url: str) -> bool:
    try:
        with urlopen(url, timeout=5) as response:
            status = int(response.status)
            success = 200 <= status < 300
            detail = f"HTTP {status}"
    except (OSError, URLError, TimeoutError) as error:
        success = False
        detail = str(error)

    print(f"{'PASS' if success else 'FAIL'} {name}: {detail}", flush=True)
    return success


def command_check(name: str, *arguments: str, expected_output: str | None = None) -> bool:
    result = compose(*arguments, capture_output=True)
    output = result.stdout.strip()
    success = result.returncode == 0 and (
        expected_output is None or output == expected_output
    )
    detail = output or result.stderr.strip() or f"código de saída {result.returncode}"
    print(f"{'PASS' if success else 'FAIL'} {name}: {detail}", flush=True)
    return success


def dynamodb_check() -> bool:
    try:
        import boto3  # type: ignore[import-untyped]
        from botocore.config import Config  # type: ignore[import-untyped]
        from botocore.exceptions import BotoCoreError, ClientError  # type: ignore[import-untyped]
    except ModuleNotFoundError as error:
        print(f"FAIL DynamoDB Local: dependência boto3 indisponível ({error}).", flush=True)
        return False

    try:
        client = boto3.client(
            "dynamodb",
            endpoint_url="http://127.0.0.1:18000",
            region_name="us-east-1",
            aws_access_key_id="local",
            aws_secret_access_key="local",
            config=Config(
                connect_timeout=3,
                read_timeout=5,
                retries={"total_max_attempts": 1},
            ),
        )
        client.list_tables()
    except (BotoCoreError, ClientError) as error:
        print(f"FAIL DynamoDB Local: {error}", flush=True)
        return False

    print("PASS DynamoDB Local: list_tables respondeu.", flush=True)
    return True


def smoke_test() -> bool:
    if not health_check():
        print("Smoke tests cancelados porque há containers sem estado saudável.", flush=True)
        return False

    results = [
        command_check(
            "PostgreSQL",
            "exec",
            "-T",
            "postgres",
            "pg_isready",
            "-U",
            "authenticator",
            "-d",
            "authenticator",
        ),
        command_check(
            "Redis",
            "exec",
            "-T",
            "redis",
            "redis-cli",
            "ping",
            expected_output="PONG",
        ),
        dynamodb_check(),
    ]
    results.extend(http_check(name, url) for name, url in HTTP_CHECKS)
    return all(results)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "action",
        choices=("start", "stop", "restart", "health-check", "smoke-test"),
        help="ação operacional para a plataforma local",
    )
    action = parser.parse_args().action

    if action == "start":
        return compose("up", "-d", "--wait").returncode
    if action == "stop":
        return compose("down").returncode
    if action == "restart":
        result = compose("restart")
        if result.returncode != 0:
            return result.returncode
        return compose("up", "-d", "--wait").returncode
    if action == "health-check":
        return 0 if health_check() else 1
    return 0 if smoke_test() else 1


if __name__ == "__main__":
    raise SystemExit(main())
