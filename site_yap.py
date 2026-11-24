"""MEÇ Dosyası kanal sitesi (GitHub Pages): YouTube kanalındaki videoları ve shortları listeleyen tek sayfalık site.
python site_yap.py            → kanalı tarar (yt-dlp, Türkçe başlıklar), index.html + sitemap.xml + robots.txt yazar
Yeni video yüklenince yeniden çalıştır, sonra: git add -A && git commit -m "yeni video" && git push"""
import html, json, os, subprocess, datetime

D = os.path.dirname(os.path.abspath(__file__))
KANAL = 'https://www.youtube.com/@mecdosyasi'
ABONE = KANAL + '?sub_confirmation=1'
SITE = os.environ.get('SITE_ADRESI', 'https://KULLANICI.github.io')   # GitHub hesabı açılınca gerçek adres yazılır

def liste(tur):
    r = subprocess.run(['yt-dlp', '--flat-playlist', '--extractor-args', 'youtube:lang=tr', '--print', '%(id)s\t%(title)s', f'{KANAL}/{tur}'],
                       capture_output=True, text=True, encoding='utf-8')
    out = []
    for l in r.stdout.splitlines():
        if '\t' in l:
            i, t = l.split('\t', 1); t = ' '.join(w for w in t.split() if not w.startswith('#')).strip().strip('”"').strip()   # sitede hashtag kalabalığı olmasın
            out.append((i, t))
    return out

def kart(i, t, short=False):
    url = f'https://www.youtube.com/{"shorts/" if short else "watch?v="}{i}'
    img = f'https://i.ytimg.com/vi/{i}/{"hq720" if not short else "oar2"}.jpg'
    yedek = f'https://i.ytimg.com/vi/{i}/hqdefault.jpg'
    return (f'<a class="kart{" dikey" if short else ""}" href="{url}" target="_blank" rel="noopener">'
            f'<img loading="lazy" src="{img}" onerror="this.onerror=null;this.src=\'{yedek}\'" alt="{html.escape(t)}">'
            f'<span>{html.escape(t)}</span></a>')

def yaz():
    V, S = liste('videos'), liste('shorts')
    bugun = datetime.date.today().isoformat()
    jsonld = {'@context': 'https://schema.org', '@type': 'ItemList', 'name': 'MEÇ Dosyası videoları',
              'itemListElement': [{'@type': 'ListItem', 'position': k + 1, 'url': f'https://www.youtube.com/watch?v={i}', 'name': t} for k, (i, t) in enumerate(V)]}
    sayfa = f'''<!doctype html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MEÇ Dosyası · Haritalarla Osmanlı ve Dünya Tarihi Videoları</title>
<meta name="description" content="MEÇ Dosyası YouTube kanalı: Mercidabık, Plevne, Kanuni, Fatih, Musul ve daha fazlası. Haritalarla, kaynaklı ve merak uyandıran tarih videoları ve shortlar.">
<meta name="keywords" content="osmanlı tarihi, haritalı tarih, mercidabık, plevne, kanuni, fatih, musul, tarih videoları, tarih shorts, meç dosyası">
<link rel="canonical" href="{SITE}/">
<meta property="og:type" content="website"><meta property="og:title" content="MEÇ Dosyası · Haritalarla Tarih">
<meta property="og:description" content="Haritalarla, kaynaklı tarih videoları ve shortlar.">
<meta property="og:url" content="{SITE}/"><meta property="og:image" content="https://i.ytimg.com/vi/{V[0][0] if V else ''}/hq720.jpg">
<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>
<style>
:root{{--zemin:#f6f1e6;--yazi:#2a1f17;--kart:#fffaf0;--vurgu:#b01c1c;--sari:#e0aa3e;--ince:#8a7a68}}
@media (prefers-color-scheme:dark){{:root{{--zemin:#18130f;--yazi:#efe6d6;--kart:#241c16;--ince:#a89880}}}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--zemin);color:var(--yazi);font:16px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif}}
header{{background:linear-gradient(135deg,#7a1414,#b01c1c);color:#fff;padding:48px 20px 40px;text-align:center}}
header h1{{margin:0;font-size:clamp(28px,6vw,48px);letter-spacing:.02em}} header p{{margin:10px auto 22px;max-width:640px;opacity:.92}}
.abone{{display:inline-block;background:var(--sari);color:#2a1f17;font-weight:800;padding:12px 26px;border-radius:999px;text-decoration:none}}
main{{max-width:1180px;margin:0 auto;padding:28px 16px 60px}} h2{{font-size:24px;margin:34px 0 14px;border-left:6px solid var(--vurgu);padding-left:12px}}
.izgara{{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:18px}}
.izgara.dikey{{grid-template-columns:repeat(auto-fill,minmax(160px,1fr))}}
.kart{{background:var(--kart);border-radius:14px;overflow:hidden;text-decoration:none;color:inherit;box-shadow:0 2px 10px rgba(0,0,0,.12);transition:transform .15s}}
.kart:hover{{transform:translateY(-3px)}} .kart img{{width:100%;aspect-ratio:16/9;object-fit:cover;display:block;background:#333}}
.kart.dikey img{{aspect-ratio:9/16}} .kart span{{display:block;padding:10px 12px 14px;font-weight:650;font-size:15px}}
footer{{text-align:center;color:var(--ince);font-size:14px;padding:30px 16px}}
</style>
</head>
<body>
<header>
<h1>MEÇ Dosyası</h1>
<p>Osmanlı ve dünya tarihini haritalarla anlatıyoruz: kaynaklı, sade ve merak uyandıran videolar. Mercidabık, Plevne, Kanuni'nin son seferi, Musul ve daha fazlası.</p>
<a class="abone" href="{ABONE}" target="_blank" rel="noopener">▶ YouTube'da abone ol</a>
</header>
<main>
<h2>Videolar</h2>
<div class="izgara">{"".join(kart(i, t) for i, t in V)}</div>
<h2>Shortlar</h2>
<div class="izgara dikey">{"".join(kart(i, t, True) for i, t in S)}</div>
</main>
<footer>Güncelleme: {bugun} · Kaynaklar her videonun açıklamasında · <a href="{KANAL}" target="_blank" rel="noopener">youtube.com/@mecdosyasi</a></footer>
</body>
</html>'''
    open(os.path.join(D, 'index.html'), 'w', encoding='utf-8').write(sayfa)
    open(os.path.join(D, 'sitemap.xml'), 'w', encoding='utf-8').write(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>{SITE}/</loc><lastmod>{bugun}</lastmod></url></urlset>\n')
    open(os.path.join(D, 'robots.txt'), 'w', encoding='utf-8').write(f'User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n')
    print(f'site hazır: {len(V)} video, {len(S)} short')

if __name__ == '__main__':
    yaz()
