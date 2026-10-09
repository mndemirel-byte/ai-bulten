#!/usr/bin/env node
// Başsız tarayıcıyla makale metni okur (WebFetch'in açamadığı siteler için yedek).
//
//   node scripts/oku.js URL [URL...]            metni basar (her URL için en fazla 8000 karakter)
//   node scripts/oku.js --liste URL             sayfadaki haber bağlantılarını (başlık | url) basar
//   node scripts/oku.js --max 3000 URL          karakter sınırı
//
// Bot koruması (401/403, "verify you are human", "Access Denied") görülen sayfa ENGELLİ olarak
// raporlanır ve atlanır: bu siteler otomatik erişimi istemiyor; aşmaya çalışılmaz.
// Chromium bulut oturumunda /opt/pw-browsers/chromium yolunda hazırdır; "playwright install" GEREKMEZ.

const { execSync } = require('child_process');

function playwrightYukle() {
  try { return require('playwright'); } catch (_) {}
  const kok = execSync('npm root -g').toString().trim();
  return require(kok + '/playwright');
}

const ENGEL = /verify you are human|verifying you are not a bot|access denied|not a robot|security verification|enable javascript and cookies to continue/i;

(async () => {
  const args = process.argv.slice(2);
  let liste = false, max = 8000;
  const urller = [];
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--liste') liste = true;
    else if (args[i] === '--max') max = parseInt(args[++i], 10);
    else urller.push(args[i]);
  }
  if (!urller.length) { console.error('kullanım: node scripts/oku.js [--liste] [--max N] URL...'); process.exit(2); }

  const { chromium } = playwrightYukle();
  const exe = require('fs').existsSync('/opt/pw-browsers/chromium') ? '/opt/pw-browsers/chromium' : undefined;
  const tarayici = await chromium.launch({ executablePath: exe });
  const baglam = await tarayici.newContext({ locale: 'en-US' });
  let engelli = 0;
  for (const u of urller) {
    const sayfa = await baglam.newPage();
    try {
      const yanit = await sayfa.goto(u, { timeout: 30000, waitUntil: 'domcontentloaded' });
      await sayfa.waitForTimeout(1500);
      const durum = yanit ? yanit.status() : 0;
      const govde = await sayfa.evaluate(() => document.body ? document.body.innerText : '');
      if (durum === 401 || durum === 403 || ENGEL.test(govde.slice(0, 1500))) {
        console.log(`### ${u} ${durum} ENGELLİ (bot koruması; atlandı)\n`);
        engelli++;
        continue;
      }
      if (liste) {
        const baglantilar = await sayfa.$$eval('a', as => {
          const g = new Set();
          return as.map(a => [a.innerText.trim().replace(/\s+/g, ' '), a.href])
            .filter(([t, h]) => t.length > 35 && /^https?:/.test(h) && !g.has(h) && g.add(h));
        });
        console.log(`### ${u} ${durum} LİSTE`);
        for (const [t, h] of baglantilar) console.log(`${t} | ${h}`);
        console.log('');
      } else {
        const baslik = await sayfa.title();
        console.log(`### ${u} ${durum} OK\nBaşlık: ${baslik}\n${govde.replace(/\n{2,}/g, '\n').slice(0, max)}\n`);
      }
    } catch (e) {
      console.log(`### ${u} HATA ${String(e.message).split('\n')[0]}\n`);
    } finally {
      await sayfa.close();
    }
  }
  await tarayici.close();
  process.exit(engelli === urller.length && urller.length > 0 ? 1 : 0);
})();
