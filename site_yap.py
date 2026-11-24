"""MEÇ Dosyası kanal sitesi (GitHub Pages).
python site_yap.py          → kanalı tarar, index.html + her uzun video için v/<ad>.html + sitemap.xml + robots.txt
python site_yap.py --cevrim → yeniden taramadan (veri/ içindekilerle) üret
Yayın: git add -A && git commit -m "güncelleme" && git push
Google için: her video sayfasında anlatımın tam metni (YouTube Türkçe altyazısı), bölümler ve VideoObject yapılandırılmış verisi
(bölümler → Google'da "Önemli anlar"). Google Search Console doğrulama etiketi: veri/google.txt (içine meta satırı)."""
import datetime, glob, html, json, os, re, subprocess, sys

D = os.path.dirname(os.path.abspath(__file__)); V = os.path.join(D, 'veri'); ALT = os.path.join(V, 'altyazi')
KANAL = 'https://www.youtube.com/@mecdosyasi'
ABONE = KANAL + '?sub_confirmation=1'
SITE = os.environ.get('SITE_ADRESI', 'https://mehmeteminncelik-cmyk.github.io/Mecdosyasi').rstrip('/')
AD = 'MEÇ Dosyası'

def yt(*a): return subprocess.run(['yt-dlp', '--no-warnings', '--extractor-args', 'youtube:lang=tr', *a], capture_output=True, text=True, encoding='utf-8').stdout

def tara():
    os.makedirs(ALT, exist_ok=True)
    open(os.path.join(V, 'videolar.jsonl'), 'w', encoding='utf-8').write(yt('--skip-download', '-j', f'{KANAL}/videos'))
    open(os.path.join(V, 'shortlar.txt'), 'w', encoding='utf-8').write(yt('--flat-playlist', '--print', '%(id)s\t%(title)s', f'{KANAL}/shorts'))
    for j in videolar():
        if not glob.glob(os.path.join(ALT, j['id'] + '.*vtt')):
            subprocess.run(['yt-dlp', '--no-warnings', '--skip-download', '--write-auto-subs', '--write-subs', '--sub-langs', 'tr-orig,tr', '--sub-format', 'vtt',
                            '-o', os.path.join(ALT, '%(id)s'), f'https://www.youtube.com/watch?v={j["id"]}'], capture_output=True)

def videolar(): return [json.loads(l) for l in open(os.path.join(V, 'videolar.jsonl'), encoding='utf-8') if l.strip()]
def shortlar():
    out = []
    for l in open(os.path.join(V, 'shortlar.txt'), encoding='utf-8'):
        if '\t' in l:
            i, t = l.rstrip('\n').split('\t', 1); out.append((i, temiz_baslik(t)))
    return out
def temiz_baslik(t): return ' '.join(w for w in t.split() if not w.startswith('#')).strip().strip('”"').strip()   # hashtag kalabalığı olmasın

def metin(vid):
    """YouTube altyazısından düz anlatım metni (yuvarlanan satır tekrarları atılır)."""
    f = next((x for x in (os.path.join(ALT, vid + '.tr-orig.vtt'), os.path.join(ALT, vid + '.tr.vtt')) if os.path.exists(x)), None)
    if not f: return ''
    satirlar, son = [], None
    for l in open(f, encoding='utf-8'):
        l = re.sub(r'<[^>]+>', '', l).strip()
        if not l or '-->' in l or l.startswith(('WEBVTT', 'Kind:', 'Language:')) or l.isdigit() or l == son: continue
        if satirlar and l.startswith(satirlar[-1]): satirlar[-1] = l
        elif not (satirlar and satirlar[-1].endswith(l)): satirlar.append(l)
        son = l
    s = ' '.join(satirlar); s = re.sub(r'\[(müzik|alkış|music|applause)\]', '', s, flags=re.I); s = re.sub(r'\s+', ' ', s).strip()   # otomatik altyazının [müzik] işaretleri metne girmesin
    return s

TR = str.maketrans('çğıöşüâîûÇĞİÖŞÜÂÎÛ', 'cgiosuaiuCGIOSUAIU')
def ad_yap(t): return re.sub(r'-+', '-', re.sub(r'[^a-z0-9]+', '-', t.translate(TR).lower())).strip('-')[:70]
def iso_sure(s): s = int(s or 0); return f'PT{s // 60}M{s % 60}S'
def iso_tarih(d): return f'{d[:4]}-{d[4:6]}-{d[6:]}T20:00:00+03:00' if d else ''
def tr_tarih(d):
    ay = ['Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran', 'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık']
    return f'{int(d[6:])} {ay[int(d[4:6]) - 1]} {d[:4]}' if d else ''
def dk(s): s = int(s); return f'{s // 60:02d}:{s % 60:02d}'
def kapak(vid): return f'https://i.ytimg.com/vi/{vid}/hqdefault.jpg'
def ilk_paragraf(d): return (d or '').strip().split('\n\n')[0].replace('\n', ' ')[:300]

