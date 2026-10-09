#!/usr/bin/env python3
"""Bülten dosyasını biçim ve kalite kurallarına göre denetler.

Hata varsa 1 ile çıkar (push edilmemeli); uyarılar yalnızca raporlanır.

Kullanım:
  python3 scripts/dogrula.py _posts/2026-10/2026-10-09-gunluk-bulten.md
  python3 scripts/dogrula.py DOSYA --okunan _calisma/okunan.txt   # ✅ maddelerin URL'si bu listede olmalı
  python3 scripts/dogrula.py _posts/**/*.md                        # toplu denetim
"""
import argparse
import os
import re
import sys
import urllib.parse

AYLAR = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
BOLUMLER = ["## 🔴 Son Dakika", "## 🧭 Stratejik Gelişmeler", "## 🟡 Söylentiler / Doğrulanmamışlar"]
ALT_YAZI = ("*Bu bülten otomatik hazırlanmıştır. ✅ işareti olmayan maddeler, birincil kaynağı okunamadığı için "
            "ikincil kaynaklara dayanır. Yatırım tavsiyesi değildir.*")
MADDE_SAYISI = 10
EMOJI_RE = re.compile("[\U0001F000-\U0001FAFF☀-➿⬀-⯿⌀-⏿]")
SOYLENTI_IPUCU = re.compile(r"doğrulanma|teyit|iddia|söylenti|isimsiz|kaynaklara göre|açıklama görülmedi|bildiriliyor", re.I)
YASAK_ALAN = {"reddit.com", "news.ycombinator.com", "x.com", "twitter.com", "facebook.com", "linkedin.com",
              "youtube.com", "aiweekly.co", "medium.com"}


def alan(url):
    h = urllib.parse.urlsplit(url).netloc.lower()
    return h[4:] if h.startswith("www.") else h


def url_normalize(u):
    p = urllib.parse.urlsplit(u.strip())
    return (p.netloc.lower().replace("www.", "", 1) + re.sub(r"/+$", "", p.path)).lower()


