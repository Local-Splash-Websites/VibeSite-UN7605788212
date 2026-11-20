#!/usr/bin/env python3
"""Static site generator. Standard library only."""

import html
import json
import re
import shutil
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "site.json"
CONTENT = ROOT / "content"
SRC = ROOT / "src"
PUBLIC = ROOT / "public"
ASSETS = ROOT / "assets" / "images"


def load_json(path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def esc(value):
    return html.escape(str(value), quote=True)


def paragraphs(items):
    return "\n".join(f"<p>{esc(text)}</p>" for text in items or [])


def linkify_phone(site, text):
    safe = esc(text)
    phone = esc(site["phone_display"])
    return safe.replace(
        phone,
        f'<a href="tel:{esc(site["phone_tel"])}">{phone}</a>',
    )


def lede_html(text):
    parts = [part.strip() for part in re.split(r"(?<=[.!?])\s+(?=[A-Z])", str(text).strip()) if part.strip()]
    if len(parts) < 2:
        return f'<p class="lede">{esc(text)}</p>'
    lines = "\n".join(f'<span class="lede-line">{esc(part)}</span>' for part in parts)
    return f'<p class="lede">{lines}</p>'


def area_slug(name):
    return name.lower().replace(" ", "-")


def area_node(name):
    if str(name).endswith("County"):
        return {"@type": "AdministrativeArea", "name": name}
    return {
        "@type": "City",
        "name": name,
        "containedInPlace": {"@type": "State", "name": "California"},
    }


def bullets(items):
    if not items:
        return ""
    lis = "\n".join(f"<li>{esc(item)}</li>" for item in items)
    return f"<ul>\n{lis}\n</ul>"


def image_lookup(images):
    return {item["id"]: item for item in images}


def picture(image, sizes, eager=False, class_name="", priority=""):
    variants = sorted(image["variants"], key=lambda item: item["width"])
    fallback = variants[0]
    largest = variants[-1]
    srcset = ", ".join(
        f"/assets/images/{esc(item['file'])} {item['width']}w" for item in variants
    )
    attrs = [
        f'src="/assets/images/{esc(fallback["file"])}"',
        f'srcset="{srcset}"' if len(variants) > 1 else "",
        f'sizes="{esc(sizes)}"' if len(variants) > 1 else "",
        f'width="{largest["width"]}"',
        f'height="{largest["height"]}"',
        f'alt="{esc(image["alt"])}"',
        'decoding="async"',
    ]
    if eager:
        attrs.append('fetchpriority="high"')
    elif priority == "low":
        attrs.append('fetchpriority="low"')
    else:
        attrs.append('loading="lazy"')
    if class_name:
        attrs.append(f'class="{esc(class_name)}"')
    return "<img " + " ".join(attr for attr in attrs if attr) + ">"


def href(path):
    if not path or path == "/":
        return "/"
    if path.endswith(".html"):
        return path
    return path.rstrip("/") + "/"


def canonical(site, path):
    host = site["canonical_host"].rstrip("/")
    return host + href(path)


def postal_address(site):
    address = site["address"]
    return {
        "@type": "PostalAddress",
        "streetAddress": address["street"],
        "addressLocality": address["city"],
        "addressRegion": address["region"],
        "postalCode": address["postal_code"],
        "addressCountry": address["country"],
    }


def opening_hours(site):
    hours = []
    for row in site["hours"]:
        hours.append({
            "@type": "OpeningHoursSpecification",
            "dayOfWeek": row["day"],
            "opens": row["opens"],
            "closes": row["closes"],
        })
    return hours


def json_ld(site, page, image):
    host = site["canonical_host"].rstrip("/")
    areas = [area_node(name) for name in site["service_areas"]]
    variants = sorted(image["variants"], key=lambda item: item["width"])
    image_url = host + "/assets/images/" + variants[-1]["file"]
    logo_url = host + "/assets/images/logo.png"
    page_url = canonical(site, page["path"])
    org_id = host + "/#organization"
    business_id = host + "/#business"
    graph = [
        {
            "@type": "Organization",
            "@id": org_id,
            "name": site["name"],
            "url": host + "/",
            "logo": logo_url,
            "telephone": site["phone_schema"],
            "foundingDate": site["established"],
            "sameAs": site["same_as"],
            "address": postal_address(site),
        },
        {
            "@type": ["Electrician", "GeneralContractor", "HomeAndConstructionBusiness"],
            "@id": business_id,
            "name": site["name"],
            "url": host + "/",
            "image": image_url,
            "logo": logo_url,
            "telephone": site["phone_schema"],
            "description": page["description"],
            "slogan": site["tagline"],
            "foundingDate": site["established"],
            "parentOrganization": {"@id": org_id},
            "address": postal_address(site),
            "geo": {
                "@type": "GeoCoordinates",
                "latitude": site["geo"]["latitude"],
                "longitude": site["geo"]["longitude"],
            },
            "areaServed": areas,
            "openingHoursSpecification": opening_hours(site),
            "paymentAccepted": ", ".join(site["payment_methods"]),
            "hasMap": site["map_link"],
            "sameAs": site["same_as"],
            "hasCredential": {
                "@type": "EducationalOccupationalCredential",
                "name": "CSLB 352894",
                "credentialCategory": "license",
                "identifier": "352894",
                "recognizedBy": {
                    "@type": "Organization",
                    "name": "Contractors State License Board",
                },
            },
        },
        {
            "@type": "WebSite",
            "@id": host + "/#website",
            "url": host + "/",
            "name": site["name"],
            "publisher": {"@id": org_id},
            "inLanguage": "en-US",
        },
    ]
    crumbs = page.get("crumbs") or []
    if crumbs:
        graph.append({
            "@type": "BreadcrumbList",
            "@id": page_url + "#breadcrumb",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": index,
                    "name": crumb["name"],
                    "item": host + href(crumb["path"]),
                }
                for index, crumb in enumerate(crumbs, start=1)
            ],
        })
    faqs = page.get("faqs") or []
    if faqs:
        graph.append({
            "@type": "FAQPage",
            "@id": page_url + "#faq",
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": item["q"],
                    "acceptedAnswer": {"@type": "Answer", "text": item["a"]},
                }
                for item in faqs
            ],
        })
    service = page.get("service")
    if service:
        served = areas
        if service.get("area"):
            served = [area_node(service["area"])]
        graph.append({
            "@type": "Service",
            "@id": page_url + "#service",
            "name": service["name"],
            "serviceType": service.get("serviceType") or service["name"],
            "url": page_url,
            "provider": {"@id": business_id},
            "areaServed": served,
        })
    return json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, indent=2)


