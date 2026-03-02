#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⭐ CONFIDENCE SCORE PREDICTOR - Termux Edition (FINAL STABLE)
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

def get_bar(score):
    """Create visual bar"""
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
    """Get status icon"""
    if score >= 80:
        return f"{Colors.GREEN}🔥 HIGH{Colors.RESET}"
    elif score >= 60:
        return f"{Colors.GREEN}⭐ MEDIUM{Colors.RESET}"
    elif score >= 40:
        return f"{Colors.YELLOW}⚠️ LOW{Colors.RESET}"
    else:
        return f"{Colors.RED}❌ VERY LOW{Colors.RESET}"

def get_rec(score):
    """Get recommendation"""
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
        print(f"{Colors.CYAN}📡 Mengambil data dari GitHub...{Colors.RESET}")
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        return r.text
    except Exception as e:
        print(f"{Colors.RED}❌ Error: {e}{Colors.RESET}")
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
    """Hitung skor detail untuk setiap digit 0-9"""
    if len(data) < 15:
        return [(i, 30.0) for i in range(10)]
    
    n = len(data)
    freq = Counter(digit for num in data for digit in num if len(num) == 4)
    max_f = max(freq.values()) if freq else 1
    
    scores = {}
    for digit in range(10):
        sc = 0
        
        # 1. Frekuensi (max 30)
        freq_score = min(30, (freq.get(digit, 0) / max_f) * 30)
        sc += freq_score
        
        # 2. Time decay (max 30)
        decay_sum = 0
        for idx, num in enumerate(reversed(data)):
            if len(num) == 4:
                weight = 0.98 ** idx
                for d_char in num:
                    if int(d_char) == digit:
                        decay_sum += weight
        dec_score = min(30, decay_sum * 30)
        sc += dec_score
        
        # 3. Gap analysis (max 25)
        last_pos = -1
        gap_sum = 0
        for idx, num in enumerate(data):
            if len(num) == 4 and str(digit) in num:
                if last_pos >= 0:
                    gap_sum += min(5, idx - last_pos)
                last_pos = idx
        gap_score = min(25, gap_sum)
        sc += gap_score
        
        # 4. Streak bonus (max 15)
        streak_count = 0
        for i in range(len(data)-1):
            if len(data[i]) == 4 and len(data[i+1]) == 4:
                if str(digit) in data[i] and str(digit) in data[i+1]:
                    streak_count += 1
        streak_score = min(15, streak_count * 3)
        sc += streak_score
        
        scores[digit] = min(100, round(sc, 2))
    
    sorted_s = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return sorted_s[:10]

# ========== DISPLAY SECTION FUNCTIONS ==========
def display_overall(score):
    """Display overall confidence"""
    print("\n" + "-"*50)
    print(f"{Colors.YELLOW}📊 OVERALL CONFIDENCE:{Colors.RESET}")
    print("-"*50)
    print(f"Score      : {Colors.GREEN}{score:.1f}%{Colors.RESET}")
    print(f"Status     : {get_icon(score)}")
    print(f"Rekomendasi: {Colors.CYAN}{get_rec(score)}{Colors.RESET}")
    print(f"Bar        : {get_bar(score)}")

def display_6a(score, all_scores):
    """Display 6 Angka confidence"""
    print("\n" + "-"*50)
    print(f"{Colors.BLUE}🔷 6 ANGKA CONFIDENCE{Colors.RESET}")
    print("-"*50)
    print(f"Score      : {Colors.GREEN}{score:.1f}%{Colors.RESET}")
    print(f"Status     : {get_icon(score)}")
    print(f"Rekomendasi: {Colors.CYAN}{get_rec(score)}{Colors.RESET}")
    print(f"Bar        : {get_bar(score)}")
    print(f"\nDigit Breakdown:{Colors.RESET}")
    for rank, (digit, s) in enumerate(all_scores[:6], 1):
        b = get_bar(s)
        ic = f"{Colors.GREEN}🔥{Colors.RESET}" if s >= 70 else \
             f"{Colors.YELLOW}⭐{Colors.RESET}" if s >= 50 else \
             f"{Colors.BLUE}⚠️{Colors.RESET}" if s >= 30 else \
             f"{Colors.WHITE}⚪{Colors.RESET}"
        print(f"  {rank}. {ic} Digit {digit:<2} - {s:.1f}%")

