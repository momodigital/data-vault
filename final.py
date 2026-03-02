#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🏆 FINAL.PY - MASTER PREDICTOR INTEGRATED (FIXED)
Menggabungkan Logika: Prediktor (Angka) + Shio (Sifat) + Confidence (Skor)
Hasil: 2D Terbaik Terfilter dari Data Live GitHub
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
    1: 'Magnum Cambodia', 2: 'Sydney Pools', 3: 'Sydney Lotto',
    4: 'China Pools', 5: 'Singapore', 6: 'Taiwan',
    7: 'Hongkong Pools', 8: 'Hongkong Lotto', 9: 'New York Evening', 10: 'Kentucky Evening'
}

# WARNA ANSI
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

def cprint(text, color=None, end='\n'):
    try:
        if color:
            formatted = f"{color}{text}{Colors.RESET}"
        else:
            formatted = str(text)
        print(formatted, end=end)
    except Exception:
        print(str(text), end=end)

# ========== FUNGSI DATA ==========
def fetch_github_csv(market_key):
    file_info = MARKET_FILES.get(market_key)
    if not file_info: 
        return None
    url = f"https://raw.githubusercontent.com/{GITHUB_CONFIG['username']}/{GITHUB_CONFIG['repo']}/{GITHUB_CONFIG['branch']}/{GITHUB_CONFIG['path']}/{file_info[1]}"
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        return r.text
    except Exception as e:
        cprint(f"Error fetch: {e}", Colors.RED)
        return None

def parse_csv(text):
    if not text: 
        return []
    results = []
    lines = text.strip().split('\n')[1:]
    for line in lines:
        if not line: 
            continue
        parts = line.split(',')
        if len(parts) >= 2:
            match = re.search(r'\d{4}', parts[1].strip())
            if match and len(match.group()) == 4:
                results.append(match.group())
    return results

# ========== LOGIKA INTI PREDIKTOR (6 ANGKA) ==========
def get_top_digits(data, limit=6):
    if len(data) < 10: 
        return []
    freq = Counter(digit for num in data for digit in num if len(num) == 4)
    sorted_d = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    return [d for d, c in sorted_d[:limit]]

# ========== LOGIKA INTI SHIO (TERAKHIR) ==========
SHIO_LIST = ['Tikus', 'Sapi', 'Macan', 'Kelinci', 'Naga', 'Ular', 
             'Kuda', 'Kambing', 'Monyet', 'Ayam', 'Anjing', 'Babi']

def get_top_shio(data):
    """Mendapatkan digit terakhir yang paling sering muncul untuk Shio"""
    if len(data) < 10:
        return []
    
    # Shio ditentukan oleh digit terakhir
    last_digits = [int(num[3]) for num in data if len(num) == 4]
    if not last_digits:
        return []
    
    freq_last = Counter(last_digits)
    # Ambil 3 digit terakhir paling sering
    top_digits = [str(d) for d, c in freq_last.most_common(3)]
    return top_digits

# ========== LOGIKA INTI CONFIDENCE (SKOR) ==========
def calculate_scores(data):
    scores = {str(d): 0 for d in range(10)}
    
    if len(data) < 10:
        return scores
    
    # Base frequency
    n = len(data)
    freq = Counter(d for num in data for d in num if len(num) == 4)
    max_f = max(freq.values()) if freq else 1
    
    # Hitung skor dasar dari frekuensi
    for d in range(10):
        sc = (freq.get(str(d), 0) / max_f) * 40
        scores[str(d)] = sc
    
    # Decay (recent wins) - 20 data terakhir dengan bobot lebih
    recent_data = data[-20:] if len(data) > 20 else data
    for idx, num in enumerate(reversed(recent_data)):
        if len(num) == 4:
            weight = 0.95 ** idx  # Decay factor
            for char in num:
                scores[char] += weight * 3
    
    # Normalisasi ke 0-100
    max_score = max(scores.values()) if scores else 100
    for d in scores:
        scores[d] = min(100, round((scores[d] / max_score) * 100, 1))
    
    return scores

# ========== FILTERING MASTER (INTI SCRIPT) ==========
def generate_best_2d(top6_digits, top3_shio_digit, scores_dict, min_conf=50):
    """Generate 2D using intersection of all 3 methods"""
    results = []
    
    if not top6_digits or not top3_shio_digit:
        return results
    
    top6_set = set(top6_digits)
    shio_digit_set = set(top3_shio_digit)
    
    for i in range(100):
        s = f"{i:02d}"
        d1, d2 = s[0], s[1]
        
        # Check Logic:
        # 1. Harus ada satu digit dari 6 angka kuat (Prediktor)
        # 2. Harus ada digit terakhir yang cocok dengan Shio Kuat
        # 3. Average skor Confidence kedua digit harus > Threshold
        
        has_strong_digit = (d1 in top6_set) or (d2 in top6_set)
        correct_tail = (d2 in shio_digit_set)
        
        avg_conf = (scores_dict.get(d1, 0) + scores_dict.get(d2, 0)) / 2
        
        if has_strong_digit and correct_tail and avg_conf >= min_conf:
            results.append((s, avg_conf))
    
    # Sort by confidence
    return sorted(results, key=lambda x: x[1], reverse=True)

