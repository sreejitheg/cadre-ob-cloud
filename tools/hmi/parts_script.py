"""Jython source of the page parts of `cadre.hmi` (COB-159), held as text and appended to `scripts.HMI`.

Kept apart from `scripts.py` so that the three builders of the eng02 ASM gaps do not edit the same
lines. Tab indented, Jython 2.7, gateway scope, like the rest of the library.

API calls used, with their evidence:
  `system.tag.exists`, `readBlocking` and `writeBlocking`   IGW:22-system-api-reference section 3.26
  `system.util.invokeAsynchronous(function, args)`          IGW:22-system-api-reference (system.util): runs a function in a
                                                            new thread; used to hold a pulse for its length. Not measured
                                                            on the gateway (wiki page 05 section "Page parts").
No other call is made. `time.sleep` is the Jython standard library (IGW:24).
"""

PARTS_HMI = '''

# Page parts (COB-159, wiki page 05 "Page parts"). A command button of a diagram page pulses a tag the
# descriptors declared (`session.custom.commands`, written by the generator from the descriptors, each entry
# {path, ms}): a script never writes a tag the descriptors did not name. The pulse is write path W18 (the
# admin role, COBD-024), like a device's pulse command.


def _page_command(session, path):
	"""The generator's entry for a declared command tag (`session.custom.commands`: {path, ms}), else None."""
	p = unicode(path or "")
	try:
		for c in session.custom.commands:
			if unicode(c["path"]) == p:
				return c
	except Exception:
		pass
	return None


def page_pulse(session, path):
	"""A page command button's pulse (write path W18, the admin role, COBD-024): true is written to the tag
	`path`, and false again after the length the descriptor gave. Refused without the role, and for a tag
	that is not a declared command of the project (`_page_command`); the role is asked first, so a session
	without it learns nothing of the project's tags. A write the gateway does not make is answered as a
	refusal. Returns an empty string, or the refusal."""
	if not allowed(session, PULSE_PATH):
		return REFUSED
	entry = _page_command(session, path)
	if entry is None:
		return "Refused: not a command of this project"
	p = unicode(entry["path"])
	try:
		ms = int(entry["ms"])
	except Exception:
		return "Refused: the command has no pulse length"
	if ms < 100 or ms > 600000:
		return "Refused: the pulse length is out of range"
	try:
		if not system.tag.exists(p):
			return "Refused: no such tag"
	except Exception:
		return "Refused: no such tag"
	msg = _written(system.tag.writeBlocking([p], [True]), [p])
	if msg:
		return msg

	def release(tag, wait):
		import time
		time.sleep(wait / 1000.0)
		system.tag.writeBlocking([tag], [False])
	system.util.invokeAsynchronous(release, args=[p, ms])
	return ""


def tag_source(tag_path):
	"""The source pattern of the alarms configured on one tag: '[default]site/F1' gives
	'prov:default:/tag:site/F1:/alm:*' (the source form measured by experiment E4, GF-34). A path without
	a provider matches nothing, never everything."""
	d = unicode(tag_path or "").strip()
	if not d.startswith("[") or "]" not in d:
		return NO_MATCH
	prov, path = d[1:].split("]", 1)
	path = path.strip("/")
	if not prov or not path:
		return NO_MATCH
	return "prov:%s:/tag:%s:/alm:*" % (prov, path)


RANGE_BAR_TRACK = "var(--border-divider-color)"
RANGE_BAR_BAND = "var(--element-inactive-color)"
RANGE_BAR_MARK = "var(--element-neutral-color)"
RANGE_BAR_VALUE = "var(--element-active-color)"
RANGE_BAR_BEYOND = "var(--alert-warning-color)"


def _number_or_none(text):
	try:
		return float(text)
	except Exception:
		return None


def range_bar_elements(spec):
	"""The elements of a range bar (`Parts/RangeBar`). `spec` is 'value|min|max|normalLo|normalHi|loLimit|
	hiLimit|vertical', a field empty where the number is absent. The bar is drawn in a 100 by 10 box (10 by
	100 when vertical, the high end at the top): the track, the normal band, a mark at each limit and the
	value marker, which takes the warning colour beyond a limit. Every figure is written here as a plain
	number, so that no number format (and no locale) is involved; a bar with no span draws the track only."""
	f = (unicode(spec or "") + "|" * 8).split("|")
	value, low, high = _number_or_none(f[0]), _number_or_none(f[1]), _number_or_none(f[2])
	nlo, nhi, llo, lhi = _number_or_none(f[3]), _number_or_none(f[4]), _number_or_none(f[5]), _number_or_none(f[6])
	vertical = f[7] == "true"
	out = []

	def box(a, b, c, d, paint, name):
		a, b = max(0.0, min(100.0, a)), max(0.0, min(100.0, b))
		if vertical:
			x0, x1, y0, y1 = c, d, 100.0 - b, 100.0 - a
		else:
			x0, x1, y0, y1 = a, b, c, d
		out.append({"type": "path", "name": name, "fill": {"paint": paint},
			"d": "M%.2f %.2fH%.2fV%.2fH%.2fZ" % (x0, y0, x1, y1, x0)})
	box(0.0, 100.0, 3.0, 7.0, RANGE_BAR_TRACK, "track")
	if low is None or high is None or high <= low:
		return out

	def at(v):
		return 100.0 * (v - low) / (high - low)
	if nlo is not None and nhi is not None and nhi > nlo:
		box(at(nlo), at(nhi), 2.0, 8.0, RANGE_BAR_BAND, "normal")
	for name, v in (("lowLimit", llo), ("highLimit", lhi)):
		if v is not None:
			box(at(v) - 0.6, at(v) + 0.6, 0.0, 10.0, RANGE_BAR_MARK, name)
	if value is not None:
		beyond = (llo is not None and value < llo) or (lhi is not None and value > lhi)
		p = max(1.0, min(99.0, at(value)))
		box(p - 1.0, p + 1.0, 0.0, 10.0, RANGE_BAR_BEYOND if beyond else RANGE_BAR_VALUE, "value")
	return out
'''
