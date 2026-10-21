---
layout: post
title: "Günlük Yapay Zeka Bülteni — 21 Ekim 2026"
date: 2026-10-21 09:00:00 +0300
one_cikanlar:
  - "OpenAI biyoteknoloji girişimi Orchestra Bio'yu aldı"
  - "SpaceX ve Tesla birleşmeyi görüşüyor"
  - "Meta, Muse sohbet paylaşımını durdurdu"
---

> Kapsam: 20 Ekim 2026 sabahı – 21 Ekim 2026 sabahı (İstanbul saati); dünkü bültende geçen DeepSeek yasağı ve eski OpenAI mühendisi davası yeni gelişme olmadığı için alınmadı.<br>
> Kaynaklar: Şirket blogları (Mistral, Microsoft, Hugging Face) ile uluslararası teknoloji ve iş basını (TechCrunch, Ars Technica, The Verge, Axios, Bloomberg, The Information).<br>
> Yöntem: Kaynaklar 28/29 başarılı açıldı (VentureBeat HTTP 429 verdi; DeepMind akışı çözümlenemedi). Mistral, Microsoft ve Hugging Face blogları ile TechCrunch, Ars Technica ve The Verge metinleri okundu; OpenAI duyurusu (403), Axios, Bloomberg ve The Information metinleri alınamadı (bot koruması, aşılmaya çalışılmadı) ve akış özetlerine dayanır. 3 ✅ var. Önceki bültenlerde geçen 5 haber elendi.

## 🔴 Son Dakika

