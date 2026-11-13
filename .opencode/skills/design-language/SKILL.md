---
name: design-language
description: Bahasa desain Dev.Team untuk dashboard dan alat internal. Berisi arah 5 baris, token warna/tipografi/gerak, sembilan lapis perbaikan, larangan slop, dan checklist. Muat saat membuat UI baru, merapikan tampilan yang terasa AI-generated, atau saat memilih warna, tipografi, spacing, radius, dan motion di proyek mana pun di repo ini.
license: CC-BY-4.0
---

# Bahasa desain Dev.Team

Panduan untuk semua UI di repo ini: dashboard, panel operasi, alat internal. Tujuannya satu — aplikasi terasa seperti **instrumen buatan orang yang paham domainnya**, bukan template AI.

Rujukan hidup: `projects/free-model-radar/src/styles.css` dan `projects/dark-fiber-core-manager/src/web/styles.css`.
Salinan publik: <https://github.com/ridayz/design-language>.

---

## 1. Kenapa UI terasa slop

Slop bukan selera jelek. Slop terjadi karena keputusan diambil per komponen, tanpa arah dan tanpa pengukuran. Tandanya selalu sama:

- gradient ungu/biru di background, teks bergradasi, glow berwarna
- emoji jadi ikon (`📊 Laporan`, `New ✨`)
- kartu kaca (glassmorphism), blob mengapung, border neon
- semua di tengah, semua kartu sama besar, jarak 13/17/22px
- animasi berdenyut tanpa alasan, hover `scale`
- angka palsu (`123.456`) dan klaim palsu (`10x lebih cepat`)

Bahasa desain ini menutup semuanya dengan aturan, bukan dengan "dibikin lebih keren".

---

## 2. Arah dulu, komponen kemudian

Sebelum menulis CSS, tulis lima baris. Tanpa ini hasilnya jadi template. Kalau perlu persetujuan, tunjukkan lima baris ini dulu dan tunggu.

| Baris | Isi |
| --- | --- |
| **Product** | Apa yang dikerjakan dan untuk siapa, satu kalimat |
| **Character** | 2–3 kata konkret (`tenang, presisi, hangat`) — bukan "modern/clean/premium" |
| **World** | Dunia/material asal produknya; ini yang menentukan tint netral dan aksen |
| **Moments** | 1–2 tempat yang boleh "kaya" warna/detail |
| **Signature** | satu detail kecil yang hanya produk ini punya |

Contoh nyata:

**Free Model Radar** — alat ukur katalog model gratis.
Product: memeringkat model gratis OpenRouter berdasarkan kepintaran, konteks, dan status API. Character: *tenang, presisi, sedikit hangat*. World: ruang NOC malam hari — instrumen, angka, kabel. Moments: scatter plot dan baris ranking. Signature: titik status hidup + sapuan radar.

**Dark Fiber Core Manager** — peta kapasitas core kabel backbone.
Product: mencatat core mana terpakai, oleh tenant siapa, sampai kapan. Character: *teknis, rapi, seperti papan kerja lapangan*. World: rak OTB, tabung fiber, label kabel. Moments: peta core 12 warna TIA-598. Signature: kode warna fiber yang konsisten di semua halaman.

---

## 3. Token

Semua nilai ada di token. Komponen tidak boleh punya warna atau jarak sendiri.

### Warna — satu ramp netral, satu aksen

