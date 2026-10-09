#!/usr/bin/env python3
"""Günlük bülten için haber adaylarını toplar.

_data/kaynaklar.json'daki RSS/Atom akışlarını ve bağlantı taranan sayfaları
çeker, son N saatteki maddeleri süzer, önceki bültenlerde geçen URL'leri eler,
aynı haberi farklı kaynaklarda eşleştirip "kapsam" sayısı (kaç kaynakta
göründüğü) üretir ve adayları JSON olarak yazar.

Yalnızca standart kütüphane kullanır; ek paket gerekmez.

Kullanım:
  python3 scripts/topla.py                      # _calisma/aday.json yazar, özeti basar
  python3 scripts/topla.py --saat 48            # pencereyi genişlet
  python3 scripts/topla.py --kayit              # ayrıca _data/calismalar/YYYY-AA-GG.json
                                                # ve _data/gorulen_sayfa.json günceller
  python3 scripts/topla.py --kaynak verge,ars   # yalnızca belirli kaynaklar
  python3 scripts/topla.py --tohum              # sayfa kaynaklarının mevcut bağlantılarını
                                                # "eski" olarak işaretler (ilk kurulum)
"""
import argparse
import email.utils
import glob
import html
import json
import os
import re
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KAYNAKLAR = os.path.join(KOK, "_data", "kaynaklar.json")
GORULEN_SAYFA = os.path.join(KOK, "_data", "gorulen_sayfa.json")
CALISMALAR = os.path.join(KOK, "_data", "calismalar")
POSTS = os.path.join(KOK, "_posts")
VARSAYILAN_CIKTI = os.path.join(KOK, "_calisma", "aday.json")
ISTANBUL = timezone(timedelta(hours=3))
ESKI = "2000-01-01T00:00:00+03:00"  # tohumlanan sayfa bağlantıları için "takipten önce" işareti

UA = "ai-bulten-rss/0.1 (+https://mndemirel-byte.github.io/ai-bulten/)"
SSL_CTX = ssl.create_default_context(cafile="/root/.ccr/ca-bundle.crt") \
    if os.path.exists("/root/.ccr/ca-bundle.crt") else ssl.create_default_context()

# Genel akışlar (anahtar_filtre: true) için yapay zeka süzgeci. Kısa olanlar kelime sınırıyla eşleşir.
ANAHTARLAR = [
    r"\bai\b", r"\ba\.i\.", "artificial intelligence", "machine learning", r"\bllms?\b",
    "openai", "chatgpt", r"\bgpt-?\d", "anthropic", r"\bclaude\b", "gemini", "deepmind",
    "mistral", r"\bllama\b", r"\bgrok\b", r"\bxai\b", "copilot", "nvidia", "hugging face",
    r"\bagents?\b", "agentic", "foundation model", "language model", "neural", "deepseek",
    "superintelligence", "super intelligence", "data cent", r"\bchips?\b", "robotaxi",
    "humanoid", "perplexity", "cursor", "codex", "sora", "midjourney", "stability ai",
]
ANAHTAR_RE = re.compile("|".join(ANAHTARLAR), re.I)

DURAK = set("""the a an and or of to in on for with from by at as is are was were be been its it
this that these those into over after before about new says said how why what will can could
would should has have had not no but his her their our your you we they he she who which when
where more most some all any than then also just out up down off than via amid during
bir ve ile için de da bu şu o ne nasıl neden yeni için""".split())

URL_ATIK = {"utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "utm_id",
            "fbclid", "gclid", "ref", "source", "cmpid", "mc_cid", "mc_eid", "ncid", "sref", "srnd"}


def url_normalize(u, taban=None):
    if not u:
        return ""
    u = html.unescape(u.strip())
    if taban:
        u = urllib.parse.urljoin(taban, u)
    p = urllib.parse.urlsplit(u)
    if p.scheme not in ("http", "https"):
        return ""
    q = [(k, v) for k, v in urllib.parse.parse_qsl(p.query, keep_blank_values=True)
         if k.lower() not in URL_ATIK and not k.lower().startswith("utm_")]
    yol = re.sub(r"/+$", "", p.path) or "/"
    # Yalnızca izleme parametresi taşıyan sorguları at; CNBC gibi gerçek sorguları koru.
    return urllib.parse.urlunsplit(("https", p.netloc.lower().replace("www.", "", 1), yol,
                                    urllib.parse.urlencode(q), ""))


