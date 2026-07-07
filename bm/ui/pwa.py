"""Make the installed web app (Add to Home Screen) use the Beautiful Mind name
and icon instead of Streamlit's defaults.

Streamlit Community Cloud serves its own ``manifest.json`` and favicon that we
cannot replace. Instead we inject a custom manifest (as a Blob URL), icons and
meta tags into the *real* page ``<head>`` from a tiny 0-height component iframe
(which is same-origin with the parent, so it can reach ``window.parent``).

On Android, Chrome reads the current manifest when you choose "Add to Home
screen"/"Install app", so it picks up this name and icon.
"""
import base64
import os

import streamlit.components.v1 as components

_ICON_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "app-icon.png",
)

APP_NAME = "Beautiful Mind"
THEME_COLOR = "#0A0A0A"
BACKGROUND_COLOR = "#FFFFFF"


def _icon_b64():
    try:
        with open(_ICON_PATH, "rb") as fh:
            return base64.b64encode(fh.read()).decode("ascii")
    except OSError:
        return ""


def inject() -> None:
    """Inject the PWA manifest, icon and name into the parent document head."""
    icon_b64 = _icon_b64()
    if not icon_b64:
        return
    html = f"""
<script>
(function () {{
  try {{
    var doc = window.parent.document;
    if (doc.__bmPwaInjected) return;   // once per page load
    doc.__bmPwaInjected = true;
    var head = doc.head;

    function b64ToBlob(b64, type) {{
      var bin = atob(b64), arr = new Uint8Array(bin.length);
      for (var i = 0; i < bin.length; i++) arr[i] = bin.charCodeAt(i);
      return new Blob([arr], {{ type: type }});
    }}
    var iconUrl = URL.createObjectURL(b64ToBlob("{icon_b64}", "image/png"));

    function setMeta(name, content) {{
      var m = doc.querySelector("meta[name='" + name + "']");
      if (!m) {{ m = doc.createElement("meta"); m.setAttribute("name", name); head.appendChild(m); }}
      m.setAttribute("content", content);
    }}
    setMeta("application-name", "{APP_NAME}");
    setMeta("apple-mobile-web-app-title", "{APP_NAME}");
    setMeta("apple-mobile-web-app-capable", "yes");
    setMeta("mobile-web-app-capable", "yes");
    setMeta("theme-color", "{THEME_COLOR}");

    function replaceLinks(rel, build) {{
      doc.querySelectorAll("link[rel='" + rel + "']").forEach(function (e) {{ e.remove(); }});
      var l = doc.createElement("link");
      l.setAttribute("rel", rel);
      build(l);
      head.appendChild(l);
    }}
    replaceLinks("apple-touch-icon", function (l) {{ l.href = iconUrl; }});
    replaceLinks("icon", function (l) {{ l.type = "image/png"; l.href = iconUrl; }});

    var base = window.parent.location.origin + window.parent.location.pathname;
    var manifest = {{
      name: "{APP_NAME}",
      short_name: "{APP_NAME}",
      start_url: base,
      scope: window.parent.location.origin + "/",
      display: "standalone",
      background_color: "{BACKGROUND_COLOR}",
      theme_color: "{THEME_COLOR}",
      icons: [
        {{ src: iconUrl, sizes: "512x512", type: "image/png", purpose: "any" }},
        {{ src: iconUrl, sizes: "512x512", type: "image/png", purpose: "maskable" }}
      ]
    }};
    var manUrl = URL.createObjectURL(
      new Blob([JSON.stringify(manifest)], {{ type: "application/manifest+json" }})
    );
    replaceLinks("manifest", function (l) {{ l.href = manUrl; }});

    try {{ doc.title = "{APP_NAME}"; }} catch (e) {{}}
  }} catch (e) {{ /* cross-origin or unsupported: leave defaults */ }}
}})();
</script>
"""
    components.html(html, height=0)
