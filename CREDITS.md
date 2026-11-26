# Credits & licences

The project's own code is MIT-licensed (see `LICENSE`). Everything below is third-party and keeps its own licence.

## Bundled in the wallpaper file

| What | Where | Licence | Notes |
|---|---|---|---|
| [globe.gl](https://github.com/vasturiano/globe.gl) 2.46.2 (bundles [three.js](https://threejs.org), [h3-js](https://github.com/uber/h3-js) and the helvetiker typeface) | `wallpaper/lib/globe.gl.min.js` | MIT (three.js MIT, h3-js Apache-2.0, typeface: MAGENTA Ltd. permissive licence) | © Vasco Asturiano; full texts in [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md) |
| [satellite.js](https://github.com/shashwatak/satellite-js) 5.0.0 | `wallpaper/lib/satellite.min.js` | MIT | © Shashwat Kandadai and UCSC |
| Night Earth — NASA **Black Marble** 2012 | `wallpaper/lib/earth-night.jpg` | Public domain | NASA Earth Observatory / NOAA NGDC, via [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:The_earth_at_night.jpg); resized to 8192×4096 |
| Day Earth — NASA **Blue Marble** | `wallpaper/lib/earth-day.jpg` | Public domain | NASA Visible Earth, via the [three-globe](https://github.com/vasturiano/three-globe) examples; dimmed slightly |
| Starfield | `wallpaper/lib/night-sky.png` | Project's own (MIT) | Generated procedurally for this project |
| [Twemoji Country Flags](https://github.com/talkjs/country-flag-emoji-polyfill) font | `wallpaper/lib/TwemojiCountryFlags.woff2` | Code MIT; artwork **CC-BY 4.0** | Flag art © Twitter, Inc. and other contributors ([Twemoji](https://github.com/twitter/twemoji)) |
| Country centres & native names — [world-countries](https://github.com/mledoze/countries) | `wallpaper/lib/countries.js` | **ODbL 1.0** | © Mohammed Le Doze; derived database stays under ODbL |
| Undersea cable routes — [TeleGeography Submarine Cable Map](https://www.submarinecablemap.com) | `wallpaper/lib/cables.js` | **CC BY-NC-SA 3.0** | © TeleGeography. **Non-commercial only**, share-alike. Refresh with `scripts/fetch_cables.py` |

## Fonts (loaded from Google Fonts, not bundled)
[Michroma](https://fonts.google.com/specimen/Michroma), [Chakra Petch](https://fonts.google.com/specimen/Chakra+Petch), [JetBrains Mono](https://fonts.google.com/specimen/JetBrains+Mono) — all SIL Open Font License 1.1.

## Live data services (fetched at runtime; free public APIs)
| Feature | Service | Terms |
|---|---|---|
| Radio stations | [Radio Browser](https://www.radio-browser.info) | Free community API; clicks are reported back as the API asks |
| Internet outages | [IODA](https://ioda.inetintel.cc.gatech.edu), Georgia Tech | Free research data |
| Security news | The Hacker News, BleepingComputer, The Record, SecurityWeek RSS via [rss2json](https://rss2json.com); backup: [Hacker News Search](https://hn.algolia.com/api) | Headlines link to the original articles |
| Weather | [Open-Meteo](https://open-meteo.com) | Free for non-commercial use, data CC BY 4.0 — credited in the weather tooltip |
| Born today | [Wikimedia / Wikipedia APIs](https://api.wikimedia.org) | Text CC BY-SA 4.0 (credited in the panel, links to the article); portraits are Wikipedia's page thumbnails, each under its own licence |
| Satellites | [CelesTrak](https://celestrak.org), [TLE API](https://tle.ivanstanojevic.me) | Public orbital elements |
| Service status | Public Statuspage APIs of GitHub, Cloudflare, Zoom, Discord, OpenAI, Claude, Reddit, Dropbox; Slack and Google Cloud status feeds | Public status information |
| PC metrics (Windows) | [Lively Wallpaper](https://github.com/rocksdanister/lively) system-information API | — |
