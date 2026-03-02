#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⭐ CONFIDENCE SCORE PREDICTOR - Termux Edition
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

# ========== FUNGSI HITUNG SKOR DIGIT ==========
def calc_digit_scores(data):
    if len(data) < 15:
        return []
    n = len(data)
    freq_scores = defaultdict(float)
    decay_scores = defaultdict(float)
    gap_scores = defaultdict(float)
    pos_scores = defaultdict(lambda: defaultdict(float))

    # 1. FREKUENSI GLOBAL
    all_freq = Counter(digit for num in data if len(num) == 4 for digit in num)
    max_freq = max(all_freq.values()) or 1
    for digit, count in all_freq.items():
        freq_scores[int(digit)] = (count / max_freq) * 30

    # 2. TIME DECAY
    for idx, num in enumerate(reversed(data)):
        if len(num) == 4:
            weight = 0.98 ** idx
            for j, digit in enumerate(num):
                pos = ['Ribu', 'Ratusan', 'Puluhan', 'Satuan'][j]
                pos_scores[pos][int(digit)] += weight * 20
                decay_scores[int(digit)] += weight * 5

    # 3. GAP ANALYSIS
    last_seen = {}
    for idx, num in enumerate(data):
        if len(num) == 4:
            for digit_char in num:
                digit = int(digit_char)
                if digit in last_seen:
                    gap = idx - last_seen[digit]
                    if gap > 10:
                        gap_scores[digit] += min(15, gap / 3)
                last_seen[digit] = idx

    # 4. POSISI SPESIFIK
    pos_counts = {p: Counter() for p in range(4)}
    for num in data:
        if len(num) == 4:
            for j, digit_char in enumerate(num):
                pos_counts[j][int(digit_char)] += 1
    max_pos_counts = [max(pc.values()) or 1 for pc in pos_counts.values()]
    for j in range(4):
        for digit, count in pos_counts[j].items():
            normalized = count / max_pos_counts[j] * 15
            if j in [2, 3]:
                normalized *= 1.5
            pos_scores[f'Pos{j+1}'][digit] += normalized

    # 5. HOT STREAK
    streak_bonus = defaultdict(int)
    for i in range(len(data)-1):
        if len(data[i]) == 4 and len(data[i+1]) == 4:
            for j in range(4):
                if int(data[i][j]) == int(data[i+1][j]):
                    streak_bonus[int(data[i][j])] += 3

    # 6. KOMBINASI FINAL
    final_scores = {}
    for digit in range(10):
        total = (freq_scores[digit] * 0.25) + \
                (decay_scores[digit] * 0.20) + \
                (gap_scores[digit] * 0.20) + \
                (sum(pos_scores[p].get(digit, 0) for p in pos_scores) * 0.25) + \
                (streak_bonus[digit] * 0.10)
        final_scores[digit] = min(100, round(total, 2))

    sorted_digits = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)
    return [(digit, score) for digit, score in sorted_digits]

# ========== FUNGSI KEPAHA/EKOR ==========
def calc_kepala_ekor_scores(data):
    if len(data) < 15:
        return {}, {}
    head_scores = defaultdict(float)
    tail_scores = defaultdict(float)
    for idx, num in enumerate(reversed(data)):
        if len(num) >= 3:
            weight = 0.98 ** idx
            head_digit = int(num[2])
            head_scores[head_digit] += weight * 40
            if len(num) >= 4:
                tail_digit = int(num[3])
                tail_scores[tail_digit] += weight * 40
    return dict(sorted(head_scores.items(), key=lambda x: x[1], reverse=True)), \
           dict(sorted(tail_scores.items(), key=lambda x: x[1], reverse=True))

# ========== STATUS & REKOMENDASI ==========
def get_confidence_status(score):
    if score >= 80:
        return "🔥 HIGH"
    elif score >= 60:
        return "⭐ MEDIUM"
    elif score >= 40:
        return "⚠️ LOW"
    else:
        return "❌ VERY LOW"

def get_recommendation(score):
    if score >= 80:
        return "Prioritaskan semua angka! ✅"
    elif score >= 60:
        return "Gunakan 60-70% kombinasi ⚠️"
    elif score >= 40:
        return "Pertimbangkan ulang 📉"
    else:
        return "JANGAN MAIN ❌"