def display_3d(score, all_scores):
    """Display 3D TOP confidence"""
    print("\n" + "-"*50)
    print(f"{Colors.GREEN}🏆 3D TOP CONFIDENCE{Colors.RESET}")
    print("-"*50)
    print(f"Score      : {Colors.GREEN}{score:.1f}%{Colors.RESET}")
    print(f"Status     : {get_icon(score)}")
    print(f"Rekomendasi: {Colors.CYAN}{get_rec(score)}{Colors.RESET}")
    print(f"Bar        : {get_bar(score)}")
    print(f"\nDigit Breakdown:{Colors.RESET}")
    for rank, (digit, s) in enumerate(all_scores[2:5], 1):
        b = get_bar(s)
        ic = f"{Colors.GREEN}🔥{Colors.RESET}" if s >= 70 else \
             f"{Colors.YELLOW}⭐{Colors.RESET}" if s >= 50 else \
             f"{Colors.BLUE}⚠️{Colors.RESET}" if s >= 30 else \
             f"{Colors.WHITE}⚪{Colors.RESET}"
        print(f"  {rank}. {ic} Digit {digit:<2} - {s:.1f}%")

def display_head(score, all_scores):
    """Display Kepala confidence"""
    print("\n" + "-"*50)
    print(f"{Colors.CYAN}🎯 KEPALA (7) CONFIDENCE{Colors.RESET}")
    print("-"*50)
    print(f"Score      : {Colors.GREEN}{score:.1f}%{Colors.RESET}")
    print(f"Status     : {get_icon(score)}")
    print(f"Rekomendasi: {Colors.CYAN}{get_rec(score)}{Colors.RESET}")
    print(f"Bar        : {get_bar(score)}")
    print(f"\nDigit Breakdown:{Colors.RESET}")
    for rank, (digit, s) in enumerate(all_scores[:7], 1):
        b = get_bar(s)
        ic = f"{Colors.GREEN}🔥{Colors.RESET}" if s >= 70 else \
             f"{Colors.YELLOW}⭐{Colors.RESET}" if s >= 50 else \
             f"{Colors.BLUE}⚠️{Colors.RESET}" if s >= 30 else \
             f"{Colors.WHITE}⚪{Colors.RESET}"
        print(f"  {rank}. {ic} Digit {digit:<2} - {s:.1f}%")

def display_tail(score, all_scores):
    """Display Ekor confidence"""
    print("\n" + "-"*50)
    print(f"{Colors.YELLOW}🎯 EKOR (7) CONFIDENCE{Colors.RESET}")
    print("-"*50)
    print(f"Score      : {Colors.GREEN}{score:.1f}%{Colors.RESET}")
    print(f"Status     : {get_icon(score)}")
    print(f"Rekomendasi: {Colors.CYAN}{get_rec(score)}{Colors.RESET}")
    print(f"Bar        : {get_bar(score)}")
    print(f"\nDigit Breakdown:{Colors.RESET}")
    for rank, (digit, s) in enumerate(all_scores[3:7], 1):
        b = get_bar(s)
        ic = f"{Colors.GREEN}🔥{Colors.RESET}" if s >= 70 else \
             f"{Colors.YELLOW}⭐{Colors.RESET}" if s >= 50 else \
             f"{Colors.BLUE}⚠️{Colors.RESET}" if s >= 30 else \
             f"{Colors.WHITE}⚪{Colors.RESET}"
        print(f"  {rank}. {ic} Digit {digit:<2} - {s:.1f}%")

def display_summary(o, s6, s3, sh, st):
    """Display summary table"""
    print("\n" + "="*50)
    print(f"{Colors.MAGENTA}📋 RINGKASAN:{Colors.RESET}")
    print("-"*50)
    print(f"Overall  : {o:.1f}% {get_icon(o)}")
    print(f"6 Angka  : {s6:.1f}% {get_icon(s6)}")
    print(f"3D Top   : {s3:.1f}% {get_icon(s3)}")
    print(f"Kepala   : {sh:.1f}% {get_icon(sh)}")
    print(f"Ekor     : {st:.1f}% {get_icon(st)}")
    print("="*50)

