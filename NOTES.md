# Notes

## Round 3 new copy for client review

New marketing copy lives in `content/marketing.json`. It does not add ratings, review counts, awards, warranties, financing, 24/7 service, response times, team size, or cities outside the profile list. Existing Google reviews are unchanged. Existing service paragraphs from the previous site were kept, including sentences that already mentioned electrical emergencies.

Hero: “Electrical work and remodeling for homes in the valley.” Support: “MB Construction and Electric has helped homeowners since 1978. We are licensed and insured under CSLB #352894.”

Why choose us:
- Licensed and insured. California contractor license CSLB #352894. We are licensed and insured.
- Working since 1978. Homeowners in La Quinta have called us for electrical work and remodeling since 1978.
- Electrical and construction. Panels, lighting, wiring, kitchens, bathrooms, additions, and design-build work are all part of the same company.
- Set hours you can plan around. The office is open Monday through Friday, 8:00 a.m. to 5:00 p.m. Saturday and Sunday are closed.

How it works:
1. Call or send a note. Phone (760) 227-5499 or use the quote form.
2. Describe the project. Share whether you need electrical work, a remodel, or both, and where the property is.
3. Pick a weekday time. Visits are scheduled Monday through Friday between 8:00 a.m. and 5:00 p.m.
4. Complete the agreed work. We do the electrical or construction work we discussed, with safety in mind on every job.

Safety line on electrical pages: “Safety is not a matter we take lightly. Electrical repairs, panels, circuits, and lighting are handled by a licensed contractor, CSLB #352894.”

FAQ: licensed (CSLB #352894), hours, the profile service-area list, the published electrical and construction services, how to request a quote, and payment methods (cash, money transfers, Zelle, check).

Call-to-action band: “Talk through the next project. Call (760) 227-5499 Monday through Friday, 8:00 a.m. to 5:00 p.m., or send a quote request.”

Per-service benefit lists repeat work already published on those pages (panels, circuits, lighting, fans, EV chargers, generators, detectors, fixtures, wall fixtures, kitchens, bathrooms, and whole-house updates). Each service page also has one or two questions that point back to that same list.

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