def hours_list(site):
    rows = []
    for row in site["hours"]:
        opens = format_time(row["opens"])
        closes = format_time(row["closes"])
        rows.append(f"<li><span>{esc(row['day'])}</span> <span>{esc(opens)}–{esc(closes)}</span></li>")
    for day in site["hours_closed"]:
        rows.append(f"<li><span>{esc(day)}</span> <span>Closed</span></li>")
    return "<ul class=\"hours\">\n" + "\n".join(rows) + "\n</ul>"


def format_time(value):
    hour, minute = value.split(":")
    hour = int(hour)
    suffix = "a.m." if hour < 12 else "p.m."
    hour12 = hour % 12 or 12
    if minute == "00":
        return f"{hour12}:00 {suffix}"
    return f"{hour12}:{minute} {suffix}"


def nav(site, pages, current_path):
    electrical = [p for p in pages if p.get("group") == "electrical"]
    construction = [p for p in pages if p.get("group") == "construction"]

    def link(path, label):
        current = ' aria-current="page"' if path == current_path else ""
        return f'<a href="{esc(href(path))}"{current}>{esc(label)}</a>'

    def group(label, control_id, items):
        child_current = any(item["path"] == current_path for item in items)
        current_attr = ' aria-current="true"' if child_current else ""
        item_class = "nav-drop is-current" if child_current else "nav-drop"
        links = "\n".join(
            f"<li>{link(item['path'], item['label'])}</li>" for item in items
        )
        return f"""
<li class="{item_class}">
  <button type="button" class="nav-drop-btn" aria-expanded="false" aria-controls="{control_id}"{current_attr}>
    <span class="nav-label">{esc(label)}</span>
    <span class="nav-caret" aria-hidden="true"></span>
  </button>
  <ul id="{control_id}" class="nav-sub">
    {links}
  </ul>
</li>
"""

    home_current = ' aria-current="page"' if current_path == "/" else ""
    about = next(p for p in pages if p["id"] == "about")
    gallery = next(p for p in pages if p["id"] == "gallery")
    contact = next(p for p in pages if p["id"] == "contact")
    electrical_items = [{"path": item["path"], "label": item["nav"]} for item in electrical]
    construction_items = [{"path": item["path"], "label": item["nav"]} for item in construction]
    area_items = [{"path": "/service-areas", "label": "All service areas"}]
    for name in site["service_areas"]:
        area_items.append({"path": f"/service-areas/{area_slug(name)}", "label": name})
    return f"""
<nav class="site-nav" aria-label="Primary">
  <button type="button" class="nav-toggle" aria-expanded="false" aria-controls="nav-panel">Menu</button>
  <div id="nav-panel" class="nav-panel">
    <a class="panel-call" href="tel:{esc(site["phone_tel"])}">Call {esc(site["phone_display"])}</a>
    <ul class="nav-links" id="nav-links">
      <li><a href="/"{home_current}>Home</a></li>
      {group("Electrical", "nav-electrical", electrical_items)}
      {group("Construction", "nav-construction", construction_items)}
      {group("Service Areas", "nav-areas", area_items)}
      <li>{link(about["path"], "About")}</li>
      <li>{link(gallery["path"], "Gallery")}</li>
      <li>{link(contact["path"], "Contact")}</li>
    </ul>
  </div>
</nav>
"""


def license_number(site):
    raw = site["license"]
    if raw.upper().startswith("CSLB"):
        raw = raw[4:]
    return raw.lstrip("#")


def header(site, pages, current_path):
    number = license_number(site)
    return f"""
<a class="skip" href="#main">Skip to content</a>
<div class="utility-bar">
  <p class="wrap utility-inner">
    <span>La Quinta, CA</span>
    <span class="utility-dot" aria-hidden="true">·</span>
    <a href="tel:{esc(site["phone_tel"])}">{esc(site["phone_display"])}</a>
    <span class="utility-dot" aria-hidden="true">·</span>
    <span>CSLB #{esc(number)}</span>
  </p>
</div>
<header class="site-header">
  <div class="wrap header-bar">
    <a class="brand" href="/">
      <img src="/assets/images/logo.png" width="275" height="275" alt="MB Construction and Electric">
    </a>
    {nav(site, pages, current_path)}
    <div class="header-actions">
      <a class="btn-slant btn-quote" href="/contact/">Get a quote</a>
      <a class="btn-slant btn-call" href="tel:{esc(site["phone_tel"])}">Call <span class="visually-hidden">{esc(site["phone_display"])}</span></a>
    </div>
  </div>
</header>
<a class="mobile-call" href="tel:{esc(site["phone_tel"])}">Call {esc(site["phone_display"])}</a>
"""


def footer(site, pages, year):
    simple = [
        ("/", "Home"),
        ("/about", "About"),
        ("/service-areas", "Service Areas"),
        ("/gallery", "Gallery"),
        ("/contact", "Contact"),
        ("/privacy-policy", "Privacy Policy"),
    ]
    services = [p for p in pages if p.get("template") == "service"]
    simple_links = "\n".join(
        f'<li><a href="{esc(href(path))}">{esc(label)}</a></li>' for path, label in simple
    )
    service_links = "\n".join(
        f'<li><a href="{esc(href(page["path"]))}">{esc(page["nav"])}</a></li>' for page in services
    )
    areas = "\n".join(
        f'<li><a href="/service-areas/{esc(area_slug(name))}/">{esc(name)}</a></li>'
        for name in site["service_areas"]
    )
    address = site["address"]
    social = site["social"]
    return f"""
<footer class="site-footer">
  <div class="wrap footer-grid">
    <section>
      <h2>{esc(site["name"])}</h2>
      <p>{esc(site["tagline"])}</p>
      <address>
        {esc(address["street"])}<br>
        {esc(address["city"])}, {esc(address["region"])} {esc(address["postal_code"])}
      </address>
      <p><a href="tel:{esc(site["phone_tel"])}">{esc(site["phone_display"])}</a></p>
      <p>License # {esc(site["license"])}</p>
      <ul class="social">
        <li><a href="{esc(social["facebook"])}">Facebook</a></li>
        <li><a href="{esc(social["yelp"])}">Yelp</a></li>
        <li><a href="{esc(social["google_maps"])}">Google Maps</a></li>
      </ul>
    </section>
    <section>
      <h2>Visit</h2>
      <ul class="footer-links">{simple_links}</ul>
    </section>
    <section>
      <h2>Services</h2>
      <ul class="footer-links">{service_links}</ul>
    </section>
    <section>
      <h2>Hours of operation</h2>
      {hours_list(site)}
    </section>
    <section class="footer-areas">
      <h2>Areas We Serve</h2>
      <ul class="area-links">{areas}</ul>
      <p class="all-areas"><a href="/service-areas/">All service areas</a></p>
    </section>
  </div>
  <div class="wrap legal">
    <p>&copy; {year} {esc(site["name"])}. All rights reserved. <a href="/privacy-policy/">Privacy Policy</a></p>
  </div>
</footer>
"""


