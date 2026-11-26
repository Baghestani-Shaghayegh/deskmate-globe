"""Bundle wallpaper/ into self-contained files in dist/.

- dist/globe-radio-wallpaper.html  -> single file (Plash on Mac, any browser, or Lively without PC metrics)
- dist/deskmate-lively.zip         -> import into Lively (Windows); includes LivelyInfo.json with
                                      --system-information so the PC metrics panel gets data.
Textures and scripts are inlined as data URIs / inline <script>, because Chrome/WebView blocks
WebGL textures loaded from file://.
"""
import base64, json, pathlib, zipfile

root = pathlib.Path(__file__).resolve().parent.parent
d = root / 'wallpaper'
html = (d / 'index.html').read_text()


def inline_script(html, name, root=None):
    js = ((root or d / 'lib') / name).read_text().replace('</script>', '<\\/script>')
    tag = '<script src="%s%s"></script>' % ('' if root else 'lib/', name)
    assert tag in html, tag
    return html.replace(tag, '<script>' + js + '</script>')


def uri(name, mime):
    return 'data:%s;base64,%s' % (mime, base64.b64encode((d / 'lib' / name).read_bytes()).decode())


html = inline_script(html, 'globe.gl.min.js')
html = inline_script(html, 'countries.js')
html = inline_script(html, 'cables.js')
html = inline_script(html, 'satellite.min.js')
html = inline_script(html, 'config.js', root=d)
html = html.replace("const IMG = 'lib/';", "const IMG = '';")
html = html.replace("IMG + 'earth-night.jpg'", "'%s'" % uri('earth-night.jpg', 'image/jpeg'))
html = html.replace('url("lib/TwemojiCountryFlags.woff2")', 'url("%s")' % uri('TwemojiCountryFlags.woff2', 'font/woff2'))
html = html.replace("IMG + 'earth-day.jpg'", "'%s'" % uri('earth-day.jpg', 'image/jpeg'))
html = html.replace("IMG + 'night-sky.png'", "'%s'" % uri('night-sky.png', 'image/png'))

out = root / 'dist'
out.mkdir(exist_ok=True)
(out / 'globe-radio-wallpaper.html').write_text(html)

lively_info = {
    "AppVersion": "1.0.0.0",
    "Title": "Deskmate Globe",
    "Desc": "World radio globe with PC metrics, internet outages and a threat feed",
    "Author": "Deskmate",
    "License": "",
    "Contact": "",
    "Type": 1,  # web wallpaper
    "FileName": "index.html",
    "Arguments": "--system-information",
    "IsAbsolutePath": False,
}
with zipfile.ZipFile(out / 'deskmate-lively.zip', 'w', zipfile.ZIP_DEFLATED) as z:
    z.writestr('index.html', html)
    z.writestr('LivelyInfo.json', json.dumps(lively_info, indent=2))

print(len(html) // 1024, 'KB  +  deskmate-lively.zip')
