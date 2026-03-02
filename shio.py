#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🐲 SHIO & NUMBER PREDICTOR 2D Edition
GitHub Integration • Multi-Factor Analysis • Export TXT • Colored Output
"""

import requests
import re
import os
import time
from collections import Counter, defaultdict
from datetime import datetime

# ========== KONFIGURASI GITHUB ==========
GITHUB_CONFIG = {
    'username': 'MOMODIGITAL',
    'repo': 'data-vault',
    'branch': 'main',
    'path': 'data'
}

MARKET_FILES = {
    1: ('magnum-cambodia', 'magnum-cambodia.csv'),
    2: ('sydney-pools', 'sydney-pools.csv'),
    3: ('sydney-lotto', 'sydney-lotto.csv'),
    4: ('china-pools', 'china-pools.csv'),
    5: ('singapore', 'singapore.csv'),
    6: ('taiwan', 'taiwan.csv'),
    7: ('hongkong-pools', 'hongkong-pools.csv'),
    8: ('hongkong-lotto', 'hongkong-lotto.csv'),
    9: ('newyork-evening', 'newyork-evening.csv'),
    10: ('kentucky-evening', 'kentucky-evening.csv')
}

MARKET_NAMES = {
    1: 'Magnum Cambodia',
    2: 'Sydney Pools',
    3: 'Sydney Lotto',
    4: 'China Pools',
    5: 'Singapore',
    6: 'Taiwan',
    7: 'Hongkong Pools',
    8: 'Hongkong Lotto',
    9: 'New York Evening',
    10: 'Kentucky Evening'
}

# ========== DAFTAR SHIO CHINESE ==========
SHIO_LIST = ['Tikus', 'Sapi', 'Macan', 'Kelinci', 'Naga', 'Ular',
             'Kuda', 'Kambing', 'Monyet', 'Ayam', 'Anjing', 'Babi']

ELEMENT_COLOR = ['Air', 'Kayu', 'Api', 'Tanah', 'Logam']

# ========== WARNA ANSI ==========
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'

def cprint(text, color=Colors.RESET):
    print(f"{color}{text}{Colors.RESET}")

# ========== FUNGSI FETCH DATA ==========
def fetch_github_csv(market_key):
    file_info = MARKET_FILES.get(market_key)
    if not file_info:
        return None
    url = f"https://raw.githubusercontent.com/{GITHUB_CONFIG['username']}/{GITHUB_CONFIG['repo']}/{GITHUB_CONFIG['branch']}/{GITHUB_CONFIG['path']}/{file_info[1]}"
    try:
        cprint("📡 Mengambil data dari GitHub...", Colors.CYAN)
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        return r.text
    except Exception as e:
        cprint(f"❌ Error: {e}", Colors.RED)
        return None

# ========== FUNGSI PARSE CSV ==========
def parse_csv(text):
    if not text:
        return [], []
    results, dates = [], []
    for line in text.strip().split('\n')[1:]:
        if not line:
            continue
        parts = line.split(',')
        if len(parts) >= 2:
            match = re.search(r'\d{4}', parts[1].strip())
            if match:
                dates.append(parts[0].strip())
                results.append(match.group())
    return results, dates

# ========== FUNGSI CONVERT DIGIT AKHIR KE SHIO ==========
def convert_digit_to_shio(last_digit):
    if str(last_digit) not in '0123456789':
        return None, "", ""
    last_num = int(last_digit) % 12
    shio_name = SHIO_LIST[last_num]
    element_idx = (last_num // 2) % 5
    element = ELEMENT_COLOR[element_idx]
    shio_no = str(last_num + 1)
    return shio_name, element, shio_no

# ========== FUNGSI ANALISIS SHIO ==========
def predict_shio_hybrid(data):
    if len(data) < 15:
        return []
    freq_scores = defaultdict(float)
    decay_scores = defaultdict(float)
    gap_scores = defaultdict(float)
    streak_bonus = defaultdict(int)
    shio_count = Counter(int(num[-1]) % 12 for num in data if len(num) >= 4)
    max_freq = max(shio_count.values()) or 1
    for shio, count in shio_count.items():
        freq_scores[shio] = (count / max_freq) * 40
    for idx, num in enumerate(reversed(data)):
        if len(num) >= 4:
            shio = int(num[-1]) % 12
            weight = 0.98 ** idx
            decay_scores[shio] += weight * 30
    last_seen = {}
    for idx, num in enumerate(data):
        if len(num) >= 4:
            shio = int(num[-1]) % 12
            if shio in last_seen:
                gap = idx - last_seen[shio]
                if gap > 15:
                    gap_scores[shio] += 20
                elif gap > 10:
                    gap_scores[shio] += 15
                elif gap > 5:
                    gap_scores[shio] += 10
            last_seen[shio] = idx
    for i in range(len(data)-1):
        if len(data[i]) >= 4 and len(data[i+1]) >= 4:
            s1 = int(data[i][-1]) % 12
            s2 = int(data[i+1][-1]) % 12
            if s1 == s2:
                streak_bonus[s1] += 5
    final_scores = {}
    for shio in range(12):
        total = (freq_scores[shio] * 0.30) + (decay_scores[shio] * 0.40) + (gap_scores[shio] * 0.20) + (streak_bonus[shio] * 0.10)
        final_scores[shio] = min(100, round(total, 2))
    sorted_shios = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)
    return [(idx, score) for idx, score in sorted_shios[:12]]

# ========== FUNGSI GET_SHIO_STATS ==========
def get_shio_stats(data):
    stats = {}
    for shio_idx in range(12):
        name = SHIO_LIST[shio_idx]
        last_digits = [str(idx) for idx in range(10) if idx % 12 == shio_idx]
        appears = sum(1 for num in data if len(num) >= 4 and int(num[-1]) % 12 == shio_idx)
        percentage = (appears / len(data) * 100) if len(data) > 0 else 0
        stats[shio_idx] = {
            'name': name,
            'digit': ', '.join(last_digits) if last_digits else '-',
            'count': appears,
            'percentage': percentage
        }
    return stats

# ========== MAIN MENU ==========
def main():
    os.system('clear')
    print("\n" + "="*50)
    cprint("   🐲 SHIO & NUMBER PREDICTOR (2D EDITION)", Colors.MAGENTA + Colors.BOLD)
    print("="*50)

    print("\n📊 PILIH PASARAN:")
    for k, v in MARKET_NAMES.items():
        cprint(f"   {k}. {v}", Colors.WHITE)

    print("\n💡 Catatan: Pilihan pasaran akan di-load dari GitHub")

    try:
        choice = int(input(Colors.GREEN + "\n➤ Nomor Pasaran (1-10) atau 0 untuk Demo Mode: " + Colors.RESET))
        if choice == 0:
            choice = 1
        elif choice not in MARKET_FILES:
            raise ValueError
    except:
        cprint("❌ Input salah!", Colors.RED)
        choice = 0

    if choice == 0:
        cprint("\n🎮 DEMO MODE (Dummy Data)", Colors.YELLOW)
        dummy_data = [
            '3721','5614','3892','7145','3267','8153','3941','6728','3519','4236',
            '1045','6283','9517','2364','7891','4156','8723','5647','2398','6514',
            '3825','7169','4538','9271','6453','2197','5843','8261','4679','3054',
            '7382','9156','5472','1863','6294'
        ]
        m_name = "Demo Mode"
        data = dummy_data
        cprint("\n✅ Menggunakan data dummy (35 putaran)")
        cprint("🔧 Tip: Pilih 1-10 untuk data GitHub asli", Colors.CYAN)
    else:
        m_name = MARKET_NAMES[choice]
        cprint(f"\n🔄 Loading {m_name}...", Colors.CYAN)
        csv = fetch_github_csv(choice)
        if not csv:
            cprint("❌ Gagal ambil data. Cek internet!", Colors.RED)
            cprint("💡 Gunakan DEMO MODE (ketik 0)", Colors.YELLOW)
            input("\nTekan Enter kembali...")
            return
        data, _ = parse_csv(csv)
        if len(data) < 15:
            cprint(f"❌ Data kurang ({len(data)}). Minimal 15.", Colors.RED)
            input("\nTekan Enter kembali...")
            return
        cprint(f"✅ Data: {len(data)} putaran. Memproses...", Colors.GREEN)
        time.sleep(1)

    cprint("\n🔬 Analisa pola Shio...", Colors.CYAN)
    time.sleep(1)

    shio_predictions = predict_shio_hybrid(data)
    shio_stats = get_shio_stats(data)

    cprint("\n" + "="*50, Colors.CYAN)
    cprint(f"🐲 HASIL SHIO PREDIKSI: {m_name}", Colors.MAGENTA + Colors.BOLD)
    cprint("="*50, Colors.CYAN)

    cprint("\n📊 TOP 7 SHIO KUAT:", Colors.YELLOW)
    print("-"*50)
    for rank, (shio_idx, score) in enumerate(shio_predictions[:7], 1):
        shio_name = SHIO_LIST[shio_idx]
        element_idx = (shio_idx // 2) % 5
        element = ELEMENT_COLOR[element_idx]
        icon = "🔥" if score >= 70 else ("⭐" if score >= 50 else ("⚠️" if score >= 30 else "⚪"))
        bar_len = int(score / 2)
        bar = "█" * bar_len + "░" * (50 - bar_len)
        cprint(f"#{rank}. {icon} {shio_name:<8} [{bar}] {score:>5.1f}% {element}",
               Colors.GREEN if score >= 70 else Colors.YELLOW if score >= 50 else Colors.WHITE)

    cprint("\n📋 SEMUA STATISTIK SHIO:", Colors.BLUE)
    print("-"*50)
    cprint(f"{'Shio':<10} {'Digit':<12} {'Count':<8} {'%':<8} {'Icon'}", Colors.CYAN)
    print("-"*50)
    for shio_idx in range(12):
        info = shio_stats[shio_idx]
        icon = "🔥" if info['percentage'] >= 10 else "⭐" if info['percentage'] >= 7 else "⚪"
        cprint(f"{info['name']:<10} {info['digit']:<12} {info['count']:<8} {info['percentage']:.1f}% {icon}",
               Colors.GREEN if info['percentage'] >= 10 else Colors.YELLOW if info['percentage'] >= 7 else Colors.WHITE)

    # Converter Feature
    cprint("\n" + "="*50, Colors.CYAN)
    cprint("🔢 FITUR CETAK COCOK - ANGKA 2D KE SHIO", Colors.MAGENTA + Colors.BOLD)
    cprint("="*50, Colors.CYAN)

    print("""
