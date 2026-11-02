"""Experiment E5: the gateway's security configuration and the session's identity (COB-063, NOTE-COB-04
section 8 step 2), read before any command check is written.

A probe project `cadre_hmi_probe` (child of `cadre_hmi_base`, deleted after use, GF-24) shows, in
gateway scope (the scope of every Perspective script):

  S1  `system.user.getUserSources()` (IGW:22 section 3.27): each object's `get*` and `is*` answers,
      from `dir()`, never from recall;
  S2  `system.user.getRoles(userSource)` for each user source S1 names: the role names, read rather
      than assumed (COBD-024);
  S3  the session's `props.auth`: what it holds with nobody signed in, and, after a sign in with the
      test login of NEEDS N-COB-9, what it holds then (`authenticated`, `user`, `user.userName`,
      `user.roles`, `securityLevels`), each read separately so one failure does not hide the rest;
  S4  `system.user.getUser(userSource, name)` for the signed in user, and the `get*` answers of the
      User object it returns (its `getRoles()` is UNVERIFIED in IGW:15 section 7);
  S5  crafted calls (NOTE-COB-04 test T9): a button calls the checked functions of `cadre.hmi` directly,
      as a crafted client would, against P-101 of the water treatment sample, and shows what each
      returned; with nobody signed in each must answer the refusal and P-101 must keep running.

The probe writes nothing unless a signed in admin presses S5. Its page has a Sign in and a Sign out
button (`system.perspective.login()` and `logout()`, IGW:23 sections 10 and 12).

Usage:
    python tools/experiments/e5_security_probe.py --deploy
    python tools/experiments/e5_security_probe.py --delete
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
from hmi import pv, parent as par  # noqa: E402
from hmi.framework import root_classes  # noqa: E402

CHILD = "cadre_hmi_probe"

ANSWERS = [
    "def answers(o):",
    "\tout = {'type': unicode(type(o))}",
    "\tfor n in sorted(set(dir(o))):",
    "\t\tif not (n.startswith('get') or n.startswith('is')):",
    "\t\t\tcontinue",
    "\t\ttry:",
    "\t\t\tv = getattr(o, n)()",
    "\t\t\tout[n] = unicode(v)[:200] + ' <' + type(v).__name__ + '>'",
    "\t\texcept Exception as ex:",
    "\t\t\tout[n] = '! ' + type(ex).__name__",
    "\treturn out",
]


def _sources_lines() -> list[str]:
    """S1 and S2."""
    return ANSWERS + [
        "res = {}",
        "try:",
        "\tsrcs = system.user.getUserSources()",
        "\tres['count'] = len(srcs)",
        "\tfor i, s in enumerate(srcs):",
        "\t\ta = answers(s)",
        "\t\tres['source %d' % i] = a",
        "\t\tname = None",
        "\t\tfor k in ('getName', 'getProfileName'):",
        "\t\t\ttry:",
        "\t\t\t\tname = unicode(getattr(s, k)())",
        "\t\t\t\tbreak",
        "\t\t\texcept Exception:",
        "\t\t\t\tpass",
        "\t\tif name:",
        "\t\t\ttry:",
        "\t\t\t\tres['roles of ' + name] = [unicode(r) for r in system.user.getRoles(name)]",
        "\t\t\texcept Exception as ex:",
        "\t\t\t\tres['roles of ' + name] = '! ' + unicode(ex)[:200]",
        "except Exception as ex:",
        "\tres['error'] = unicode(ex)[:300]",
        "return system.util.jsonEncode(res, 1)",
    ]


def _auth_lines() -> list[str]:
    """S3 and S4."""
    return ANSWERS + [
        "res = {}",
        "a = self.session.props.auth",
        "res['type'] = unicode(type(a))",
        "for k in ('authenticated', 'securityLevels', 'idp'):",
        "\ttry:",
        "\t\tv = getattr(a, k)",
        "\t\tres[k] = unicode(v)[:300] + ' <' + type(v).__name__ + '>'",
        "\texcept Exception as ex:",
        "\t\tres[k] = '! ' + type(ex).__name__ + ' ' + unicode(ex)[:120]",
        "# the user's name, identity and the provider's token claims are never shown, only their shapes",
        "for k in ('userName', 'id', 'firstName', 'lastName', 'roles'):",
        "\ttry:",
        "\t\tv = getattr(a.user, k)",
        "\t\tres['user.' + k] = (unicode(v)[:300] if k == 'roles' else ('set' if v else 'empty')) + ' <' + type(v).__name__ + '>'",
        "\texcept Exception as ex:",
        "\t\tres['user.' + k] = '! ' + type(ex).__name__",
        "try:",
        "\tres['idpAttributes keys'] = sorted([unicode(k) for k in a.idpAttributes])",
        "except Exception as ex:",
        "\tres['idpAttributes keys'] = '! ' + type(ex).__name__",
        "return system.util.jsonEncode(res, 1)",
    ]


def probe_view() -> dict:
    def label(name, y, h, lines):
        return pv.node("ia.display.label", name, pv.cpos(16, y, 1560, h), {
            "style": {"classes": "cadre/font/label cadre/text/active", "whiteSpace": "pre-wrap",
                      "overflow": "hidden"}},
            prop_config={"props.text": pv.bind(pv.expr("now(3000)"), [pv.script_transform(lines)])})

    sign_in = pv.node("ia.input.button", "SignIn", pv.cpos(16, 1250, 200, 40), {"text": "Sign in"},
                      events=pv.on_action(["system.perspective.login()"]))
    sign_out = pv.node("ia.input.button", "SignOut", pv.cpos(232, 1250, 200, 40), {"text": "Sign out"},
                       events=pv.on_action(["system.perspective.logout()"]))
    dev = "[default]cadre_hmi_wtp/P101"
    crafted = pv.node("ia.input.button", "Crafted", pv.cpos(448, 1250, 240, 40), {"text": "S5 crafted calls"},
                      events=pv.on_action([
                          "out = {}",
                          f"out['command W1'] = cadre.hmi.command(self.session, 'W1', '{dev}', 'cmd', False)",
                          f"out['bypass W10'] = cadre.hmi.bypass(self.session, '{dev}', 'C01', True)",
                          f"out['reset W11'] = cadre.hmi.reset_interlocks(self.session, '{dev}')",
                          "out['ack_top W6'] = unicode(cadre.hmi.ack_top('*cadre_hmi_wtp*', self.session))",
                          "ids = [a['id'] for a in cadre.hmi.alarm_list('*cadre_hmi_wtp*')]",
                          "out['ack W8'] = unicode(cadre.hmi.ack(ids, self.session))",
                          f"out['P101 state'] = unicode(system.tag.readBlocking(['{dev}/state'])[0].value)",
                          "self.view.custom.crafted = system.util.jsonEncode(out, 1)"]))
    result = pv.node("ia.display.label", "CraftedResult", pv.cpos(704, 1250, 880, 40), {
        "style": {"classes": "cadre/font/label cadre/text/active", "whiteSpace": "pre-wrap", "overflow": "hidden"}},
        prop_config={"props.text": pv.bind(pv.expr("{view.custom.crafted}"))})
    kids = [label("Sources", 8, 620, _sources_lines()), label("Auth", 640, 600, _auth_lines()), sign_in, sign_out,
            crafted, result]
    root = pv.node("ia.container.coord", "root", {}, {"style": {"overflow": "auto"}},
                   prop_config={"props.style.classes": root_classes("cadre/surface/page")}, children=kids)
    return pv.view(root, size={"width": 1600, "height": 1300}, custom={"crafted": ""})


def build() -> pv.Project:
    prj = pv.Project(CHILD, "Cadre HMI probe (E5)", parent=par.PARENT,
                     description="Experiment E5 security probe; deleted after use")
    prj.add_view("Probe", probe_view())
    prj.set_page_config({"pages": {"/": {"title": "Probe", "viewPath": "Probe"}}})
    return prj


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--deploy", action="store_true")
    ap.add_argument("--delete", action="store_true")
    a = ap.parse_args()
    from hmi import deploy
    if a.delete:
        gw, _ = deploy._gateway()
        print(gw._req("DELETE", f"/data/api/v1/projects/{CHILD}"))
        return 0
    prj = build()
    if a.deploy:
        print(deploy.ensure_trial())
        print(deploy.import_project(prj))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