STIL = '''
:root{--zemin:#f6f1e6;--yazi:#2a1f17;--kart:#fffaf0;--vurgu:#b01c1c;--sari:#e0aa3e;--ince:#7a6a58;--cizgi:#e2d8c6}
@media (prefers-color-scheme:dark){:root{--zemin:#18130f;--yazi:#efe6d6;--kart:#241c16;--ince:#a89880;--cizgi:#3a2f26}}
*{box-sizing:border-box} body{margin:0;background:var(--zemin);color:var(--yazi);font:16px/1.6 system-ui,-apple-system,"Segoe UI",sans-serif}
a{color:var(--vurgu)} header{background:linear-gradient(135deg,#7a1414,#b01c1c);color:#fff;padding:40px 20px 34px;text-align:center}
header h1{margin:0;font-size:clamp(26px,6vw,44px)} header p{margin:10px auto 20px;max-width:640px;opacity:.92} header a.ust{color:#fff;text-decoration:none}
.abone{display:inline-block;background:var(--sari);color:#2a1f17;font-weight:800;padding:12px 26px;border-radius:999px;text-decoration:none}
main{max-width:1180px;margin:0 auto;padding:26px 16px 60px} h2{font-size:24px;margin:30px 0 14px;border-left:6px solid var(--vurgu);padding-left:12px}
.izgara{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:18px} .izgara.dikey{grid-template-columns:repeat(auto-fill,minmax(160px,1fr))}
.kart{background:var(--kart);border-radius:14px;overflow:hidden;text-decoration:none;color:inherit;box-shadow:0 2px 10px rgba(0,0,0,.12)}
.kart img{width:100%;aspect-ratio:16/9;object-fit:cover;display:block;background:#333} .kart.dikey img{aspect-ratio:9/16}
.kart span{display:block;padding:10px 12px 14px;font-weight:650;font-size:15px}
article{max-width:820px;margin:0 auto;padding:26px 16px 60px} article h1{font-size:clamp(24px,4.5vw,36px);line-height:1.2;margin:0 0 8px}
.tarih{color:var(--ince);font-size:14px;margin-bottom:16px} .oynatici{position:relative;aspect-ratio:16/9;border-radius:14px;overflow:hidden;background:#000}
.oynatici iframe{position:absolute;inset:0;width:100%;height:100%;border:0} .bolumler{list-style:none;padding:0} .bolumler li{padding:6px 0;border-bottom:1px solid var(--cizgi)}
.bolumler b{font-variant-numeric:tabular-nums;display:inline-block;min-width:58px;color:var(--vurgu)} .metin{max-width:68ch} .metin p{margin:0 0 14px}
footer{text-align:center;color:var(--ince);font-size:14px;padding:30px 16px}'''

def bas(baslik, aciklama, yol, ek=''):
    g = open(os.path.join(V, 'google.txt'), encoding='utf-8').read().strip() if os.path.exists(os.path.join(V, 'google.txt')) else ''
    return f'''<!doctype html>
<html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(baslik)}</title><meta name="description" content="{html.escape(aciklama)}">
<link rel="canonical" href="{SITE}/{yol}">{g}
<meta property="og:site_name" content="{AD}"><meta property="og:title" content="{html.escape(baslik)}"><meta property="og:description" content="{html.escape(aciklama)}">
{ek}<style>{STIL}</style></head><body>'''

def ust(kucuk=False):
    if kucuk: return f'<header style="padding:18px 20px"><a class="ust" href="{SITE}/"><b>{AD}</b> · Haritalarla tarih</a></header>'
    return f'''<header><h1>{AD}</h1><p>Osmanlı ve dünya tarihini haritalarla, "sen orada olsaydın" gözüyle anlatıyoruz: kaynaklı, sade ve merak uyandıran videolar.</p>
<a class="abone" href="{ABONE}" target="_blank" rel="noopener">▶ YouTube'da abone ol</a></header>'''
def alt(): return f'<footer>Kaynaklar her videonun açıklamasında · <a href="{KANAL}" target="_blank" rel="noopener">youtube.com/@mecdosyasi</a> · <a href="{SITE}/">Tüm videolar</a></footer></body></html>'

