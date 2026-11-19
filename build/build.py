#!/usr/bin/env python3
"""Static site generator. Standard library only."""

import html
import json
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


def bullets(items):
    if not items:
        return ""
    lis = "\n".join(f"<li>{esc(item)}</li>" for item in items)
    return f"<ul>\n{lis}\n</ul>"


def image_lookup(images):
    return {item["id"]: item for item in images}


def picture(image, sizes, eager=False, class_name=""):
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


def json_ld(site, page, image):
    host = site["canonical_host"].rstrip("/")
    address = site["address"]
    areas = []
    for name in site["service_areas"]:
        if name.endswith("County"):
            areas.append({"@type": "AdministrativeArea", "name": name})
        else:
            areas.append({
                "@type": "City",
                "name": name,
                "containedInPlace": {"@type": "State", "name": "California"},
            })
    hours = []
    for row in site["hours"]:
        hours.append({
            "@type": "OpeningHoursSpecification",
            "dayOfWeek": row["day"],
            "opens": row["opens"],
            "closes": row["closes"],
        })
    image_url = host + "/assets/images/" + image["variants"][-1]["file"]
    logo_url = host + "/assets/images/logo.png"
    data = {
        "@context": "https://schema.org",
        "@type": ["Electrician", "GeneralContractor"],
        "@id": host + "/#business",
        "name": site["name"],
        "url": host + "/",
        "image": image_url,
        "logo": logo_url,
        "telephone": site["phone_schema"],
        "email": site["email"],
        "description": page["description"],
        "slogan": site["tagline"],
        "foundingDate": site["established"],
        "priceRange": None,
        "address": {
            "@type": "PostalAddress",
            "streetAddress": address["street"],
            "addressLocality": address["city"],
            "addressRegion": address["region"],
            "postalCode": address["postal_code"],
            "addressCountry": address["country"],
        },
        "geo": {
            "@type": "GeoCoordinates",
            "latitude": site["geo"]["latitude"],
            "longitude": site["geo"]["longitude"],
        },
        "areaServed": areas,
        "openingHoursSpecification": hours,
        "paymentAccepted": ", ".join(site["payment_methods"]),
        "identifier": {
            "@type": "PropertyValue",
            "name": "CSLB license",
            "value": site["license"],
        },
        "hasMap": site["map_link"],
        "sameAs": site["same_as"],
    }
    data.pop("priceRange", None)
    return json.dumps(data, ensure_ascii=False, indent=2)


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

    def group(label, items):
        links = "\n".join(f"<li>{link(item['path'], item['nav'])}</li>" for item in items)
        return (
            f'<li class="nav-group"><details>'
            f"<summary>{esc(label)}</summary><ul>{links}</ul></details></li>"
        )

    home_current = ' aria-current="page"' if current_path == "/" else ""
    about = next(p for p in pages if p["id"] == "about")
    gallery = next(p for p in pages if p["id"] == "gallery")
    contact = next(p for p in pages if p["id"] == "contact")
    return f"""
<nav class="site-nav" aria-label="Primary">
  <input class="nav-check" id="nav-check" type="checkbox">
  <label class="nav-toggle" for="nav-check">Menu</label>
  <ul class="nav-links" id="nav-links">
    <li><a href="/"{home_current}>Home</a></li>
    {group("Electrical", electrical)}
    {group("Construction", construction)}
    <li>{link(about["path"], "About")}</li>
    <li>{link(gallery["path"], "Gallery")}</li>
    <li>{link(contact["path"], "Contact")}</li>
  </ul>
</nav>
"""


def header(site, pages, current_path):
    return f"""
<a class="skip" href="#main">Skip to content</a>
<header class="site-header">
  <div class="wrap header-bar">
    <a class="brand" href="/">
      <img src="/assets/images/logo.png" width="275" height="275" alt="MB Construction and Electric">
    </a>
    {nav(site, pages, current_path)}
    <a class="phone-button" href="tel:{esc(site["phone_tel"])}">
      <span class="phone-kicker">Call</span>
      <span class="phone-number">{esc(site["phone_display"])}</span>
    </a>
  </div>
</header>
"""


