"""Identidad visual de Barrio Pizza para el dashboard.

En esta versión de Streamlit, st.markdown elimina las etiquetas <style> y
st.html aísla su contenido en un shadow DOM. Por eso cada bloque de marca
(encabezado + cinta, y comandas de alerta) se entrega como una sola llamada
st.html que lleva su propio <style> junto al HTML: el CSS se aplica dentro
del mismo componente y los widgets nativos usan el Theme de .streamlit/config.toml.
"""

import base64
import os

_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGO_NEGRO = "assets/logo_negro.png"


def _logo_data_uri(path):
    with open(os.path.join(_DIR, path), "rb") as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode()

_SHORT_TIPO = {
    "RIESGO QUIEBRE": "QUIEBRE",
    "SOBRE-PEDIDO": "DE MÁS",
    "SE OLVIDO": "OLVIDÓ",
    "INGREDIENTE DESCONOCIDO": "¿?",
}

_MOD_TIPO = {
    "RIESGO QUIEBRE": "tomato",
    "SOBRE-PEDIDO": "gold",
    "SE OLVIDO": "azulejo",
    "INGREDIENTE DESCONOCIDO": "stone",
}

# --------------------------------------------------------------------------
# CSS del encabezado, cinta SI HAY PIZZA y comandas.
# Se reutiliza en los bloques <style> de cada st.html.
# --------------------------------------------------------------------------

CSS_ENCABEZADO = """
.bp-header{display:flex;align-items:flex-start;justify-content:space-between;gap:1rem;flex-wrap:wrap;margin-bottom:.4rem;}
.bp-brand{display:flex;align-items:center;gap:1.1rem;}
.bp-logo{height:112px;width:auto;}
.bp-title{font-family:'Fraunces',serif;font-weight:900;font-size:clamp(1.7rem,4vw,2.6rem);letter-spacing:-.02em;line-height:1.02;margin:0;color:#241F1B;}
.bp-title .barrio-accent{font-style:italic;font-weight:600;color:#B5331F;}
.bp-eyebrow{font-family:'JetBrains Mono',monospace;font-size:.68rem;font-weight:600;text-transform:uppercase;letter-spacing:.18em;color:#8B857A;margin-bottom:.45rem;}
.bp-week{font-family:'JetBrains Mono',monospace;font-size:.72rem;color:#8B857A;border:1px dashed #E7DFCF;border-radius:10px;padding:.45rem .7rem;white-space:nowrap;}
.bp-week b{color:#B5331F;font-weight:700;}
.bp-marquee{margin:1.1rem 0 1.6rem;overflow:hidden;border-top:2px solid #241F1B;border-bottom:2px solid #241F1B;background:#FFFDF8;}
.bp-marquee-track{display:flex;width:max-content;animation:bpmarq 26s linear infinite;}
.bp-marquee span{font-family:'Fraunces',serif;font-weight:700;font-style:italic;font-size:1.05rem;letter-spacing:.02em;color:#241F1B;white-space:nowrap;padding:.28rem .5rem;}
.bp-marquee .si{color:#B5331F;}
@keyframes bpmarq{from{transform:translateX(0);}to{transform:translateX(-50%);}}
@media (prefers-reduced-motion: reduce){.bp-marquee-track{animation:none;width:100%;justify-content:center;flex-wrap:wrap;}}
"""

CSS_COMANDA = """
.comanda{background:#FFFDF8;border:1px solid #E7DFCF;border-radius:14px;padding:1rem 1.1rem .9rem;margin-bottom:.9rem;box-shadow:0 1px 0 rgba(36,31,27,.04),0 10px 28px rgba(36,31,27,.06);}
.comanda-head{display:flex;justify-content:space-between;align-items:flex-start;gap:1rem;}
.comanda-branch{font-family:'JetBrains Mono',monospace;font-size:.68rem;font-weight:700;letter-spacing:.16em;color:#8B857A;}
.comanda-stamp{font-family:'JetBrains Mono',monospace;font-weight:700;font-size:.74rem;text-transform:uppercase;letter-spacing:.14em;border:2px solid;padding:.18rem .55rem;transform:rotate(-4deg);border-radius:4px;white-space:nowrap;}
.comanda-stamp.tomato{color:#B5331F;border-color:#B5331F;background:#F7E4DD;}
.comanda-stamp.gold{color:#BF8A2C;border-color:#BF8A2C;background:#F7EEDB;}
.comanda-stamp.azulejo{color:#3E6B8A;border-color:#3E6B8A;background:#E4EDF2;}
.comanda-stamp.stone{color:#8B857A;border-color:#8B857A;}
.comanda-title{font-family:'Fraunces',serif;font-weight:700;font-size:1.25rem;letter-spacing:-.01em;color:#241F1B;margin:.1rem 0 .55rem;}
.comanda-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:.5rem;border-top:1px dashed #E7DFCF;border-bottom:1px dashed #E7DFCF;padding:.55rem 0;}
.comanda-grid .cell span{display:block;font-family:'JetBrains Mono',monospace;font-size:.6rem;font-weight:600;letter-spacing:.1em;color:#8B857A;text-transform:uppercase;}
.comanda-grid .cell b{font-family:'JetBrains Mono',monospace;font-size:.9rem;font-weight:700;color:#241F1B;}
.comanda-msg{font-family:'Inter',sans-serif;font-size:.9rem;color:#241F1B;line-height:1.5;margin:.6rem 0 .35rem;}
.comanda-foot{display:flex;gap:1rem;font-family:'JetBrains Mono',monospace;font-size:.62rem;letter-spacing:.06em;text-transform:uppercase;color:#8B857A;}
.comanda-foot .fresh{color:#3E6B8A;font-weight:700;}
"""

