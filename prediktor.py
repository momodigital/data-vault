#!/usr/bin/env python3
import requests
import re
import os
import time
from collections import Counter
from datetime import datetime

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

def fetch_github_csv(market_key):
    file_info = MARKET_FILES.get(market_key)
    if not file_info:
        return None
    url = f"https://raw.githubusercontent.com/{GITHUB_CONFIG['username']}/{GITHUB_CONFIG['repo']}/{GITHUB_CONFIG['branch']}/{GITHUB_CONFIG['path']}/{file_info[1]}"
    try:
        print("Mengambil data dari GitHub...")
        r = requests.get(url, timeout=30)
        r.raise_for_status()        return r.text
    except Exception as e:
        print(f"Error: {e}")
        return None

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

def calc6(data):
    if len(data) < 15:
        return {'h6': [], 'det': []}
    n = len(data)
    freq = Counter()
    pos = {i: Counter() for i in range(4)}
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
                    sc += 2            sc = min(sc, 15)
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
            sc += 2
        scores[digit] = round(sc, 2)
    sorted_s = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return {'h6': [d for d, s in sorted_s[:6]], 'det': sorted_s}

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
            mx = max(pos[p].values()) or 1            sc += (pos[p].get(digit, 0) / mx) * weights[i]
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

def gen2d(top6):
    return [f"{i:02d}" for i in range(100) if int(str(i)[0]) in top6 or int(str(i)[-1]) in top6]

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

def main():
    os.system('clear')
    print("\n" + "="*50)
    print("   PREDIKTOR 6 ANGKA - TERMUX")
    print("="*50)
    print("\nPILIH PASARAN:")
    for k, v in MARKET_NAMES.items():
        print(f"   {k}. {v}")
    try:
        choice = int(input("\nNomor Pasaran (1-10): "))
        if choice not in MARKET_FILES:
            raise ValueError
    except:
        print("Input salah!")
        return
    m_name = MARKET_NAMES[choice]    print(f"\nLoading {m_name}...")
    csv = fetch_github_csv(choice)
    if not csv:
        print("Gagal ambil data. Cek internet!")
        return
    data, _ = parse_csv(csv)
    if len(data) < 15:
        print(f"Data kurang ({len(data)}). Minimal 15.")
        return
    print(f"Data: {len(data)} putaran. Memproses...")
    time.sleep(1)
    h6 = calc6(data)
    h3 = calc3(data)
    print("\n" + "="*50)
    print(f"HASIL: {m_name}")
    print("="*50)
    print(f"6 ANGKA: {' - '.join(map(str, h6['h6']))}")
    print(f"3D TOP: {' - '.join(map(str, h3['h3']))}")
    c2 = gen2d(h6['h6'])
    print(f"\n2D ({len(c2)}): " + "*".join(c2[:10]) + "...")
    filt = input("\nFilter digit (contoh: 159) / Enter skip: ").strip()
    f_c2 = c2
    if filt:
        digits = [int(x) for x in filt if x.isdigit()]
        f_c2 = [x for x in c2 if any(int(c) in digits for c in x)]
        print(f"Sisa Filter: {len(f_c2)}")
    c3 = gen3d(f_c2, h3['h3'])
    if c3:
        print(f"3D Combo ({len(c3)}): " + "*".join(c3[:8]) + "...")
    save = input("\nSimpan ke file? (y/n): ").lower()
    if save == 'y':
        fname = f"prediktor_{choice}_{datetime.now().strftime('%H%M%S')}.txt"
        path = '/sdcard/Download/' + fname if os.path.exists('/sdcard') else fname
        with open(path, 'w') as f:
            f.write(f"PASARAN: {m_name}\n")
            f.write(f"6 ANGKA: {' - '.join(map(str, h6['h6']))}\n")
            f.write(f"3D: {' - '.join(map(str, h3['h3']))}\n")
            f.write(f"2D COUNT: {len(c2)}\n")
            f.write(f"FILTERED 2D: {len(f_c2)}\n")
            f.write(f"3D COMBO: {len(c3)}\n")
        print(f"Tersimpan di: {path}")
    print("\nSelesai.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nDibatalkan.")
    except Exception as e:
        print(f"Error: {e}")
