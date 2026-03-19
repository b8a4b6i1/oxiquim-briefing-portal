"""
Briefing Matutino — Gerencia de Personas Oxiquim
Genera index.html con noticias del día vía Anthropic API + web_search.

Regla estricta de fecha: solo noticias publicadas HOY.
Si una sección no tiene noticias del día, no se muestra.

Requiere variable de entorno:
  ANTHROPIC_API_KEY   — API key de Anthropic
"""

import os
import json
import datetime
import requests

# ── Configuración ─────────────────────────────────────────────────────────────

ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]

TODAY     = datetime.date.today()
TODAY_STR = TODAY.strftime("%-d de %B de %Y")
TODAY_ISO = TODAY.isoformat()

WEEKDAYS_ES = {
    0:"lunes", 1:"martes", 2:"miércoles", 3:"jueves",
    4:"viernes", 5:"sábado", 6:"domingo"
}
WEEKDAY = WEEKDAYS_ES[TODAY.weekday()]
TODAY_FULL = f"{WEEKDAY.capitalize()} {TODAY_STR}"

# ── Secciones ─────────────────────────────────────────────────────────────────

SECCIONES = [
    {
        "id": "laboral",
        "nombre": "Política laboral Chile",
        "color": "#7cad8a",
        "foto": "https://images.unsplash.com/photo-1589829545856-d10d557cf95f?w=1200&q=65&auto=format&fit=crop",
        "label": "Legislación & Normativa",
        "chile_first": True,
    },
    {
        "id": "regulacion",
        "nombre": "Regulación y compliance laboral",
        "color": "#c47d8a",
        "foto": "https://images.unsplash.com/photo-1450101499163-c8848c66ca85?w=1200&q=65&auto=format&fit=crop",
        "label": "Compliance & OIT",
        "chile_first": True,
    },
    {
        "id": "gestion",
        "nombre": "Gestión organizacional y liderazgo",
        "color": "#e0a07a",
        "foto": "https://images.unsplash.com/photo-1519389950473-47ba0277781c?w=1200&q=65&auto=format&fit=crop",
        "label": "Liderazgo & Cultura",
        "chile_first": True,
    },
    {
        "id": "rrhh",
        "nombre": "Mundo RR.HH. y futuro del trabajo",
        "color": "#6b9fd4",
        "foto": "https://images.unsplash.com/photo-1552664730-d307ca884978?w=1200&q=65&auto=format&fit=crop",
        "label": "People & Talent",
        "chile_first": True,
    },
    {
        "id": "ecl",
        "nombre": "Economía Chile",
        "color": "#c8a96e",
        "foto": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=1200&q=65&auto=format&fit=crop",
        "label": "Macroeconomía nacional",
        "chile_first": True,
    },
    {
        "id": "eint",
        "nombre": "Economía y negocios internacional",
        "color": "#a98bcb",
        "foto": "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=1200&q=65&auto=format&fit=crop",
        "label": "Mercados globales",
        "chile_first": False,
    },
]

