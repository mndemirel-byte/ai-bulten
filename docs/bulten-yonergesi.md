# Günlük Yapay Zeka Bülteni — Çalışma Yönergesi

Bu belge, bülteni hazırlayan ajanın her gün izlediği akışı ve editoryal kuralları tanımlar.
Rutin prompt'ları kısa tutulur; kurallar burada yaşar ve sürümlenir. Değişiklikler bu dosyada yapılır.

Yayın: https://mndemirel-byte.github.io/ai-bulten/ · Depo: `mndemirel-byte/ai-bulten` · Saat dilimi: Europe/Istanbul

## İlke: toplama koddan, yazı modelden

- **`scripts/topla.py`** kaynakları çeker, son 36 saati süzer, önceki bültenlerde geçen bağlantıları eler,
  aynı haberi farklı kaynaklarda eşleştirip **kapsam** (kaç kaynakta göründüğü) üretir. Deterministiktir; her gün
  aynı şekilde çalışır. Ek paket gerektirmez.
- **Ajan** aday listesinden 10 haberi seçer, makaleleri okur, Türkçe yazar.
- **`scripts/dogrula.py`** dosyayı biçim ve kalite kurallarına göre denetler. Hata varsa push edilmez.
- **`scripts/oku.js`** WebFetch'in açamadığı siteler için başsız tarayıcı yedeğidir.

## Günlük akış

```bash
TZ=Europe/Istanbul date +%F                          # bugünün tarihi (GG)
git push --dry-run origin HEAD:main                   # push erişimi
ls _posts/YYYY-AA/YYYY-AA-GG-gunluk-bulten.md         # varsa: "bugünün bülteni zaten var", bitir

python3 -I scripts/topla.py --kayit                   # adaylar → _calisma/aday.json; kayıt → _data/calismalar/GG.json
#   aday.json: kapsam'a göre sıralı kümeler; her kümede benzerler (aynı haberin diğer kaynakları) listelenir.
#   Çıktıdaki "Kaynaklar (N/M başarılı)" tablosunu bülten notuna taşı.

# Seçim ve okuma (aşağıdaki editoryal kurallar)
# Okunan makalelerin URL'lerini _calisma/okunan.txt'ye satır satır yaz (✅ denetimi için).

python3 -I scripts/dogrula.py _posts/YYYY-AA/YYYY-AA-GG-gunluk-bulten.md --okunan _calisma/okunan.txt
git status --short                                    # yalnızca _posts ve _data değişmiş olmalı
git checkout main && git pull --rebase -q origin main && git add _posts _data && git commit -m "Bülten: YYYY-AA-GG" && git push origin main
```

Push bir kez başarısız olursa `git pull --rebase` yapıp bir kez daha dene. Yine başarısızsa bülten metnini son
mesaja ekle, hatayı tek cümleyle açıkla, "elle yayımla" notu düş ve PushNotification ile bildir.

Push'tan ~2 dakika sonra siteyi WebFetch ile kontrol et; son kartta bugünün tarihi görünmeli. Görünmüyorsa 2 dakika
bekleyip `?v=<zaman damgası>` ekleyerek bir kez daha dene.

### Manuel taslak çalışması (push yok)

Aynı akış, şu farklarla: `--kayit` kullanma; dosyayı repoya değil scratchpad'e yaz; aynı tarihli bülten olsa bile devam et;
`git commit/push` yok. Çıktıyı Artifact (HTML) olarak yayımla ve markdown dosyasını SendUserFile ile ilet.
`git status` temiz kalmalı.

## Kaynak erişimi

- **Önce** aday listesindeki URL'yi WebFetch ile oku.
- WebFetch engel hatası veya 403 verirse **`node scripts/oku.js URL`** dene. Chromium bulut oturumunda hazırdır
  (`/opt/pw-browsers/chromium`); `playwright install` **çalıştırma**.
- `oku.js` **ENGELLİ** derse (401/403, bot koruması) **aşmaya çalışma.** Bu siteler otomatik erişimi istemiyor.
  Bilinen durum: Axios, CNBC, Bloomberg, WSJ, FT, The Information makale metni vermez; Reuters'ın akışı da yok.
  Bu kaynakların haberleri yalnızca akıştaki başlık/özet ve diğer yayıncıların aktarımıyla kullanılır; ✅ almaz.