def form(site, page_path, form_name):
    return f"""
<form class="lead-form" action="/v1/lead" method="post" data-lead>
  <input type="hidden" name="site_id" value="{esc(site["site_id"])}">
  <input type="hidden" name="form_name" value="{esc(form_name)}">
  <input type="hidden" name="page" value="{esc(href(page_path))}">
  <p class="hp">
    <label for="{esc(form_name)}-company">Company website</label>
    <input id="{esc(form_name)}-company" type="text" name="company_website" tabindex="-1" autocomplete="off">
  </p>
  <div class="fields">
    <p>
      <label for="{esc(form_name)}-name">Name</label>
      <input id="{esc(form_name)}-name" name="name" type="text" autocomplete="name" required>
    </p>
    <p>
      <label for="{esc(form_name)}-phone">Phone</label>
      <input id="{esc(form_name)}-phone" name="phone" type="tel" autocomplete="tel" required>
    </p>
    <p>
      <label for="{esc(form_name)}-email">Email</label>
      <input id="{esc(form_name)}-email" name="email" type="email" autocomplete="email" required>
    </p>
    <p>
      <label for="{esc(form_name)}-address">Address</label>
      <input id="{esc(form_name)}-address" name="address" type="text" autocomplete="street-address">
    </p>
    <p class="full">
      <label for="{esc(form_name)}-message">Message</label>
      <textarea id="{esc(form_name)}-message" name="message" rows="5" required></textarea>
    </p>
  </div>
  <button type="submit">Send message</button>
  <p class="form-note">Thank you for contacting us. We will get back to you as soon as possible.</p>
</form>
"""


def cta(site, marketing, place=""):
    block = marketing["cta"]
    heading = block["heading"] if not place else f"Talk through a project in {place}"
    text = block["text"] if not place else (
        f"Call {site['phone_display']} Monday through Friday, 8:00 a.m. to 5:00 p.m., "
        f"or send a quote request for work in {place}."
    )
    return f"""
<aside class="cta-band">
  <div class="wrap cta-inner">
    <div>
      <h2>{esc(heading)}</h2>
      <p>{linkify_phone(site, text)}</p>
    </div>
    <div class="cta-actions">
      <a class="btn-slant btn-call" href="tel:{esc(site["phone_tel"])}">{esc(block["call_label"])}</a>
      <a class="btn-slant btn-quote" href="/contact/">{esc(block["quote_label"])}</a>
    </div>
  </div>
</aside>
"""


def why_section(marketing):
    block = marketing["why"]
    items = "\n".join(
        f"<li><h3>{esc(item['title'])}</h3><p>{esc(item['text'])}</p></li>"
        for item in block["items"]
    )
    return f"""
<section class="section band-paper">
  <div class="wrap">
    <p class="eyebrow">{esc(block["eyebrow"])}</p>
    <h2>{esc(block["heading"])}</h2>
    <ul class="why-grid">{items}</ul>
  </div>
</section>
"""


def trust_badges(marketing):
    icons = {
        "shield": '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 2.2 4.6 5.1v6.2c0 4.6 3.1 7.9 7.4 9.4 4.3-1.5 7.4-4.8 7.4-9.4V5.1L12 2.2zm-1.1 12.2-2.4-2.4 1.2-1.2 1.2 1.2 3.3-3.3 1.2 1.2-4.5 4.5z"/></svg>',
        "calendar": '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M7 2h2v2h6V2h2v2h3a1 1 0 0 1 1 1v16a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V5a1 1 0 0 1 1-1h3V2zm12 8H5v9h14v-9zM8 13h2v2H8v-2zm3.5 0h2v2h-2v-2z"/></svg>',
        "clock": '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 2a10 10 0 1 0 .01 20.01A10 10 0 0 0 12 2zm0 2a8 8 0 1 1 0 16 8 8 0 0 1 0-16zm1 3h-2v6.1l3.7 2.2 1-1.7-2.7-1.6V7z"/></svg>',
    }
    items = []
    for badge in marketing["services_intro"]["badges"]:
        items.append(
            "<li>"
            f'<span class="trust-icon" aria-hidden="true">{icons[badge["icon"]]}</span>'
            '<span class="trust-copy">'
            f"<strong>{esc(badge['title'])}</strong>"
            f"<span>{esc(badge['text'])}</span>"
            "</span></li>"
        )
    return f'<ul class="trust-badges">{"".join(items)}</ul>'


def process_section(site, marketing):
    block = marketing["process"]
    steps = "\n".join(
        f"<li><span class=\"step-num\">{index}</span><h3>{esc(step['title'])}</h3><p>{linkify_phone(site, step['text'])}</p></li>"
        for index, step in enumerate(block["steps"], start=1)
    )
    return f"""
<section class="section band-navy process">
  <div class="wrap">
    <p class="eyebrow">{esc(block["eyebrow"])}</p>
    <h2>{esc(block["heading"])}</h2>
    <ul class="steps">{steps}</ul>
  </div>
</section>
"""


def faq_section(items, eyebrow, heading):
    rows = "\n".join(
        f'<details name="faq"><summary>{esc(item["q"])}</summary><p>{esc(item["a"])}</p></details>'
        for item in items
    )
    return f"""
<section class="section band-white">
  <div class="wrap faq-wrap">
    <p class="eyebrow">{esc(eyebrow)}</p>
    <h2>{esc(heading)}</h2>
    <div class="faq">{rows}</div>
  </div>
</section>
"""


def preload_image(image, sizes):
    variants = sorted(image["variants"], key=lambda item: item["width"])
    srcset = ", ".join(
        f"/assets/images/{item['file']} {item['width']}w" for item in variants
    )
    href_value = "/assets/images/" + variants[0]["file"]
    return (
        f'<link rel="preload" as="image" href="{esc(href_value)}" '
        f'imagesrcset="{esc(srcset)}" imagesizes="{esc(sizes)}" fetchpriority="high">'
    )


