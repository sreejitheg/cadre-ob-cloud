#!/usr/bin/env bash
# Cadre OpenBridge cloud environment: setup for Claude Code cloud sessions (spike T0, cloud/SPIKE-T0.md section 3.6).
#
#   cloud/setup.sh              environment only: packages, Python tools, Docker daemon, the Ignition image, npm ci,
#                               the Gradle cache and /root/.cadre/env.sh. Idempotent. Paste the body of this mode into
#                               the cloud environment's setup script so that later sessions start warm.
#   cloud/setup.sh gateway      start and commission the Ignition 8.3.6 gateway in Docker on port 8088: admin user,
#                               API token, test user, unsigned modules allowed. Needs ACCEPT_IGNITION_EULA=Y, set by
#                               the owner on the cloud environment; this script never sets it.
#   cloud/setup.sh trust-module after a module install and restart: trust the unsigned Cadre HMI Components module at the
#                               gateway's commissioning step and restart the container, so that the module starts.
#
# Measured in the T0 session (2026-11-03) on Ubuntu 24.04 with Docker CLI 29.9.2:
#   - No Docker daemon runs at session start; `dockerd` started by the session works (overlayfs snapshotter, cgroup v1,
#     bridge network). Docker Hub is admitted by the network policy; the image pull takes about one minute.
#   - The image's Playwright browsers are build 1243, which Playwright for Python 1.63.0 expects; the newest PyPI
#     release (1.64.1) expects build 1248 and fails to launch. The pin avoids downloading browsers.
#   - JDK 17 comes from the Ubuntu packages; the Gradle cache needs one online build (about 2 min 10 s), after which
#     module/tools/build_module.py builds offline as it does at the source.
#   - Secrets (admin password, API token, test login) are generated here and kept in /root/.cadre (mode 700), never in
#     the repository and never printed.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# A second, throwaway gateway can be set up beside the first with CADRE_HOME, CADRE_GW_CONTAINER, CADRE_GW_VOLUME and
# CADRE_GW_PORT (used to test this script from scratch).
CADRE=${CADRE_HOME:-/root/.cadre}
IMAGE=inductiveautomation/ignition:8.3.6
CONTAINER=${CADRE_GW_CONTAINER:-cadre-gw}
VOLUME=${CADRE_GW_VOLUME:-cadre-gw-data}
PORT=${CADRE_GW_PORT:-8088}
GW=http://localhost:$PORT
PW_VERSION=1.63.0

say() { printf '[setup %(%H:%M:%S)T] %s\n' -1 "$*"; }

ensure_dockerd() {
  if docker info >/dev/null 2>&1; then return 0; fi
  say "starting dockerd"
  mkdir -p "$CADRE/logs"
  # setsid: a daemon in its own session survives a restart of the session's worker process (measured: a plain
  # background dockerd stopped with the worker)
  setsid nohup dockerd >"$CADRE/logs/dockerd.log" 2>&1 < /dev/null &
  for _ in $(seq 1 60); do docker info >/dev/null 2>&1 && return 0; sleep 1; done
  say "dockerd did not answer within 60 s; see $CADRE/logs/dockerd.log"; return 1
}

environment() {
  mkdir -p "$CADRE/logs"; chmod 700 "$CADRE"
  if ! [ -x /usr/lib/jvm/java-17-openjdk-amd64/bin/javac ]; then
    say "installing JDK 17"
    apt-get update -qq && DEBIAN_FRONTEND=noninteractive apt-get install -y -qq openjdk-17-jdk-headless >/dev/null
  fi
  if ! python3 -c "import playwright, PIL, importlib.metadata as m; assert m.version('playwright') == '$PW_VERSION'" 2>/dev/null; then
    say "installing Playwright $PW_VERSION and Pillow"
    python3 -m pip install --quiet "playwright==$PW_VERSION" pillow
  fi
  ensure_dockerd
  docker image inspect "$IMAGE" >/dev/null 2>&1 || { say "pulling $IMAGE"; docker pull -q "$IMAGE" >/dev/null; }
  if ! [ -d "$REPO/module/web/node_modules/@oicl/openbridge-webcomponents" ]; then
    say "npm ci (pinned lock file)"; (cd "$REPO/module/web" && npm ci --no-audit --no-fund >/dev/null)
  fi
  chmod +x "$REPO/module/gradlew"
  if ! [ -d /root/.gradle/caches/modules-2/files-2.1/com.inductiveautomation.ignitionsdk ]; then
    say "warming the Gradle cache (one online build)"
    (cd "$REPO/module" && JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64 ./gradlew build --console=plain -q >/dev/null)
  fi
  cat >"$CADRE/env.sh" <<EOF
# Cadre cloud session variables (CLAUDE.md section 4); source before every command.
export CTIG_SRC=$REPO/cloud/vendor
export CTIG_IGNITION_TOKEN_FILE=$CADRE/ignition-token
export CADRE_IGNITION_GATEWAY_URL=$GW
export CADRE_TEST_LOGIN=$CADRE/test-login.properties
export CADRE_PIL_PYTHON=$(command -v python3)
export CADRE_IGNITION_WIKI=$REPO/cloud/vendor/ignition-wiki
export CADRE_JDK17=/usr/lib/jvm/java-17-openjdk-amd64
export CHROME_PATH=\${CHROME_PATH:-/usr/bin/google-chrome}
EOF
  say "environment ready; source $CADRE/env.sh"
}