- The Verge, Ars Technica, TechCrunch, Guardian, BBC ve resmi şirket blogları metin verir.
- Kaynak eklemek/çıkarmak için `_data/kaynaklar.json` düzenlenir. Erişilemeyen kaynak silinmez, `aktif: false` yapılır ve
  `not` yazılır. Yeni RSS adresi bulunursa `python3 -I scripts/topla.py --kaynak <id>` ile tek başına denenir.

## Editoryal kurallar

**Seçim**
1. Sıralama ölçütü önce **kapsam** (kaç bağımsız kaynakta göründüğü), sonra kaynak önceliği, sonra tazelik. Tek kaynaklı
   bir resmi duyuru (model çıkışı, politika değişikliği) yine de "son dakika" olabilir; tek kaynaklı bir basın haberi
   genellikle "stratejik" veya "söylenti"dir.
2. **Çeşitlilik:** aynı şirket hakkında en fazla 2 madde (o şirket günün açık ara ana gündemiyse 3), aynı yayıncıdan en
   fazla 3 madde. "Yalnızca tek site okunabildi" diye bülten o siteye yaslanmaz; erişilemiyorsa bunu notta yaz.
3. **Tazelik:** son 24 saat. 24–36 saat arası yalnızca gelişme sürüyorsa ve bunu belirterek. Daha eskisi girmez.
4. **Tekrar:** önceki bültenlerde geçen haber (topla.py bunları eler) ancak **yeni bir gelişme** varsa ve "dünkü bültende …
   demiştik, bugün …" bağlamıyla girer.
5. **Kesif** türü kaynaklar (AI Weekly) ve derleme siteleri (Investing.com, Crunchbase haftalık derlemesi, canlı akış
   sayfaları, kategori sayfaları) **kaynak olarak gösterilmez**; orijinal yayıncı bulunur. Bulunamıyorsa haber girmez.
6. Sosyal medya, Reddit, HN, Türkçe kaynak yok.

**Doğrulama ve ✅**
7. ✅ yalnızca **birincil kaynağın tam metni okunduysa** verilir: şirket duyurusu, resmi blog, dava dilekçesi, düzenleyici
   kurum sayfası, araştırma makalesi. Bir basın haberinin okunması ✅ vermez; o haber aktardığı belgeyi okutursa verir.
8. Rakamlar: birincil kaynakta doğrulanan rakam düz yazılır. Yalnızca basın aktarımındaki rakam "X'e göre" ile yazılır.
   Yalnızca arama özetinde görülen rakam ya kullanılmaz ya da "(sayfa okunamadı; arama özeti)" notuyla yazılır.
9. Bir kaynağın (örn. FT) haberini başka bir kaynaktan (TechCrunch) aktarıyorsan Kaynak satırı
   `[TechCrunch (FT aktarımı)](url)` biçiminde olur.

**Söylentiler bölümü**
10. İsimsiz kaynaklı ("konuya yakın kişiler", "bir derleme sitesine göre") ve resmi teyitsiz haberler buraya girer.
    Her maddede bunun **açıkça** yazılması gerekir ("resmi teyit yok", "isimsiz kaynaklara dayanıyor"). 2–3 madde hedeflenir.
    Söylenti maddesi de 2–3 özet satırı taşır: iddia, kaynağın niteliği, şirketin tutumu/yorum vermediği.

**Yazım**
11. Her madde 2–3 özet satırı (en fazla 4). İlk satır olayı, ikinci satır **neden önemli** olduğunu ya da bağlamı
    (önceki gelişme, rakip hamlesi, sektöre etkisi) verir. Üçüncü satır varsa ayrıntı veya çekince.
12. Türkçe, sade, kısa cümleler. İngilizce ürün/şirket adları olduğu gibi kalır. Yorum ve tahmin yapılmaz;
    kaynağın söylediği aktarılır. "Devrim", "çığır açan" gibi sıfatlar kullanılmaz.
