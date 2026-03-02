#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⭐ CONFIDENCE SCORE PREDICTOR - Termux Edition (FIXED)
GitHub Integration • Multi-Factor Analysis • Visual Display • Export TXT
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
    """Print text with color"""
    try:
        print(f"{color}{text}{Colors.RESET}")
    except:
        print(text)

# ========== FUNGSI FETCH DATA ==========
def fetch_github_csv(market_key):
    if market_key not in MARKET_FILES:
        return None
    url = f"https://raw.githubusercontent.com/{GITHUB_CONFIG['username']}/{GITHUB_CONFIG['repo']}/{GITHUB_CONFIG['branch']}/{GITHUB_CONFIG['path']}/{MARKET_FILES[market_key][1]}"
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
            if match and len(match.group()) == 4:
                dates.append(parts[0].strip())
                results.append(match.group())
    return results, dates

# ========== FUNGSI HITUNG SKOR DIGIT ==========
def calc_digit_scores(data):
    """Hitung skor detail untuk setiap digit 0-9"""
    if len(data) < 15:
        return [(i, 30.0) for i in range(10)]
    
    freq = Counter(digit for num in data if len(num) == 4 for digit in num)
    max_f = max(freq.values()) or 1
    
    scores = {}
    for digit in range(10):
        sc = 0
        # 1. Frekuensi
        sc += (freq.get(str(digit), 0) / max_f) * 25
        # 2. Time decay
        decay = 0
        for idx, num in enumerate(reversed(data)):
            if len(num) == 4 and str(digit) in num:
                decay += 0.98 ** idx
        sc += min(decay * 30, 25)
        # 3. Gap analysis
        gap = 0
        last_pos = -1
        for idx, num in enumerate(data):
            if len(num) == 4 and str(digit) in num:
                if last_pos >= 0:
                    gap = idx - last_pos
                last_pos = idx
        sc += min(gap / 2, 25)
        # 4. Streak bonus
        streak = 0
        for i in range(len(data)-1):
            if len(data[i]) == 4 and len(data[i+1]) == 4:
                if str(digit) in data[i] and str(digit) in data[i+1]:
                    streak += 1
        sc += min(streak * 3, 25)
        scores[digit] = min(100, round(sc, 2))
    
    sorted_s = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return sorted_s[:10]

# ========== MAIN MENU ==========
def main():
    os.system('clear')
    print("\n" + "="*50)
    cprint("   ⭐ CONFIDENCE SCORE PREDICTOR", Colors.MAGENTA + Colors.BOLD)
    print("="*50)
    
    print("\n📊 PILIH PASARAN:")
    for k, v in MARKET_NAMES.items():
        print(f"   {k}. {v}")
    
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
        data = [
            '3721','5614','3892','7145','3267','8153','3941','6728','3519','4236',
            '1045','6283','9517','2364','7891','4156','8723','5647','2398','6514',
            '3825','7169','4538','9271','6453','2197','5843','8261','4679','3054',
            '7382','9156','5472','1863','6294'
        ]
        m_name = "Demo Mode"
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
    
    # Hitung skor
    all_scores = calc_digit_scores(data)
    avg = sum(s for d, s in all_scores) / len(all_scores)
    
    print("\n" + "="*50)
    cprint(f"⭐ HASIL CONFIDENCE: {m_name}", Colors.MAGENTA + Colors.BOLD)
    print("="*50)
    cprint(f"Rata-rata skor digit: {avg:.1f}%", Colors.CYAN)
    for rank, (digit, score) in enumerate(all_scores, 1):
        icon = "🔥" if score >= 70 else ("⭐" if score >= 50 else ("⚠️" if score >= 30 else "⚪"))
        bar = "█" * int(score/2) + "░" * (50-int(score/2))
        cprint(f"{rank}. {icon} Digit {digit} [{bar}] {score:.1f}%", Colors.GREEN if score >= 70 else Colors.YELLOW if score >= 50 else Colors.WHITE)
    
   # Save Option
    save = input(Colors.GREEN + "\n💾 Simpan ke file? (y/n): " + Colors.RESET).lower()
    if save == 'y':
        fname = f"confidence_{m_name.replace(' ', '_')}_{datetime.now().strftime('%H%M%S')}.txt"
        path = '/sdcard/Download/' + fname if os.path.exists('/sdcard') else fname

        with open(path, 'w', encoding='utf-8') as f:
            f.write("="*50 + "\n")
            f.write("⭐ CONFIDENCE SCORE - HASIL LENGKAP\n")
            f.write("="*50 + "\n")
            f.write(f"Pasaran: {m_name}\n")
            f.write(f"Tanggal: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write(f"Data: {len(data)} putaran\n\n")

            f.write("OVERALL CONFIDENCE:\n")
            f.write(f"Score: {overall:.1f}%\n")
            f.write(f"Status: {get_icon(overall)}\n")
            f.write(f"Recommendation: {get_rec(overall)}\n\n")

            f.write("DETAIL PER DIGIT (TOP 10):\n")
            for digit, score in all_scores:
                f.write(f"Digit {digit}: {score:.1f}%\n")

            f.write("\n" + "="*50 + "\n")
            f.write("Gunakan dengan bijak. Good luck! 🍀\n")

        cprint(f"\n✅ Tersimpan di: {Colors.GREEN}{path}{Colors.RESET}", Colors.WHITE)

    cprint("\n⭐ Selesai. Jalankan lagi untuk pasaran lain.", Colors.CYAN)
    input("\nTekan Enter untuk keluar...")

# ========== ENTRY POINT ==========
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        cprint("\n\n⚠️ Dibatalkan.", Colors.YELLOW)
    except Exception as e:
        cprint(f"❌ Error: {e}", Colors.RED)