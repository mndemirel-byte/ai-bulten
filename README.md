# ai-bulten

Günlük Türkçe yapay zeka haber bülteni — https://mndemirel-byte.github.io/ai-bulten/

Bültenler `_posts/YYYY-AA/YYYY-AA-GG-gunluk-bulten.md` olarak tutulur; site GitHub Pages (Jekyll, minima) ile yayımlanır, RSS: `/feed.xml`.

Bültenler her sabah ~09:00 (İstanbul) otomatik yayımlanır.

## Nasıl hazırlanıyor

Akış ve editoryal kurallar: [`docs/bulten-yonergesi.md`](docs/bulten-yonergesi.md)

| Dosya | Görev |
|---|---|
| `_data/kaynaklar.json` | RSS/Atom akışları ve bağlantı taranan sayfalar (öncelik, süzgeç, erişim notları) |
| `scripts/topla.py` | Kaynakları çeker, son 36 saati süzer, önceki bültenleri eler, aynı haberi kaynaklar arasında eşleştirir (yalnızca standart kütüphane) |
| `scripts/dogrula.py` | Bülten dosyasını biçim ve kalite kurallarına göre denetler; hata varsa push edilmez |
| `scripts/oku.js` | WebFetch'in açamadığı siteler için başsız tarayıcı okuyucu (bot korumasını aşmaz) |
| `_data/calismalar/` | Günlük çalışma kayıtları: hangi kaynak açıldı, kaç aday bulundu |
| `_data/gorulen_sayfa.json` | RSS'i olmayan sayfa kaynaklarında bağlantıların ilk görülme zamanı |

```bash
python3 -I scripts/topla.py            # adayları _calisma/aday.json'a yazar, özeti basar
python3 -I scripts/dogrula.py _posts/2026-10/2026-10-09-gunluk-bulten.md
node scripts/oku.js https://www.theverge.com/...
```
