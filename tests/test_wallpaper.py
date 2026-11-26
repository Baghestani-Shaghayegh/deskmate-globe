"""Render the built wallpaper headless with all APIs mocked, then screenshot.

Run:  python3 scripts/build_wallpaper.py && python3 tests/test_wallpaper.py
Set LIVE=1 to use the real outage + news APIs instead of mocks (radio stays mocked).
"""
import json, math, os, random, time
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
URL = "file://" + os.path.abspath(os.path.join(HERE, "../dist/globe-radio-wallpaper.html"))
LIVE = os.environ.get("LIVE") == "1"
CORS = {"Access-Control-Allow-Origin": "*"}

random.seed(1)
fake = [{"stationuuid": f"id{i}", "name": f"Station {i}", "url_resolved": "https://example.com/s.mp3",
         "geo_lat": random.uniform(-50, 60), "geo_long": random.uniform(-170, 170), "state": "",
         "country": random.choice(["Japan", "France", "Kenya", "Brazil"]),
         "countrycode": random.choice(["JP", "FR", "KE", "BR"]), "tags": "pop,jazz", "favicon": "",
         "codec": "MP3", "bitrate": 128} for i in range(1500)]

outages = {"data": [
    {"scores": {"bgp.median": 5.2e6, "gtr.sarima": 1e4, "overall": 5.5e7}, "event_cnt": 2, "entity": {"code": "IR", "name": "Iran", "type": "country"}},
    {"scores": {"merit-nt.median": 3.9e5, "overall": 3.9e5}, "event_cnt": 1, "entity": {"code": "NL", "name": "Netherlands", "type": "country"}},
    {"scores": {"ping-slash24.median": 2.3e5, "overall": 2.3e5}, "event_cnt": 1, "entity": {"code": "GE", "name": "Georgia", "type": "country"}},
    {"scores": {"bgp.median": 3.2e4, "overall": 3.2e4}, "event_cnt": 3, "entity": {"code": "SC", "name": "Seychelles", "type": "country"}},
    {"scores": {"bgp.median": 2.0e4, "overall": 2.0e4}, "event_cnt": 1, "entity": {"code": "RS", "name": "Serbia", "type": "country"}},
    {"scores": {"bgp.median": 1.0e4, "overall": 1.0e4}, "event_cnt": 1, "entity": {"code": "XX", "name": "Nowhere", "type": "country"}},
]}
now = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
news = {"status": "ok", "items": [
    {"title": "VMware vCenter Hit by Critical 9.8-Rated Auth Bypass Flaw After Zero-Day Exploitation", "pubDate": now, "link": "https://example.com/a", "description": "<p>Broadcom has released fixes for a <b>critical</b> authentication bypass in VMware vCenter Server, weeks after a separate zero-day was exploited in the wild.</p> [&#8230;]"},
    {"title": "New ransomware gang&#8217;s <img src=x onerror=alert(1)> leak site", "pubDate": "2026-11-20 10:00:00", "link": "https://example.com/b"},
]}


def person(year, text, title, desc, extract, img=True):
    return {"year": year, "text": text, "pages": [{"title": title, "normalizedtitle": title.replace("_", " "), "description": desc, "extract": extract,
            "thumbnail": {"source": "https://upload.wikimedia.org/x/" + title + ".jpg"} if img else None,
            "content_urls": {"desktop": {"page": "https://en.wikipedia.org/wiki/" + title}}}]}
births = {"births": [
    person(1946, "Ted Bundy, American serial killer (died 1989)", "Ted_Bundy", "American serial killer", "Bundy was an American serial killer."),
    person(1978, "Katherine Heigl, American actress", "Katherine_Heigl", "American actress", "Actress."),
    person(1784, "Zachary Taylor, American general and politician, 12th President of the United States (died 1850)", "Zachary_Taylor",
           "President of the United States from 1849 to 1850", "Zachary Taylor was the 12th president of the United States."),
    person(1632, "Baruch Spinoza, Dutch philosopher and scholar (died 1677)", "Baruch_Spinoza", "Portuguese-Dutch philosopher (1632–1677)", "Spinoza was a philosopher."),
    person(1897, "Lucky Luciano, Italian-American mob boss (died 1962)", "Lucky_Luciano", "Italian-American mobster", "Luciano was an Italian-American gangster."),
]}
views = {"Zachary Taylor": 60051, "Baruch Spinoza": 46542, "Lucky Luciano": 79439, "Ted Bundy": 488090}
def wiki(route):
    url = route.request.url
    if "prop=pageviews" in url:
        pages = [{"title": t, "pageviews": {"2026-11-01": v}} for t, v in views.items()]
        body = {"query": {"pages": pages}}
    else:
        body = {"query": {"pages": [{"title": "Zachary Taylor", "extract": "Zachary Taylor (November 24, 1784 – July 9, 1850) was the 12th president of the United States, serving from 1849 until his death in 1850.\nTaylor was a career officer in the United States Army, rising to the rank of major general."}]}}
    route.fulfill(status=200, content_type="application/json", body=json.dumps(body), headers=CORS)


WX = {"current": {"temperature_2m": 81.4, "apparent_temperature": 84.0, "relative_humidity_2m": 62, "weather_code": 2, "is_day": 1, "wind_speed_10m": 11.2}, "daily": {"temperature_2m_max": [83.1], "temperature_2m_min": [71.6], "precipitation_probability_max": [30]}}


