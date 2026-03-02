#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 ANALISIS POLA - BATCH EDITION v2.0 (FIXED)
Support: Single Market & Multi-Market Auto Run
GitHub Integration • Pattern Detection • Export TXT
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

# 🔧 SETING MODE DI SINI
RUN_ALL_AUTO_MODE = False 
# ===========================================

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
        if color:
            formatted = f"{color}{text}{Colors.RESET}"
        else:
            formatted = str(text)
        print(formatted, end=end)
    except Exception as e:
        print(str(text), end=end)
    return True

# ========== FUNGSI FETCH DATA ==========
def fetch_github_csv(market_key):
    """Ambil data CSV dari GitHub"""
    file_info = MARKET_FILES.get(market_key)
    if not file_info:
        return None
    
    url = f"https://raw.githubusercontent.com/{GITHUB_CONFIG['username']}/{GITHUB_CONFIG['repo']}/{GITHUB_CONFIG['branch']}/{GITHUB_CONFIG['path']}/{file_info[1]}"
    
    try:
        cprint(f"  📡 Mengambil data...", Colors.CYAN, end="")
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        print()  # Newline setelah selesai
        return r.text
    except Exception as e:
        print()  # Newline setelah error
        cprint(f"  ❌ Error: {e}", Colors.RED)
        return None

# ========== FUNGSI PARSE CSV ==========
def parse_csv(text):
    """Parse data CSV"""
    if not text:
        return []
    
    results = []
    lines = text.strip().split('\n')
    
    # Skip header jika ada
    start_idx = 0
    if lines and ('date' in lines[0].lower() or 'tanggal' in lines[0].lower()):
        start_idx = 1
    
    for line in lines[start_idx:]:
        if not line.strip():
            continue
        parts = line.split(',')
        if len(parts) >= 2:
            match = re.search(r'(\d{4})', parts[1].strip())
            if match and len(match.group()) == 4:
                results.append(match.group())
    
    return results

# ========== FUNGSI DETEKSI POLA ==========
def detect_patterns(data):
    """Deteksi pola dari data"""
    if len(data) < 10:
        return {"error": f"Data terlalu sedikit ({len(data)} putaran)"}
    
    n = len(data)
    patterns = {}
    
    # 1. Ganjil/Genap
    odd_even = []
    for num in data[-50:]:
        if len(num) == 4:
            odds = sum(int(c) % 2 for c in num)
            if odds >= 3:
                odd_even.append('GANJIL')
            elif odds <= 1:
                odd_even.append('GENAP')
            else:
                odd_even.append('SEIMBANG')
    
    patterns['odd_even'] = {
        'list': odd_even[-20:], 
        'ratio': {
            'G': odd_even.count('GANJIL'), 
            'E': odd_even.count('GENAP'),
            'S': odd_even.count('SEIMBANG')
        }
    }
    
    # 2. Naik/Turun Satuan
    rd = []
    for i in range(min(n-1, 50)):
        if len(data[i]) == 4 and len(data[i+1]) == 4:
            if int(data[i+1][3]) > int(data[i][3]):
                rd.append('NAIK')
            elif int(data[i+1][3]) < int(data[i][3]):
                rd.append('TURUN')
            else:
                rd.append('SAMA')
    
    patterns['rise_down'] = {
        'list': rd[-20:], 
        'ratio': {
            'N': rd.count('NAIK'), 
            'T': rd.count('TURUN'), 
            'S': rd.count('SAMA')
        }
    }
    
    # 3. Kembaran
    kembar = []
    for num in data[-50:]:
        if len(num) == 4:
            has_pair = any(num[j] == num[k] for j in range(4) for k in range(j+1, 4))
            kembar.append(has_pair)
    
    patterns['kembar'] = {
        'count': kembar.count(True), 
        'normal': kembar.count(False),
        'total': len(kembar)
    }
    
    # 4. Posisi Stats
    pos_stats = {}
    for p in range(4):
        nums = [int(num[p]) for num in data[-100:] if len(num) == 4]
        if nums:
            counter = Counter(nums)
            pos_stats[f'Pos{p+1}'] = counter.most_common(5)
    patterns['positions'] = pos_stats
    
    # 5. Top 2D
    two_d = Counter([d[2:] for d in data[-50:] if len(d) == 4]).most_common(10)
    patterns['two_d_top'] = two_d
    
    # 6. Frekuensi digit terakhir
    last_digit = Counter([d[3] for d in data[-50:] if len(d) == 4]).most_common(5)
    patterns['last_digit_freq'] = last_digit
    
    # 7. Gap Analysis
    last_seen = defaultdict(list)
    for idx, num in enumerate(data):
        if len(num) == 4:
            last_seen[num[3]].append(idx)
    
    gap_stats = {}
    for digit, positions in last_seen.items():
        if len(positions) > 1:
            gaps = [positions[i+1] - positions[i] for i in range(len(positions)-1)]
            gap_stats[digit] = {
                'avg': round(sum(gaps) / len(gaps), 1), 
                'max': max(gaps),
                'last_seen': len(data) - positions[-1] - 1
            }
    
    patterns['gaps'] = dict(sorted(gap_stats.items(), key=lambda x: x[1]['avg'], reverse=True)[:5])
    
    return patterns