```css
:root[data-theme="dark"] {
  --bg: #0b0c0e;
  --surface: #111316;
  --surface-2: #16181c;
  --surface-3: #1d2025;
  --line: rgba(233, 236, 241, 0.075);
  --line-strong: rgba(233, 236, 241, 0.14);
  --text: #e8eaee;      /* teks utama */
  --text-2: #a4aab4;    /* sekunder */
  --text-3: #6f7683;    /* meta, label */
  --accent: #f0a63c;    /* amber: aksi utama, angka penting, seleksi */
  --accent-soft: rgba(240, 166, 60, 0.14);
  --ok: #63b892;
  --bad: #d9756b;
}

:root[data-theme="light"] {
  --bg: #f3f2ef;
  --surface: #fbfaf8;
  --surface-2: #f2f1ed;
  --surface-3: #e9e8e3;
  --line: rgba(22, 24, 28, 0.09);
  --line-strong: rgba(22, 24, 28, 0.16);
  --text: #16181c;
  --text-2: #5a6069;
  --text-3: #868c96;
  --accent: #9c5b08;    /* versi gelap amber, supaya kontras teks cukup */
  --ok: #2f7d5b;
  --bad: #b2453a;
}
```

Aturan:

- Warna di luar ramp hanya **semantik** (ok/warn/bad). Tidak ada hue acak.
- Aksen dipakai hemat: tombol utama, seleksi, satu angka yang menentukan.
- Tema terang dan gelap punya token sendiri, bukan hasil invert.
- Border = warna teks dengan opasitas 7–16%, bukan abu-abu baru.
- Kedalaman di tema gelap datang dari **step surface + hairline**, bukan bayangan.

### Tipografi

```css
--font-sans: "Inter Tight", "Segoe UI Variable Text", "Segoe UI", system-ui, sans-serif;
--font-mono: "Cascadia Code", "JetBrains Mono", ui-monospace, Consolas, monospace;
```

- Body 14px, line-height 1.5. Label 11–12px.
- **Semua angka pakai mono** + `font-variant-numeric: tabular-nums`, supaya kolom rata.
- Heading besar: tracking negatif (−0,02 s/d −0,03em). Teks kecil: tanpa tracking negatif, dan jangan uppercase ber-tracking lebar.
- Berat 400/500, maksimal 600 untuk penekanan langka. Tidak ada 700–900.

### Bentuk

```css
--r-sm: 8px;   /* kontrol */
--r-md: 12px;  /* kartu */
--r-lg: 16px;  /* panel */
--r-xl: 20px;  /* panel besar */
```

Radius bersarang: radius dalam = radius luar − padding antar keduanya, minimal 4px.

### Gerak

```css
--ease: cubic-bezier(0.2, 0.7, 0.2, 1);
--t-fast: 160ms;   /* feedback: hover, press */
--t-mid: 260ms;    /* masuk/keluar panel */
--t-slow: 460ms;   /* perpindahan data */
```

- Satu easing untuk seluruh aplikasi.
- Hanya transisikan `color`, `background-color`, `border-color`, `opacity`, `transform`. Jangan `width`, `height`, `top`, `left`, `margin`, atau blur besar.
- Animasi harus membawa informasi: angka naik saat data berubah, baris berpindah pakai FLIP, dot masuk berurutan. Tidak ada denyut, parallax, atau float.

### Jarak

Skala 4px: 4, 8, 12, 16, 22, 32. Di luar skala hanya untuk pemusatan optis yang terukur.

- Padding: panel 16–20, kartu 16–18, tepi halaman 24–32.
- Sidebar = bagian terpadat: baris 32–36, gap 2–4, ikon satu kolom.
- Jarak di dalam grup < jarak antar grup, supaya hierarki terbaca tanpa garis tambahan.

---

## 4. Sembilan lapis perbaikan (urutan wajib)

Jangan loncat lapis. Spacing dulu karena semua terlihat berbeda setelah ritmenya benar.