wait_running() {
  local s=""
  for _ in $(seq 1 100); do
    s=$(curl -s "$GW/StatusPing" || true)
    [ "$s" = '{"state":"RUNNING"}' ] && return 0
    [[ "$s" == *COMMISSIONING* ]] && { say "gateway in commissioning: $s"; return 2; }
    sleep 3
  done
  say "gateway not RUNNING after 300 s (last: $s)"; return 1
}

gateway() {
  [ "${ACCEPT_IGNITION_EULA:-}" = "Y" ] || { say "ACCEPT_IGNITION_EULA is not Y in the environment: stop (the owner sets it)"; exit 3; }
  ensure_dockerd
  mkdir -p "$CADRE"; chmod 700 "$CADRE"
  umask 077
  [ -s "$CADRE/admin-password" ] || python3 -c "import secrets; print(secrets.token_urlsafe(18))" >"$CADRE/admin-password"
  printf 'GATEWAY_ADMIN_USERNAME=admin\nGATEWAY_ADMIN_PASSWORD=%s\n' "$(cat "$CADRE/admin-password")" >"$CADRE/gateway.env"
  if ! docker container inspect "$CONTAINER" >/dev/null 2>&1; then
    say "creating $CONTAINER"
    # 8.3 commissions from ACCEPT_IGNITION_EULA (passed through from the owner's environment, never given a value
    # here), GATEWAY_ADMIN_USERNAME, GATEWAY_ADMIN_PASSWORD and IGNITION_EDITION. Arguments after `--` that start with
    # -D become JVM arguments (the image's entrypoint); -Dignition.allowunsignedmodules=true allows unsigned modules.
    docker run -d --name "$CONTAINER" -p "$PORT:8088" -v "$VOLUME:/usr/local/bin/ignition/data" \
      -e ACCEPT_IGNITION_EULA --env-file "$CADRE/gateway.env" -e IGNITION_EDITION=standard -e TZ=Australia/Sydney \
      "$IMAGE" -n cadre-cloud -m 2048 -- -Dignition.allowunsignedmodules=true >/dev/null
  else
    docker start "$CONTAINER" >/dev/null
  fi
  wait_running || true
  local data; data="$(docker volume inspect -f '{{.Mountpoint}}' "$VOLUME")"
  # The API token and the test user as configuration resources of the volume (no web interface needed):
  #   - api-token/<name>/config.json: profile type `basic-token`, settings.tokenHash = base64url(SHA-256(raw key));
  #     the request header is `X-Ignition-API-Token: <name>:<base64url key>`.
  #   - a token cannot be granted Authenticated/Roles from configuration (the gateway logs and ignores it), so a
  #     custom security level `CadreApi` is declared and added to the gateway's read and write permissions.
  #   - user-source/default/users.json: password "[SALT]" + hex(SHA-256(password + SALT)), SALT 8 hex digits.
  local changed
  changed=$(CADRE="$CADRE" DATA="$data" python3 - <<'PY'
import base64, hashlib, json, os, re, secrets, time, uuid
from pathlib import Path
cadre, root = Path(os.environ["CADRE"]), Path(os.environ["DATA"]) / "config/resources/core/ignition"
b64 = lambda x: base64.urlsafe_b64encode(x).rstrip(b"=").decode()
changed = False
lv_file = root / "security-levels/config.json"; lv = json.loads(lv_file.read_text())
if not any(l["name"] == "CadreApi" for l in lv["securityLevels"]):
    lv["securityLevels"].append({"children": [], "name": "CadreApi",
                                 "description": "Granted to the Cadre cloud API token: gateway read and write over REST."})
    lv_file.write_text(json.dumps(lv, indent=2)); changed = True
sp_file = root / "security-properties/config.json"; sp = json.loads(sp_file.read_text())
for k in ("readPermissions", "writePermissions"):
    if not any(l["name"] == "CadreApi" for l in sp[k]["securityLevels"]):
        sp[k]["securityLevels"].append({"children": [], "name": "CadreApi"}); changed = True
sp_file.write_text(json.dumps(sp, indent=2))
tok_dir = root / "api-token/cadre"
if not (cadre / "ignition-token").exists() or not tok_dir.exists():
    raw = secrets.token_bytes(32)
    tok_dir.mkdir(parents=True, exist_ok=True)
    (tok_dir / "config.json").write_text(json.dumps({"profile": {"type": "basic-token", "secureChannelRequired": False,
        "securityLevels": [{"name": "CadreApi", "children": []}], "timestamp": int(time.time() * 1000)},
        "settings": {"tokenHash": b64(hashlib.sha256(raw).digest())}}, indent=2))
    (tok_dir / "resource.json").write_text(json.dumps({"scope": "A", "version": 1, "restricted": False, "overridable": True,
        "files": ["config.json"], "attributes": {"enabled": True, "description": "Cadre cloud deploy token"}}, indent=2))
    (cadre / "ignition-token").write_text(f"cadre:{b64(raw)}"); changed = True
us_file = root / "user-source/default/users.json"; us = json.loads(us_file.read_text())
if not (cadre / "test-login.properties").exists() or not any(u["username"] == "cadre_test" for u in us["users"]):
    admin = next(u for u in us["users"] if u["username"] == "admin")
    role = next(r["uuid"] for r in us["roles"] if r["rolename"] == "Administrator")
    pw, salt = secrets.token_urlsafe(15), secrets.token_hex(4).upper()
    us["users"] = [u for u in us["users"] if u["username"] != "cadre_test"]
    us["users"].append(dict(admin, uuid=str(uuid.uuid4()), username="cadre_test", roles=[role], passwordHistory=[],
                            password=f"[{salt}]{hashlib.sha256((pw + salt).encode()).hexdigest()}"))
    us_file.write_text(json.dumps(us, indent=2))
    (cadre / "test-login.properties").write_text(f"user=cadre_test\npassword={pw}\n"); changed = True
print("CHANGED" if changed else "UNCHANGED")
PY
)
  chown -R 2003:2003 "$data/config/resources/core/ignition"
  if [ "$changed" = CHANGED ]; then
    say "restarting $CONTAINER to load the token and the test user"
    docker restart "$CONTAINER" >/dev/null
  fi
  wait_running
  local code
  code=$(curl -s -o /dev/null -w '%{http_code}' -H "X-Ignition-API-Token: $(cat "$CADRE/ignition-token")" \
         "$GW/data/api/v1/projects/names")
  [ "$code" = 200 ] || { say "API token answered $code"; return 1; }
  history_provider
  say "gateway ready; API token answers 200"
}