def video_sayfasi(j, ad):
    vid, t = j['id'], j['title']; acik = ilk_paragraf(j.get('description')); bol = j.get('chapters') or []; m = metin(vid)
    ld = {'@context': 'https://schema.org', '@type': 'VideoObject', 'name': t, 'description': acik or t, 'thumbnailUrl': [kapak(vid)],
          'uploadDate': iso_tarih(j.get('upload_date')), 'duration': iso_sure(j.get('duration')), 'embedUrl': f'https://www.youtube.com/embed/{vid}',
          'url': f'https://www.youtube.com/watch?v={vid}', 'inLanguage': 'tr',
          'publisher': {'@type': 'Organization', 'name': AD, 'url': KANAL}}
    if bol:
        ld['hasPart'] = [{'@type': 'Clip', 'name': b['title'], 'startOffset': int(b['start_time']), 'endOffset': int(b['end_time']),
                          'url': f'https://www.youtube.com/watch?v={vid}&t={int(b["start_time"])}s'} for b in bol]
    ek = f'<meta property="og:type" content="video.other"><meta property="og:image" content="{kapak(vid)}"><script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>'
    paragraflar = ''
    if m:   # okunabilsin diye ~70 kelimelik paragraflar
        k = m.split(); paragraflar = ''.join(f'<p>{html.escape(" ".join(k[i:i + 70]))}</p>' for i in range(0, len(k), 70))
    aciklama_html = ''.join(f'<p>{html.escape(p).replace(chr(10), "<br>")}</p>' for p in (j.get('description') or '').strip().split('\n\n') if p.strip() and not re.match(r'^\d\d:\d\d', p.strip()))
    s = bas(f'{t} | {AD}', acik or t, f'v/{ad}.html', ek) + ust(True) + f'''<article>
<h1>{html.escape(t)}</h1><div class="tarih">{tr_tarih(j.get('upload_date'))} · {int(j.get('duration') or 0) // 60} dakika · <a href="https://www.youtube.com/watch?v={vid}" target="_blank" rel="noopener">YouTube'da izle</a></div>
<div class="oynatici"><iframe src="https://www.youtube-nocookie.com/embed/{vid}" title="{html.escape(t)}" loading="lazy" allow="encrypted-media; picture-in-picture; fullscreen" allowfullscreen></iframe></div>
<h2>Video hakkında</h2><div class="metin">{aciklama_html}</div>'''
    if bol: s += '<h2>Bölümler</h2><ul class="bolumler">' + ''.join(f'<li><b>{dk(b["start_time"])}</b> <a href="https://www.youtube.com/watch?v={vid}&t={int(b["start_time"])}s" target="_blank" rel="noopener">{html.escape(b["title"])}</a></li>' for b in bol) + '</ul>'
    if paragraflar: s += f'<h2>Videonun metni</h2><div class="metin">{paragraflar}<p class="tarih">Metin, videonun Türkçe altyazısından alınmıştır.</p></div>'
    s += f'<p><a class="abone" href="{ABONE}" target="_blank" rel="noopener">▶ Kanala abone ol</a></p></article>' + alt()
    open(os.path.join(D, 'v', ad + '.html'), 'w', encoding='utf-8').write(s)

def yaz():
    os.makedirs(os.path.join(D, 'v'), exist_ok=True)
    for f in glob.glob(os.path.join(D, 'v', '*.html')): os.remove(f)
    VV, SS = videolar(), shortlar(); bugun = datetime.date.today().isoformat(); adlar = []
    for j in VV:
        ad = ad_yap(j['title']); n = 2
        while ad in adlar: ad = f'{ad_yap(j["title"])}-{n}'; n += 1
        adlar.append(ad); video_sayfasi(j, ad)
    ld = {'@context': 'https://schema.org', '@type': 'WebSite', 'name': AD, 'url': SITE + '/', 'inLanguage': 'tr',
          'publisher': {'@type': 'Organization', 'name': AD, 'url': KANAL, 'sameAs': [KANAL]}}
    ek = f'<meta property="og:type" content="website"><meta property="og:image" content="{kapak(VV[0]["id"]) if VV else ""}"><script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>'
    kartlar = ''.join(f'<a class="kart" href="v/{ad}.html"><img loading="lazy" src="{kapak(j["id"])}" alt="{html.escape(j["title"])}"><span>{html.escape(j["title"])}</span></a>' for j, ad in zip(VV, adlar))
    skart = ''.join(f'<a class="kart dikey" href="https://www.youtube.com/shorts/{i}" target="_blank" rel="noopener"><img loading="lazy" src="https://i.ytimg.com/vi/{i}/oar2.jpg" onerror="this.onerror=null;this.src=\'https://i.ytimg.com/vi/{i}/hqdefault.jpg\'" alt="{html.escape(t)}"><span>{html.escape(t)}</span></a>' for i, t in SS)
    s = bas(f'{AD} · Haritalarla Osmanlı ve Dünya Tarihi Videoları', 'MEÇ Dosyası: Mercidabık, Plevne, Kanuni, Fatih, Genç Osman, Musul ve daha fazlası. Haritalarla, kaynaklı tarih videoları ve shortlar.', '', ek)
    s += ust() + f'<main><h2>Videolar</h2><div class="izgara">{kartlar}</div><h2>Shortlar</h2><div class="izgara dikey">{skart}</div></main>' + alt()
    open(os.path.join(D, 'index.html'), 'w', encoding='utf-8').write(s)
    urls = [f'{SITE}/'] + [f'{SITE}/v/{a}.html' for a in adlar]
    open(os.path.join(D, 'sitemap.xml'), 'w', encoding='utf-8').write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join(f'<url><loc>{u}</loc><lastmod>{bugun}</lastmod></url>' for u in urls) + '</urlset>\n')
    open(os.path.join(D, 'robots.txt'), 'w', encoding='utf-8').write(f'User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n')
    print(f'site hazır: {len(VV)} video sayfası, {len(SS)} short · metinli sayfa: {sum(1 for j in VV if metin(j["id"]))}')

if __name__ == '__main__':
    if '--cevrim' not in sys.argv: tara()
    yaz()