# ========== MAIN MENU ==========
def main():
    os.system('clear' if os.name == 'posix' else 'cls')
    
    print("\n" + "="*50)
    print(f"{Colors.MAGENTA}   ⭐ CONFIDENCE SCORE PREDICTOR{Colors.RESET}")
    print("="*50)
    
    print("\n📊 PILIH PASARAN:")
    for k, v in MARKET_NAMES.items():
        print(f"   {k}. {v}")
    
    try:
        choice = input(f"{Colors.GREEN}\n➤ Nomor Pasaran (1-10) atau 0 untuk Demo Mode: {Colors.RESET}")
        choice = int(choice)
    except ValueError:
        print(f"{Colors.RED}❌ Input salah! Masukkan angka.{Colors.RESET}")
        choice = 0
    
    # Demo Mode
    if choice == 0:
        print(f"\n{Colors.YELLOW}🎮 DEMO MODE (Dummy Data){Colors.RESET}")
        dummy_data = [
            '3721', '5614', '3892', '7145', '3267',
            '8153', '3941', '6728', '3519', '4236',
            '1045', '6283', '9517', '2364', '7891',
            '4156', '8723', '5647', '2398', '6514',
            '3825', '7169', '4538', '9271', '6453',
            '2197', '5843', '8261', '4679', '3054',
            '7382', '9156', '5472', '1863', '6294'
        ]
        m_name = "Demo Mode"
        data = dummy_data
        print(f"\n{Colors.GREEN}✅ Menggunakan data dummy (35 putaran){Colors.RESET}")
        
    elif choice in MARKET_FILES:
        m_name = MARKET_NAMES[choice]
        print(f"\n{Colors.CYAN}🔄 Loading {m_name}...{Colors.RESET}")
        
        csv = fetch_github_csv(choice)
        if not csv:
            print(f"{Colors.RED}❌ Gagal ambil data. Cek internet!{Colors.RESET}")
            print(f"{Colors.YELLOW}💡 Gunakan DEMO MODE (ketik 0){Colors.RESET}")
            input("\nTekan Enter untuk kembali...")
            return
        
        data, _ = parse_csv(csv)
        if len(data) < 15:
            print(f"{Colors.RED}❌ Data kurang ({len(data)}). Minimal 15.{Colors.RESET}")
            input("\nTekan Enter untuk kembali...")
            return
        
        print(f"{Colors.GREEN}✅ Data: {len(data)} putaran. Memproses...{Colors.RESET}")
        time.sleep(1)
    else:
        print(f"{Colors.RED}❌ Pilihan tidak valid!{Colors.RESET}")
        input("\nTekan Enter untuk kembali...")
        return
    
    # Calculate Scores
    print(f"\n{Colors.CYAN}🔬 Memproses semua skor...{Colors.RESET}")
    time.sleep(0.5)
    
    all_scores = calc_digit_scores(data)
    
    # Calculate averages
    top6_scores = [s for d, s in all_scores[:6]]
    avg_6a = sum(top6_scores) / len(top6_scores) if top6_scores else 50
    
    tail_scores = [s for d, s in all_scores[2:5]]
    avg_3d = sum(tail_scores) / len(tail_scores) if tail_scores else 50
    
    head_scores = [s for d, s in all_scores[:7]]
    avg_head = sum(head_scores) / len(head_scores) if head_scores else 50
    
    tail_all_scores = [s for d, s in all_scores[3:7]]
    avg_tail = sum(tail_all_scores) / len(tail_all_scores) if tail_all_scores else 50
    
    overall = (avg_6a + avg_3d + avg_head + avg_tail) / 4
    overall = min(100, overall)
    
    # Display Results
    print("\n" + "="*50)
    print(f"{Colors.MAGENTA}⭐ HASIL CONFIDENCE: {m_name}{Colors.RESET}")
    print("="*50)
    
    display_overall(overall)
    display_6a(avg_6a, all_scores)
    display_3d(avg_3d, all_scores)
    display_head(avg_head, all_scores)
    display_tail(avg_tail, all_scores)
    display_summary(overall, avg_6a, avg_3d, avg_head, avg_tail)
    
    # Save Option
    try:
        save = input(f"{Colors.GREEN}\n💾 Simpan ke file? (y/n): {Colors.RESET}").lower()
        if save == 'y':
            # Buat nama file dengan timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            safe_name = m_name.replace(' ', '_').lower()
            fname = f"confidence_{safe_name}_{timestamp}.txt"
            
            # Tentukan path penyimpanan
            if os.path.exists('/sdcard'):
                path = os.path.join('/sdcard/Download', fname)
            else:
                path = os.path.join(os.getcwd(), fname)
            
            # Pastikan direktori ada
            os.makedirs(os.path.dirname(path), exist_ok=True)
            
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
                
                f.write("DIGIT DETAILS:\n")
                f.write("-"*50 + "\n")
                for digit, score in all_scores:
                    f.write(f"Digit {digit}: {score:.1f}%\n")
                
                f.write("\n" + "="*50 + "\n")
                f.write("Gunakan dengan bijak. Good luck! 🍀\n")
            
            print(f"\n{Colors.GREEN}✅ Tersimpan di: {path}{Colors.RESET}")
    except Exception as e:
        print(f"{Colors.RED}❌ Gagal menyimpan file: {e}{Colors.RESET}")
    
    print(f"\n{Colors.CYAN}⭐ Selesai. Jalankan lagi untuk pasaran lain.{Colors.RESET}")
    input("\nTekan Enter untuk keluar...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}⚠️ Dibatalkan.{Colors.RESET}")
    except Exception as e:
        print(f"\n{Colors.RED}❌ Error utama: {e}{Colors.RESET}")
        print(f"{Colors.YELLOW}💡 Coba jalankan ulang program.{Colors.RESET}")