history_provider() {
  # The sample tag models record history to `Sample_SQLite_Database` (wiki/07 GF-53), which the source gateway has
  # and a fresh one does not: without it no trend draws (G10 F19, walk T). Created through the REST resource routes
  # as an SQLite connection and an SQL historian of the same name (our own minimal configuration, not the vendor's
  # quick start, which would also install a sample project). No restart is needed.
  local api="$GW/data/api/v1" tok; tok="$(cat "$CADRE/ignition-token")"
  local name=Sample_SQLite_Database
  if ! curl -s -H "X-Ignition-API-Token: $tok" "$api/resources/names/ignition/database-connection" | grep -q "\"$name\""; then
    curl -s -o /dev/null -X POST -H "X-Ignition-API-Token: $tok" -H 'Content-Type: application/json' \
      "$api/resources/ignition/database-connection" -d '[{"name":"'$name'","collection":"core","enabled":true,
      "description":"Cadre cloud: SQLite store of the tag history the sample tag models name",
      "config":{"driver":"SQLite","translator":"SQLITE","connectURL":"jdbc:sqlite:${data}/local/cadre/history.db","validationQuery":"SELECT 1"}}]'
    say "database connection $name created"
  fi
  if ! curl -s -H "X-Ignition-API-Token: $tok" "$api/resources/names/com.inductiveautomation.historian/historian-provider" | grep -q "\"$name\""; then
    curl -s -o /dev/null -X POST -H "X-Ignition-API-Token: $tok" -H 'Content-Type: application/json' \
      "$api/resources/com.inductiveautomation.historian/historian-provider" -d '[{"name":"'$name'","collection":"core",
      "enabled":true,"description":"Cadre cloud: SQL historian over the connection of the same name",
      "config":{"profile":{"type":"SqlHistorian"},"settings":{}}}]'
    say "history provider $name created"
  fi
}

trust_module() {
  # An unsigned module installed through REST waits, after the restart, at the commissioning step `modules`; the
  # commissioning page's own call trusts it (measured: POST /post-step with the module id in acceptedCertificates).
  local s; s=$(curl -s "$GW/StatusPing" || true)
  if [[ "$s" == *COMMISSIONING* ]]; then
    local jar; jar=$(mktemp)
    curl -s -c "$jar" -b "$jar" "$GW/bootstrap" >/dev/null
    local step lic='[]'; step=$(curl -s -c "$jar" -b "$jar" "$GW/get-step?step=modules&name=modules" || true)
    # A module whose licence page changed (0.8.0) also lists a licence entry at this step; accept the module's own page.
    [[ "$step" == *license* ]] && lic='["cadre.hmi.ob"]'
    curl -s -c "$jar" -b "$jar" -H 'Content-Type: application/json' -X POST "$GW/post-step" \
      -d '{"id":"modules","step":"modules","data":{"acceptedLicenses":'"$lic"',"acceptedCertificates":["cadre.hmi.ob"]}}' >/dev/null
    rm -f "$jar"
    say "unsigned module trusted; restarting $CONTAINER"
    docker restart "$CONTAINER" >/dev/null
  fi
  wait_running
}

case "${1:-environment}" in
  environment) environment ;;
  gateway) gateway ;;
  trust-module) trust_module ;;
  *) echo "usage: $0 [environment|gateway|trust-module]"; exit 2 ;;
esac
