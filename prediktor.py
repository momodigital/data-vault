#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔷 PREDIKTOR 6 ANGKA - Termux Edition
GitHub Integration • Export TXT • Colored Output
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
class Colors:    RESET = '\033[0m'
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

# ========== FUNGSI 6 ANGKA ==========
def calc6(data):
    if len(data) < 15:
        return {'h6': [], 'det': []}
    n = len(data)
    freq = Counter()    pos = {i: Counter() for i in range(4)}
    d2_freq = Counter()
    
    for num in 
        if len(num) != 4:
            continue
        for j in range(4):
            d = int(num[j])
            freq[d] += 1
            pos[j][d] += 1
        d2_freq[num[2:]] += 1
    
    scores = {}
    for digit in range(10):
        sc = 0
        max_f = max(freq.values()) or 1
        sc += (freq.get(digit, 0) / max_f) * 20
        f2 = sum(v for k, v in d2_freq.items() if str(digit) in k)
        max_2d = max(d2_freq.values()) or 1
        sc += (f2 / (max_2d * 2)) * 25
        ps = sum((pos[p].get(digit, 0) / (max(pos[p].values()) or 1)) * 7.5 for p in [2, 3])
        sc += ps
        if n > 1:
            last = data[-1][2:]
            for i in range(n-1):
                if data[i][2:] == last and str(digit) in data[i+1][2:]:
                    sc += 2
            sc = min(sc, 15)
        exp = (n*4)/10
        if freq.get(digit, 0) < exp:
            sc += (exp - freq.get(digit, 0)) * 0.3
        sc = min(sc, 10)
        for k, v in d2_freq.most_common(5):
            if v >= 2 and str(digit) in k:
                sc += 1
        sc = min(sc, 5)
        fq = freq.get(digit, 0)
        if fq <= n*0.2:
            sc += 5
        elif fq <= n*0.3:
            sc += 3
        hf = n//2
        f1 = sum(1 for i in range(hf) if str(digit) in data[i])
        f2c = sum(1 for i in range(hf, n) if str(digit) in data[i])
        if f2c > f1*1.2:
            sc += 3
        elif f2c < f1*0.8:
            sc += 1
        else:
            sc += 2        scores[digit] = round(sc, 2)
    
    sorted_s = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return {'h6': [d for d, s in sorted_s[:6]], 'det': sorted_s}

# ========== FUNGSI 3D ==========
def calc3(data):
    if len(data) < 15:
        return {'h3': [], 'det': []}
    n = len(data)
    freq = Counter()
    pos = {i: Counter() for i in [1, 2, 3]}
    gaps = {i: [] for i in range(10)}
    
    for idx, num in enumerate(data):
        if len(num) != 4:
            continue
        for p in [1, 2, 3]:
            d = int(num[p])
            freq[d] += 1
            pos[p][d] += 1
            gaps[d].append(idx)
    
    scores = {}
    for digit in range(10):
        sc = 0
        ts = sum((0.98 ** (n-1-j)) for j in range(n-1, -1, -1) if str(digit) in data[j][1:])
        sc += min(ts * 4, 25)
        weights = [5, 7, 8]
        for i, p in enumerate([1, 2, 3]):
            mx = max(pos[p].values()) or 1
            sc += (pos[p].get(digit, 0) / mx) * weights[i]
        gp = gaps[digit]
        if not gp:
            sc += 12
        else:
            lg = n - 1 - gp[-1]
            ag = n / (freq.get(digit, 1) or 1)
            if lg > ag*1.6:
                sc += 12
            elif lg > ag*1.2:
                sc += 8
            else:
                sc += 5
        sc += 4
        scores[digit] = round(sc, 2)
    
    sorted_s = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return {'h3': [d for d, s in sorted_s[:3]], 'det': sorted_s}
# ========== FUNGSI 2D ==========
def gen2d(top6):
    result = []
    for i in range(100):
        s = f"{i:02d}"
        if int(s[0]) in top6 or int(s[1]) in top6:
            result.append(s)
    return result

# ========== FUNGSI 3D COMBO ==========
def gen3d(f2, top3):
    if not f2 or not top3:
        return []
    res, seen = [], set()
    for s in f2:
        a, b = int(s[0]), int(s[1])
        for x in top3:
            for p in [f"{a}{b}{x}", f"{a}{x}{b}", f"{b}{a}{x}", f"{b}{x}{a}", f"{x}{a}{b}", f"{x}{b}{a}"]:
                if p not in seen:
                    seen.add(p)
                    res.append(p)
    return sorted(res, key=int)