# ========== MAIN MENU ==========
def main():
    os.system('clear' if os.name == 'posix' else 'cls')
    print("\n" + "="*60)
    cprint("   🏆 FINAL.PY - MASTER PREDICTOR", Colors.MAGENTA + Colors.BOLD)
    print("="*60)
    
    print("\n📊 PILIH PASARAN:")
    for k, v in MARKET_NAMES.items():
        cprint(f"   {k}. {v}", Colors.WHITE)
    
    choice = input(f"\n{Colors.GREEN}➤ Nomor Pasaran (1-10): {Colors.RESET}").strip()
    
    if choice.upper() == 'X':
        return
    
    try:
        m_key = int(choice)
        if m_key not in MARKET_FILES:
            cprint("❌ Nomor pasar tidak valid!", Colors.RED)
            return
    except ValueError:
        cprint("❌ Input harus angka!", Colors.RED)
        return
    
    market_name = MARKET_NAMES[m_key]
    cprint(f"\n🔄 Loading {market_name}...", Colors.CYAN)
    
    csv_text = fetch_github_csv(m_key)
    if not csv_text:
        cprint("❌ Error fetching data dari GitHub!", Colors.RED)
        return
    
    data = parse_csv(csv_text)
    if len(data) < 10:
        cprint(f"❌ Data kurang ({len(data)} putaran)", Colors.RED)
        return
    
    cprint(f"✅ Analisa {len(data)} riwayat data...", Colors.GREEN)
    time.sleep(1)
    
    # Execute Core Logic
    top6 = get_top_digits(data, 6)
    top3_shio = get_top_shio(data)
    scores = calculate_scores(data)
    
    # Filter 2D
    best_2d = generate_best_2d(top6, top3_shio, scores, min_conf=50)
    
    # Display
    print("\n" + "="*60)
    cprint("🔷 HASIL EKSEKUSI FINAL - ANALISA TERPADU", Colors.CYAN + Colors.BOLD)
    print("="*60)
    
    print(f"\n📈 Data: {len(data)} | Pasaran: {market_name}\n")
    
    # Source Summary
    cprint("📊 Logika Sumber:", Colors.BLUE)
    cprint(f"• Prediktor (Top 6): {' - '.join(map(str, top6))}", Colors.WHITE)
    cprint(f"• Shio Terakhir (Top 3): {' - '.join(map(str, top3_shio))}", Colors.YELLOW)
    cprint(f"• Min Confidence: ≥ 50%", Colors.GREEN)
    
    if not best_2d:
        cprint("\n⚠️ Tidak ada kombinasi yang memenuhi kriteria!", Colors.YELLOW)
        cprint("   Coba turunkan threshold atau periksa data.", Colors.WHITE)
    else:
        print("\n💎 TOP 2D REKOMENDASI (High Confidence):\n")
        cprint(f"{'No':<5} {'2D':<5} {'Score':<8} {'Status'}", Colors.MAGENTA)
        print("-"*40)
        
        # Limit display to avoid clutter (show top 20)
        count = 0
        for combo, conf in best_2d:
            if count >= 20: 
                break
            if conf >= 70:
                icon = "🔥"
                status = "PANAS"
                color = Colors.GREEN
            elif conf >= 60:
                icon = "⭐"
                status = "BAIK"
                color = Colors.YELLOW
            else:
                icon = "⚪"
                status = "RATA-RATA"
                color = Colors.WHITE
            
            cprint(f"{count+1:<5} {combo:<5} {conf:.1f}%   {icon} {status}", color)
            count += 1
        
        if len(best_2d) > 20:
            cprint(f"... dan {len(best_2d)-20} kombinasi lainnya.\n", Colors.CYAN)
        
        print("-"*40)
        cprint(f"Total Rekomendasi: {len(best_2d)} kombinasi", Colors.YELLOW)
    
    # Save Option
    save = input(f"\n{Colors.GREEN}💾 Simpan semua ke File? (y/n): {Colors.RESET}").lower()
    if save == 'y':
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        fname = f"FINAL_{market_name.replace(' ','_')}_{timestamp}.txt"
        
        # Determine save path
        if os.path.exists('/sdcard'):
            save_dir = '/sdcard/Download'
            if not os.path.exists(save_dir):
                save_dir = '/sdcard'
        else:
            save_dir = '.'
        
        path = os.path.join(save_dir, fname)
        
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write("="*60 + "\n")
                f.write("🏆 FINAL.PY - LAPORAN HASIL AKHIR\n")
                f.write("="*60 + "\n\n")
                f.write(f"Pasaran: {market_name}\n")
                f.write(f"Tanggal: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n")
                f.write(f"Data: {len(data)} putaran\n\n")
                f.write(f"6 Angka Kuat: {' - '.join(map(str, top6))}\n")
                f.write(f"Shio Kuat: {' - '.join(map(str, top3_shio))}\n\n")
                f.write(f"TOP 2D COMBO ({len(best_2d)})\n")
                f.write("-"*40 + "\n")
                for combo, conf in best_2d:
                    f.write(f"{combo}: {conf:.1f}%\n")
            
            cprint(f"\n✅ Tersimpan di: {Colors.GREEN}{path}{Colors.RESET}")
        except Exception as e:
            cprint(f"\n❌ Error menyimpan file: {e}", Colors.RED)
    
    cprint("\n🔷 Selesai. Gunakan dengan bijak.", Colors.CYAN)
    input("\nTekan Enter untuk keluar...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}⚠️ Dibatalkan.{Colors.RESET}")
    except Exception as e:
        print(f"\n{Colors.RED}❌ Error utama: {e}{Colors.RESET}")
        import traceback
        traceback.print_exc()