# Notes

## Round 3 new copy for client review

New marketing copy lives in `content/marketing.json`. It does not add ratings, review counts, awards, warranties, financing, 24/7 service, response times, team size, or cities outside the profile list. Existing Google reviews are unchanged. Existing service-page paragraphs from the previous site were kept, including sentences that already mentioned electrical emergencies. The old homepage lines “Reliable Consistency,” “Customer Satisfaction,” and “Fast Responsiveness” were removed.

Hero eyebrow: “Electrician · General contractor · La Quinta.”
Hero headline: “Electrical work and remodeling for the home you live in.”
Hero lede: “Panels, lighting, kitchens, and baths. Licensed and insured since 1978.”
Hero buttons: “Call (760) 227-5499” and “Get a quote.”
Seal on the hero photo: “Licensed and insured / Since 1978 / CSLB #352894.”
Top strip: “La Quinta, CA · (760) 227-5499 · CSLB #352894.”

Services intro heading: “Electrical and remodeling for homes like yours.”
Services intro: “A full panel, a circuit that keeps tripping, a kitchen that no longer works, a bathroom that has to be rebuilt. MB Construction and Electric takes the electrical work and the remodeling. Homeowners have called this company since 1978. The license is CSLB #352894, and the company is licensed and insured.”
Trust lines under that intro: “Licensed and insured · CSLB #352894,” “Working since 1978,” “Monday–Friday, 8:00 a.m.–5:00 p.m.”

Service card blurbs:
- Residential Electrical: “Panel changes, service upgrades, lighting, ceiling fans, breakers, and circuit repair for the house.”
- Electrical Installation: “New circuits, panel upgrades, fans, EV chargers, generators, and smoke detectors.”
- Light Fixtures: “Install a new fixture, repair the one you have, or switch to energy-efficient lighting.”
- Wall Fixtures: “Shelves, cabinets, mirrors, and artwork, mounted for the wall they are going on.”
- Home Renovations: “Kitchens, bathrooms, additions, ADUs, and whole-house updates planned as one job.”
- Kitchen and Bathroom Remodeling: “A kitchen or bathroom remodel, from the first plan through the finished room.”

Service-page hero ledes (the long body copy under them is unchanged):
- Residential: “Panel changes, lighting, ceiling fans, breakers, and circuit repair for the house you live in.”
- Installation: “New circuits, panel upgrades, fans, EV chargers, generators, and detectors, installed by a licensed contractor.”
- Light fixtures: “A new fixture, a repair, or a switch to energy-efficient lighting for a home or a business.”
- Wall fixtures: “Shelves, cabinets, mirrors, and artwork, mounted for the way the wall is built.”
- Home renovations: “Kitchens, bathrooms, additions, and whole-house updates, planned as one job.”
- Kitchen and bathroom: “A kitchen or bathroom remodel, from the first idea through the finished room.”

Why choose us:
- Licensed and insured. The published California contractor license is CSLB #352894. Electrical work and remodeling are done by a company that is licensed and insured.
- Working since 1978. Homeowners in La Quinta have called MB Construction and Electric for electrical work and remodeling since 1978.
- Electrical and the build. A circuit that trips, a panel with no open spaces, a kitchen that does not fit how you cook, a bath that needs new work. Those jobs stay with one company instead of two separate crews.
- The work we list. Wiring, panels, lighting, ceiling fans, generators, EV chargers, kitchens, bathrooms, room and garage additions, ADUs, and design-build projects are on the published service list.
- Hours you can plan around. The office is open Monday through Friday, 8:00 a.m. to 5:00 p.m. Saturday and Sunday are closed, so a visit is set on a weekday.
- A clear way to start. Call (760) 227-5499 or send the quote form. Share the address and whether the job is electrical, a remodel, or both.

How it works:
1. Call or send a note. Phone (760) 227-5499 or use the quote form. Leave your name and the best way to reach you.
2. Describe the project. Say whether you need electrical work, a remodel, or both, and which city the property is in.
3. Pick a weekday time. Visits are scheduled Monday through Friday between 8:00 a.m. and 5:00 p.m.
4. Complete the agreed work. We do the electrical or construction work we discussed, with safety in mind on every job.

Safety line on electrical pages: “Safety is not a matter we take lightly. Electrical repairs, panels, circuits, and lighting are handled by a licensed contractor, CSLB #352894.”