FONTS = ("@import url('https://fonts.googleapis.com/css2?"
         "family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,600;0,9..144,700;0,9..144,900;1,9..144,400;1,9..144,600"
         "&family=Inter:wght@400;500;600;700"
         "&family=JetBrains+Mono:wght@400;600;700&display=swap');")

# --------------------------------------------------------------------------
# Cursor de pizza: la rebanada es el puntero (la punta queda en el hotspot)
# y al hacer clic "muerdes" la rebanada (variante con mordisco).
# --------------------------------------------------------------------------

_CURSOR_WHOLE = """<svg xmlns="http://www.w3.org/2000/svg" width="26" height="30" viewBox="0 0 26 30">
<path d="M5 6.5 L21.5 8.5 Q24 18.5 15 26.5 Z" fill="#D44A26" stroke="#5E2410" stroke-width="1.3" stroke-linejoin="round"/>
<path d="M21.6 8.6 Q24.2 18 15.4 26.3" fill="none" stroke="#D9A441" stroke-width="5" stroke-linecap="round"/>
<path d="M21.6 8.6 Q24.2 18 15.4 26.3" fill="none" stroke="#9C6B2F" stroke-width="1.1" stroke-linecap="round"/>
<path d="M7.5 8 Q9.4 10.6 8.4 12.6 Q6.6 12 7.5 8 Z" fill="#FBE9B0" opacity="0.95"/>
<path d="M12 11.4 Q13.8 13.8 12 16 Q10.6 15 12 11.4 Z" fill="#FBE9B0" opacity="0.9"/>
<circle cx="9.6" cy="15.6" r="2.6" fill="#B23F27" stroke="#7C2A18" stroke-width="0.8"/>
<circle cx="14.4" cy="19.4" r="2.2" fill="#B23F27" stroke="#7C2A18" stroke-width="0.8"/>
<circle cx="12.4" cy="11.8" r="1.8" fill="#B23F27" stroke="#7C2A18" stroke-width="0.7"/>
<circle cx="17" cy="13.4" r="0.9" fill="#4E7A2E"/>
<circle cx="16.6" cy="21.4" r="0.75" fill="#4E7A2E"/>
<circle cx="7.6" cy="19.4" r="0.65" fill="#4E7A2E"/>
</svg>"""

_CURSOR_BITE = """<svg xmlns="http://www.w3.org/2000/svg" width="26" height="30" viewBox="0 0 26 30">
<defs><mask id="m"><rect x="0" y="0" width="26" height="30" fill="white"/><circle cx="4.4" cy="8.6" r="5" fill="black"/></mask></defs>
<g mask="url(#m)">
<path d="M5 6.5 L21.5 8.5 Q24 18.5 15 26.5 Z" fill="#D44A26" stroke="#5E2410" stroke-width="1.3" stroke-linejoin="round"/>
<path d="M21.6 8.6 Q24.2 18 15.4 26.3" fill="none" stroke="#D9A441" stroke-width="5" stroke-linecap="round"/>
<path d="M21.6 8.6 Q24.2 18 15.4 26.3" fill="none" stroke="#9C6B2F" stroke-width="1.1" stroke-linecap="round"/>
<path d="M7.5 8 Q9.4 10.6 8.4 12.6 Q6.6 12 7.5 8 Z" fill="#FBE9B0" opacity="0.95"/>
<path d="M12 11.4 Q13.8 13.8 12 16 Q10.6 15 12 11.4 Z" fill="#FBE9B0" opacity="0.9"/>
<circle cx="9.6" cy="15.6" r="2.6" fill="#B23F27" stroke="#7C2A18" stroke-width="0.8"/>
<circle cx="14.4" cy="19.4" r="2.2" fill="#B23F27" stroke="#7C2A18" stroke-width="0.8"/>
<circle cx="12.4" cy="11.8" r="1.8" fill="#B23F27" stroke="#7C2A18" stroke-width="0.7"/>
<circle cx="17" cy="13.4" r="0.9" fill="#4E7A2E"/>
<circle cx="16.6" cy="21.4" r="0.75" fill="#4E7A2E"/>
<circle cx="7.6" cy="19.4" r="0.65" fill="#4E7A2E"/>
</g>
</svg>"""

_CURSOR_HOTX = 5
_CURSOR_HOTY = 6


def _cursor_uri(svg):
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode("utf-8")).decode("ascii")