PROMPTS = {
    "laboral": f"""Busca noticias publicadas ESTRICTAMENTE HOY {TODAY_ISO} ({TODAY_STR}) sobre política laboral en Chile: legislación laboral, reforma previsional, Dirección del Trabajo, Ministerio del Trabajo, sindicatos, empleo formal Chile. Fuentes: DT, Mintrab, El Mercurio, Diario Financiero, La Tercera, BioBioChile, El Mostrador.
REGLA: incluye SOLO noticias con fecha de publicación exactamente {TODAY_ISO}. La primera noticia DEBE ser de fuente chilena. Si no hay noticias de hoy, devuelve [].
JSON array, cada objeto: titulo, bajada (máx 160 chars), fuente, url (URL real y funcional), fecha_publicacion (YYYY-MM-DD), relevancia ("Urgente"|"Estratégico"|"Informativo"), es_chile (true|false). SOLO JSON, sin texto adicional.""",

    "regulacion": f"""Busca noticias publicadas ESTRICTAMENTE HOY {TODAY_ISO} ({TODAY_STR}) sobre regulación y compliance laboral: OIT, normativas laborales, Diario Oficial Chile, Ley Chile, cumplimiento normativo empresarial, fiscalización DT.
REGLA: solo noticias con fecha exactamente {TODAY_ISO}. Primera noticia de fuente chilena si existe. Si no hay, devuelve [].
JSON array, cada objeto: titulo, bajada (máx 160 chars), fuente, url, fecha_publicacion (YYYY-MM-DD), relevancia ("Urgente"|"Estratégico"|"Informativo"), es_chile (true|false). SOLO JSON.""",

    "gestion": f"""Busca noticias o artículos publicados ESTRICTAMENTE HOY {TODAY_ISO} ({TODAY_STR}) sobre gestión organizacional, liderazgo, cultura empresarial, engagement, cambio organizacional, people analytics. Fuentes: McKinsey, Deloitte, HBR, Gallup, MIT Sloan, RRHHDigital.
REGLA: solo contenido publicado hoy. Primera noticia de fuente chilena o LATAM si existe. Si no hay, devuelve [].
JSON array, cada objeto: titulo, bajada (máx 160 chars), fuente, url, fecha_publicacion (YYYY-MM-DD), relevancia ("Urgente"|"Estratégico"|"Informativo"), es_chile (true|false). SOLO JSON.""",

    "rrhh": f"""Busca noticias publicadas ESTRICTAMENTE HOY {TODAY_ISO} ({TODAY_STR}) sobre recursos humanos, HR tech, people analytics, talento, futuro del trabajo, IA en RRHH, transformación de recursos humanos. Fuentes: HBR, MIT Sloan, SHRM, McKinsey People, Mercer, Gartner, RRHHDigital, medios chilenos.
REGLA: solo noticias con fecha exactamente {TODAY_ISO}. Primera noticia de fuente chilena si existe. Si no hay, devuelve [].
JSON array, cada objeto: titulo, bajada (máx 160 chars), fuente, url, fecha_publicacion (YYYY-MM-DD), relevancia ("Urgente"|"Estratégico"|"Informativo"), es_chile (true|false). SOLO JSON.""",

    "ecl": f"""Busca noticias publicadas ESTRICTAMENTE HOY {TODAY_ISO} ({TODAY_STR}) sobre economía chilena: PIB, inflación, desempleo, Banco Central de Chile, INE, sector industrial, mercado laboral Chile, tipo de cambio. Fuentes: Diario Financiero, El Mercurio Economía, La Tercera Negocios, Banco Central, INE, Bloomberg Línea Chile, Ex-Ante.
REGLA: solo noticias con fecha exactamente {TODAY_ISO}. Primera noticia DEBE ser de fuente chilena. Si no hay, devuelve [].
JSON array, cada objeto: titulo, bajada (máx 160 chars), fuente, url, fecha_publicacion (YYYY-MM-DD), relevancia ("Urgente"|"Estratégico"|"Informativo"), es_chile (true|false). SOLO JSON.""",

    "eint": f"""Busca noticias publicadas ESTRICTAMENTE HOY {TODAY_ISO} ({TODAY_STR}) sobre economía internacional relevante para empresa química industrial en Chile: mercados globales, commodities, petróleo, aranceles, FMI, Fed, BCE, LATAM, cadenas de suministro. Fuentes: FT, Reuters, Bloomberg, CNN Economía, Infobae Economía.
REGLA: solo noticias con fecha exactamente {TODAY_ISO}. Orden por relevancia. Si no hay, devuelve [].
JSON array, cada objeto: titulo, bajada (máx 160 chars), fuente, url, fecha_publicacion (YYYY-MM-DD), relevancia ("Urgente"|"Estratégico"|"Informativo"), es_chile (false). SOLO JSON.""",
}

# ── Validación de fecha ───────────────────────────────────────────────────────

