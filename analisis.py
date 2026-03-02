#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 ANALISIS POLA - BATCH EDITION v2.1 (FIXED 100%)
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
    1: 'Magnum Cambodia', 2: 'Sydney Pools', 3: 'Sydney Lotto',
    4: 'China Pools', 5: 'Singapore', 6: 'Taiwan',
    7: 'Hongkong Pools', 8: 'Hongkong Lotto', 9: 'New York Evening', 10: 'Kentucky Evening'
}

RUN_ALL_AUTO_MODE = False 

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

# ✅ DIPERBAIKI - Support end parameter
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

# ========== FUNGSI DETEKSI POLA ==========
def detect_patterns(data):
    if len(data) < 10:
        return {"error": "Data kurang"}    
    n = len(data)
    patterns = {}
    
    # Odd/Even pattern
    odd_even = ['GANJIL' if sum(int(c)%2 for c in num)>=2 else 'GENAP' for num in data if len(num)==4]
    patterns['odd_even'] = {'list': odd_even[-20:], 'ratio': {'G': odd_even.count('GANJIL'), 'E': odd_even.count('GENAP')}}
    
    # Rise/Down pattern
    rd = ['NAIK' if int(data[i+1][3])>int(data[i][3]) else ('TURUN' if int(data[i+1][3])<int(data[i][3]) else 'SAMA') for i in range(n-1)]
    patterns['rise_down'] = {'list': rd[-20:], 'ratio': {'N': rd.count('NAIK'), 'T': rd.count('TURUN'), 'S': rd.count('SAMA')}}
    
    # Kembar pattern
    kembar = [any(num[j]==num[k] for j in range(4) for k in range(j+1,4)) for num in data if len(num)==4]
    patterns['kembar'] = {'count': kembar.count(True), 'normal': kembar.count(False)}
    
    # Position stats
    pos_stats = {}
    for p in range(4):
        nums = [int(num[p]) for num in data if len(num)==4]
        if nums: pos_stats[f'Pos{p+1}'] = Counter(nums).most_common(5)
    patterns['positions'] = pos_stats
    
    # Last digit frequency
    last_digits = [num[3] for num in data if len(num)==4]
    if last_digits:
        patterns['last_digit_freq'] = Counter(last_digits).most_common(5)
    
    # 2D top
    two_d = Counter([d[2:] for d in data if len(d)==4][-50:]).most_common(10)
    patterns['two_d_top'] = two_d
    
    # Gap analysis
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

# ========== FUNGSI DISPLAY HASIL ==========
def display_patterns(patterns, market_name, market_num):
    print("\n" + "="*50)
    cprint(f"[#{market_num}] ANALISIS: {market_name}", Colors.MAGENTA + Colors.BOLD)
    print("="*50)
    
    if isinstance(patterns, dict) and 'error' in patterns:
        cprint(f"{Colors.RED}⚠️ Data tidak cukup: {patterns['error']}{Colors.RESET}")
        return False
    
    oe = patterns['odd_even']['ratio']
    tot = oe['G']+oe['E']
    rate = oe['G']/tot*100 if tot else 0
    icon = "🔥" if rate>=55 else ("⭐" if rate>=45 else "⚪")
    cprint(f"\n🎲 O/E : G:{oe['G']} | E:{oe['E']} | {rate:.1f}% {icon}")
    
    rd = patterns['rise_down']['ratio']
    tot = rd['N']+rd['T']
    cprint(f"📈 N/T/S : N:{rd['N']} | T:{rd['T']} | S:{rd['S']}")
    
    km = patterns['kembar']
    cprint(f"👬 KM/NM : KM:{km['count']} | NM:{km['normal']}")
    
    if patterns['two_d_top']:
        cprint(f"🔢 TOP 2D :", end=" ")
        items = ', '.join([f"{n}" for n,c in patterns['two_d_top'][:3]])
        cprint(items, Colors.GREEN)
    
    cprint("\n💎 REKOMENDASI:", Colors.YELLOW)
    hot_digits = [d for d,c in list(patterns.get('last_digit_freq', []))[:3]]
    cprint(f"• Digit Panas: {', '.join(hot_digits) if hot_digits else '-'}")
    
    return True

def save_pattern_file(patterns, market_name):
    fname = f"pola_{market_name.replace(' ','_')}_{datetime.now().strftime('%H%M%S')}.txt"
    path = '/sdcard/Download/' + fname if os.path.exists('/sdcard') else fname
    try:
        with open(path,'w') as f:
            f.write("="*50 + "\n" + f"POLA: {market_name}\n\n")
            f.write(f"2D Top: {','.join([n for n,c in patterns['two_d_top'][:5]])}")
            f.write("\n\n" + "="*50)
        return path
    except: 
        return None

# ========== ANALISIS SINGLE MARKET ==========
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

# ========== MAIN MENU ==========
def run_market_analysis(choice=None):
    if RUN_ALL_AUTO_MODE:
        cprint(f"\n{Colors.CYAN}▶️ RUNNING AUTO MODE - ALL MARKETS{Colors.RESET}\n")
        for m_choice in MARKET_NAMES.keys():
            _analyze_single_market(m_choice)
            print("\n" + "-"*50)
            if m_choice != max(MARKET_NAMES.keys()):
                cprint("Tekan Enter untuk lanjut ke pasaran berikutnya...", Colors.CYAN)
                input()
    else:
        if choice is not None:
            # Single market selected
            _analyze_single_market(choice)
        else:
            # Manual mode with menu
            print("\n" + "-"*50)
            for num, name in MARKET_NAMES.items():
                print(f"{num}. {name}")
            print("X. Exit")
            
            sel = input(f"\n{Colors.GREEN}Pilih nomor pasaran (1-10): {Colors.RESET}").strip()
            
            if sel.upper() == 'X':
                return
            
            if sel.isdigit():
                c = int(sel)
                if c in MARKET_NAMES:
                    _analyze_single_market(c)
                else:
                    print("❌ Pilihan tidak valid")
            else:
                print("❌ Input angka saja")

# ========== MAIN ENTRY POINT ==========
def main():
    os.system('clear' if os.name == 'posix' else 'cls')
    
    print("\n" + "="*50)
    cprint("🔍 ANALISIS POLA - MULTI-PASARAN", Colors.MAGENTA + Colors.BOLD)
    print("="*50)
    
    if RUN_ALL_AUTO_MODE:
        cprint(f"\n{Colors.GREEN}⚡ AUTO MODE ENABLED - RUNNING ALL MARKETS{Colors.RESET}")
        run_market_analysis()
    else:
        cprint(f"\n{Colors.YELLOW}📋 MANUAL MODE - PILIH PASARAN{Colors.RESET}")
        print("(Edit script: ubah RUN_ALL_AUTO_MODE=True untuk auto mode)\n")
        run_market_analysis()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        cprint("\n\n⚠️ Dibatalkan.", Colors.YELLOW)
    except Exception as e:
        cprint(f"\n{Colors.RED}❌ Error utama: {e}{Colors.RESET}")