# ========== FUNGSI DISPLAY HASIL ==========
def display_patterns(patterns, market_name, market_num):
    """Tampilkan hasil analisis pola"""
    print("\n" + "="*50)
    cprint(f"[#{market_num}] ANALISIS: {market_name}", Colors.MAGENTA + Colors.BOLD)
    print("="*50)
    
    if isinstance(patterns, dict) and 'error' in patterns:
        cprint(f"{Colors.RED}⚠️ {patterns['error']}{Colors.RESET}")
        return False    
    
    # Odd/Even
    oe = patterns['odd_even']['ratio']
    tot = oe['G'] + oe['E'] + oe['S']
    if tot > 0:
        rate = oe['G'] / tot * 100 if tot else 0
        icon = "🔥" if rate >= 50 else ("⭐" if rate >= 30 else "⚪")
        cprint(f"\n🎲 GANJIL/GENAP:", Colors.YELLOW)
        cprint(f"   Ganjil : {oe['G']} | Genap : {oe['E']} | Seimbang : {oe['S']}")
        cprint(f"   Rate Ganjil: {rate:.1f}% {icon}")
    
    # Rise/Down
    rd = patterns['rise_down']['ratio']
    tot = rd['N'] + rd['T'] + rd['S']
    if tot > 0:
        cprint(f"\n📈 NAIK/TURUN:", Colors.YELLOW)
        cprint(f"   Naik  : {rd['N']} | Turun : {rd['T']} | Sama : {rd['S']}")
    
    # Kembaran
    km = patterns['kembar']
    if km['total'] > 0:
        pct = (km['count'] / km['total'] * 100) if km['total'] > 0 else 0
        cprint(f"\n👬 KEMBARAN:", Colors.YELLOW)
        cprint(f"   Kembar : {km['count']} ({pct:.1f}%) | Normal : {km['normal']}")
    
    # Top 2D
    if patterns['two_d_top']:
        cprint(f"\n🔢 TOP 5 2D:", Colors.GREEN + Colors.BOLD)
        for i, (num, count) in enumerate(patterns['two_d_top'][:5], 1):
            bar_len = int(count / patterns['two_d_top'][0][1] * 20) if patterns['two_d_top'] else 0
            bar = "█" * bar_len
            cprint(f"   {i}. {num}: {count}x [{bar}]", Colors.WHITE)
    
    # Last digit frequency
    if patterns['last_digit_freq']:
        cprint(f"\n🎯 FREKUENSI DIGIT TERAKHIR:", Colors.MAGENTA)
        max_count = patterns['last_digit_freq'][0][1] if patterns['last_digit_freq'] else 1
        for digit, count in patterns['last_digit_freq']:
            bar_len = int(count / max_count * 20)
            bar = "█" * bar_len
            cprint(f"   Digit {digit}: {count}x [{bar}]", Colors.WHITE)
    
    # Gap Analysis
    if patterns['gaps']:
        cprint(f"\n📊 ANALISIS GAP (Digit Terakhir):", Colors.BLUE)
        for digit, stats in patterns['gaps'].items():
            cprint(f"   Digit {digit}: Avg Gap {stats['avg']}, Max {stats['max']}, Last {stats['last_seen']} draw ago", Colors.WHITE)
    
    # Rekomendasi
    cprint(f"\n💎 REKOMENDASI:", Colors.YELLOW + Colors.BOLD)
    
    # Hot digits from last digit frequency
    if patterns['last_digit_freq']:
        hot_digits = [d for d, _ in patterns['last_digit_freq'][:3]]
        cprint(f"   • Digit Panas: {', '.join(hot_digits)}", Colors.GREEN)
    
    # 2D recommendation
    if patterns['two_d_top']:
        top_2d = [n for n, _ in patterns['two_d_top'][:3]]
        cprint(f"   • Top 2D: {', '.join(top_2d)}", Colors.CYAN)
    
    # Odds/Evens recommendation
    if oe['G'] > oe['E']:
        cprint(f"   • Cenderung GANJIL", Colors.YELLOW)
    elif oe['E'] > oe['G']:
        cprint(f"   • Cenderung GENAP", Colors.YELLOW)
    
    return True