def is_today(item: dict) -> bool:
    fecha = item.get("fecha_publicacion", "")
    if fecha:
        try:
            return datetime.date.fromisoformat(str(fecha).strip()[:10]) == TODAY
        except ValueError:
            pass
    # Fallback: buscar la fecha ISO en titulo+bajada
    texto = (item.get("titulo", "") + " " + item.get("bajada", "")).lower()
    return TODAY_ISO in texto

# ── Llamada a Anthropic ───────────────────────────────────────────────────────

def fetch_news(sec: dict) -> list:
    headers = {
        "Content-Type": "application/json",
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
    }
    body = {
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 2000,
        "tools": [{"type": "web_search_20250305", "name": "web_search"}],
        "messages": [{"role": "user", "content": PROMPTS[sec["id"]]}],
    }
    try:
        r = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers, json=body, timeout=90
        )
        r.raise_for_status()
        data = r.json()
        raw = "".join(
            b.get("text", "") for b in data.get("content", [])
            if b.get("type") == "text"
        )
        raw = raw.replace("```json", "").replace("```", "").strip()
        s, e = raw.find("["), raw.rfind("]")
        if s == -1 or e == -1:
            return []
        items = json.loads(raw[s:e+1])
        today_items = [
            {**n, "_id": f"{sec['id']}_{i}"}
            for i, n in enumerate(items)
            if isinstance(n, dict) and is_today(n)
        ]
        # Chile primero en secciones nacionales
        if sec.get("chile_first") and today_items:
            cl = [n for n in today_items if n.get("es_chile")]
            ot = [n for n in today_items if not n.get("es_chile")]
            today_items = cl + ot
        print(f"  {sec['id']}: {len(today_items)} noticias de hoy")
        return today_items
    except Exception as ex:
        print(f"  ERROR {sec['id']}: {ex}")
        return []

# ── HTML ──────────────────────────────────────────────────────────────────────

def badge_cls(r):
    return "rb-u" if r == "Urgente" else "rb-e" if r == "Estratégico" else "rb-i"

def card_cls(r):
    return " u" if r == "Urgente" else ""