📌 CARA PENGGUNAAN:
──────────────────────────────────────────────
1️⃣ Ketik angka 2D pilihan Anda (contoh: 16, 27, 38)
2️⃣ Sistem akan cek Shio dari angka tersebut
3️⃣ Dibandingkan dengan prediksi Shio hari ini
4️⃣ Jika MATCH → Angkanya kuat sesuai pola! 🔥
──────────────────────────────────────────────
""")

    while True:
        angka_2d = input("\n➤ Angka 2D: ").strip()
        if not angka_2d:
            break
        if not angka_2d.isdigit() or len(angka_2d) != 2:
            cprint("❌ Masukkan tepat 2 digit angka", Colors.RED)
            continue
        digit_last = int(angka_2d[-1])
        shio_name, element, shio_no = convert_digit_to_shio(digit_last)
        if shio_name:
            cprint(f"\nAngka 2D        : {angka_2d}", Colors.WHITE)
            cprint(f"Digit Terakhir  : {digit_last}", Colors.WHITE)
            cprint(f"Shio            : {shio_name.upper()} {element}", Colors.MAGENTA)
            cprint(f"Nomor Shio      : {shio_no}/12", Colors.CYAN)
            found_rank = False
            for i, (shio_idx, score) in enumerate(shio_predictions[:7], 1):
                if SHIO_LIST[shio_idx] == shio_name:
                    found_rank = True
                    icon_match = "✅ MATCH!" if score >= 60 else ("⚠️ OK" if score >= 40 else "❌ LEMAH")
                    cprint(f"Rank Prediksi   : #{i} ({score:.1f}%) {icon_match}",
                           Colors.GREEN if score >= 60 else Colors.YELLOW if score >= 40 else Colors.RED)
                    break
            if not found_rank:
                cprint("Shio tidak masuk Top 7 Prediksi ⚠️", Colors.YELLOW)

    save = input(Colors.GREEN + "\n💾 Simpan ke file? (y/n): " + Colors.RESET).lower()
    if save == 'y':
        fname = f"shio_{m_name.replace(' ', '_')}_{datetime.now().strftime('%H%M%S')}.txt"
        path = '/sdcard/Download/' + fname if os.path.exists('/sdcard') else fname
        with open(path, 'w', encoding='utf-8') as f:
            f.write("="*50 + "\n")
            f.write("  🐲 SHIO PREDICTOR - HASIL LENGKAP\n")
            f.write("="*50 + "\n")
            f.write(f"Pasaran: {m_name}\n")
            f.write(f"Tanggal: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write(f"Data: {len(data)} putaran\n\n")
            f.write("TOP 7 SHIO:\n")
            for rank, (shio_idx, score) in enumerate(shio_predictions[:7], 1):
                shio_name = SHIO_LIST[shio_idx]
                element_idx = (shio_idx // 2) % 5
                element = ELEMENT_COLOR[element_idx]
                f.write(f"#{rank}. {shio_name} ({element}) - {score:.1f}%\n")
            f.write("\nALL STATISTICS:\n")
            for shio_idx in range(12):
                info = shio_stats[shio_idx]
                f.write(f"{info['name']}: Digit {info['digit']} | Count {info['count']} | {info['percentage']:.1f}%\n")
            f.write("\n" + "="*50 + "\n")
            f.write("Gunakan dengan bijak. Good luck! 🍀\n")
        cprint(f"\n✅ Tersimpan di: {Colors.GREEN}{path}{Colors.RESET}", Colors.WHITE)

    cprint("\n🐲 Selesai. Jalankan lagi untuk pasaran lain.", Colors.CYAN)
    input("\nTekan Enter untuk keluar...")

# ========== ENTRY POINT ==========
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        cprint("\n\n⚠️ Dibatalkan.", Colors.YELLOW)
    except Exception as e:
        cprint(f"❌ Error: {e}", Colors.RED)