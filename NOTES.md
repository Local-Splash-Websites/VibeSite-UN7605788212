# Notes

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