def metin_temizle(s, en_fazla=400):
    if not s:
        return ""
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s)
    s = re.sub(r"\s+", " ", s).strip()
    return s[:en_fazla]


def tarih_coz(s):
    if not s:
        return None
    s = s.strip()
    try:
        d = email.utils.parsedate_to_datetime(s)
        if d.tzinfo is None:
            d = d.replace(tzinfo=timezone.utc)
        return d
    except Exception:
        pass
    try:
        d = datetime.fromisoformat(s.replace("Z", "+00:00"))
        if d.tzinfo is None:
            d = d.replace(tzinfo=timezone.utc)
        return d
    except Exception:
        return None


def http_al(url, zaman_asimi, deneme=2):
    """Bir URL'yi okur; 429/5xx'te bir kez bekleyip yeniden dener. Bot koruması (401/403)
    yeniden denenmez: bu, sitenin otomatik erişimi istemediği anlamına gelir."""
    son_hata = None
    for i in range(deneme):
        try:
            istek = urllib.request.Request(url, headers={
                "User-Agent": UA,
                "Accept": "application/rss+xml, application/atom+xml, application/xml;q=0.9, text/html;q=0.8, */*;q=0.5",
            })
            with urllib.request.urlopen(istek, timeout=zaman_asimi, context=SSL_CTX) as r:
                return r.status, r.read(3_000_000), None
        except urllib.error.HTTPError as e:
            son_hata = f"HTTP {e.code}"
            if e.code in (401, 403, 404, 410) or i == deneme - 1:
                return e.code, b"", son_hata
            time.sleep(3)
        except Exception as e:
            son_hata = type(e).__name__ + ": " + str(e)[:80]
            if i == deneme - 1:
                return 0, b"", son_hata
            time.sleep(3)
    return 0, b"", son_hata


def _yerel(etiket):
    return etiket.split("}", 1)[1] if "}" in etiket else etiket


def _cocuk(el, ad):
    for c in el:
        if _yerel(c.tag) == ad:
            return c
    return None


def _cocuk_metin(el, *adlar):
    for ad in adlar:
        c = _cocuk(el, ad)
        if c is not None and (c.text or "").strip():
            return c.text.strip()
    return ""


def akis_coz(veri):
    """RSS 2.0 ve Atom akışlarını ortak yapıya çevirir."""
    kok = ET.fromstring(veri)
    maddeler = []
    if _yerel(kok.tag) == "feed":  # Atom
        for e in kok:
            if _yerel(e.tag) != "entry":
                continue
            link = ""
            for l in e:
                if _yerel(l.tag) == "link":
                    rel = l.get("rel", "alternate")
                    if rel == "alternate" and l.get("href"):
                        link = l.get("href")
                        break
            maddeler.append({
                "baslik": metin_temizle(_cocuk_metin(e, "title"), 300),
                "url": link or _cocuk_metin(e, "id"),
                "yayin": tarih_coz(_cocuk_metin(e, "published", "updated")),
                "ozet": metin_temizle(_cocuk_metin(e, "summary", "content")),
            })
    else:  # RSS
        kanal = _cocuk(kok, "channel") or kok
        for it in kanal.iter():
            if _yerel(it.tag) != "item":
                continue
            link = _cocuk_metin(it, "link")
            if not link:
                g = _cocuk(it, "guid")
                if g is not None and (g.text or "").startswith("http"):
                    link = g.text.strip()
            maddeler.append({
                "baslik": metin_temizle(_cocuk_metin(it, "title"), 300),
                "url": link,
                "yayin": tarih_coz(_cocuk_metin(it, "pubDate", "date", "published")),
                "ozet": metin_temizle(_cocuk_metin(it, "description", "encoded", "summary")),
            })
    return maddeler


def sayfa_coz(veri, kaynak):
    h = veri.decode("utf-8", "replace")
    gorulen, maddeler = set(), []
    for m in re.findall(kaynak["desen"], h):
        u = url_normalize(m, kaynak.get("taban"))
        if not u or u in gorulen:
            continue
        gorulen.add(u)
        slug = u.rstrip("/").rsplit("/", 1)[-1]
        maddeler.append({"baslik": slug.replace("-", " ").strip(), "url": u, "yayin": None, "ozet": "",
                         "baslik_slugdan": True})
    return maddeler