def check_meta(page):
    title = page["title"]
    description = page["description"]
    if len(title) > 60:
        raise SystemExit(f"Title is {len(title)} characters: {title}")
    if len(description) > 155:
        raise SystemExit(f"Description is {len(description)} characters: {description}")


def layout(site, page, pages, body, hero_image, year, extra_head=""):
    check_meta(page)
    title = page["title"]
    description = page["description"]
    url = canonical(site, page["path"])
    variants = sorted(hero_image["variants"], key=lambda item: item["width"])
    largest = variants[-1]
    og_image = site["canonical_host"].rstrip("/") + "/assets/images/" + largest["file"]
    robots = page.get("robots", "index, follow")
    ld = json_ld(site, page, hero_image)
    hero_preload = preload_image(hero_image, "100vw")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(description)}">
  <meta name="robots" content="{esc(robots)}">
  <link rel="canonical" href="{esc(url)}">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="{esc(site["name"])}">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(description)}">
  <meta property="og:url" content="{esc(url)}">
  <meta property="og:image" content="{esc(og_image)}">
  <meta property="og:image:alt" content="{esc(hero_image["alt"])}">
  <meta property="og:image:width" content="{largest["width"]}">
  <meta property="og:image:height" content="{largest["height"]}">
  <meta property="og:locale" content="{esc(site["locale"])}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{esc(title)}">
  <meta name="twitter:description" content="{esc(description)}">
  <meta name="twitter:image" content="{esc(og_image)}">
  <meta name="twitter:image:alt" content="{esc(hero_image["alt"])}">
  {hero_preload}
  <link rel="icon" href="/assets/images/favicon-32.png" sizes="32x32" type="image/png">
  <link rel="icon" href="/assets/images/favicon.png" sizes="48x48" type="image/png">
  <link rel="apple-touch-icon" href="/assets/images/apple-touch-icon.png">
  <link rel="stylesheet" href="/assets/site.css">
  {extra_head}
  <script type="application/ld+json">
{ld}
  </script>
</head>
<body>
{header(site, pages, page["path"])}
<main id="main">
{body}
</main>
{footer(site, pages, year)}
<script src="/assets/site.js" defer></script>
</body>
</html>
"""


def portrait_card(item, image, blurb, sizes):
    return f"""
<article class="portrait-card">
  <a href="{esc(href(item["path"]))}">
    {picture(image, sizes)}
    <span class="portrait-shade" aria-hidden="true"></span>
    <span class="portrait-copy">
      <h3>{esc(item["nav"])}</h3>
      <p>{esc(blurb)}</p>
    </span>
  </a>
</article>
"""


def render_home(site, page, pages, images, reviews, marketing):
    hero = images[page["hero_image"]]
    card_copy = marketing.get("cards", {})
    cards = []
    for item in pages:
        if item.get("template") != "service":
            continue
        photo = images[item.get("hero") or item["image"]]
        blurb = card_copy.get(item["id"], item["card"])
        cards.append(portrait_card(item, photo, blurb, "(max-width: 700px) 78vw, 220px"))
    areas = "\n".join(
        f'<li><a href="/service-areas/{esc(area_slug(name))}/">{esc(name)}</a></li>'
        for name in site["service_areas"]
    )
    areas += '\n<li><a href="/service-areas/">All service areas</a></li>'
    review_html = []
    for review in reviews:
        review_html.append(f"""
<blockquote>
  <p class="stars"><span aria-hidden="true">★★★★★</span> <span class="visually-hidden">Rated {review["rating"]} out of 5</span></p>
  <p>{esc(review["text"])}</p>
  <footer><cite>{esc(review["name"])}</cite> <time datetime="{esc(review["date"])}">{esc(review["date"])}</time></footer>
</blockquote>
""")
    gallery_ids = [
        "kitchen-tile-backsplash",
        "modern-courtyard-blue-doors",
        "covered-patio-ceiling-fans",
        "black-ceiling-fan",
        "bathroom-freestanding-tub",
        "labeled-breaker-panel",
        "kitchen-remodel-in-progress",
        "desert-home-arched-gate",
    ]
    thumbs = "\n".join(
        f'<li><a href="/gallery/">{picture(images[item], "(max-width: 700px) 50vw, 240px")}</a></li>'
        for item in gallery_ids
    )
    hero_copy = marketing["hero"]
    intro = marketing["services_intro"]
    home_inner = f"""
<p class="eyebrow">{esc(hero_copy["eyebrow"])}</p>
<h1>{esc(hero_copy["headline"])}</h1>
{lede_html(hero_copy["support"])}
<div class="hero-actions">
  <a class="btn-slant btn-call" href="tel:{esc(site["phone_tel"])}">{esc(hero_copy["call_label"])}</a>
  <a class="btn-slant btn-quote" href="/contact/">{esc(hero_copy["quote_label"])}</a>
</div>
"""
    frame = picture(
        images["kitchen-tile-backsplash"],
        "(max-width: 899px) 70vw, 320px",
        priority="low",
        class_name="stage-frame-img",
    )
    seal = f"""
<div class="seal">
  <div class="seal-face">
    <p class="seal-kicker">Licensed and insured</p>
    <p class="seal-year">Since {esc(site["established"])}</p>
    <p class="seal-license">CSLB #{esc(license_number(site))}</p>
  </div>
</div>
"""
    aside = f'<figure class="stage-frame">{frame}</figure>{seal}'
    body = f"""
{photo_hero(hero, home_inner, aside=aside, kind="home")}
<section class="section band-white services-band">
  <div class="wrap">
    <div class="services-intro">
      <div>
        <p class="eyebrow">{esc(intro["eyebrow"])}</p>
        <h2>{esc(intro["heading"])}</h2>
      </div>
      <div>
        <p>{esc(intro["text"])}</p>
      </div>
    </div>
    {trust_badges(marketing)}
    <div class="portrait-row" tabindex="0" aria-label="Services">
      {"".join(cards)}
    </div>
  </div>
</section>
{why_section(marketing)}
{process_section(site, marketing)}
<section class="section band-white">
  <div class="wrap split">
    <div>
      <p class="eyebrow">Our story</p>
      <h2>{esc(page["story_heading"])}</h2>
      {paragraphs(page["story"])}
      <p><a class="text-link" href="/about/">Read our story</a></p>
    </div>
    {picture(images["interior-slat-accent-wall"], "(max-width: 800px) 100vw, 560px")}
  </div>
