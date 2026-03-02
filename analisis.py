#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 ANALISIS POLA - FULL BATCH EDITION v3.0 (FIXED)
Support: Single Market • All Markets Auto Run • Multi-Factor Analysis
"""

import os
import requests
import re
from collections import Counter, defaultdict
from datetime import datetime
import time

# ========== KONFIGURASI UTAMA ==========
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

def cprint(text, color=Colors.RESET, end='\n'):
    """Print text with color handling - FIXED VERSION"""
    try:
        formatted = f"{color}{text}{Colors.RESET}" if color != Colors.RESET else str(text)
        print(formatted, end=end)
    except Exception as e:
        print(str(text), end=end)
    return True

# ========== FUNGSI FETCH DATA ==========
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
        cprint(f"  ❌ Error: {e}", Colors.RED)
        return None

# ========== FUNGSI PARSE CSV ==========
def parse_csv(text):
    if not text:
        return []
    results = []
    for line in text.strip().split('\n')[1:]:
        if not line: continue
        parts = line.split(',')
        if len(parts) >= 2:
            match = re.search(r'\d{4}', parts[1].strip())
            if match and len(match.group()) == 4:
                results.append(match.group())
    return results

# ========== LEGEND PENTING UNTUK PEMAHAMAN ==========
LEGEND_TEXT = """
==================================================
   📖 KETERANGAN SINGKAT (LEARNER GUIDE)
==================================================

🎲 O/E   →  ODD / EVEN (Ganjil / Genap)           
           Jumlah angka ganjil dan genap dalam satu hasil
           
📈 N/T/S →  NAIK / TURUN / SAMA
           Trend digit satuan (naik/turun/stagnan)
           
👬 KM/NM →  KEMBAR / NORMAL
           Kembar: ada dua digit sama
           Normal: semua digit berbeda
           
💎 REKOMENDASI
           Rekomendasi berbasis pola data