CURSOR_WHOLE_URI = _cursor_uri(_CURSOR_WHOLE)
CURSOR_BITE_URI = _cursor_uri(_CURSOR_BITE)

CSS_CURSOR = f"""
.bp-cursor-hide{{display:none;}}
html,html *{{cursor:url("{CURSOR_WHOLE_URI}") {_CURSOR_HOTX} {_CURSOR_HOTY},auto !important;}}
a,button,input,select,textarea,label,[role="button"],[role="slider"],[role="tab"],[role="option"],[role="combobox"],[role="radio"],[role="checkbox"]{{cursor:url("{CURSOR_WHOLE_URI}") {_CURSOR_HOTX} {_CURSOR_HOTY},pointer !important;}}
html:active,html:active *{{cursor:url("{CURSOR_BITE_URI}") {_CURSOR_HOTX} {_CURSOR_HOTY},auto !important;}}
a:active,button:active,input:active,select:active,textarea:active,label:active,[role="button"]:active,[role="slider"]:active,[role="tab"]:active,[role="option"]:active,[role="combobox"]:active,[role="radio"]:active,[role="checkbox"]:active{{cursor:url("{CURSOR_BITE_URI}") {_CURSOR_HOTX} {_CURSOR_HOTY},pointer !important;}}
"""


def cursor_pizza():
    """Bloque <style> (self-contained) que convierte el puntero en una rebanada."""
    return f"<style>{CSS_CURSOR}</style><div class='bp-cursor-hide'></div>"


def cabecera_html(metodo):
    """Encabezado de marca + cinta SI HAY PIZZA (un solo st.html autocontenido)."""
    logo = _logo_data_uri(LOGO_NEGRO)
    frase = ("SI HAY PIZZA&nbsp; • &nbsp;DEL BARRIO Y PARA EL BARRIO&nbsp; • &nbsp;"
             "SUPPORT YOUR LOCAL BARRIO&nbsp; • &nbsp;#TEAMBARRIO&nbsp; • &nbsp;")
    marquee = (
        '<div class="bp-marquee"><div class="bp-marquee-track">'
        f'<span class="si">{frase}</span><span class="si">{frase}</span>'
        "</div></div>"
    )
    return (
        "<style>" + FONTS + CSS_ENCABEZADO + "</style>"
        '<div class="bp-header">'
        f'  <div class="bp-brand">'
        f'    <img src="{logo}" class="bp-logo" alt="Barrio Pizza" />'
        f'    <div>'
        f'      <div class="bp-eyebrow">Control de órdenes de compra · Panamá, desde 2015</div>'
        f'      <div class="bp-title">SI HAY PIZZA — <span class="barrio-accent">del barrio y para el barrio</span></div>'
        f"    </div>"
        f"  </div>"
        f'  <div class="bp-week">SEMANA 7 · PROYECCIÓN <b>{metodo}</b></div>'
        f"</div>"
        + marquee
    )


def _comanda(r):
    short = _SHORT_TIPO.get(r["tipo"], r["tipo"])
    mod = _MOD_TIPO.get(r["tipo"], "stone")
    unidad = r["unidad_base"]
    formato = r["formato_compra"]
    perecedero = "perecible · frío" if r["es_perecedero"] == "Si" else "no perecible"
    return f"""
<div class="comanda">
  <div class="comanda-head">
    <span class="comanda-branch">{r['sucursal'].upper()}</span>
    <span class="comanda-stamp {mod}">{short}</span>
  </div>
  <div class="comanda-title">{r['nombre']}</div>
  <div class="comanda-grid">
    <div class="cell"><span>Pedido</span><b>{r['pedido_formatos']:g} {formato}</b></div>
    <div class="cell"><span>Proyección</span><b>{r['proyeccion_base']:g} {unidad}</b></div>
    <div class="cell"><span>Stock hoy</span><b>{r['stock_base']:g} {unidad}</b></div>
    <div class="cell"><span>Recomendado</span><b>{r['recomendado_formatos']:g} {formato}</b></div>
  </div>
  <p class="comanda-msg">{r['mensaje']}</p>
  <div class="comanda-foot">
    <span>Proveedor: {r['proveedor']}</span>
    <span class="fresh">{perecedero}</span>
  </div>
</div>
"""


def comandas_html(alertas):
    """Devuelve el HTML completo de las comandas con su <style> (un solo st.html)."""
    return "<style>" + FONTS + CSS_COMANDA + "</style>" + "".join(_comanda(r) for _, r in alertas.iterrows())


def pie_html():
    return (
        "<style>" + FONTS + "</style>"
        '<div style="margin-top:2.4rem;padding-top:1rem;border-top:1px solid #E7DFCF;'
        'font-family:\'JetBrains Mono\',monospace;font-size:.66rem;letter-spacing:.08em;'
        'text-transform:uppercase;color:#8B857A;display:flex;justify-content:space-between;'
        'gap:1rem;flex-wrap:wrap;">'
        "<span>Barrio Pizza · Panel de compras</span>"
        "<span>Si hay pizza, hay barrio · #TeamBarrio</span>"
        "</div>"
    )