</section>
<section class="photo-band">
  {picture(images["pool-and-stucco-home"], "100vw", class_name="photo-band-img")}
  <div class="photo-band-copy">
    <div class="wrap">
      <h2>Service area</h2>
      <ul class="area-list">{areas}</ul>
    </div>
  </div>
</section>
<section class="section band-paper">
  <div class="wrap">
    <div class="section-head">
      <p class="eyebrow">Reviews</p>
      <h2>What our customers say</h2>
      <p>Reviews from our Google customers. <a href="{esc(site["review_url"])}">Share your experience on Google</a></p>
    </div>
    <div class="reviews">
      {"".join(review_html)}
    </div>
  </div>
</section>
{faq_section(marketing["faq"]["items"], marketing["faq"]["eyebrow"], marketing["faq"]["heading"])}
<section class="section band-white">
  <div class="wrap">
    <div class="section-head">
      <p class="eyebrow">Gallery</p>
      <h2>Project photos</h2>
      <a class="text-link" href="/gallery/">View the gallery</a>
    </div>
    <ul class="thumb-grid">{thumbs}</ul>
  </div>
</section>
<section class="section band-paper" id="quote">
  <div class="wrap split">
    {picture(images["kitchen-gray-cabinets-shelves"], "(max-width: 800px) 100vw, 520px")}
    <div>
      <p class="eyebrow">Quote</p>
      <h2>Request a quote</h2>
      <p>Tell us about the electrical or remodeling work, or call <a href="tel:{esc(site["phone_tel"])}">{esc(site["phone_display"])}</a>.</p>
      {form(site, "/", "home-quote")}
    </div>
  </div>
</section>
"""
    return body


def photo_hero(image, inner, aside="", kind="page"):
    aside_html = f'<div class="stage-aside">{aside}</div>' if aside else ""
    return f"""
<header class="stage stage-{kind}">
  {picture(image, "100vw", eager=True, class_name="stage-photo")}
  <div class="stage-shade" aria-hidden="true"></div>
  <div class="wrap stage-grid">
    <div class="stage-copy">
      {inner}
    </div>
    {aside_html}
  </div>
  <div class="stage-slant" aria-hidden="true"></div>
</header>
"""


def render_service(site, page, pages, images, marketing):
    hero = images[page.get("hero") or page["image"]]
    photo = images[page["image"]]
    sections = []
    for section in page["sections"]:
        sections.append(f"""
<section>
  <h2>{esc(section["h2"])}</h2>
  {paragraphs(section.get("paragraphs"))}
  {bullets(section.get("bullets"))}
  {paragraphs(section.get("closing"))}
</section>
""")
    related = [
        item for item in pages
        if item.get("group") == page.get("group") and item["id"] != page["id"]
    ]
    card_copy = marketing.get("cards", {})
    related_html = "\n".join(
        portrait_card(
            item,
            images[item.get("hero") or item["image"]],
            card_copy.get(item["id"], item["card"]),
            "(max-width: 700px) 78vw, 280px",
        )
        for item in related
    )
    extra = marketing["services"].get(page["id"], {})
    benefits = ""
    if extra.get("benefits"):
        benefits = f"""
<section>
  <h2>{esc(extra["benefits_heading"])}</h2>
  {bullets(extra["benefits"])}
</section>
"""
    safety = ""
    if page.get("group") == "electrical":
        safety = f"<section><h2>{esc(marketing['safety']['heading'])}</h2><p>{esc(marketing['safety']['text'])}</p></section>"
    service_faq = ""
    if extra.get("faq"):
        service_faq = faq_section(extra["faq"], "Questions", page["nav"])
    before_after = ""
    if page["id"] == "home-renovations":
        shot = images["renovation-render-interior"]
        before_after = f"""
<figure class="before-after">
  {picture(shot, "(max-width: 900px) 100vw, 1100px", class_name="natural-photo")}
  <figcaption>{esc(shot["alt"])}</figcaption>
</figure>
"""
    inner = f"""
<p class="eyebrow"><a href="/">Home</a> <span aria-hidden="true">·</span> {esc(page["group"].title())}</p>
<h1>{esc(page["h1"])}</h1>
{lede_html(extra.get("hero_lede") or page["lede"])}
<div class="hero-actions">
  <a class="btn-slant btn-call" href="tel:{esc(site["phone_tel"])}">Call {esc(site["phone_display"])}</a>
  <a class="btn-slant btn-quote" href="/contact/">Get a quote</a>
</div>
"""
    return f"""
<article class="page">
  {photo_hero(hero, inner)}
  <div class="wrap trust-band">{trust_badges(marketing)}</div>
  <div class="wrap page-grid">
    <div class="prose">
      {"".join(sections)}
      {benefits}
      {safety}
      {before_after}
    </div>
    <aside class="page-photo">
      {picture(photo, "(max-width: 800px) 100vw, 420px")}
    </aside>
  </div>
    <div class="wrap related">
    <p class="eyebrow">More services</p>
    <h2>Related services</h2>
    <div class="portrait-row compact" tabindex="0" aria-label="Related services">{related_html}</div>
  </div>
  {process_section(site, marketing)}
  {service_faq}
</article>
{cta(site, marketing)}
"""


def render_about(site, page, images, marketing):
    hero = images[page.get("hero") or page["image"]]
    services = bullets(page["services"])
    paragraphs_html = page["paragraphs"]
    inner = f"""
<p class="eyebrow">Established {esc(site["established"])} · License # {esc(site["license"])}</p>
<h1>{esc(page["h1"])}</h1>
{lede_html("“" + site["tagline"] + "”")}
<div class="hero-actions">
  <a class="btn-slant btn-call" href="tel:{esc(site["phone_tel"])}">Call {esc(site["phone_display"])}</a>
  <a class="btn-slant btn-quote" href="/contact/">Get a quote</a>
</div>
"""
    return f"""