def kaynak_cek(kaynak, zaman_asimi):
    t0 = time.time()
    durum, veri, hata = http_al(kaynak["url"], zaman_asimi)
    sonuc = {"id": kaynak["id"], "durum": durum, "sure_sn": round(time.time() - t0, 1), "hata": hata, "madde": 0}
    maddeler = []
    if veri:
        try:
            maddeler = sayfa_coz(veri, kaynak) if kaynak.get("bicim") == "sayfa" else akis_coz(veri)
        except ET.ParseError as e:
            sonuc["hata"] = "XML çözümlenemedi: " + str(e)[:80]
    sonuc["madde"] = len(maddeler)
    return sonuc, maddeler


def onceki_bulten_urlleri():
    """_posts altındaki tüm bültenlerde geçen bağlantılar (normalize)."""
    urller = {}
    for yol in sorted(glob.glob(os.path.join(POSTS, "**", "*.md"), recursive=True)):
        ad = os.path.basename(yol)[:10]
        with open(yol, encoding="utf-8") as f:
            for u in re.findall(r"\]\((https?://[^)\s]+)\)", f.read()):
                urller.setdefault(url_normalize(u), ad)
    return urller


def kokler(baslik):
    """Başlığı kaba köklere indirger: 'annualised revenues $20bn' ve 'annualized revenue $20 billion'
    aynı kökleri ('annual', 'revenu', '20', 'bn') versin diye İngilizce ekler ve para/sayı biçimleri sadeleştirilir."""
    s = baslik.lower().replace("’", "'")
    s = re.sub(r"'s\b", "", s)
    s = re.sub(r"\$(\d+(?:\.\d+)?)\s*(bn|billion|b)\b", r"\1 bn", s)
    s = re.sub(r"\$(\d+(?:\.\d+)?)\s*(m|mn|million)\b", r"\1 mn", s)
    s = re.sub(r"(\d+),(\d{3})", r"\1\2", s)
    sonuc = set()
    for k in re.findall(r"[a-z0-9çğıöşü]+", s):
        if k in DURAK or (len(k) < 3 and not k.isdigit()):
            continue
        if not k.isdigit():
            k = re.sub(r"(ised|ized|ises|izes|ise|ize|ing|ies|ed|es|s)$", "", k) if len(k) > 4 else k
            k = k[:6]
        sonuc.add(k)
    return sonuc