### 1. OpenAI, yapay zeka biyoteknoloji girişimi Orchestra Bio'yu satın aldı
- TechCrunch'a göre OpenAI, dört yıllık Orchestra Bio'yu salı günü satın aldığını kendi sitesinde duyurdu; anlaşma bedeli açıklanmadı. Orchestra, biyoteknoloji şirketleri için ilaç keşfi operasyonlarını (finans takibi, klinik araştırma planlaması) yöneten yapay zeka ajanları geliştiriyor ve 2025 itibarıyla yaklaşık 20 milyon dolar yatırım almıştı.
- OpenAI ekibi ve teknolojiyi, yaşam bilimleri modeli Rosalind'e ve deney planlamaya yardım eden Rosalind Workbench'e ekleyecek. TechCrunch'a göre Moderna ve Novo Nordisk, Rosalind'in müşterileri arasında; OpenAI'ın duyuru sayfası okunamadı.
- Kaynak: [TechCrunch](https://techcrunch.com/2026/10/20/openai-acquires-startup-orchestra-bio%e2%81%a0-to-beef-up-its-biotech-business)

### 2. SpaceX ve Tesla birleşmeyi görüşmek için komite kurdu
- Axios'a göre Elon Musk, SpaceX'in bilanço toplantısında iki şirketin potansiyel birleşmeyi görüşmek üzere özel komiteler oluşturduğunu söyledi ve bunun "iyi bir fikir" olduğunu belirtti. Axios, iki şirketin çip ve yapay zeka projelerinde giderek daha çok iş birliği yaptığını not ediyor; Axios metni okunamadı, akış özetine dayanır.
- TechCrunch'a göre SpaceX, SpaceX'in yasal başvurusundaki rakamlarla üçüncü çeyrekte 14,6 milyar dolar gelir ve 4,4 milyar dolar net kâr bildirdi. Yapay zeka birimi (Cursor, Grok ve 1,7 GW'lık bulut hesaplama işi) 7,5 milyar dolar gelir getirdi; birimin kârı, Cursor satın alımına bağlı 1,2 milyar dolarlık hisse tazminatı sonrası 431 milyon dolar.
- Kaynak: [Axios](https://axios.com/2026/10/20/spacex-tesla-merger-talks) · [TechCrunch](https://techcrunch.com/2026/10/20/spacexs-ai-business-is-beating-expectations)

### 3. Meta, Muse sohbet paylaşımını durdurdu
- Güvenlik firması Claroc'un raporuna göre Muse'un paylaşım bağlantıları sohbet başlığından türetilen alan adlarıyla oluşturuluyor; herkese açık DNS kayıtlarından 6.800'den fazla bağlantı bulundu. Ars Technica'ya göre açılan birkaç yüz sohbetin arasında bir şirketin gelir raporu, bir kredi başvurusu ve bir banka dolandırıcılık uyarısı vardı.
- Claroc, bulguyu 8 Ekim'de Meta'nın ödül programına bildirdiğini söylüyor. Meta, paylaşım özelliğini raporu incelerken durdurduğunu ve bağlantıların bulunma biçimini değiştirmeyi düşündüğünü açıkladı. Claroc raporunun kendisi okunamadı.
- Kaynak: [Ars Technica](https://arstechnica.com/security/2026/10/meta-muse-exposes-users-personal-and-business-secrets-when-they-share-conversations) · [The Verge](https://theverge.com/tech/1014627/meta-muse-ai-sharing-ai-chats)

### 4. Mistral, Voxtral 3 ses modelleri ve sesli ajan SDK'sını duyurdu ✅
- Voxtral 3 ailesi konuşma tanıma (Small Transcribe 3, Mini Transcribe Realtime 3), konuşma sentezi (Voxtral Speech 3) ve LiveKit tabanlı bir sesli ajan SDK'sı içeriyor. Transkripsiyon 50'den fazla dili, konuşmacı ayrımını ve anahtar kelime ipucunu destekliyor; gerçek zamanlı model 500 ms altı gecikme hedefliyor.
- Fiyatlar dakika başına 0,0035 dolardan başlıyor; Voxtral Speech 3 için 1 milyon karakter 13 dolar. Mistral'in kendi ölçümlerine göre Small Transcribe 3, konuşmacı ayrımında Whisper ve Scribe v2'den iyi (cpWER %18,4); sentez sonuçları Mistral'in iç değerlendirmesi. Sayfa lisans belirtmiyor, kendi altyapında çalıştırma mümkün.
- Kaynak: [Mistral](https://mistral.ai/news/voxtral-3)

---

## 🧭 Stratejik Gelişmeler

### 5. Google TorchTPU'yu açık kaynak yaptı; Hugging Face desteği hazır ✅
- Hugging Face'e göre TorchTPU, PyTorch için yerel bir TPU arka ucu; `torch_xla` veya JAX gerekmeden TPU "başka bir cihaz" olarak kullanılıyor. Transformers v5, Diffusers ve Kernels doğrudan destekliyor; TPU üzerinde çalışan Transformers testlerinin %96,5'i geçiyor.
- TechCrunch'a göre bu, Amazon'un dünkü bültende anılan TorchNeuron hamlesinin ardından Google'ın Nvidia'nın yazılım avantajını aşındırma girişimi; Meta, Hugging Face, vLLM ve SGLang yapımcılarıyla uyumluluk çalışılmış. Hugging Face'in v6e-4 ölçümlerinde 1024×1024 görüntü üretimi derlenmiş modda 3,5 saniye. Google'ın kendi duyurusu okunamadı.
- Kaynak: [Hugging Face](https://huggingface.co/blog/hf-torchtpu) · [TechCrunch](https://techcrunch.com/2026/10/20/google-has-joined-amazon-in-attacking-nvidias-stronghold-with-ai-app-developers)

### 6. Anthropic'in taslak yasası: 50'den fazla ölüm riski olan model durdurulabilir
- TechCrunch, Politico'nun 16 Ekim'de haberleştirdiği taslağı aktarıyor; Anthropic sözcüsü taslağın varlığını Politico'ya doğruladı. Taslağa göre biyolojik silah, geliştiricinin denetiminden çıkma veya siber saldırı kaynaklı "öngörülebilir, yakın" bir risk (50'den fazla ölüm veya 1 milyar doların üstünde mal hasarı) bir modelin yayımını engelleyebilir.
- Bağımsız değerlendiriciler Ticaret Bakanlığı'na kayıt olacak, riski 72 saat içinde bildirecek ve bakanlık bir federal yargıçtan yayımın durdurulmasını isteyecek. Eşikler California'nın SB 53'üne benziyor; TechCrunch, laboratuvarların değerlendiricilere ödeme yapmasının sonucu nasıl etkilemeyeceğinin belirsiz olduğunu yazıyor. Taslak metni okunamadı.
- Kaynak: [TechCrunch (Politico aktarımı)](https://techcrunch.com/2026/10/20/anthropic-pitches-ai-safety-bill-that-may-block-a-model-if-50-people-could-be-killed)

### 7. Microsoft egemen bulut seçeneklerini genişletti ✅
- Microsoft Specialized Clouds'dan Douglas Phillips'in yazısına göre AB ve EFTA müşterileri için Data Guardian (Microsoft mühendislerinin uzaktan erişimine güvenilir bir AB ortağının gözetimi) kademeli sunuluyor; Production Touch Ledger bu erişimin değiştirilemez kaydını tutacak. Azure Managed HSM ile harici anahtar yönetimi genel kullanıma açıldı.
- Azure Local'da Foundry Local, GitHub Enterprise Local ve gizli sanal makineler Ignite'ta genel kullanıma giriyor; Microsoft 365 Local seçili müşteriler için önizlemede. Yazı ulusal ortak bulutlar olarak Fransa'da Bleu, Almanya'da Delos'u anıyor; çoklu kiracılık için tarih verilmiyor.
- Kaynak: [Microsoft](https://blogs.microsoft.com/blog/2026/10/20/advancing-digital-sovereignty-with-greater-control-and-choice)

### 8. Spotify, önerilerinden 50 milyondan fazla yapay zeka "çöp" parçayı çıkardı
- The Verge'e göre Spotify, geçen yıl içinde yapay zekayla üretilmiş çöp veya spam sayılan 50 milyondan fazla parçayı kullanıcı önerilerinden çıkardığını duyurdu ve öneri sistemini insan sanatçıları öne çıkaracak şekilde değiştirdi. Şirket, editörlerinin de bu içerikleri programlamadığını söylüyor.
- Spotify tüm yapay zeka parçalarına etiket zorunluluğu getirmedi; gerçek kişiyi temsil etmeyen yapay zeka kimlikleri için "AI Persona" rozeti başlattı ve bu kimliklerin müziğini önermiyor. YouTube Music yapay zeka şarkılarını etiketliyor, Deezer filtre seçeneği sunuyor, Bandcamp ise yapay zeka müziğini yasakladı. Spotify'ın duyurusu okunamadı.
- Kaynak: [The Verge](https://theverge.com/entertainment/1014284/spotify-ai-slop-spam-songs-removed)

---

## 🟡 Söylentiler / Doğrulanmamışlar

### 9. Nvidia'nın, halka arzdan vazgeçen Firmus'a yatırım için görüştüğü öne sürüldü
- The Information, bu ay başında halka arzını aniden geri çeken Avustralyalı yapay zeka bulut sağlayıcısı Firmus'a Nvidia'nın yüz milyonlarca dolarlık yatırım için görüştüğünü yazdı. Haber "konuya yakın kişiler"e dayanıyor; resmi teyit yok.
- Bloomberg, haberi The Information'a atıfla aktardı. Nvidia'nın yorumu görülmedi; The Information metni okunamadı, akış özetine dayanır.
- Kaynak: [Bloomberg (The Information aktarımı)](https://bloomberg.com/news/articles/2026-10-20/nvidia-in-talks-to-back-firmus-after-ipo-flop-information-says)

### 10. Anthropic'in önümüzdeki yıllarda 750 milyar dolar hesaplama harcayabileceği öne sürüldü
- Bloomberg'e göre Wall Street Journal, Anthropic'in halka arz hazırlığı sırasında ek hesaplama gücüne yaklaşık 750 milyar dolar harcayabileceğini bildirdi. Rakam şirket açıklaması değil, basın aktarımı; resmi teyit yok.
- Anthropic'in yorumu görülmedi; WSJ ve Bloomberg metinleri okunamadı, yalnızca akış özeti kullanıldı.
- Kaynak: [Bloomberg (WSJ aktarımı)](https://bloomberg.com/news/articles/2026-10-20/anthropic-could-spend-750-billion-on-computing-costs-wsj-says)

---

**Radarda (kısa):** Google'ın kişiselleştirilmiş Gemini'si arabalara geliyor (The Verge, 21 Ekim) · Ars Technica'ya göre Meta'dan, yapay zeka eğitimi için torrent indirmeyi onaylayan yöneticilerin isimlerini vermesi istendi (20 Ekim) · OpenAI, ChatGPT'de PIN veya biyometrikle sohbet kilidi başlattı (TechCrunch, 20 Ekim) · Meta'nın Muse uygulaması 40 günde ABD'de 10 milyon indirmeye ulaştı (TechCrunch, 20 Ekim)

*Bu bülten otomatik hazırlanmıştır. ✅ işareti olmayan maddeler, birincil kaynağı okunamadığı için ikincil kaynaklara dayanır. Yatırım tavsiyesi değildir.*