def footer(site, pages, year):
    simple = [
        ("/", "Home"),
        ("/about", "About"),
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
    areas = ", ".join(esc(area) for area in site["service_areas"])
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
      <p><a href="tel:{esc(site["phone_tel"])}">{esc(site["phone_display"])}</a><br>
      <a href="mailto:{esc(site["email"])}">{esc(site["email"])}</a></p>
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
      <p class="areas"><span class="label">Service area.</span> {areas}.</p>
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


def cta(site):
    return f"""
<aside class="cta-band">
  <div class="wrap cta-inner">
    <div>
      <h2>Talk through the project</h2>
      <p>Call {esc(site["name"])} in {esc(site["address"]["city"])}, {esc(site["address"]["region"])}.</p>
    </div>
    <div class="cta-actions">
      <a class="button" href="tel:{esc(site["phone_tel"])}">Call {esc(site["phone_display"])}</a>
      <a class="button button-quiet" href="/contact/">Request a quote</a>
    </div>
  </div>
</aside>
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


def layout(site, page, pages, body, hero_image, year, extra_head=""):
    title = page["title"]
    description = page["description"]
    url = canonical(site, page["path"])
    og_image = site["canonical_host"].rstrip("/") + "/assets/images/" + hero_image["variants"][-1]["file"]
    ld = json_ld(site, page, hero_image)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(description)}">
  <link rel="canonical" href="{esc(url)}">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="{esc(site["name"])}">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(description)}">
  <meta property="og:url" content="{esc(url)}">
  <meta property="og:image" content="{esc(og_image)}">
  <meta property="og:locale" content="{esc(site["locale"])}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{esc(title)}">
  <meta name="twitter:description" content="{esc(description)}">
  <meta name="twitter:image" content="{esc(og_image)}">
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


def render_home(site, page, pages, images, reviews):
    hero = images[page["hero_image"]]
    cards = []
    for item in pages:
        if item.get("template") != "service":
            continue
        photo = images[item.get("hero") or item["image"]]
        eager = len(cards) < 3
        cards.append(f"""
<article class="service-card">
  <a href="{esc(href(item["path"]))}">
    {picture(photo, "(max-width: 700px) 100vw, 360px", eager=eager)}
    <div>
      <h3>{esc(item["nav"])}</h3>
      <p>{esc(item["card"])}</p>
      <span class="text-link">View service</span>
    </div>
  </a>
</article>
""")
    trust_photos = ["pool-and-stucco-home", "labeled-breaker-panel", "kitchen-range-hood"]
    trust = "\n".join(
        "<li>"
        + picture(images[photo_id], "(max-width: 700px) 100vw, 380px")
        + f"<div><h3>{esc(item['title'])}</h3><p>{esc(item['text'])}</p></div></li>"
        for item, photo_id in zip(page["trust"], trust_photos)
    )
    areas = "\n".join(f"<li>{esc(area)}</li>" for area in site["service_areas"])
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
    home_inner = f"""
<p class="eyebrow">{esc(page["eyebrow"])}</p>
<h1>{esc(page["h1"])}</h1>
<p class="tagline">“{esc(site["tagline"])}”</p>
<p class="lede">{esc(page["intro"])}</p>
<div class="hero-actions">
  <a class="button" href="tel:{esc(site["phone_tel"])}">Call {esc(site["phone_display"])}</a>
  <a class="button button-quiet" href="/contact/">Request a quote</a>
</div>
<p class="license">License # {esc(site["license"])} · Established {esc(site["established"])} · Licensed and insured</p>
"""
    body = f"""
{photo_hero(hero, home_inner)}
<section class="trust-bar" aria-label="Business facts">
  <div class="wrap">
    <ul>
      <li>Licensed and insured</li>
      <li>CSLB #{esc(site["license"])}</li>
      <li>Since {esc(site["established"])}</li>
      <li>{esc(" · ".join(site["service_areas"]))}</li>
      <li>{esc(" · ".join(site["payment_methods"]))}</li>
    </ul>
  </div>
</section>
<section class="section tight">
  <div class="wrap">
    <div class="section-head">
      <h2>{esc(page["services_heading"])}</h2>
      <p>{esc(page["services_intro"])}</p>
    </div>
    <div class="service-grid">
      {"".join(cards)}
    </div>
  </div>
</section>
<section class="section tight">
  <div class="wrap split">
    <div>
      <h2>{esc(page["story_heading"])}</h2>
      {paragraphs(page["story"])}
      <p><a class="text-link" href="/about/">Read our story</a></p>
    </div>
    {picture(images["interior-slat-accent-wall"], "(max-width: 800px) 100vw, 560px")}
  </div>
</section>
<section class="section tight">
  <div class="wrap">
    <h2>{esc(page["trust_heading"])}</h2>
    <ul class="trust-grid">{trust}</ul>
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
<section class="section tight">
  <div class="wrap">
    <div class="section-head">
      <h2>What our customers say</h2>
      <p>Google reviews from the previous website. <a href="{esc(site["review_url"])}">Share your experience on Google</a></p>
    </div>
    <div class="reviews">
      {"".join(review_html)}
    </div>
  </div>
</section>
<section class="section tight">
  <div class="wrap">
    <div class="section-head">
      <h2>Project photos</h2>
      <a class="text-link" href="/gallery/">View the gallery</a>
    </div>
    <ul class="thumb-grid">{thumbs}</ul>
  </div>
</section>
<section class="section tight" id="quote">
  <div class="wrap split">
    {picture(images["kitchen-gray-cabinets-shelves"], "(max-width: 800px) 100vw, 520px")}
    <div>
      <h2>Request a quote</h2>
      <p>Tell us about the electrical or remodeling work, or call <a href="tel:{esc(site["phone_tel"])}">{esc(site["phone_display"])}</a>.</p>
      {form(site, "/", "home-quote")}
    </div>
  </div>
</section>
"""
    return body


def photo_hero(image, inner):
    return f"""
<header class="photo-hero">
  {picture(image, "100vw", eager=True, class_name="photo-hero-img")}
  <div class="photo-hero-copy">
    <div class="wrap">
      {inner}
    </div>
  </div>
</header>
"""


def render_service(site, page, pages, images):
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
    related_html = "\n".join(
        f"""<article class="service-card"><a href="{esc(href(item["path"]))}">
          {picture(images[item.get("hero") or item["image"]], "(max-width: 700px) 100vw, 280px")}
          <div><h3>{esc(item["nav"])}</h3></div>
        </a></article>"""
        for item in related
    )
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
<p class="eyebrow"><a href="/">Home</a> · {esc(page["group"].title())}</p>
<h1>{esc(page["h1"])}</h1>
<p class="lede">{esc(page["lede"])}</p>
<p class="hero-actions"><a class="button" href="tel:{esc(site["phone_tel"])}">Call {esc(site["phone_display"])}</a>
<a class="button button-quiet" href="/contact/">Request a quote</a></p>
"""
    return f"""
<article class="page">
  {photo_hero(hero, inner)}
  <div class="wrap page-grid">
    <div class="prose">
      {"".join(sections)}
      {before_after}
    </div>
    <aside class="page-photo">
      {picture(photo, "(max-width: 800px) 100vw, 420px")}
    </aside>
  </div>
  <div class="wrap related">
    <h2>Related services</h2>
    <div class="service-grid">{related_html}</div>
  </div>
</article>
{cta(site)}
"""


def render_about(site, page, images):
    hero = images[page.get("hero") or page["image"]]
    services = bullets(page["services"])
    paragraphs_html = page["paragraphs"]
    inner = f"""
<p class="eyebrow">Established {esc(site["established"])} · License # {esc(site["license"])}</p>
<h1>{esc(page["h1"])}</h1>
<p class="lede">“{esc(site["tagline"])}”</p>
<p class="hero-actions"><a class="button" href="tel:{esc(site["phone_tel"])}">Call {esc(site["phone_display"])}</a>
<a class="button button-quiet" href="/contact/">Request a quote</a></p>
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
{cta(site)}
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
<p class="lede">{esc(page["intro"])}</p>
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
    areas = "\n".join(f"<li>{esc(area)}</li>" for area in site["service_areas"])
    hero = images[page.get("hero") or "desert-home-tile-roof"]
    inner = f"""
<h1>{esc(page["h1"])}</h1>
<p class="lede">{esc(page["intro"])}</p>
<p class="hero-actions"><a class="button" href="tel:{esc(site["phone_tel"])}">Call {esc(site["phone_display"])}</a></p>
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
      <p>Email: <a href="mailto:{esc(site["email"])}">{esc(site["email"])}</a></p>
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


def robots(site):
    host = site["canonical_host"].rstrip("/")
    return f"User-agent: *\nAllow: /\n\nSitemap: {host}/sitemap.xml\n"


def main():
    site = load_json(DATA)
    content = load_json(CONTENT / "pages.json")
    reviews = load_json(CONTENT / "reviews.json")
    privacy = load_json(CONTENT / "privacy.json")
    images = image_lookup(load_json(CONTENT / "images.json"))
    pages = content["pages"]
    home = content["home"]
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
    }
    home_html = layout(
        site,
        home_page,
        pages,
        render_home(site, home, pages, images, reviews),
        hero,
        year,
        extra_head=preload_image(hero, "100vw"),
    )
    write_page(PUBLIC / "index.html", home_html)

    for page in pages:
        if page["template"] == "service":
            body = render_service(site, page, pages, images)
        elif page["template"] == "about":
            body = render_about(site, page, images)
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
        meta = {"path": page["path"], "title": page["title"], "description": page["description"]}
        write_page(output_path(PUBLIC, page["path"]), layout(site, meta, pages, body, hero_image, year))

    missing, missing_body = render_not_found(site)
    write_page(PUBLIC / "404.html", layout(site, missing, pages, missing_body, hero, year))

    (PUBLIC / "sitemap.xml").write_text(sitemap(site, [home_page] + pages), encoding="utf-8")
    (PUBLIC / "robots.txt").write_text(robots(site), encoding="utf-8")

    forbidden = "578-8212"
    blob = "\n".join(path.read_text(encoding="utf-8") for path in PUBLIC.rglob("*") if path.suffix in {".html", ".xml", ".txt", ".css", ".js", ".json"})
    if forbidden in blob or "5788212" in blob:
        raise SystemExit("Primary phone leaked into public output")
    if "cdn-website.com" in blob:
        raise SystemExit("CDN reference leaked into public output")
    print(f"Wrote {PUBLIC}")


if __name__ == "__main__":
    main()