def denetle(yol, okunan=None):
    hatalar, uyarilar = [], []
    H, U = hatalar.append, uyarilar.append
    with open(yol, encoding="utf-8") as f:
        metin = f.read()
    satirlar = metin.split("\n")

    # --- Front matter
    m = re.match(r"^---\n(.*?)\n---\n", metin, re.S)
    if not m:
        H("Dosya '---' ile başlayan front matter içermiyor.")
        return hatalar, uyarilar
    fm = m.group(1)
    govde = metin[m.end():]
    dosya_tarih = re.match(r"(\d{4})-(\d{2})-(\d{2})-gunluk-bulten\.md$", os.path.basename(yol))
    if not dosya_tarih:
        H("Dosya adı YYYY-AA-GG-gunluk-bulten.md biçiminde değil.")
    if not re.search(r"^layout: post$", fm, re.M):
        H("Front matter'da 'layout: post' yok.")
    t = re.search(r'^title: "(.*)"$', fm, re.M)
    d = re.search(r"^date: (\d{4})-(\d{2})-(\d{2}) 09:00:00 \+0300$", fm, re.M)
    if not d:
        H("date satırı 'YYYY-AA-GG 09:00:00 +0300' biçiminde değil.")
    if d and dosya_tarih and d.groups() != dosya_tarih.groups():
        H(f"date ({'-'.join(d.groups())}) dosya adındaki tarihle ({'-'.join(dosya_tarih.groups())}) uyuşmuyor.")
    if dosya_tarih:
        klasor = os.path.basename(os.path.dirname(os.path.abspath(yol)))
        if klasor != f"{dosya_tarih.group(1)}-{dosya_tarih.group(2)}":
            H(f"Dosya _posts/{dosya_tarih.group(1)}-{dosya_tarih.group(2)}/ klasöründe olmalı (şu an: {klasor}).")
    if not t:
        H("title satırı yok veya çift tırnak içinde değil.")
    elif d:
        beklenen = f"Günlük Yapay Zeka Bülteni — {int(d.group(3))} {AYLAR[int(d.group(2)) - 1]} {d.group(1)}"
        if t.group(1) != beklenen:
            H(f"title '{t.group(1)}' beklenen '{beklenen}' ile uyuşmuyor.")
    oc = re.search(r"^one_cikanlar:\n((?:  - .*\n?)+)", fm, re.M)
    if not oc:
        H("one_cikanlar listesi yok.")
    else:
        ogeler = re.findall(r'^  - "(.*)"$', oc.group(1), re.M)
        ham = [s for s in oc.group(1).split("\n") if s.strip()]
        if len(ogeler) != len(ham):
            H("one_cikanlar öğeleri çift tırnak içinde olmalı.")
        if not 1 <= len(ogeler) <= 3:
            H(f"one_cikanlar 1–3 öğe olmalı ({len(ogeler)} var).")
        for o in ogeler:
            if '"' in o:
                H(f"one_cikanlar öğesinde çift tırnak var: {o}")
            if EMOJI_RE.search(o):
                H(f"one_cikanlar öğesinde emoji var: {o}")
            if len(o) > 70:
                H(f"one_cikanlar öğesi 70 karakterden uzun ({len(o)}): {o}")
            elif len(o) > 55:
                U(f"one_cikanlar öğesi uzun ({len(o)}; hedef ~50): {o}")
        if len(set(ogeler)) != len(ogeler):
            H("one_cikanlar öğeleri birbirinin aynısı.")

    # --- Gövde: H1, not satırları, alt yazı
    g_satirlar = govde.split("\n")
    for i, s in enumerate(g_satirlar):
        if re.match(r"^# ", s):
            H(f"Satır {i + 1 + fm.count(chr(10)) + 3}: H1 başlık var; başlık front matter'dan gelir.")
    dolu = [s for s in g_satirlar if s.strip()]
    notlar = []
    for s in dolu:
        if s.startswith(">"):
            notlar.append(s)
        else:
            break
    if len(notlar) < 2:
        H("Gövde en az iki '>' not satırıyla (kapsam, kaynaklar, yöntem) başlamalı.")
    for n in notlar[:-1]:
        if not n.rstrip().endswith("<br>"):
            H(f"Son hariç her not satırı '<br>' ile bitmeli: {n[:60]}…")
    if notlar and notlar[-1].rstrip().endswith("<br>"):
        H("Son not satırı '<br>' ile bitmemeli.")
    if not dolu or dolu[-1].strip() != ALT_YAZI:
        H("Son satır standart alt yazı değil.")

    # --- Bölümler
    bolum_konum = [(i, s.strip()) for i, s in enumerate(g_satirlar) if s.startswith("## ")]
    basliklar = [b for _, b in bolum_konum]
    if basliklar != BOLUMLER:
        H(f"Bölüm başlıkları tam olarak şu sırayla olmalı: {BOLUMLER}; bulunan: {basliklar}")
    for (i, _), (j, _) in zip(bolum_konum, bolum_konum[1:]):
        if not any(s.strip() == "---" for s in g_satirlar[i:j]):
            H(f"'{g_satirlar[i].strip()}' ile sonraki bölüm arasında '---' ayırıcı yok.")

    # --- Maddeler
    madde_konum = [(i, s) for i, s in enumerate(g_satirlar) if s.startswith("### ")]
    numaralar = []
    for i, s in madde_konum:
        mm = re.match(r"^### (\d+)\. (.+?)\s*$", s)
        if not mm:
            H(f"Madde başlığı '### N. Başlık' biçiminde değil: {s[:60]}")
            continue
        numaralar.append(int(mm.group(1)))
    if numaralar != list(range(1, MADDE_SAYISI + 1)):
        H(f"Maddeler 1'den {MADDE_SAYISI}'a kadar sırayla numaralanmalı; bulunan: {numaralar}")

    bolum_madde = {b: 0 for b in BOLUMLER}
    alan_sayac, onay_sayisi, onay_okunmamis = {}, 0, []
    for k, (bas, s) in enumerate(madde_konum):
        # Madde bloğu: başlıktan sonra gelen satırlar; sonraki madde/bölüm başlığı, '---',
        # Radarda satırı veya alt yazıya kadar.
        blok = []
        for x in g_satirlar[bas + 1:]:
            if x.startswith("### ") or x.startswith("## ") or x.strip() == "---" \
                    or x.startswith("**Radarda") or x.strip() == ALT_YAZI:
                break
            blok.append(x)
        hangi = None
        for bi, b in bolum_konum:
            if bi < bas:
                hangi = b
        if hangi in bolum_madde:
            bolum_madde[hangi] += 1
        baslik = s[4:].strip()
        onayli = baslik.endswith("✅")
        maddeler = [x for x in blok if re.match(r"^- (?!Kaynak(lar)?:)", x)]
        kaynak = [x for x in blok if re.match(r"^- Kaynak(lar)?:", x)]
        diger = [x for x in blok if x.strip() and not x.startswith("- ")]
        if not 2 <= len(maddeler) <= 4:
            H(f"Madde {baslik[:40]}: 2–3 (en fazla 4) özet maddesi olmalı ({len(maddeler)} var).")
        if len(kaynak) != 1:
            H(f"Madde {baslik[:40]}: tam olarak bir '- Kaynak:' satırı olmalı ({len(kaynak)} var).")
        if diger:
            U(f"Madde {baslik[:40]}: madde dışı satır var: {diger[0][:50]}")
        if kaynak:
            if blok and [x for x in blok if x.strip()][-1] != kaynak[0]:
                H(f"Madde {baslik[:40]}: Kaynak satırı maddenin son satırı olmalı.")
            baglar = re.findall(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", kaynak[0])
            if not baglar:
                H(f"Madde {baslik[:40]}: Kaynak satırında [Yayıncı](https://…) bağlantısı yok.")
            for ad, u in baglar:
                a = alan(u)
                if a in YASAK_ALAN:
                    H(f"Madde {baslik[:40]}: izin verilmeyen kaynak alanı {a}.")
                if not u.startswith("https://"):
                    U(f"Madde {baslik[:40]}: https olmayan bağlantı {u}")
                alan_sayac[a] = alan_sayac.get(a, 0) + 1
            if onayli:
                onay_sayisi += 1
                if okunan is not None:
                    if not any(url_normalize(u) in okunan for _, u in baglar):
                        onay_okunmamis.append(baslik)
        if hangi == BOLUMLER[2] and not SOYLENTI_IPUCU.search("\n".join(blok)):
            U(f"Söylenti maddesi {baslik[:40]}: doğrulanmamış/isimsiz kaynaklı olduğunu açıkça yazmalı.")
        if hangi == BOLUMLER[2] and onayli:
            U(f"Söylenti maddesi {baslik[:40]}: ✅ taşıyor; söylentiler genelde birincil kaynakla doğrulanamaz.")
        for x in maddeler:
            if re.search(r"\d", x) and len(x) < 40:
                U(f"Madde {baslik[:40]}: çok kısa özet satırı: {x[:50]}")

    for b, n in bolum_madde.items():
        if n == 0:
            H(f"'{b}' bölümünde hiç madde yok.")
    if bolum_madde[BOLUMLER[2]] > 4:
        U(f"Söylenti bölümünde {bolum_madde[BOLUMLER[2]]} madde var; 2–3 hedeflenir.")
    for a, n in alan_sayac.items():
        if n > 3:
            U(f"Aynı kaynaktan {n} madde ({a}); en fazla 3 hedeflenir.")
    if onay_sayisi == 0:
        U("Hiçbir madde ✅ taşımıyor: birincil kaynak okunamadı mı? Not satırında belirtilmeli.")
    for b in onay_okunmamis:
        H(f"✅ taşıyan maddenin kaynağı okunan listesinde yok: {b[:60]}")
    if "## 🟡" in govde and "söylenti" not in govde.lower() and "doğrulanmam" not in govde.lower():
        U("Söylenti bölümünde 'doğrulanmamış/söylenti' ifadesi geçmiyor.")
    return hatalar, uyarilar


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dosyalar", nargs="+")
    ap.add_argument("--okunan", help="tam metni okunan URL'lerin listesi (satır başına bir URL)")
    arg = ap.parse_args()
    okunan = None
    if arg.okunan:
        with open(arg.okunan, encoding="utf-8") as f:
            okunan = {url_normalize(s) for s in f if s.strip() and not s.startswith("#")}
    toplam_hata = 0
    for yol in arg.dosyalar:
        hatalar, uyarilar = denetle(yol, okunan)
        toplam_hata += len(hatalar)
        durum = "HATA" if hatalar else "TAMAM"
        print(f"{durum}  {yol}  ({len(hatalar)} hata, {len(uyarilar)} uyarı)")
        for h in hatalar:
            print(f"   ✗ {h}")
        for u in uyarilar:
            print(f"   ~ {u}")
    return 1 if toplam_hata else 0


if __name__ == "__main__":
    sys.exit(main())