def kumele(adaylar):
    """Aynı haberi farklı kaynaklarda eşleştirir. Benzerlik, nadir köklere ağırlık veren
    IDF tabanlı örtüşme: ortak köklerin IDF toplamı / küçük başlığın IDF toplamı."""
    import math
    n = len(adaylar)
    kok = [kokler(a["baslik"]) for a in adaylar]
    df = {}
    for s in kok:
        for k in s:
            df[k] = df.get(k, 0) + 1
    idf = {k: math.log((n + 1) / (v + 0.5)) for k, v in df.items()}
    agirlik = [sum(idf[k] for k in s) for s in kok]
    ebeveyn = list(range(n))

    def bul(i):
        while ebeveyn[i] != i:
            ebeveyn[i] = ebeveyn[ebeveyn[i]]
            i = ebeveyn[i]
        return i

    for i in range(n):
        for j in range(i + 1, n):
            ortak = kok[i] & kok[j]
            if len(ortak) < 2 or min(agirlik[i], agirlik[j]) == 0:
                continue
            skor = sum(idf[k] for k in ortak) / min(agirlik[i], agirlik[j])
            if skor >= 0.5:
                ebeveyn[bul(i)] = bul(j)
    kumeler = {}
    for i in range(n):
        kumeler.setdefault(bul(i), []).append(adaylar[i])
    return list(kumeler.values())


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--saat", type=float, default=36, help="kaç saat geriye bakılsın (varsayılan 36)")
    ap.add_argument("--cikti", default=VARSAYILAN_CIKTI, help="aday JSON dosyası")
    ap.add_argument("--kayit", action="store_true", help="çalışma kaydı ve sayfa görülme durumunu _data altına yaz")
    ap.add_argument("--kaynak", help="virgülle ayrılmış kaynak id'leri; yalnızca bunları çek")
    ap.add_argument("--tekrar-dahil", action="store_true", help="önceki bültenlerde geçen bağlantıları da listele")
    ap.add_argument("--tohum", action="store_true", help="sayfa kaynaklarının mevcut bağlantılarını eski olarak kaydet ve çık")
    ap.add_argument("--zaman-asimi", type=int, default=25)
    ap.add_argument("--sessiz", action="store_true")
    arg = ap.parse_args()

    with open(KAYNAKLAR, encoding="utf-8") as f:
        kaynaklar = [k for k in json.load(f)["kaynaklar"] if k.get("aktif", True)]
    if arg.kaynak:
        secili = set(arg.kaynak.split(","))
        kaynaklar = [k for k in kaynaklar if k["id"] in secili]
    kaynak_haritasi = {k["id"]: k for k in kaynaklar}

    gorulen_sayfa = {}
    if os.path.exists(GORULEN_SAYFA):
        with open(GORULEN_SAYFA, encoding="utf-8") as f:
            gorulen_sayfa = json.load(f)

    simdi = datetime.now(ISTANBUL)
    esik = simdi - timedelta(hours=arg.saat)

    with ThreadPoolExecutor(max_workers=8) as ex:
        sonuclar = list(ex.map(lambda k: kaynak_cek(k, arg.zaman_asimi), kaynaklar))

    if arg.tohum:
        for (sonuc, maddeler), k in zip(sonuclar, kaynaklar):
            if k.get("bicim") == "sayfa":
                for m in maddeler:
                    gorulen_sayfa.setdefault(m["url"], ESKI)
        os.makedirs(os.path.dirname(GORULEN_SAYFA), exist_ok=True)
        with open(GORULEN_SAYFA, "w", encoding="utf-8") as f:
            json.dump(gorulen_sayfa, f, ensure_ascii=False, indent=0, sort_keys=True)
        print(f"Tohumlandı: {len(gorulen_sayfa)} sayfa bağlantısı eski olarak işaretlendi.")
        return 0

    onceki = onceki_bulten_urlleri()
    adaylar, elenen = [], {"tarih_disi": 0, "tarihsiz": 0, "anahtar": 0, "disla": 0, "onceki_bulten": 0,
                           "gecersiz_url": 0, "yinelenen_url": 0}
    yeni_sayfa_url, gorulen_url = {}, set()
    for (sonuc, maddeler), k in zip(sonuclar, kaynaklar):
        disla = re.compile(k["disla"], re.I) if k.get("disla") else None
        for m in maddeler:
            u = url_normalize(m["url"])
            if not u:
                elenen["gecersiz_url"] += 1
                continue
            if u in gorulen_url:
                elenen["yinelenen_url"] += 1
                continue
            gorulen_url.add(u)
            if disla and disla.search(m["baslik"]):
                elenen["disla"] += 1
                continue
            if k.get("bicim") == "sayfa":
                ilk = gorulen_sayfa.get(u)
                if ilk is None:
                    ilk = simdi.isoformat(timespec="seconds")
                    yeni_sayfa_url[u] = ilk
                m["yayin"] = tarih_coz(ilk)
                m["tarih_tahmini"] = True
            if m["yayin"] is None:
                elenen["tarihsiz"] += 1
                continue
            if m["yayin"] < esik:
                elenen["tarih_disi"] += 1
                continue
            if k.get("anahtar_filtre") and not ANAHTAR_RE.search(m["baslik"] + " " + m["ozet"]):
                elenen["anahtar"] += 1
                continue
            if u in onceki and not arg.tekrar_dahil:
                elenen["onceki_bulten"] += 1
                continue
            adaylar.append({
                "baslik": m["baslik"], "url": u, "kaynak": k["id"], "yayinci": k["ad"], "tur": k["tur"],
                "oncelik": k.get("oncelik", 3), "yayin": m["yayin"].astimezone(ISTANBUL).isoformat(timespec="minutes"),
                "ozet": m["ozet"], "tarih_tahmini": bool(m.get("tarih_tahmini")),
                "baslik_slugdan": bool(m.get("baslik_slugdan")), "onceki_bulten": onceki.get(u),
            })

    kumeler = kumele(adaylar)
    cikti = []
    for grup in kumeler:
        grup.sort(key=lambda a: ({"resmi": 0, "basin": 1, "kesif": 2}[a["tur"]], a["oncelik"], a["yayin"]))
        temsilci = grup[0]
        kaynak_seti = sorted({a["kaynak"] for a in grup})
        cikti.append({
            "baslik": temsilci["baslik"], "url": temsilci["url"], "yayinci": temsilci["yayinci"], "tur": temsilci["tur"],
            "oncelik": min(a["oncelik"] for a in grup),
            "yayin": max(a["yayin"] for a in grup), "ilk_yayin": min(a["yayin"] for a in grup),
            "kapsam": len(kaynak_seti), "kaynaklar": kaynak_seti, "ozet": temsilci["ozet"],
            "tarih_tahmini": temsilci["tarih_tahmini"], "baslik_slugdan": temsilci["baslik_slugdan"],
            "onceki_bulten": temsilci["onceki_bulten"],
            "benzerler": [{"baslik": a["baslik"], "url": a["url"], "yayinci": a["yayinci"], "yayin": a["yayin"]} for a in grup[1:]],
        })
    # Kapsam azalan; eşitlikte kaynak önceliği, sonra en yeni.
    cikti.sort(key=lambda c: (-c["kapsam"], c["oncelik"], {"resmi": 0, "basin": 1, "kesif": 2}[c["tur"]]))
    for c in cikti:
        del c["oncelik"]

    calisma = {
        "tarih": simdi.strftime("%Y-%m-%d"), "zaman": simdi.isoformat(timespec="seconds"), "pencere_saat": arg.saat,
        "kaynaklar": [dict(s, ad=kaynak_haritasi[s["id"]]["ad"]) for s, _ in sonuclar],
        "basarili_kaynak": sum(1 for s, _ in sonuclar if s["durum"] == 200),
        "toplam_kaynak": len(sonuclar), "ham_madde": sum(s["madde"] for s, _ in sonuclar),
        "elenen": elenen, "aday": len(adaylar), "kume": len(cikti),
        "coklu_kapsam": sum(1 for c in cikti if c["kapsam"] >= 2),
    }

    os.makedirs(os.path.dirname(os.path.abspath(arg.cikti)), exist_ok=True)
    with open(arg.cikti, "w", encoding="utf-8") as f:
        json.dump({"calisma": calisma, "adaylar": cikti}, f, ensure_ascii=False, indent=1)

    if arg.kayit:
        os.makedirs(CALISMALAR, exist_ok=True)
        with open(os.path.join(CALISMALAR, calisma["tarih"] + ".json"), "w", encoding="utf-8") as f:
            json.dump(calisma, f, ensure_ascii=False, indent=1)
        if yeni_sayfa_url:
            gorulen_sayfa.update(yeni_sayfa_url)
            with open(GORULEN_SAYFA, "w", encoding="utf-8") as f:
                json.dump(gorulen_sayfa, f, ensure_ascii=False, indent=0, sort_keys=True)

    if not arg.sessiz:
        print(f"Kaynaklar ({calisma['basarili_kaynak']}/{calisma['toplam_kaynak']} başarılı):")
        for s, _ in sonuclar:
            isaret = "OK " if s["durum"] == 200 else "!! "
            print(f"  {isaret}{s['id']:15} {s['durum']:>3} madde={s['madde']:<4} {s['hata'] or ''}")
        print(f"\nHam {calisma['ham_madde']} madde → pencere içi aday {len(adaylar)} → küme {len(cikti)} "
              f"(çok kaynaklı {calisma['coklu_kapsam']}). Elenen: {elenen}")
        print(f"\nİlk 25 küme (kapsam · yayıncı · başlık):")
        for c in cikti[:25]:
            ek = " [tarih=ilk görülme]" if c["tarih_tahmini"] else ""
            print(f"  {c['kapsam']}  {c['yayinci']:18} {c['baslik'][:90]}{ek}")
            for b in c["benzerler"][:3]:
                print(f"       ↳ {b['yayinci']}: {b['baslik'][:80]}")
        print(f"\nAdaylar: {arg.cikti}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