1. **Spacing** — semua kelipatan 4; hal yang sama ukurannya sama; angka rata satu kolom.
2. **Warna** — satu ramp, tiga peran teks, satu aksen; buang gradient/glow/wash.
3. **Ikon** — satu set, satu ukuran (16–18px), stroke 1.5, ikut warna teksnya. Emoji jadi ikon garis.
4. **Copy** — label pendek, tanpa tanda seru, tanpa kata hype, tanpa sapaan. Perubahan menyebut pembandingnya (`−3 vs pindai sebelumnya`).
5. **Type** — beberapa ukuran, dua bobot. Hierarki dari ukuran dan warna, bukan ketebalan.
6. **Layout** — shell mengisi viewport, sidebar 240–280, konten fluid; jangan menyusut jadi kolom sempit. Grid `minmax(0, 1fr)` supaya tidak overflow.
7. **Detail** — radius bersarang, meta jadi teks mono redup (bukan pill menyala), fokus keyboard terlihat, hover = perubahan surface kecil.
8. **Visual** — dashboard hampir tidak butuh gambar. Momen datang dari produknya: chart yang digambar serius, angka yang ditata, status yang terasa hidup.
9. **Motion** — maksimal satu animasi masuk saat load, durasi pendek, easing sama.

---

## 5. Larangan

- Gradient hue pada surface, teks bergradasi, glow/warna pada bayangan, blob.
- Emoji sebagai ikon atau hiasan label.
- Glassmorphism, border neon, `hover:scale` pada kartu.
- `animate-pulse` pada hal yang tidak live.
- Uppercase ber-tracking lebar untuk label navigasi.
- Angka dengan format berbeda-beda dalam satu layar.
- Data palsu, `[X]`, `123.456`, atau klaim yang tidak bisa dicek.
- Menukar satu tren dengan tren lain (glass → grain → bento) sebagai "perbaikan".
- Menyalin tampilan aplikasi lain. Arah ditentukan dunia produknya.

---

## 6. Komponen khas

**Stat card** — label kecil (11px, `--text-3`), angka besar mono, satu baris kaki yang menyebut pembanding atau konteks. Tanpa sparkline, tanpa ikon hiasan.

**Ranking row** — nomor, nama, meta yang membungkus (bukan terpotong), satu angka besar di kanan, satu tombol aksi. Bar tipis sebagai pembanding, bukan pelangi.

**Matriks kapabilitas** — header sticky, angka rata kanan, kolom sempit boleh jadi kartu per baris di ≤760px.

**Panel detail (drawer)** — lebar `min(440px, 100vw)`, scroll sendiri, tutup dengan Esc dan scrim, `body` dikunci saat terbuka.

**Status** — titik 6px + teks pendek: `siap`, `sibuk`, `agentic only`, `kuota habis`. Jangan menutupi kegagalan dengan warna hijau.

---

## 7. Checklist sebelum selesai

- [ ] Arah 5 baris ditulis (walau hanya di commit message)
- [ ] Semua spacing kelipatan 4, hal serupa berspasi sama
- [ ] Satu ramp netral, 3 peran teks, 1 aksen, kontras teks ≥ 4.5:1
- [ ] Tidak ada gradient/glow/emoji/glass
- [ ] Angka mono + tabular, satu format
- [ ] Ikon satu set, satu ukuran
- [ ] Radius bersarang benar
- [ ] Animasi membawa informasi, satu easing, ≤ 3 durasi
- [ ] Screenshot di 1440 / 900 / 390, tidak ada overflow horizontal
- [ ] Console bersih, tidak ada error
- [ ] Copy tidak hype, tidak ada klaim palsu

---

## 8. Implementasi rujukan

| Aplikasi | Stack | Path |
| --- | --- | --- |
| Free Model Radar | Node + vanilla HTML/CSS/JS | `projects/free-model-radar/` |
| Dark Fiber Core Manager | Python stdlib + SQLite + vanilla | `projects/dark-fiber-core-manager/` |

Keduanya tanpa framework UI, tanpa CDN, tanpa build step — aturan di atas berlaku di CSS biasa.

---

## 9. Kredit

Prinsip dan struktur sembilan lapis mengacu pada skill **unslop** oleh Damir Sokolovsky ([@heydamir](https://x.com/heydamir), [heydamir.design/unslop](https://heydamir.design/unslop)), lisensi CC BY 4.0. Untuk pekerjaan unslop penuh (dengan video before/after), muat skill `unslop`.