13. Not satırları (`>`) üç adettir: kapsam tarihleri; kullanılan kaynak türleri; yöntem (hangi siteler okunabildi,
    hangileri okunamadı, kaç ✅, tekrarlanmayan haberler). Son hariç her satır `<br>` ile biter.
14. `one_cikanlar`: 3 başlık, ~50 karakter, emojisiz, çift tırnaksız; en önemli haber ilk sırada.
15. İsteğe bağlı `**Radarda (kısa):**` satırı: bültene girmeyen 3–5 küçük haber, "·" ile ayrılmış, her biri yayıncı ve tarihle.
16. Son satır sabit alt yazıdır (dogrula.py denetler).

## Dosya biçimi (özet; tam denetim `scripts/dogrula.py`)

```
---
layout: post
title: "Günlük Yapay Zeka Bülteni — 9 Ekim 2026"
date: 2026-10-09 09:00:00 +0300
one_cikanlar:
  - "..."
  - "..."
  - "..."
---

> Kapsam: ...<br>
> Kaynaklar: ...<br>
> Yöntem: ...

## 🔴 Son Dakika

### 1. Başlık ✅
- ...
- ...
- Kaynak: [Yayıncı](https://...)

---

## 🧭 Stratejik Gelişmeler
...
---

## 🟡 Söylentiler / Doğrulanmamışlar
...
---

**Radarda (kısa):** ...

*Bu bülten otomatik hazırlanmıştır. ✅ işareti olmayan maddeler, birincil kaynağı okunamadığı için ikincil kaynaklara dayanır. Yatırım tavsiyesi değildir.*
```

H1 başlık yok; başlık front matter'dan gelir. Dosya `_posts/YYYY-AA/YYYY-AA-GG-gunluk-bulten.md`.
Sitenin diğer dosyalarına (`index.md`, `_layouts`, `_includes`, `assets`, `_config.yml`) ve `.env`'e dokunulmaz.

## Kalite izleme

- `_data/calismalar/YYYY-AA-GG.json`: o günkü çalışmanın kaynak durumu (hangi akış açıldı, kaç madde, kaç aday,
  kaç çok kaynaklı küme). Birkaç gün üst üste düşen "başarılı kaynak" sayısı, bir akışın bozulduğunu gösterir.
- `_data/gorulen_sayfa.json`: RSS'i olmayan sayfa kaynaklarında (Anthropic, Meta AI) bağlantıların ilk görülme zamanı.
  Bu kaynaklarda "yayın tarihi" ilk görülme anıdır; makale içindeki tarihle doğrulanır.
- Bültende ✅ sayısı 3'ün altındaysa veya 29 kaynaktan 20'den azı açıldıysa özet mesajında bunu açıkça yaz.

## Rutin prompt'ları

Günlük (zamanlanmış):

> Sen Mehmet'in kişisel yapay zeka haber ajanısın. Bu oturuma bağlı mndemirel-byte/ai-bulten reposundaki
> docs/bulten-yonergesi.md dosyasını oku ve "Günlük akış" bölümünü adım adım uygula: bugünün Türkçe bültenini hazırla,
> dogrula.py'den geçir ve doğrudan main dalına push ederek yayımla. claude/ önekli dal veya PR açma. Bitince kısa bir özet
> yaz ve PushNotification ile gönder: yayın durumu, site linki, en önemli 3 başlık, erişilemeyen kaynaklar, ✅ sayısı.

Manuel taslak (zamanlamasız):

> Sen Mehmet'in kişisel yapay zeka haber ajanısın. Bu oturuma bağlı mndemirel-byte/ai-bulten reposundaki
> docs/bulten-yonergesi.md dosyasını oku ve "Manuel taslak çalışması" bölümünü uygula: bugünün Türkçe bültenini hazırla,
> dogrula.py'den geçir, Artifact olarak yayımla ve markdown dosyasını ilet. GitHub'a hiçbir şey yazma: commit, push,
> dal, PR yok. Bitince kısa özet yaz: Artifact linki, en önemli 3 başlık, erişilemeyen kaynaklar, ✅ sayısı.
