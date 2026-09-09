@'
# ThingsBoard IoT System Test Framework

System and integration testing project around ThingsBoard Community Edition,
using a Smart Energy / EV Charging site as the test domain.

ThingsBoard is an external system under test. Its source code is not modified.

## Current status

Phase 0 environment verified manually:
- PostgreSQL healthy
- ThingsBoard HTTP response: 200
- System administrator login successful

First automated REST test verified: administrator login and authenticated user identity.

## Environment

- ThingsBoard CE: 4.3.1.4
- PostgreSQL: 18
- Docker Compose with Linux containers
- Web UI / REST: http://localhost:8080
- MQTT: localhost:1883

PostgreSQL data persists in a Docker named volume.
Published application ports are bound to localhost.
Database credentials in Compose are for local development only.

The PostgreSQL tag tracks major version 18; its patch version is not pinned.

## First-time setup

Run from the repository root in PowerShell:

```powershell
docker compose -f infra/thingsboard/compose.yaml config --quiet
docker compose -f infra/thingsboard/compose.yaml pull
docker compose -f infra/thingsboard/compose.yaml run --rm -e INSTALL_TB=true thingsboard
```

Run initialization only for a fresh database.
Wait for successful installation before starting the application.

## Start

```powershell
docker compose -f infra/thingsboard/compose.yaml up -d
docker compose -f infra/thingsboard/compose.yaml logs -f --tail 50 thingsboard
```

Ctrl+C leaves the log stream without stopping the containers.

Open http://localhost:8080.

Initial local administrator:
- Email: sysadmin@thingsboard.org
- Password: sysadmin

This installation does not load demo data.

## Verify

```powershell
docker compose -f infra/thingsboard/compose.yaml ps
(Invoke-WebRequest -Uri "http://localhost:8080" -UseBasicParsing -TimeoutSec 30).StatusCode
```

Expected: PostgreSQL healthy, ThingsBoard running, HTTP 200.
Confirm login through the browser.

## Stop

```powershell
docker compose -f infra/thingsboard/compose.yaml down
```

The database volume is preserved. Adding `-v` deletes the database volume.

## Planned scope

Virtual Python devices, REST/MQTT integration tests, controlled failure
injection, TypeScript/Playwright browser tests, performance testing,
a focused Java API suite and CI/CD.

These capabilities are planned, not implemented.

## Installation reference

https://thingsboard.io/docs/installation/docker-windows/
'@ | Set-Content -Encoding UTF8 README.md

## Python API tests

Verified locally with Python 3.14.7.

Create the virtual environment and install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

With ThingsBoard running, configure the local test account and run:

```powershell
$env:TB_BASE_URL = "http://localhost:8080"
$env:TB_USERNAME = "sysadmin@thingsboard.org"
$env:TB_PASSWORD = "sysadmin"

.\.venv\Scripts\python.exe -m pytest -v --tb=short
```

Credentials shown above belong to the local development installation.
Environment variables must be set again in a new PowerShell session.

The first test verifies:
- Successful REST login
- A non-empty access token
- Authenticated access to the current-user endpoint
- Expected email and SYS_ADMIN authority

This test covers JWT login. API keys and tenant-level tests are not yet covered.

Authentication negative coverage:
- Missing authentication header returns HTTP 401.
- Malformed bearer token returns HTTP 401.

All three authentication cases passed locally.
Expired tokens, invalid signatures and role-based authorization are not yet covered.

## Tenant device tests

Local setup:
- Tenant: Smart Energy Test Lab
- Tenant administrator: qa.admin@example.com
- Created manually through the UI and activated using an activation link.

Before running the full suite, configure tenant credentials in PowerShell:

```powershell
$env:TB_TENANT_USERNAME = "qa.admin@example.com"
$tenantCredential = Get-Credential -UserName $env:TB_TENANT_USERNAME -Message "Tenant administrator password"
$env:TB_TENANT_PASSWORD = $tenantCredential.GetNetworkCredential().Password
Remove-Variable tenantCredential
```

Keep TB_USERNAME and TB_PASSWORD configured for the system administrator test.

Device lifecycle coverage:
- Authenticate as TENANT_ADMIN.
- Create a device with a unique name.
- Read it back and verify its ID, name and type.
- Delete it and verify that subsequent retrieval returns HTTP 404.
- Attempt cleanup through a pytest finalizer if intermediate checks fail.

Four test cases passed locally. No MQTT connection or telemetry is tested yet.

Tenant provisioning is currently manual and must be repeated if the database
volume is deleted. Cleanup requires the API to remain reachable and cannot
run if the test process is forcibly terminated.