FAQ: licensed (CSLB #352894); weekday hours; weekends closed; the profile city list; electrical and remodeling in one company; the published electrical list (panels, lighting, fans, breakers, water heaters, circuits, EV chargers, generators, detectors); kitchen and bathroom remodeling; what to say when you call; how to ask for a quote; payment methods (cash, money transfers, Zelle, check).

Call-to-action band: “Talk through the next project. Call (760) 227-5499 Monday through Friday, 8:00 a.m. to 5:00 p.m., or send a quote request.” Buttons: “Call (760) 227-5499” and “Get a quote.”

Per-service benefit lists repeat work already published on those pages. Each service page also has one or two questions that point back to that same list.

## Round 2 photos

The client sent 20 project photos. They are the same scenes as the Duda gallery, several of them at a higher resolution (panels, lighting, kitchens, the before-and-after room). Those files replaced the smaller copies. The before-and-after renovation image is shown at its natural aspect, not cropped. A tighter duplicate of the lit recessed downlight was left out of the gallery so the page does not show the same ceiling twice.

## Resolved

Display phone is **(760) 227-5499** everywhere: header, calls to action, footer, contact page, `tel:+17602275499` links, JSON-LD `telephone`, and `data/site.json`.

The profile also has a separate primary phone. The site owner decided that number is not displayed. It is not in `data/site.json` and not in the built pages. The previous Duda site and the profile’s own services copy already used (760) 227-5499.

## Capture

- Live URL `https://mbconstructionandelectric.com/` redirects to the published Duda site `https://mysite.localsplash.com/site/394d9953/`.
- Raw HTML is in `capture/`. A Google reviews widget value and the Duda form recipient fields were redacted before commit. No API key is reused.
- Pages crawled: `/`, `/about`, `/contact`, `/gallery`, `/privacy-policy`, `/home-renovations`, `/kitchen-and-bathroom-remodeling`, `/light-fixtures`, `/wall-fixtures`, `/electrical-installation`, and `/​residential-electrical-services` (a zero-width space is the first character of that slug). The clean path `/residential-electrical-services` 404s on Duda. This rebuild uses the clean path and 301s the zero-width URL, plus `/site/394d9953/...`.
- The Duda Google reviews widget stored 10 reviews. Carlos Sanchez (2024-02-14) had a rating and no written comment, so that review is not shown. The other nine are on the homepage. The widget’s total rating field was empty, so the site does not publish an aggregate score.
- Several Duda image alt texts did not match the photos (they read like automatic captions). Alts on this site describe the actual photos. Two gallery files are computer renderings, not job photographs: `renovation-render-interior` and `lounge-interior-rendering`. They were in the Duda gallery, so they are included and labeled as renderings.
- Template stock hosted on another Duda site id (`f1bb1071`, Adobe Stock) and a shared orange-square graphic were not used.
- Logo file is a raster PNG on a white background, so the header is white. It was not traced into an SVG.

## Copy edits

- Added the missing question mark in “Does your home need safe power… from start to finish?”
- Light-fixture page: “We MB Construction and Electric work quickly” is now “We work quickly…”. The heading “Light Fixture Need s” is now “Light Fixture Needs”.
- Wall-fixture title no longer keeps the stray plus in “La Quinta, CA+”.
- Duplicate “La Quinta” in the service-area list was removed.
- Spacing before punctuation was cleaned. Review wording was not rewritten. Carla Howard’s review still says “florescent,” which is how it was written.

## Open questions for the client

- The street address 79887 Memorial Place, La Quinta, CA 92253 is in the profile and in the old site’s JSON-LD, but it was not printed in the visible Duda page body. Address status in the profile is Hybrid. Confirm the street address should stay visible.
- Email `michael@goproremodel.com` is in the profile and was not shown on the Duda pages. It is on the contact page and in JSON-LD. Confirm it should be public.
- Profile `WebsiteURL` is `https://www.goproremodel.com/`. This rebuild does not link that domain. Confirm the public site should stay on mbconstructionandelectric.com.
- Yelp placement URL is `https://www.yelp.com/biz/mb-construction-palm-springs-4`. The slug says Palm Springs. Confirm it is the right listing.
- The about copy says the company holds multiple licenses covering general contracting, painting, and electrical work. The only published license number is CSLB352894. Send any other numbers that should be displayed.
- Profile company size is 4. That number is not shown on the site.
- Reviews name Michael Berryhill. There is no staff page, because the profile and Duda site do not list a roster.
- Bing Places was still in progress in the profile, so it is not linked.
- Canonical host is `https://www.mbconstructionandelectric.com`. Say if the apex host should be canonical instead.