def create_visual_bar(score, width=50):
    filled = int((score / 100) * width)
    empty = width - filled
    bar = "█" * filled + "░" * empty
    if score >= 80:
        bar_color = Colors.GREEN
    elif score >= 60:
        bar_color = Colors.YELLOW
    elif score >= 40:
        bar_color = Colors.BLUE
    else:
        bar_color = Colors.WHITE
    return f"{bar_color}[{bar}]{Colors.RESET}"

# ========== FUNGSI UTAMA ==========
def main():
    os.system('clear')
    print("\n" + "="*50)
    cprint("   ⭐ CONFIDENCE SCORE PREDICTOR", Colors.MAGENTA + Colors.BOLD)
    print("="*50)

    print("\n📊 PILIH PASARAN:")
    for k, v in MARKET_NAMES.items():
        cprint(f"   {k}. {v}", Colors.WHITE)

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

    # Hitung semua skor
    cprint("\n🔬 Memproses semua skor...", Colors.CYAN)
    time.sleep(1)
    all_scores = calc_digit_scores(data)
    head_scores, tail_scores = calc_kepala_ekor_scores(data)

    # Hitung confidence
    confidences = {}
    scores_top6 = [score for digit, score in all_scores[:6]]
    avg_6a = sum(scores_top6)/len(scores_top6) if scores_top6 else 0
    confidences['6a'] = {'score': avg_6a, 'status': get_confidence_status(avg_6a), 'recommendation': get_recommendation(avg_6a)}
    scores_tail = list(tail_scores.values())[:3]
    avg_3d = sum(scores_tail)/len(scores_tail) if scores_tail else 0
    confidences['3d'] = {'score': avg_3d, 'status': get_confidence_status(avg_3d), 'recommendation': get_recommendation(avg_3d)}
    scores_head = list(head_scores.values())[:7]
    avg_head = sum(scores_head)/len(scores_head) if scores_head else 0
    confidences['head'] = {'score': avg_head, 'status': get_confidence_status(avg_head), 'recommendation': get_recommendation(avg_head)}
    scores_tail_all = list(tail_scores.values())[:7]
    avg_tail = sum(scores_tail_all)/len(scores_tail_all) if scores_tail_all else 0
    confidences['tail'] = {'score': avg_tail, 'status': get_confidence_status(avg_tail), 'recommendation': get_recommendation(avg_tail)}
    overall_score = (avg_6a+avg_3d+avg_head+avg_tail)/4
    confidences['overall'] = {'score': overall_score, 'status': get_confidence_status(overall_score), 'recommendation': get_recommendation(overall_score)}

    # Tampilkan hasil
    cprint("\n" + "="*50, Colors.CYAN)
    cprint(f"⭐ HASIL CONFIDENCE: {m_name}", Colors.MAGENTA + Colors.BOLD)
    cprint("="*50, Colors.CYAN)
    cprint(f"\n📊 OVERALL CONFIDENCE: {confidences['overall']['score']:.1f}% {confidences['overall']['status']}", Colors.YELLOW)
    cprint(f"Rekomendasi: {confidences['overall']['recommendation']}", Colors.CYAN)
    cprint(f"Visualisasi: {create_visual_bar(confidences['overall']['score'])}", Colors.GREEN)

    # Save Option
    save = input(Colors.GREEN + "\n💾 Simpan ke file? (y/n): " + Colors.RESET).lower()
    if save == 'y':
        fname = f"confidence_{m_name.replace(' ', '_')}_{datetime.now().strftime('%H%M%S')}.txt"
        path = '/sdcard/Download/' + fname if os.path.exists('/sdcard') else fname
        with open(path, 'w', encoding='utf-8') as f:
            f.write("="*50 + "\n")
            f.write("  ⭐ CONFIDENCE SCORE - HASIL LENGKAP\n")
            f.write("="*50 + "\n")
            f.write(f"Pasaran: {m_name}\n")
            f.write(f"Tanggal: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write(f"Data: {len(data)} putaran\n\n")
            for feature in ['overall','6a','3d','head','tail']:
                f.write(f"{feature.upper()} CONFIDENCE: {confidences[feature]['score']:.1f}% {confidences[feature]['status']}\n")
                f.write(f"Rekomendasi: {confidences[feature]['recommendation']}\n\n")
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