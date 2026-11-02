"""Tests of `module/tools/restart_gateway.py` on a fake HTTP server (S11-D). The gateway is never contacted:
the server listens on the loopback interface, the token is a placeholder given by the environment, and the
fake records what it was sent so that the tests can show what the tool did and did not do."""
import io
import json
import os
import sys
import threading
import unittest
from contextlib import redirect_stdout
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "module" / "tools"))

import restart_gateway  # noqa: E402

TOKEN = "placeholder-token-for-the-fake"


class FakeGateway:
    """A server that lists a pending task, accepts the restart, then answers 503 to `down` pings and RUNNING after."""

    def __init__(self, down: int = 2, restart_code: int = 200, pending=None):
        self.requests: list[tuple[str, str, str | None]] = []
        self.down = down
        self.restart_code = restart_code
        self.pending = [{"name": "Module Upgraded: example.module"}] if pending is None else pending
        self.restarted = False
        fake = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def reply(self, code, body, ctype="application/json"):
                data = body.encode("utf-8")
                self.send_response(code)
                self.send_header("Content-Type", ctype)
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def do_GET(self):
                fake.requests.append(("GET", self.path, self.headers.get("X-Ignition-API-Token")))
                if self.path.startswith("/data/api/v1/restart-tasks/pending"):
                    self.reply(200, json.dumps(fake.pending))
                elif self.path == "/StatusPing":
                    if fake.restarted and fake.down > 0:
                        fake.down -= 1
                        self.reply(503, "restarting", "text/plain")
                    else:
                        self.reply(200, "RUNNING", "text/plain")
                else:
                    self.reply(404, "{}")

            def do_POST(self):
                fake.requests.append(("POST", self.path, self.headers.get("X-Ignition-API-Token")))
                if self.path.startswith("/data/api/v1/restart-tasks/restart"):
                    fake.restarted = fake.restart_code == 200
                    self.reply(fake.restart_code, "{}")
                else:
                    self.reply(404, "{}")

        self.server = HTTPServer(("127.0.0.1", 0), Handler)
        self.url = f"http://127.0.0.1:{self.server.server_port}"
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)

    def __enter__(self):
        self.thread.start()
        return self

    def __exit__(self, *exc):
        self.server.shutdown()
        self.server.server_close()

    def posts(self):
        return [r for r in self.requests if r[0] == "POST"]


def run(*argv, token=TOKEN):
    """`main(argv)` with the token variables cleared and `token` (when not None) given as CTIG_IGNITION_TOKEN."""
    printed = io.StringIO()
    with mock.patch.dict(os.environ), redirect_stdout(printed):
        for name in ("CTIG_IGNITION_TOKEN", "CTIG_IGNITION_TOKEN_FILE", "IGNITION_API_TOKEN"):
            os.environ.pop(name, None)
        if token is not None:
            os.environ["CTIG_IGNITION_TOKEN"] = token
        code = restart_gateway.main(list(argv))
    return code, printed.getvalue()


class RestartGatewayTests(unittest.TestCase):
    def test_without_confirm_it_lists_and_never_restarts(self):
        with FakeGateway() as gw:
            code, out = run("--gateway-url", gw.url)
        self.assertEqual(code, 0)
        self.assertIn("Module Upgraded: example.module", out)
        self.assertIn("not restarting", out)
        self.assertEqual(gw.posts(), [])

    def test_confirm_posts_the_restart_with_confirm_true(self):
        with FakeGateway() as gw:
            code, out = run("--gateway-url", gw.url, "--confirm")
        self.assertEqual(code, 0)
        self.assertEqual([p[1] for p in gw.posts()], ["/data/api/v1/restart-tasks/restart?confirm=true"])
        self.assertIn("HTTP 200", out)

    def test_the_token_is_sent_and_never_printed(self):
        with FakeGateway() as gw:
            code, out = run("--gateway-url", gw.url, "--confirm", "--wait", "5", "--poll", "0.01")
        self.assertEqual(code, 0)
        self.assertTrue(gw.requests and all(r[2] == TOKEN for r in gw.requests))
        self.assertNotIn(TOKEN, out)
        self.assertIn("token source env CTIG_IGNITION_TOKEN", out)

    def test_wait_sees_the_gateway_go_down_and_come_back(self):
        with FakeGateway(down=3) as gw:
            code, out = run("--gateway-url", gw.url, "--confirm", "--wait", "5", "--poll", "0.01")
        self.assertEqual(code, 0)
        self.assertIn("gateway RUNNING", out)
        self.assertEqual(gw.down, 0)  # every 503 was polled before the tool called the gateway running

    def test_a_gateway_that_never_goes_down_is_not_a_restarted_one(self):
        with FakeGateway(down=0) as gw:
            code, out = run("--gateway-url", gw.url, "--confirm", "--wait", "0.3", "--poll", "0.02")
        self.assertEqual(code, 1)
        self.assertIn("not RUNNING again", out)

    def test_a_refused_restart_exits_1(self):
        with FakeGateway(restart_code=403) as gw:
            code, out = run("--gateway-url", gw.url, "--confirm")
        self.assertEqual(code, 1)
        self.assertIn("HTTP 403", out)

    def test_a_missing_token_stops_before_any_request(self):
        with FakeGateway() as gw, mock.patch.object(restart_gateway.deploy, "ACCOUNTS", []):
            with self.assertRaises(SystemExit) as stop:
                run("--gateway-url", gw.url, "--confirm", token=None)
        self.assertIn("no gateway API token", str(stop.exception))
        self.assertEqual(gw.requests, [])

    def test_the_gateway_url_must_be_a_base_url(self):
        for bad in ("localhost:8088", "ftp://host", "http://", "http://h:1/?x=1"):
            with self.assertRaises(SystemExit, msg=bad):
                run("--gateway-url", bad)

    def test_the_url_is_required(self):
        with self.assertRaises(SystemExit), mock.patch("sys.stderr", io.StringIO()):
            run()


if __name__ == "__main__":
    unittest.main()