def save_pattern_file(patterns, market_name):
    """Simpan hasil analisis ke file"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    safe_name = market_name.replace(' ', '_').lower()
    fname = f"pola_{safe_name}_{timestamp}.txt"
    
    if os.path.exists('/sdcard'):
        path = os.path.join('/sdcard/Download', fname)
    else:
        path = os.path.join(os.getcwd(), fname)
    
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write("="*50 + "\n")
            f.write(f"🔍 ANALISIS POLA: {market_name}\n")
            f.write("="*50 + "\n")
            f.write(f"Tanggal: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n")
            
            if isinstance(patterns, dict) and 'error' not in patterns:
                # Odd/Even
                oe = patterns['odd_even']['ratio']
                f.write(f"GANJIL/GENAP:\n")
                f.write(f"  Ganjil : {oe['G']}\n")
                f.write(f"  Genap  : {oe['E']}\n")
                f.write(f"  Seimbang: {oe['S']}\n\n")
                
                # Top 2D
                if patterns['two_d_top']:
                    f.write("TOP 5 2D:\n")
                    for num, count in patterns['two_d_top'][:5]:
                        f.write(f"  {num}: {count}x\n")
                    f.write("\n")
                
                # Last digit frequency
                if patterns['last_digit_freq']:
                    f.write("FREKUENSI DIGIT TERAKHIR:\n")
                    for digit, count in patterns['last_digit_freq']:
                        f.write(f"  Digit {digit}: {count}x\n")
                    f.write("\n")
            
            f.write("="*50 + "\n")
            f.write("Analisis selesai. Gunakan dengan bijak.\n")
        
        return path
    except Exception as e:
        cprint(f"  ❌ Gagal menyimpan: {e}", Colors.RED)
        return None

# ========== FUNGSI ANALISIS ==========
def _analyze_single_market(choice):
    """Logika analisis satu pasaran"""
    m_name = MARKET_NAMES[choice]
    print(f"\n{Colors.CYAN}🔄 Loading {m_name}...{Colors.RESET}")
    
    csv_text = fetch_github_csv(choice)
    if not csv_text:
        cprint("  ❌ Data kosong/tidak tersedia", Colors.RED)
        return False
    
    data = parse_csv(csv_text)
    if len(data) < 10:
        cprint(f"  ❌ Data terlalu sedikit ({len(data)} putaran)", Colors.RED)
        return False
    
    cprint(f"  ✅ Memproses {len(data)} data...", Colors.GREEN)
    print()
    
    patterns = detect_patterns(data)
    display_patterns(patterns, m_name, choice)
    
    save_opt = input(f"\n{Colors.GREEN}💾 Simpan laporan {m_name}? (y/n): {Colors.RESET}").lower()
    if save_opt == 'y':
        path = save_pattern_file(patterns, m_name)
        if path:
            cprint(f"  ✅ Tersimpan di {path}", Colors.GREEN)
    
    return True

# ========== MAIN MENU ==========
def run_market_analysis(choice=None):
    """Analisis untuk 1 atau semua pasaran"""
    market_keys = list(MARKET_NAMES.keys())
    
    # Jika mode auto, loop semua
    if RUN_ALL_AUTO_MODE:
        cprint(f"\n{Colors.CYAN}▶️ RUNNING AUTO MODE - ALL MARKETS{Colors.RESET}\n")
        
        for m_choice in market_keys:
            success = _analyze_single_market(m_choice)
            if success:
                cprint(f"\n{Colors.BLUE}✓ Selesai: {MARKET_NAMES[m_choice]}{Colors.RESET}")
            else:
                cprint(f"\n{Colors.RED}✗ Gagal: {MARKET_NAMES[m_choice]}{Colors.RESET}")
            
            if m_choice != market_keys[-1]:
                print("\n" + "-"*50)
                input(f"{Colors.CYAN}Tekan Enter untuk lanjut ke pasaran berikutnya...{Colors.RESET}")
            
    elif choice is not None:
        # Mode single market
        _analyze_single_market(choice)
    else:
        # Mode interaktif
        while True:
            print(f"\n{Colors.YELLOW}Pilih Pasaran:{Colors.RESET}")
            for k, v in MARKET_NAMES.items():
                print(f"  {k}. {v}")
            print("  0. Kembali")
            
            try:
                sel = input(f"\n{Colors.GREEN}➤ Pilih (1-10): {Colors.RESET}").strip()
                
                if sel == '0':
                    break
                
                c = int(sel)
                if c in MARKET_NAMES:
                    _analyze_single_market(c)
                else:
                    cprint("  ❌ Pilihan tidak valid", Colors.RED)
            except ValueError:
                cprint("  ❌ Masukkan angka yang valid", Colors.RED)
            
            print()

# ========== MAIN ENTRY POINT ==========
def main():
    os.system('clear' if os.name == 'posix' else 'cls')
    
    print("\n" + "="*50)
    cprint("🔍 ANALISIS POLA - MULTI-PASARAN", Colors.MAGENTA + Colors.BOLD)
    print("="*50)
    
    print(f"\n{Colors.YELLOW}🔧 KONFIGURASI: {Colors.RESET}", end="")
    if RUN_ALL_AUTO_MODE:
        cprint(f"{Colors.GREEN}AUTO RUN ALL MARKETS{Colors.RESET}", Colors.GREEN)
        cprint(f"  Akan menganalisis {len(MARKET_NAMES)} pasaran secara berurutan", Colors.CYAN)
    else:
        cprint(f"{Colors.YELLOW}MANUAL SELECT MODE{Colors.RESET}", Colors.YELLOW)
        cprint(f"  Edit script: RUN_ALL_AUTO_MODE = True untuk auto run", Colors.CYAN)
    
    print("\n" + "="*50)
    
    # Input utama
    if RUN_ALL_AUTO_MODE:
        # Langsung auto run semua
        run_market_analysis()
    else:
        # Tanya mode
        print("\n1️⃣ Analisis Satu Pasaran")
        print("2️⃣ Analisis Semua Pasaran (Batch Mode)")
        
        choice_type = input(f"\n{Colors.GREEN}Pilih Mode (1/2): {Colors.RESET}").strip()
        
        if choice_type == '2':
            # Batch mode - tanya konfirmasi
            cprint(f"\n{Colors.YELLOW}⚠️ Akan menganalisis {len(MARKET_NAMES)} pasaran{Colors.RESET}")
            confirm = input(f"{Colors.GREEN}Lanjutkan? (y/n): {Colors.RESET}").lower()
            
            if confirm == 'y':
                for m_choice in MARKET_NAMES.keys():
                    _analyze_single_market(m_choice)
                    if m_choice != list(MARKET_NAMES.keys())[-1]:
                        print()
                        input(f"{Colors.CYAN}Tekan Enter untuk lanjut...{Colors.RESET}")
            else:
                cprint("  ⚠️ Dibatalkan", Colors.YELLOW)
        else:
            # Mode manual biasa
            try:
                choice = int(input(f"\n{Colors.GREEN}Nomor Pasaran (1-10): {Colors.RESET}"))
                if choice in MARKET_NAMES:
                    run_market_analysis(choice=choice)
                else:
                    cprint("  ❌ Pilihan tidak valid", Colors.RED)
            except ValueError:
                cprint("  ❌ Input angka saja", Colors.RED)
    
    cprint(f"\n{Colors.CYAN}✅ Selesai. Jalankan lagi untuk analisis baru.{Colors.RESET}")
    input("\nTekan Enter untuk keluar...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        cprint(f"\n\n{Colors.YELLOW}⚠️ Dibatalkan.{Colors.RESET}")
    except Exception as e:
        cprint(f"\n{Colors.RED}❌ Error utama: {e}{Colors.RESET}")
        import traceback
        traceback.print_exc()