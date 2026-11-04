"""Build a throwaway bundle for the `items` mechanism check (`items.mjs`): the component bundle and the generated wrappers for
one synthetic host component, `test.host` (an `obc-notification-badge-button` whose `items` build `obc-app-button` elements,
which may hold `obc-notification-badge-button` elements), and a harness page for it. Nothing under `module/` is written.

Usage:  python module/tools/harness/items_bundle.py <out directory>
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import gen_module_assets as g   # noqa: E402


def main(out: Path) -> None:
    manifest = json.loads((g.PKG / "custom-elements.json").read_text(encoding="utf-8"))
    defaults = json.loads((g.HERE / "web/defaults.json").read_text(encoding="utf-8"))
    g.ITEM_CHILDREN["obc-app-button"] = ["obc-notification-badge-button"]
    spec = {"tag": "obc-notification-badge-button", "type": "test.host", "name": "host", "title": "Host", "palette": "test",
            "size": {"width": 10, "height": 10}, "exclude": [], "events": ["click"],
            "items": {"items": {"tags": ["obc-app-button"], "slot": ""}, "other": {"tags": ["obc-app-button"], "slot": "x"}}}
    g.ITEM_TABLE.clear()
    g.ITEM_TABLE.update(g.build_item_table(manifest, [spec]))
    d = {k: (None if v == "__undefined__" else v) for k, v in defaults[spec["tag"]].items()}
    schema, fields = g.schema_for(spec, g.declaration(manifest, spec["tag"]), g.enums(), d)
    assert schema["properties"]["items"]["type"] == "array" and schema["properties"]["other"]["type"] == "array"
    events = [{"dom": "click", "name": "onPress", "payload": "item"}]
    items = [{"name": n, "tags": e["tags"], "slot": e.get("slot", "")} for n, e in spec["items"].items()]
    script = g.wrapper_script([g.js_spec(spec, fields, events, [], items)])
    out.mkdir(parents=True, exist_ok=True)
    bundle = (g.HERE / "web/dist/ob-components.js").read_text(encoding="utf-8")
    (out / "bundle.js").write_text(bundle + "\n" + script, encoding="utf-8")
    page = (HERE / "harness.html").read_text(encoding="utf-8")
    page = (page.replace("../../gateway/src/main/resources/mounted/css/cadre-ob.css", (g.MOUNTED / "css/cadre-ob.css").as_uri())
            .replace('src="vendor/', f'src="{(HERE / "vendor").as_uri()}/')
            .replace("../../gateway/src/main/resources/mounted/js/cadre-ob.js", "bundle.js"))
    (out / "harness.html").write_text(page, encoding="utf-8")


if __name__ == "__main__":
    main(Path(sys.argv[1]))
