#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⭐ CONFIDENCE SCORE PREDICTOR - Termux Edition (FINAL FIX)
GitHub Integration • Multi-Factor Analysis • Visual Display • Export TXT
"""

import requests
import re
import os
import time
from collections import Counter
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
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'

def clear_print(text):
    """Wrapper for print with safe execution"""
    try:
        print(text)
        return True
    except Exception as e:
        print(f"PRINT ERROR: {str(e)[:100]}")
        return False

def get_bar(score):
    filled = int((score / 100) * 50)
    empty = 50 - filled
    bar = "█" * filled + "░" * empty
    if score >= 80:
        return f"{Colors.GREEN}[{bar}]{Colors.RESET}"
    elif score >= 60:
        return f"{Colors.YELLOW}[{bar}]{Colors.RESET}"
    elif score >= 40:
        return f"{Colors.BLUE}[{bar}]{Colors.RESET}"
    else:
        return f"{Colors.WHITE}[{bar}]{Colors.RESET}"

def get_icon(score):
    if score >= 80:
        return f"{Colors.GREEN}🔥 HIGH{Colors.RESET}"
    elif score >= 60:
        return f"{Colors.GREEN}⭐ MEDIUM{Colors.RESET}"
    elif score >= 40:
        return f"{Colors.YELLOW}⚠️ LOW{Colors.RESET}"
    else:
        return f"{Colors.RED}❌ VERY LOW{Colors.RESET}"

def get_rec(score):
    if score >= 80:
        return "Prioritaskan semua angka! ✅"
    elif score >= 60:
        return "Gunakan 60-70% kombinasi ⚠️"
    elif score >= 40:
        return "Pertimbangkan ulang 📉"
    else:
        return "JANGAN MAIN! ❌"

# ========== FUNGSI FETCH DATA ==========
def fetch_github_csv(market_key):
    if market_key not in MARKET_FILES:
        return None
    url = f"https://raw.githubusercontent.com/{GITHUB_CONFIG['username']}/{GITHUB_CONFIG['repo']}/{GITHUB_CONFIG['branch']}/{GITHUB_CONFIG['path']}/{MARKET_FILES[market_key][1]}"
    try:
        clear_print(f"{Colors.CYAN}📡 Mengambil data dari GitHub...{Colors.RESET}")
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        return r.text
    except Exception as e:
        clear_print(f"{Colors.RED}❌ Error: {e}{Colors.RESET}")
        return None

# ========== FUNGSI PARSE CSV ==========
def parse_csv(text):
    if not text:
        return [], []
    results, dates = [], []
    lines = text.strip().split('\n')[1:]
    for line in lines:
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
    if len(data) < 15:
        return [(i, 30.0) for i in range(10)]
    freq = Counter(digit for num in data if len(num) == 4 for digit in num)
    max_f = max(freq.values()) or 1
    scores = {}
    for digit in range(10):
        sc = 0
        sc += (freq.get(str(digit), 0) / max_f) * 30
        scores[digit] = min(100, round(sc, 2))
    sorted_s = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return sorted_s[:10]

# ========== MAIN MENU ==========
def main():
    os.system('clear')
    clear_print("\n" + "="*50)
    clear_print(f"{Colors.MAGENTA}   ⭐ CONFIDENCE SCORE PREDICTOR{Colors.RESET}")
    clear_print("="*50)
    clear_print("\n📊 PILIH PASARAN:")
    for k, v in MARKET_NAMES.items():
        clear_print(f"   {k}. {v}")
    try:
        choice = int(input(f"{Colors.GREEN}\n➤ Nomor Pasaran (1-10) atau 0 untuk Demo Mode: {Colors.RESET}"))
        if choice == 0:
            choice = 1
        elif choice not in MARKET_FILES:
            raise ValueError
    except:
        clear_print(f"{Colors.RED}❌ Input salah!{Colors.RESET}")
        choice = 0
    if choice == 0:
        clear_print(f"\n{Colors.YELLOW}🎮 DEMO MODE (Dummy Data){Colors.RESET}")
        data = ['3721','5614','3892','7145','3267','8153','3941','6728','3519','4236',
                '1045','6283','9517','2364','7891','4156','8723','5647','2398','6514',
                '3825','7169','4538','9271','6453','2197','5843','8261','4679','3054',
                '7382','9156','5472','1863','6294']
        m_name = "Demo Mode"
    else:
        m_name = MARKET_NAMES[choice]
        clear_print(f"\n{Colors.CYAN}🔄 Loading {m_name}...{Colors.RESET}")
        csv = fetch_github_csv(choice)
        if not csv:
            clear_print(f"{Colors.RED}❌ Gagal ambil data. Cek internet!{Colors.RESET}")
            input("\nTekan Enter kembali...")
            return
        data, _ = parse_csv(csv)
        if len(data) < 15:
            clear_print(f"{Colors.RED}❌ Data kurang ({len(data)}). Minimal 15.{Colors.RESET}")
            input("\nTekan Enter kembali...")
            return
        clear_print(f"{Colors.GREEN}✅ Data: {len(data)} putaran. Memproses...{Colors.RESET}")
        time.sleep(1)

    # Hitung skor digit
    all_scores = calc_digit_scores(data)
    avg = sum(s for d, s in all_scores) / len(all_scores)

    clear_print("\n" + "="*50)
    clear_print(f"{Colors.MAGENTA}⭐ HASIL CONFIDENCE: {m_name}{Colors.RESET}")
    clear_print("="*50)
    clear_print(f"Rata-rata skor digit: {avg:.1f}%")

    for rank, (digit, score) in enumerate(all_scores, 1):
        ic = "🔥" if score >= 70 else "⭐" if score >= 50 else "⚠️" if score >= 30 else "⚪"
        bar = get_bar(score)
        clear_print(f"{rank}. {ic} Digit {digit} - {score:.1f}% {bar}")

    # Save Option
    save = input(f"{Colors.GREEN}\n💾 Simpan ke file? (y/n): {Colors.RESET}").lower()
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
            f.write(f"Score: {avg:.1f}%\n")
            f.write(f"Status: {get_icon(avg)}\n")
            f.write(f"Recommendation: {get_rec(avg)}\n\n")
            f.write("DETAIL PER DIGIT:\n")
            for digit, score in all_scores:
                f.write(f"Digit {digit}: {score:.1f}%\n")
            f.write("\n" + "="*50 + "\n")
            f.write("Gunakan dengan bijak. Good luck! 🍀\n")
        clear_print(f"\n{Colors.GREEN}✅ Tersimpan di: {path}{Colors.RESET}")

    clear_print(f"\n{Colors.CYAN}⭐ Selesai. Jalankan lagi untuk pasaran lain.{Colors.RESET}")
    input("\nTekan Enter untuk keluar...")

# ========== ENTRY POINT ==========
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        clear_print(f"\n\n{Colors.YELLOW}⚠️ Dibatalkan.{Colors.RESET}")
    except Exception as e:
        clear_print(f"\n{Colors.RED}❌ Error utama: {e}{Colors.RESET}")
        import traceback
        traceback.print_exc()