<article class="page">
  {photo_hero(hero, inner)}
  <div class="wrap page-grid">
    <div class="prose">
      {paragraphs(paragraphs_html[:2])}
      <blockquote class="mission"><p>{esc(site["mission"])}</p></blockquote>
    </div>
    <aside class="page-photo">
      {picture(images["pool-and-stucco-home"], "(max-width: 800px) 100vw, 480px")}
    </aside>
  </div>
  <div class="wrap page-grid">
    <aside class="page-photo">
      {picture(images["kitchen-pass-through-chandelier"], "(max-width: 800px) 100vw, 480px")}
    </aside>
    <div class="prose">
      {paragraphs(paragraphs_html[2:])}
      <p>License # {esc(site["license"])}.</p>
    </div>
  </div>
  <div class="wrap prose">
    <h2>Our services</h2>
    <p>{esc(page["services_intro"])}</p>
    <div class="service-columns">{services}</div>
  </div>
</article>
{cta(site, marketing)}
"""


def render_gallery(page, images):
    hero = images[page.get("hero") or "desert-home-tile-roof"]
    natural = []
    figures = []
    for image in images.values():
        if image.get("role") in ("logo", "archive"):
            continue
        if image.get("uncropped"):
            natural.append(f"""
<li class="full">
  <figure>
    {picture(image, "(max-width: 900px) 100vw, 1100px", class_name="natural-photo")}
    <figcaption>{esc(image["alt"])}</figcaption>
  </figure>
</li>
""")
            continue
        figures.append(f"""
<li>
  <figure>
    {picture(image, "(max-width: 700px) 100vw, 320px")}
    <figcaption>{esc(image["alt"])}</figcaption>
  </figure>
</li>
""")
    inner = f"""
<h1>{esc(page["h1"])}</h1>
{lede_html(page["intro"])}
"""
    return f"""
<article class="page">
  {photo_hero(hero, inner)}
  <div class="wrap">
    <ul class="gallery">{"".join(figures)}{"".join(natural)}</ul>
  </div>
</article>
"""


def render_contact(site, page, images):
    address = site["address"]
    payments = ", ".join(esc(item) for item in site["payment_methods"])
    areas = "\n".join(
        f'<li><a href="/service-areas/{esc(area_slug(name))}/">{esc(name)}</a></li>'
        for name in site["service_areas"]
    )
    hero = images[page.get("hero") or "desert-home-tile-roof"]
    inner = f"""
<h1>{esc(page["h1"])}</h1>
{lede_html(page["intro"])}
<div class="hero-actions"><a class="btn-slant btn-call" href="tel:{esc(site["phone_tel"])}">Call {esc(site["phone_display"])}</a></div>
"""
    return f"""
<article class="page">
  {photo_hero(hero, inner)}
  <div class="wrap contact-grid">
    <section class="contact-card" aria-labelledby="contact-info">
      <h2 id="contact-info">Contact info</h2>
      <p><strong>{esc(site["name"])}</strong></p>
      <address>
        {esc(address["street"])}<br>
        {esc(address["city"])}, {esc(address["region"])} {esc(address["postal_code"])}
      </address>
      <p>Contact number: <a href="tel:{esc(site["phone_tel"])}">{esc(site["phone_display"])}</a></p>
      <p>License # {esc(site["license"])}</p>
      <h3>Payment methods</h3>
      <p>{payments}</p>
      <h3>Hours of operation</h3>
      {hours_list(site)}
      <h3>Service area</h3>
      <ul class="area-list">{areas}</ul>
    </section>
    <section id="quote">
      <h2>Contact us</h2>
      {form(site, "/contact", "contact")}
    </section>
  </div>
  <div class="wrap map-wrap">
    <h2>Map</h2>
    <iframe class="map" title="Map showing MB Construction and Electric at 79887 Memorial Place, La Quinta, California" src="{esc(site["map_embed"])}" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>
    <p><a href="{esc(site["map_link"])}">Open in Google Maps</a></p>
  </div>
</article>
"""


def render_privacy(page, privacy, site):
    sections = []
    for section in privacy["sections"]:
        text = section["paragraphs"]
        if section["h2"] == "Contact":
            text = [
                f'If The Customer has any questions or concerns regarding this Privacy Policy or our privacy practices, please contact us at {site["phone_display"]}.'
            ]
        sections.append(f"""
<section>
  <h2>{esc(section["h2"])}</h2>
  {paragraphs(text)}
  {bullets(section.get("bullets"))}
</section>
""")
    return f"""
<article class="page">
  <header class="page-hero">
    <div class="wrap">
      <h1>{esc(page["h1"])}</h1>
    </div>
  </header>
  <div class="wrap prose privacy">
    <p>{esc(privacy["intro"])}</p>
    <p>{esc(privacy["agreement"])}</p>
    {"".join(sections)}
  </div>
</article>
"""


def render_not_found(site):
    page = {
        "path": "/404.html",
        "title": "Page not found | MB Construction and Electric",
        "description": "That page is not on the MB Construction and Electric website. Call (760) 227-5499 or return to the homepage.",
        "robots": "noindex, follow",
        "crumbs": [
            {"name": "Home", "path": "/"},
            {"name": "Page not found", "path": "/404.html"},
        ],
    }
    body = f"""
<article class="page">
  <header class="page-hero">
    <div class="wrap">
      <h1>Page not found</h1>
      <p class="lede">That address is not on this site. Call <a href="tel:{esc(site["phone_tel"])}">{esc(site["phone_display"])}</a> or go back to the <a href="/">homepage</a>.</p>
    </div>
  </header>
</article>
"""
    return page, body


def write_page(path, html_text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html_text, encoding="utf-8")


def output_path(public, url_path):
    if url_path == "/":
        return public / "index.html"
    if url_path.endswith(".html"):
        return public / url_path.lstrip("/")
    return public / url_path.lstrip("/") / "index.html"


def service_link_list(pages):
    items = [page for page in pages if page.get("template") == "service"]
    return "\n".join(
        f'<li><a href="{esc(href(page["path"]))}">{esc(page["nav"])}</a></li>' for page in items
    )


def nearby_links(names):
    return "\n".join(
        f'<li><a href="/service-areas/{esc(area_slug(name))}/">{esc(name)}</a></li>'
        for name in names
    )


def render_area_index(site, areas, images, marketing):
    index = areas["index"]
    hero = images[index["hero"]]
    cards = []
    for city in areas["cities"]:
        photo = images[city["hero"]]
        cards.append(f"""
<li>
  <a href="/service-areas/{esc(city["slug"])}/">
    {picture(photo, "(max-width: 700px) 100vw, 280px")}
    <div>
      <h2>{esc(city["name"])}</h2>
      <p>{esc(city["blurb"])}</p>
    </div>
  </a>
</li>
""")
    inner = f"""