def build_html(all_news: dict) -> str:
    total   = sum(len(v) for v in all_news.values())
    urgente = sum(1 for v in all_news.values() for n in v if n.get("relevancia") == "Urgente")
    secs_con_noticias = sum(1 for v in all_news.values() if v)

    secs_html = ""
    for i, sec in enumerate(SECCIONES):
        items = all_news.get(sec["id"], [])
        if not items:
            continue
        cards = ""
        for n in items:
            rel   = n.get("relevancia", "Informativo")
            url   = n.get("url", "#")
            cards += f"""
    <a class="nc{card_cls(rel)}" data-sec="{sec['id']}" data-rel="{rel}"
       href="{url}" target="_blank" rel="noopener">
      <div class="nc-inner">
        <span class="rb {badge_cls(rel)}">{rel}</span>
        <h2 class="nt">{n.get('titulo','Sin título')}</h2>
        <p class="nb">{n.get('bajada','')}</p>
        <div class="nf"><span class="ns">{n.get('fuente','—')}</span></div>
      </div>
    </a>"""

        secs_html += f"""
  <section class="sec" data-sec="{sec['id']}" style="animation-delay:{i*55}ms">
    <div class="sh">
      <div class="sd" style="background:{sec['color']}"></div>
      <span class="sn">{sec['nombre']}</span>
      <span class="sc">{len(items)} nota{'s' if len(items)!=1 else ''}</span>
    </div>
    <div class="sph">
      <img src="{sec['foto']}" alt="" loading="lazy">
      <span class="spl">{sec['label']}</span>
    </div>
    <div class="ng">{cards}</div>
  </section>"""

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Briefing Matutino — Gerencia de Personas Oxiquim — {TODAY_STR}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,500;1,400&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
<style>
:root{{--ink:#0e0e0e;--chalk:#fff;--mist:rgba(255,255,255,.06);--div:rgba(255,255,255,.1);--acc:#c8a96e;--urg:#e05a4e;--str:#6b9fd4;--sf:'Playfair Display',Georgia,serif;--ss:'DM Sans',system-ui,sans-serif}}
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
html{{font-size:16px;scroll-behavior:smooth}}
body{{background:#0e0e0e;color:#fff;font-family:var(--ss);font-weight:300;line-height:1.65;-webkit-font-smoothing:antialiased}}
.mast{{position:sticky;top:0;z-index:100;background:rgba(14,14,14,.95);backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);border-bottom:1px solid var(--div)}}
.mast-in{{max-width:1280px;margin:0 auto;padding:0 clamp(1rem,4vw,3rem);display:flex;align-items:center;justify-content:space-between;gap:1rem;height:60px;flex-wrap:wrap}}
.brand{{display:flex;align-items:baseline;gap:10px}}
.bn{{font-family:var(--sf);font-size:1.15rem;font-weight:400;letter-spacing:.02em}}
.bs{{font-size:.6rem;font-weight:500;text-transform:uppercase;letter-spacing:.14em;color:var(--acc)}}
.ctrl{{display:flex;align-items:center;gap:8px;flex-wrap:wrap}}
.sw{{position:relative}}
.sw svg{{position:absolute;left:9px;top:50%;transform:translateY(-50%);opacity:.3;pointer-events:none}}
.si{{background:var(--mist);border:1px solid var(--div);border-radius:4px;color:#fff;font-family:var(--ss);font-size:.74rem;font-weight:300;height:33px;padding:0 12px 0 30px;width:185px;outline:none;transition:border-color .2s}}
.si::placeholder{{color:rgba(255,255,255,.22)}}
.si:focus{{border-color:rgba(255,255,255,.28)}}
.fs{{background:var(--mist);border:1px solid var(--div);border-radius:4px;color:rgba(255,255,255,.6);font-family:var(--ss);font-size:.7rem;height:33px;padding:0 8px;cursor:pointer;outline:none}}
.fs option{{background:#1a1a1a}}
.hero{{position:relative;height:clamp(190px,26vw,310px);overflow:hidden;display:flex;align-items:flex-end}}
.hero img{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;filter:brightness(.38) saturate(.72)}}
.hero-g{{position:absolute;inset:0;background:linear-gradient(to top,rgba(14,14,14,.98) 0%,rgba(14,14,14,.12) 65%,transparent 100%)}}
.hero-b{{position:relative;padding:clamp(1.2rem,3vw,2.5rem) clamp(1rem,4vw,3rem);max-width:1280px;width:100%;margin:0 auto}}
.ey{{font-size:.6rem;font-weight:500;text-transform:uppercase;letter-spacing:.18em;color:var(--acc);margin-bottom:.35rem}}
.h1{{font-family:var(--sf);font-size:clamp(1.7rem,4.5vw,3rem);font-weight:400;line-height:1.1;letter-spacing:-.01em}}
.h1 em{{font-style:italic;color:var(--acc)}}
.stats{{border-bottom:1px solid var(--div);padding:0 clamp(1rem,4vw,3rem)}}
.stats-in{{max-width:1280px;margin:0 auto;display:flex;overflow-x:auto}}
.st{{padding:.8rem 2rem .8rem 0;margin-right:2rem;border-right:1px solid var(--div);flex-shrink:0}}
.st:last-child{{border-right:none}}
.sv{{font-family:var(--sf);font-size:1.6rem;font-weight:400;line-height:1}}
.sl{{font-size:.58rem;font-weight:500;text-transform:uppercase;letter-spacing:.1em;color:rgba(255,255,255,.27);margin-top:2px}}
.main{{max-width:1280px;margin:0 auto;padding:2.2rem clamp(1rem,4vw,3rem) 4rem}}
.sec{{margin-bottom:3.2rem;animation:fu .45s ease both}}
@keyframes fu{{from{{opacity:0;transform:translateY(12px)}}to{{opacity:1;transform:translateY(0)}}}}
.sh{{display:flex;align-items:center;gap:10px;margin-bottom:1.1rem;padding-bottom:.8rem;border-bottom:1px solid var(--div)}}
.sd{{width:6px;height:6px;border-radius:50%;flex-shrink:0}}
.sn{{font-family:var(--sf);font-size:.96rem;font-weight:400}}
.sc{{font-size:.6rem;font-weight:500;text-transform:uppercase;letter-spacing:.1em;color:rgba(255,255,255,.26);margin-left:auto}}
.sph{{position:relative;border-radius:5px;overflow:hidden;margin-bottom:1rem;height:clamp(90px,11vw,145px)}}
.sph img{{width:100%;height:100%;object-fit:cover;filter:brightness(.36) saturate(.62);transition:transform 7s ease,filter .4s}}
.sph:hover img{{transform:scale(1.05);filter:brightness(.46) saturate(.8)}}
.spl{{position:absolute;bottom:10px;left:12px;font-size:.56rem;font-weight:500;text-transform:uppercase;letter-spacing:.14em;color:rgba(255,255,255,.36)}}
.ng{{display:grid;gap:8px;background:transparent}}
@media(min-width:600px){{.ng{{grid-template-columns:repeat(2,minmax(0,1fr))}}}}
@media(min-width:900px){{.ng{{grid-template-columns:repeat(3,minmax(0,1fr))}}}}
.nc{{background:#131313;border:.5px solid rgba(255,255,255,.08);border-radius:8px;display:flex;flex-direction:column;position:relative;transition:background .18s,border-color .18s;text-decoration:none;color:inherit;cursor:pointer;overflow:hidden}}
.nc:hover{{background:#1c1c1c;border-color:rgba(255,255,255,.16)}}
.nc-inner{{padding:1.05rem 1.15rem;display:flex;flex-direction:column;gap:.42rem;flex:1}}
.nc.u{{background:rgba(224,90,78,.06);border-color:rgba(224,90,78,.2)}}
.nc.u:hover{{background:rgba(224,90,78,.12);border-color:rgba(224,90,78,.35)}}
.nc.u::before{{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:var(--urg);opacity:.7}}
@media(min-width:600px){{.nc.u{{grid-column:1/-1}}}}
.nc::after{{content:'↗';position:absolute;top:10px;right:12px;font-size:.65rem;color:rgba(255,255,255,.12);transition:color .18s,transform .18s}}
.nc:hover::after{{color:var(--acc);transform:translate(2px,-2px)}}
.rb{{display:inline-flex;align-items:center;gap:4px;font-size:.56rem;font-weight:500;text-transform:uppercase;letter-spacing:.1em;width:fit-content}}
.rb::before{{content:'';width:4px;height:4px;border-radius:50%;background:currentColor;flex-shrink:0}}
.rb-u{{color:var(--urg)}}.rb-e{{color:var(--str)}}.rb-i{{color:rgba(255,255,255,.27)}}
.nt{{font-family:var(--sf);font-size:clamp(.86rem,1.2vw,.97rem);font-weight:400;line-height:1.34;padding-right:1.2rem}}
.nc.u .nt{{font-size:clamp(.92rem,1.4vw,1.06rem)}}
.nb{{font-size:.74rem;font-weight:300;color:rgba(255,255,255,.4);line-height:1.54;flex:1}}
.nf{{display:flex;align-items:center;gap:6px;margin-top:.3rem}}
.ns{{font-size:.6rem;font-weight:500;text-transform:uppercase;letter-spacing:.06em;color:rgba(255,255,255,.25)}}
.nc:hover .ns{{color:var(--acc)}}
footer{{border-top:1px solid var(--div);padding:1.2rem clamp(1rem,4vw,3rem);display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px;margin-top:2rem}}
.fb{{font-family:var(--sf);font-size:.8rem;color:rgba(255,255,255,.18)}}
.fn{{font-size:.6rem;color:rgba(255,255,255,.12)}}
@media(max-width:480px){{.si{{width:140px}}.ctrl{{gap:5px}}}}
</style>
</head>
<body>
<header class="mast">
  <div class="mast-in">
    <div class="brand"><span class="bn">Oxiquim</span><span class="bs">Briefing · Personas</span></div>
    <div class="ctrl">
      <div class="sw">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
        <input class="si" type="text" placeholder="Buscar noticias..." id="si">
      </div>
      <select class="fs" id="sf">
        <option value="">Todas las secciones</option>
        {''.join(f'<option value="{s["id"]}">{s["nombre"]}</option>' for s in SECCIONES)}
      </select>
      <select class="fs" id="rf">
        <option value="">Toda relevancia</option>
        <option value="Urgente">Urgente</option>
        <option value="Estratégico">Estratégico</option>
        <option value="Informativo">Informativo</option>
      </select>
    </div>
  </div>
</header>
<section class="hero">
  <img src="https://images.unsplash.com/photo-1497366216548-37526070297c?w=1600&q=75&auto=format&fit=crop" alt="" loading="eager">
  <div class="hero-g"></div>
  <div class="hero-b">
    <div class="ey">{TODAY_FULL}</div>
    <h1 class="h1">Briefing <em>matutino</em><br>Gerencia de Personas Oxiquim</h1>
  </div>
</section>
<div class="stats">
  <div class="stats-in">
    <div class="st"><div class="sv" id="stT">{total}</div><div class="sl">Noticias hoy</div></div>
    <div class="st"><div class="sv" id="stU">{urgente}</div><div class="sl">Urgentes</div></div>
    <div class="st"><div class="sv" id="stM">0</div><div class="sl">Marcadas</div></div>
    <div class="st"><div class="sv">{secs_con_noticias}</div><div class="sl">Secciones</div></div>
  </div>
</div>
<main class="main" id="main">
{secs_html if secs_html else '<p style="padding:2rem;color:rgba(255,255,255,.3);font-style:italic;font-family:var(--sf)">Sin noticias del día disponibles.</p>'}
</main>
<footer>
  <span class="fb">Briefing Matutino · Gerencia de Personas Oxiquim</span>
  <span class="fn">Solo noticias del {TODAY_STR} · Haz clic en cualquier noticia para ir a la fuente</span>
</footer>
<script>
(function(){{
  var fS='',fR='',fQ='';
  function go(){{
    var q=fQ.toLowerCase(),tot=0,urg=0;
    document.querySelectorAll('.sec').forEach(function(sec){{
      var sid=sec.dataset.sec,vis=0;
      sec.querySelectorAll('.nc').forEach(function(c){{
        var rel=c.dataset.rel||'';
        var tx=(c.querySelector('.nt')||{{}}).textContent+' '+(c.querySelector('.nb')||{{}}).textContent+' '+(c.querySelector('.ns')||{{}}).textContent;
        var ok=true;
        if(fS&&sid!==fS)ok=false;
        if(fR&&rel!==fR)ok=false;
        if(q&&!tx.toLowerCase().includes(q))ok=false;
        c.style.display=ok?'':'none';
        if(ok){{vis++;tot++;if(rel==='Urgente')urg++;}}
      }});
      sec.style.display=vis?'':'none';
    }});
    var t=document.getElementById('stT');if(t)t.textContent=tot;
    var u=document.getElementById('stU');if(u)u.textContent=urg;
  }}
  document.getElementById('si').addEventListener('input',function(){{fQ=this.value;go()}});
  document.getElementById('sf').addEventListener('change',function(){{fS=this.value;go()}});
  document.getElementById('rf').addEventListener('change',function(){{fR=this.value;go()}});
  go();
}})();
</script>
</body>
</html>"""

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print(f"\n=== Briefing Matutino Oxiquim — {TODAY_STR} ===")
    print(f"    Filtro: solo noticias del {TODAY_ISO}\n")

    all_news = {}
    for sec in SECCIONES:
        print(f"Buscando: {sec['nombre']}...")
        all_news[sec["id"]] = fetch_news(sec)

    total = sum(len(v) for v in all_news.values())
    print(f"\nTotal noticias validadas: {total}")

    print("Generando index.html...")
    html = build_html(all_news)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✓ index.html generado ({len(html):,} bytes)\n")

if __name__ == "__main__":
    main()