def sysinfo(t):
    return json.dumps({"NameCpu": "AMD Ryzen 7 7800X3D 8-Core Processor", "NameGpu": "NVIDIA GeForce RTX 4070",
                       "NameNetCard": "Intel(R) Ethernet Controller I225-V",
                       "CurrentCpu": 22 + 15 * math.sin(t / 3), "CurrentGpu3D": 91, "CurrentRamAvail": 14336, "TotalRam": 32768,
                       "CurrentNetDown": 2.4e6 * (1 + math.sin(t / 4)), "CurrentNetUp": 1.8e5 * (1 + math.cos(t / 5))})


with sync_playwright() as p:
    b = p.chromium.launch(executable_path=os.environ.get("CHROMIUM") or None, args=["--use-gl=swiftshader", "--enable-webgl", "--ignore-gpu-blocklist"])
    pg = b.new_page(viewport={"width": 1600, "height": 900})
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.on("console", lambda m: m.type == "error" and errs.append(m.text))
    pg.on("dialog", lambda d: (errs.append("XSS dialog!"), d.dismiss()))
    pg.route("**/*radio-browser.info/**", lambda r: r.fulfill(status=200, content_type="application/json", body=json.dumps(fake), headers=CORS))
    if not LIVE:
        pg.route("**/api.ioda.inetintel.cc.gatech.edu/**", lambda r: r.fulfill(status=200, content_type="application/json", body=json.dumps(outages), headers=CORS))
        pg.route("**/api.open-meteo.com/**", lambda r: r.fulfill(status=200, content_type="application/json", body=json.dumps(WX), headers=CORS))
        pg.route("**/api.wikimedia.org/**", lambda r: r.fulfill(status=200, content_type="application/json", body=json.dumps(births), headers=CORS))
        pg.route("**/en.wikipedia.org/**", wiki)
        pg.route("**/upload.wikimedia.org/**", lambda r: r.fulfill(status=200, content_type="image/svg+xml", body="<svg xmlns='http://www.w3.org/2000/svg' width='64' height='64'><rect width='64' height='64' fill='#a87'/></svg>"))
        pg.route("**/api.rss2json.com/**", lambda r: r.fulfill(status=200, content_type="application/json", body=json.dumps(news), headers=CORS))
    pg.route("**/fonts.googleapis.com/**", lambda r: r.abort())
    pg.route("https://example.com/**", lambda r: r.abort())
    pg.goto(URL)
    pg.wait_for_timeout(1500)
    assert not pg.is_visible("#sys"), "System panel should stay hidden without Lively"
    for t in range(40):  # what Lively does once a second
        pg.evaluate("d => window.livelySystemInformation(d)", sysinfo(t))
    pg.wait_for_timeout(8000 if LIVE else 5000)
    pg.screenshot(path=HERE + "/shot1.png")
    pg.click("#searchBtn"); pg.fill("#q", "station 12"); pg.wait_for_timeout(300)
    pg.screenshot(path=HERE + "/shot_search.png")
    pg.click("#results div >> nth=0"); pg.wait_for_timeout(2500)
    pg.screenshot(path=HERE + "/shot2.png")
    pg.click(".nrow >> nth=0"); pg.wait_for_timeout(400)
    pg.screenshot(path=HERE + "/shot_reader.png")
    print("reader:", pg.is_visible("#reader"), "|", pg.inner_text("#reader .rsum")[:80])
    pg.click("#rBack"); pg.wait_for_timeout(200)
    print("back to list:", pg.is_visible("#nlist"), pg.is_visible("#reader"))
    pg.click("#outages .fold"); pg.wait_for_timeout(300)
    pg.screenshot(path=HERE + "/shot_folded.png")
    print("outages folded:", not pg.is_visible("#olist"))
    pg.reload(); pg.wait_for_timeout(1500)
    print("still folded after restart:", not pg.is_visible("#olist"))
    for t in range(40):  # Lively keeps sending after a restart too
        pg.evaluate("d => window.livelySystemInformation(d)", sysinfo(t))
    pg.click("#outages .fold")
    print("weather:", pg.inner_text("#wx").replace("\n", " "), "|", pg.get_attribute("#wx", "title"))
    print("born:", pg.inner_text("#bcard").replace("\n", " | "))
    pg.click("#bcard"); pg.wait_for_timeout(600)
    print("born reader:", pg.inner_text("#btext")[:90].replace("\n", " / "))
    pg.screenshot(path=HERE + "/shot_born.png")
    pg.click("#bBack"); pg.wait_for_timeout(200)
    print("now:", pg.inner_text("#sname"), "|", pg.inner_text("#metaText"))
    print("outages:", pg.locator(".orow").count(), "|", pg.inner_text("#ometa"))
    print("news:", pg.locator(".nrow").count(), "|", pg.inner_text(".nrow >> nth=0").replace("\n", " "))
    print("sys:", pg.inner_text("#gCpu b"), pg.inner_text("#gRam b"), pg.inner_text("#netD"), "|", pg.inner_text("#hw1"), "|", pg.inner_text("#hw2"))
    print("us:", pg.inner_text("#us"))
    # a milestone day: 300 days together
    pg2 = b.new_page(viewport={"width": 1600, "height": 900})
    pg2.clock.set_fixed_time("2027-01-13T20:00:00")
    pg2.route("**/*", lambda r: r.abort() if "file://" not in r.request.url else r.continue_())
    pg2.goto(URL); pg2.wait_for_timeout(1500)
    print("us on 2027-01-13:", pg2.inner_text("#us"))
    pg2.locator("#clock").screenshot(path=HERE + "/shot_us_party.png")
    print("errors:", [e for e in errs if 'example.com' not in e and 'fonts' not in e and 'ERR_FAILED' not in e][:5])
    b.close()