==================================================
"""

# ========== FUNGSI DETEKSI POLA ==========
def detect_patterns(data):
    if len(data) < 10:
        return {"error": "Data kurang"}
    
    n = len(data)
    patterns = {}
    
    # 1. Ganjil/Genap
    odd_even = ['GANJIL' if sum(int(c)%2 for c in num)>=2 else 'GENAP' for num in data if len(num)==4]
    patterns['odd_even'] = {'list': odd_even[-20:], 'ratio': {'G': odd_even.count('GANJIL'), 'E': odd_even.count('GENAP')}}
    
    # 2. Naik/Turun Satuan
    rd = ['NAIK' if int(data[i+1][3])>int(data[i][3]) else ('TURUN' if int(data[i+1][3])<int(data[i][3]) else 'SAMA') for i in range(n-1)]
    patterns['rise_down'] = {'list': rd[-20:], 'ratio': {'N': rd.count('NAIK'), 'T': rd.count('TURUN'), 'S': rd.count('SAMA')}}
    
    # 3. Kembaran
    kembar = [any(num[j]==num[k] for j in range(4) for k in range(j+1,4)) for num in data if len(num)==4]
    patterns['kembar'] = {'count': kembar.count(True), 'normal': kembar.count(False)}
    
    # 4. Posisi Stats
    pos_stats = {}
    for p in range(4):
        nums = [int(num[p]) for num in data if len(num)==4]
        if nums: pos_stats[f'Pos{p+1}'] = Counter(nums).most_common(5)
    patterns['positions'] = pos_stats
    
    # 5. Last digit frequency
    last_digits = [num[3] for num in data if len(num)==4]
    if last_digits:
        patterns['last_digit_freq'] = Counter(last_digits).most_common(5)
    
    # 6. Top 2D
    two_d = Counter([d[2:] for d in data if len(d)==4][-50:]).most_common(10)
    patterns['two_d_top'] = two_d
    
    # 7. Gap Analysis
    last_seen = defaultdict(list)
    for idx, num in enumerate(data):
        if len(num)==4: last_seen[num[3]].append(idx)
    gap_stats = {}
    for digit, positions in last_seen.items():
        if len(positions)>1:
            gaps = [positions[i+1]-positions[i] for i in range(len(positions)-1)]
            gap_stats[digit] = {'avg': round(sum(gaps)/len(gaps), 1), 'max': max(gaps)}
    patterns['gaps'] = dict(sorted(gap_stats.items(), key=lambda x:x[1]['avg'], reverse=True)[:5])
    
    return patterns

# ========== FUNGSI DISPLAY HASIL DENGAN LEGEND ==========
def display_patterns(patterns, market_name, market_num):
    print("\n" + "="*50)
    cprint(f"[#{market_num}] ANALISIS: {market_name}", Colors.MAGENTA + Colors.BOLD)
    print("="*50)
    
    if isinstance(patterns, dict) and 'error' in patterns:
        cprint(f"\n{Colors.RED}⚠️ Data tidak cukup: {patterns['error']}{Colors.RESET}")
        return False
    
    cprint(f"\n📊 STATISTIK DETAIL:", Colors.CYAN)
    print("-"*50)
    
    # Odd/Even dengan legenda lengkap
    oe = patterns['odd_even']['ratio']
    tot = oe['G']+oe['E']
    rate = oe['G']/tot*100 if tot else 0
    icon = "🔥" if rate>=55 else ("⭐" if rate>=45 else "⚪")
    
    cprint(f"🎲 O/E   →  GANJIL/GENAP", Colors.GREEN)
    cprint(f"         G:{oe['G']} | E:{oe['E']} | Rate:{rate:.1f}% {icon}")
    cprint("         → Persentase hasil ganjil vs genap", Colors.BLUE)
    
    # Rise/Down dengan legenda
    rd = patterns['rise_down']['ratio']
    tot = rd['N']+rd['T']
    trend_text = "NAIK" if rd['N']>rd['T']+2 else ("TURUN" if rd['T']>rd['N']+2 else "STABIL")
    
    cprint(f"\n📈 N/T/S →  NAIK/TURUN/SAMA", Colors.GREEN)
    cprint(f"         N:{rd['N']} | T:{rd['T']} | S:{rd['S']}")
    cprint(f"         Trend: {trend_text}", Colors.CYAN if trend_text=="STABIL" else Colors.YELLOW)
    
    # Kembaran dengan legenda
    km = patterns['kembar']
    total_count = km['count'] + km['normal']
    km_rate = (km['count']/total_count*100) if total_count else 0
    icon_km = "🔥" if km_rate>=45 else ("⭐" if km_rate>=30 else "⚪")
    
    cprint(f"\n👬 KM/NM →  KEMBAR/NORMAL", Colors.GREEN)
    cprint(f"         KM:{km['count']} | NM:{km['normal']} ({km_rate:.1f}%) {icon_km}")
    cprint("         → Kembar = Ada 2 digit sama dalam angka", Colors.BLUE)
    
    # Top 2D
    cprint(f"\n🔢 TOP 2D →  2 DIGIT TERAKHIR", Colors.GREEN)
    if patterns['two_d_top']:
        items = ', '.join([f"{n}" for n,c in patterns['two_d_top'][:5]])
        cprint(f"         {items}", Colors.GREEN)
        cprint("         → Kombinasi yang sering muncul", Colors.BLUE)
    
    # Rekomendasi
    cprint(f"\n💎 REKOMENDASI:", Colors.YELLOW)
    hot_digits = [d for d,c in list(patterns.get('last_digit_freq', []))[:3]]
    cprint(f"• Digit Panas: {', '.join(hot_digits) if hot_digits else '-'}")
    cprint("         → Angka terakhir yang sering keluar", Colors.BLUE)
    
    return True

# ========== FUNGSI SAVE FILE ==========
def save_pattern_file(patterns, market_name):
    fname = f"pola_{market_name.replace(' ','_')}_{datetime.now().strftime('%H%M%S')}.txt"
    path = '/sdcard/Download/' + fname if os.path.exists('/sdcard') else fname
    try:
        with open(path,'w') as f:
            f.write("="*50 + "\n")
            f.write(f"POLA: {market_name}\n")
            f.write(f"Tanggal: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n")
            
            oe = patterns['odd_even']['ratio']
            f.write(f"O/E Ratio: G={oe['G']} E={oe['E']}\n")
            
            km = patterns['kembar']
            f.write(f"Kembar: {km['count']}x\n")
            
            f.write(f"\nTOP 2D: {','.join([n for n,c in patterns['two_d_top'][:5]])}\n")
            f.write("\n" + "="*50)
        return path
    except: 
        return None

# ========== FUNGSI ANALISIS SINGLE MARKET ==========
def _analyze_single_market(choice):
    m_name = MARKET_NAMES[choice]
    cprint(f"\nLoading {m_name}...", Colors.CYAN)
    
    csv_text = fetch_github_csv(choice)
    if not csv_text:
        cprint("❌ Data kosong/tidak tersedia", Colors.RED)
        return
    
    data = parse_csv(csv_text)
    if len(data) < 10:
        cprint(f"❌ Data sedikit ({len(data)} putaran)", Colors.RED)
        return
    
    cprint(f"✅ Memproses {len(data)} data...", Colors.GREEN)
    
    patterns = detect_patterns(data)
    display_patterns(patterns, m_name, choice)
    
    save_opt = input(f"\nSimpan laporan {m_name}? (y/n): ").lower()
    if save_opt == 'y':
        pth = save_pattern_file(patterns, m_name)
        if pth: 
            cprint(f"✅ Tersimpan di {pth}", Colors.GREEN)

# ========== LEGEND DISPLAY ==========
def show_legend():
    """Show legend when asked"""
    print(LEGEND_TEXT)
    input("\nTekan Enter untuk lanjut...")

# ========== RUN ALL MARKETS AUTO ==========
def run_all_markets_auto():
    """Run ALL markets automatically"""
    cprint(f"\n{Colors.GREEN}▶️ FULL AUTO MODE - RUNNING ALL MARKETS{Colors.RESET}\n")
    
    start_time = datetime.now()
    total_files = 0
    successful = 0
    failed = 0
    
    for m_choice in MARKET_FILES.keys():
        m_name = MARKET_NAMES[m_choice]
        
        cprint(f"\n[{m_choice}/10] Processing {m_name}...", Colors.CYAN)
        
        csv_text = fetch_github_csv(m_choice)
        if not csv_text:
            cprint(f"  ⚠️ Skip: Tidak tersedia", Colors.YELLOW)
            failed += 1
            continue
        
        data = parse_csv(csv_text)
        if len(data) < 10:
            cprint(f"  ⚠️ Skip: Data sedikit ({len(data)} putaran)", Colors.YELLOW)
            failed += 1
            continue
        
        cprint(f"  ✅ {len(data)} data diproses...", Colors.GREEN)
        patterns = detect_patterns(data)
        display_patterns(patterns, m_name, m_choice)
        
        save_opt = input(f"\nSimpan laporan {m_name}? (y/n): ").lower()
        if save_opt == 'y':
            pth = save_pattern_file(patterns, m_name)
            if pth: 
                cprint(f"  ✅ Tersimpan di {pth}", Colors.GREEN)
                total_files += 1
        else:
            total_files += 1  # Still count as analyzed
        
        successful += 1
        
        # Progress indicator
        progress = (m_choice / len(MARKET_FILES)) * 100
        bar = "█" * int(progress/10) + "░" * (10 - int(progress/10))
        cprint(f"\nProgress: [{bar}] {progress:.0f}%", Colors.CYAN)
        
        # Check if user wants to pause
        if m_choice < max(MARKET_FILES.keys()):
            cont = input("Lanjut ke pasaran berikutnya? (y/n): ").lower()
            if cont != 'y':
                cprint(f"\n{Colors.YELLOW}⚠️ Mode auto berhenti di pasar {m_choice}{Colors.RESET}")
                break
    
    end_time = datetime.now()
    duration = (end_time - start_time).seconds
    
    # Summary Report
    print("\n" + "="*50)
    cprint("🏁 FULL MODE SUMMARY", Colors.MAGENTA + Colors.BOLD)
    print("="*50)
    cprint(f"Total Pasar Diproses: {successful}/{len(MARKET_FILES)}", Colors.GREEN)
    cprint(f"Gagal: {failed}", Colors.RED)
    cprint(f"Waktu Eksekusi: {duration} detik", Colors.CYAN)
    cprint(f"File Generated: {total_files}", Colors.YELLOW)
    print("="*50)

# ========== MAIN MENU ==========
def main():
    os.system('clear' if os.name == 'posix' else 'cls')
    
    print("\n" + "="*50)
    cprint("🔍 ANALISIS POLA - MULTI-PASARAN v3.0", Colors.MAGENTA + Colors.BOLD)
    print("="*50)
    
    while True:
        print("\n📋 PILIHAN:")
        print("1️⃣ Pilih SATU Pasaran Manual")
        print("2️⃣ 🔄 Jalankan SEMUA Pasaran (Full Auto Mode)")
        print("3️⃣ ℹ️ Lihat KETERANGAN Istilah")
        print("X Exit")
        
        choice_type = input(f"\n{Colors.GREEN}Pilih (1/2/3/X): {Colors.RESET}").strip().upper()
        
        if choice_type == 'X':
            cprint("\n✅ Keluar. Sampai jumpa!", Colors.WHITE)
            break
        elif choice_type == '1':
            # Show market list
            print("\n" + "-"*50)
            for num, name in MARKET_NAMES.items():
                print(f"{num}. {name}")
            
            try:
                choice = int(input(f"\n{Colors.GREEN}Nomor Pasaran (1-10): {Colors.RESET}"))
                if choice in MARKET_NAMES:
                    _analyze_single_market(choice)
                else:
                    print("❌ Pilihan tidak valid")
            except ValueError:
                print("❌ Masukkan angka saja")
        elif choice_type == '2':
            confirm = input(f"{Colors.YELLOW}⚠️ Ini akan memproses SEMUA 10 pasaran! Lanjut? (y/n): {Colors.RESET}").lower()
            if confirm == 'y':
                run_all_markets_auto()
            else:
                cprint("❌ Dibatalkan", Colors.RED)
        elif choice_type == '3':
            show_legend()
        else:
            print("❌ Input salah, pilih 1/2/3/X")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        cprint("\n\n⚠️ Dibatalkan.", Colors.YELLOW)
    except Exception as e:
        cprint(f"\n{Colors.RED}❌ Error utama: {e}{Colors.RESET}")