<p class="eyebrow">Where we work</p>
<h1>{esc(index["h1"])}</h1>
{lede_html(index["lede"])}
<div class="hero-actions">
  <a class="btn-slant btn-call" href="tel:{esc(site["phone_tel"])}">Call {esc(site["phone_display"])}</a>
  <a class="btn-slant btn-quote" href="/contact/">Get a quote</a>
</div>
"""
    return f"""
<article class="page">
  {photo_hero(hero, inner)}
  <div class="wrap prose">
    {paragraphs(index["paragraphs"])}
    <ul class="area-index">{"".join(cards)}</ul>
  </div>
  {faq_section(index["faq"], "Questions", "Questions about the service area")}
</article>
{cta(site, marketing)}
"""


def render_city(site, city, pages, images, marketing):
    hero = images[city["hero"]]
    side = images[city["side"]]
    inner = f"""
<p class="eyebrow"><a href="/service-areas/">Service areas</a> <span aria-hidden="true">·</span> {esc(city["name"])}</p>
<h1>{esc(city["h1"])}</h1>
{lede_html(city["lede"])}
<div class="hero-actions">
  <a class="btn-slant btn-call" href="tel:{esc(site["phone_tel"])}">Call {esc(site["phone_display"])}</a>
  <a class="btn-slant btn-quote" href="/contact/">Get a quote</a>
</div>
"""
    return f"""
<article class="page">
  {photo_hero(hero, inner)}
  <div class="wrap trust-band">{trust_badges(marketing)}</div>
  <div class="wrap page-grid">
    <div class="prose">
      {paragraphs(city["paragraphs"])}
      <h2>Services in {esc(city["name"])}</h2>
      <p>{esc(city["services_intro"])}</p>
      <ul>
        {service_link_list(pages)}
      </ul>
    </div>
    <aside class="page-photo">
      {picture(side, "(max-width: 800px) 100vw, 420px")}
    </aside>
  </div>
  <div class="wrap nearby-areas">
    <h2>Nearby areas</h2>
    <ul class="area-list">{nearby_links(city["nearby"])}</ul>
  </div>
  {faq_section(city["faq"], "Local questions", f"Questions about work in {city['name']}")}