# ========== FUNGSI UTAMA ==========
def main():
    os.system('clear')
    
    cprint("\n" + "="*50, Colors.CYAN)
    cprint("   🔷 PREDIKTOR 6 ANGKA - TERMUX", Colors.BOLD + Colors.CYAN)
    cprint("="*50, Colors.CYAN)
    
    cprint("\n📊 PILIH PASARAN:", Colors.YELLOW)
    for k, v in MARKET_NAMES.items():
        cprint(f"   {k}. {v}", Colors.WHITE)
    
    try:
        choice = int(input(Colors.GREEN + "\n➤ Nomor Pasaran (1-10): " + Colors.RESET))
        if choice not in MARKET_FILES:
            raise ValueError
    except:
        cprint("❌ Input salah!", Colors.RED)
        return
    m_name = MARKET_NAMES[choice]
    cprint(f"\n🔄 Loading {m_name}...", Colors.CYAN)
    
    csv = fetch_github_csv(choice)
    if not csv:
        cprint("❌ Gagal ambil data. Cek internet!", Colors.RED)
        return    
    data, _ = parse_csv(csv)
    if len(data) < 15:
        cprint(f"❌ Data kurang ({len(data)}). Minimal 15.", Colors.RED)
        return
    
    cprint(f"✅ Data: {len(data)} putaran. Memproses...", Colors.GREEN)
    time.sleep(1)
    
    h6 = calc6(data)
    h3 = calc3(data)
    
    cprint("\n" + "="*50, Colors.CYAN)
    cprint(f"🔷 HASIL: {m_name}", Colors.BOLD + Colors.MAGENTA)
    cprint("="*50, Colors.CYAN)
    
    cprint(f"\n🔷 6 ANGKA: {Colors.BOLD + Colors.YELLOW}{' - '.join(map(str, h6['h6']))}{Colors.RESET}", Colors.WHITE)
    cprint(f"🏆 3D TOP : {Colors.BOLD + Colors.GREEN}{' - '.join(map(str, h3['h3']))}{Colors.RESET}", Colors.WHITE)
    
    c2 = gen2d(h6['h6'])
    cprint(f"\n🔢 2D AUTO ({Colors.CYAN}{len(c2)}{Colors.RESET} kombinasi):", Colors.WHITE)
    
    if len(c2) <= 50:
        cprint("  " + " ".join(c2), Colors.WHITE)
    else:
        cprint("  " + " ".join(c2[:30]) + f" ... ({len(c2)-30} lainnya)", Colors.WHITE)
    
    filt = input(Colors.YELLOW + "\n🔧 Filter digit (contoh: 159) / Enter skip: " + Colors.RESET).strip()
    f_c2 = c2
    if filt:
        digits = [int(x) for x in filt if x.isdigit()]
        f_c2 = [x for x in c2 if any(int(c) in digits for c in x)]
        cprint(f"\n✂️ Setelah Filter: {Colors.RED}{len(f_c2)}{Colors.RESET} dari {Colors.CYAN}{len(c2)}{Colors.RESET}", Colors.WHITE)
        if len(f_c2) > 0:
            if len(f_c2) <= 50:
                cprint("  " + " ".join(f_c2), Colors.WHITE)
            else:
                cprint("  " + " ".join(f_c2[:30]) + f" ... ({len(f_c2)-30} lainnya)", Colors.WHITE)
    
    c3 = gen3d(f_c2, h3['h3'])
    if c3:
        cprint(f"\n🎲 3D COMBO ({Colors.MAGENTA}{len(c3)}{Colors.RESET} kombinasi):", Colors.WHITE)
        if len(c3) <= 50:
            cprint("  " + " ".join(c3), Colors.WHITE)
        else:
            cprint("  " + " ".join(c3[:30]) + f" ... ({len(c3)-30} lainnya)", Colors.WHITE)
    
    save = input(Colors.GREEN + "\n💾 Simpan ke file? (y/n): " + Colors.RESET).lower()
    if save == 'y':
        fname = f"prediktor_{choice}_{datetime.now().strftime('%H%M%S')}.txt"
        path = '/sdcard/Download/' + fname if os.path.exists('/sdcard') else fname
        with open(path, 'w', encoding='utf-8') as f:
            f.write("="*50 + "\n")
            f.write("  🔷 PREDIKTOR 6 ANGKA - HASIL LENGKAP\n")
            f.write("="*50 + "\n")
            f.write(f"Pasaran: {m_name}\n")
            f.write(f"Tanggal: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write(f"Data: {len(data)} putaran\n\n")
            f.write(f"6 ANGKA: {' - '.join(map(str, h6['h6']))}\n")
            f.write(f"3D TOP: {' - '.join(map(str, h3['h3']))}\n\n")
            f.write(f"2D ({len(c2)}):\n" + "\n".join(c2) + "\n\n")
            if filt and f_c2 != c2:
                f.write(f"2D FILTERED ({len(f_c2)}):\n" + "\n".join(f_c2) + "\n\n")
            if c3:
                f.write(f"3D COMBO ({len(c3)}):\n" + "\n".join(c3) + "\n")
            f.write("="*50 + "\n")
            f.write("Gunakan dengan bijak. Good luck! 🍀\n")
        cprint(f"\n✅ Tersimpan di: {Colors.GREEN}{path}{Colors.RESET}", Colors.WHITE)
    
    cprint("\n🔷 Selesai. Jalankan lagi untuk pasaran lain.", Colors.CYAN)

# ========== ENTRY POINT ==========
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        cprint("\n⚠️ Dibatalkan.", Colors.YELLOW)
    except Exception as e:
        cprint(f"❌ Error: {e}", Colors.RED)