</article>
{cta(site, marketing, city["name"])}
"""


def sitemap(site, pages):
    host = site["canonical_host"].rstrip("/")
    today = date.today().isoformat()
    urls = [host + "/"]
    for page in pages:
        if page["path"] == "/":
            continue
        urls.append(host + page["path"] + "/")
    body = ["<?xml version=\"1.0\" encoding=\"UTF-8\"?>", '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for url in urls:
        body.append("  <url>")
        body.append(f"    <loc>{esc(url)}</loc>")
        body.append(f"    <lastmod>{today}</lastmod>")
        body.append("  </url>")
    body.append("</urlset>")
    return "\n".join(body) + "\n"


def audit_public(public):
    email_re = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
    linked = set()
    for path in public.rglob("*"):
        if not path.is_file() or path.suffix not in {".html", ".xml", ".txt", ".css", ".js", ".json"}:
            continue
        text = path.read_text(encoding="utf-8")
        if email_re.search(text) or "mailto:" in text.lower():
            raise SystemExit(f"Email leaked in {path}")
        if path.suffix != ".html":
            continue
        h1_count = len(re.findall(r"<h1\b", text))
        if h1_count != 1:
            raise SystemExit(f"{path} has {h1_count} h1 elements")
        if re.search(r"<img\b(?![^>]*\balt=\"[^\"]+\")", text):
            raise SystemExit(f"Image missing descriptive alt in {path}")
        blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', text, re.S)
        if not blocks:
            raise SystemExit(f"Missing JSON-LD in {path}")
        for block in blocks:
            data = json.loads(block)
            types = []

            def walk(node):
                if isinstance(node, dict):
                    if "email" in node:
                        raise SystemExit(f"JSON-LD email in {path}")
                    if "@type" in node:
                        kind = node["@type"]
                        types.extend(kind if isinstance(kind, list) else [kind])
                    for value in node.values():
                        walk(value)
                elif isinstance(node, list):
                    for value in node:
                        walk(value)

            walk(data)
            if "HomeAndConstructionBusiness" not in types:
                raise SystemExit(f"Missing local business schema in {path}")
            if "WebSite" not in types:
                raise SystemExit(f"Missing WebSite schema in {path}")
        for href in re.findall(r'(?:href|src)="(/[^"]*)"', text):
            bare = href.split("#", 1)[0]
            if not bare or bare.startswith("/v1/"):
                continue
            linked.add(bare)
    for href in sorted(linked):
        target = public / href.lstrip("/")
        if href.endswith("/"):
            target = public / href.strip("/") / "index.html"
        if not target.is_file():
            raise SystemExit(f"Broken internal link {href}")


def robots(site):
    host = site["canonical_host"].rstrip("/")
    agents = [
        "*",
        "GPTBot",
        "OAI-SearchBot",
        "ChatGPT-User",
        "Google-Extended",
        "GoogleOther",
        "Applebot",
        "Applebot-Extended",
        "anthropic-ai",
        "ClaudeBot",
        "Claude-SearchBot",
        "PerplexityBot",
        "Amazonbot",
        "Bytespider",
        "CCBot",
        "meta-externalagent",
    ]
    blocks = []
    for agent in agents:
        blocks.append(f"User-agent: {agent}\nAllow: /\n")
    return "\n".join(blocks) + f"\nSitemap: {host}/sitemap.xml\n"


def llms_txt(site, pages):
    host = site["canonical_host"].rstrip("/")
    address = site["address"]
    services = [page for page in pages if page.get("template") == "service"]
    lines = [
        f"# {site['name']}",
        "",
        "MB Construction and Electric is an electrician and general contractor based in La Quinta, California. The company has worked with homeowners since 1978 and is licensed and insured. The California contractor license number is CSLB #352894.",
        "",
        f"Phone: {site['phone_display']}",
        "Hours: Monday through Friday, 8:00 a.m. to 5:00 p.m. Closed Saturday and Sunday.",
        f"Address: {address['street']}, {address['city']}, {address['region']} {address['postal_code']}",
        "",
        "Use the phone number or the contact form.",
        "",
        "## Services",
    ]
    for page in services:
        lines.append(f"- {page['nav']}: {host}{href(page['path'])} — {page['description']}")
    lines.extend(["", "## Service areas"])
    for name in site["service_areas"]:
        lines.append(f"- {name}: {host}/service-areas/{area_slug(name)}/")
    lines.extend([
        "",
        "## Pages",
        f"- Home: {host}/",
        f"- About: {host}/about/",
        f"- Contact: {host}/contact/",
        f"- Gallery: {host}/gallery/",
        f"- Service areas: {host}/service-areas/",
        "",
    ])
    return "\n".join(lines)


def main():
    site = load_json(DATA)
    content = load_json(CONTENT / "pages.json")
    reviews = load_json(CONTENT / "reviews.json")
    privacy = load_json(CONTENT / "privacy.json")
    marketing = load_json(CONTENT / "marketing.json")
    areas = load_json(CONTENT / "areas.json")
    images = image_lookup(load_json(CONTENT / "images.json"))
    pages = content["pages"]
    home = content["home"]
    city_names = [city["name"] for city in areas["cities"]]
    if city_names != site["service_areas"]:
        raise SystemExit("Service area pages do not match the profile list")
    for city in areas["cities"]:
        if area_slug(city["name"]) != city["slug"]:
            raise SystemExit(f"Slug mismatch for {city['name']}")
        count = len(re.findall(r"[A-Za-z0-9']+", " ".join(city["paragraphs"])))
        if not 300 <= count <= 450:
            raise SystemExit(f"{city['name']} copy is {count} words")
        if city["hero"] not in images or city["side"] not in images:
            raise SystemExit(f"Missing image for {city['name']}")
    shared = {}
    for city in areas["cities"]:
        for sentence in re.split(r"(?<=[.!?])\s+", " ".join(city["paragraphs"])):
            sentence = sentence.strip()
            if len(sentence) < 40:
                continue
            shared.setdefault(sentence, set()).add(city["name"])
    repeated = [names for names in shared.values() if len(names) > 1]
    if repeated:
        raise SystemExit("City pages repeat the same sentence")
    year = date.today().year

    if PUBLIC.exists():
        shutil.rmtree(PUBLIC)
    PUBLIC.mkdir()
    shutil.copytree(ASSETS, PUBLIC / "assets" / "images")
    shutil.copy(SRC / "site.css", PUBLIC / "assets" / "site.css")
    shutil.copy(SRC / "site.js", PUBLIC / "assets" / "site.js")
    shutil.copy(SRC / ".htaccess", PUBLIC / ".htaccess")

    hero = images[home["hero_image"]]
    home_page = {
        "path": "/",
        "title": home["title"],
        "description": home["description"],
        "faqs": marketing["faq"]["items"],
    }
    home_html = layout(
        site,
        home_page,
        pages,
        render_home(site, home, pages, images, reviews, marketing),
        hero,
        year,
    )
    write_page(PUBLIC / "index.html", home_html)

    for page in pages:
        if page["template"] == "service":
            body = render_service(site, page, pages, images, marketing)
        elif page["template"] == "about":
            body = render_about(site, page, images, marketing)
        elif page["template"] == "gallery":
            body = render_gallery(page, images)
        elif page["template"] == "contact":
            body = render_contact(site, page, images)
        elif page["template"] == "privacy":
            body = render_privacy(page, privacy, site)
        else:
            raise SystemExit(f"Unknown template {page['template']}")
        hero_key = page.get("hero") or page.get("image") or "desert-home-tile-roof"
        hero_image = images[hero_key]
        service = None
        faqs = []
        crumbs = [{"name": "Home", "path": "/"}, {"name": page["nav"], "path": page["path"]}]
        if page["template"] == "service":
            faqs = marketing["services"].get(page["id"], {}).get("faq") or []
            service = {"name": page["nav"], "serviceType": page["nav"]}
        meta = {
            "path": page["path"],
            "title": page["title"],
            "description": page["description"],
            "crumbs": crumbs,
            "faqs": faqs,
            "service": service,
        }
        write_page(output_path(PUBLIC, page["path"]), layout(site, meta, pages, body, hero_image, year))

    index_meta = {
        "path": "/service-areas",
        "title": areas["index"]["title"],
        "description": areas["index"]["description"],
        "crumbs": [
            {"name": "Home", "path": "/"},
            {"name": "Service areas", "path": "/service-areas"},
        ],
        "faqs": areas["index"]["faq"],
    }
    index_hero = images[areas["index"]["hero"]]
    write_page(
        output_path(PUBLIC, "/service-areas"),
        layout(
            site,
            index_meta,
            pages,
            render_area_index(site, areas, images, marketing),
            index_hero,
            year,
        ),
    )
    area_pages = [index_meta]
    for city in areas["cities"]:
        city_path = f"/service-areas/{city['slug']}"
        city_meta = {
            "path": city_path,
            "title": city["title"],
            "description": city["description"],
            "crumbs": [
                {"name": "Home", "path": "/"},
                {"name": "Service areas", "path": "/service-areas"},
                {"name": city["name"], "path": city_path},
            ],
            "faqs": city["faq"],
            "service": {
                "name": f"Electrical and general contracting in {city['name']}",
                "serviceType": "Electrical and general contracting",
                "area": city["name"],
            },
        }
        city_hero = images[city["hero"]]
        write_page(
            output_path(PUBLIC, city_meta["path"]),
            layout(
                site,
                city_meta,
                pages,
                render_city(site, city, pages, images, marketing),
                city_hero,
                year,
            ),
        )
        area_pages.append(city_meta)

    missing, missing_body = render_not_found(site)
    write_page(PUBLIC / "404.html", layout(site, missing, pages, missing_body, hero, year))

    (PUBLIC / "sitemap.xml").write_text(sitemap(site, [home_page] + pages + area_pages), encoding="utf-8")
    (PUBLIC / "robots.txt").write_text(robots(site), encoding="utf-8")
    (PUBLIC / "llms.txt").write_text(llms_txt(site, pages), encoding="utf-8")

    forbidden = "578-8212"
    blob = "\n".join(path.read_text(encoding="utf-8") for path in PUBLIC.rglob("*") if path.suffix in {".html", ".xml", ".txt", ".css", ".js", ".json"})
    if forbidden in blob or "5788212" in blob:
        raise SystemExit("Primary phone leaked into public output")
    if "cdn-website.com" in blob:
        raise SystemExit("CDN reference leaked into public output")
    if "goproremodel" in blob.lower() or "mailto:" in blob.lower():
        raise SystemExit("Email address leaked into public output")
    audit_public(PUBLIC)
    print(f"Wrote {PUBLIC}")


if __name__ == "__main__":
    main()
