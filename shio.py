#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🐲 SHIO PREDICTOR ADVANCED
Integrasi Analisis Data + Shio Chinese
"""

import os
from collections import Counter, defaultdict

# ========== KONFIGURASI ==========
SHIO_LIST = ['Tikus', 'Sapi', 'Macan', 'Kelinci', 'Naga', 'Ular', 
             'Kuda', 'Kambing', 'Monyet', 'Ayam', 'Anjing', 'Babi']

ELEMENT_COLOR = ['Air', 'Kayu', 'Api', 'Tanah', 'Logam']

class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'

def cprint(text, color=Colors.RESET):
    print(f"{color}{text}{Colors.RESET}")

# ========== FUNGSI SHIO PREDIKSI ==========
def predict_shio_hybrid(data):
    if len(data) < 15:
        return []
    n = len(data)
    freq_scores = defaultdict(float)
    decay_scores = defaultdict(float)
    gap_scores = defaultdict(float)
    shio_count = Counter(int(num[-1]) % 12 for num in data if len(num) >= 4)
    max_freq = max(shio_count.values()) or 1
    for shio, count in shio_count.items():
        freq_scores[shio] = (count / max_freq) * 40
    for idx, num in enumerate(reversed(data)):
        if len(num) >= 4:
            shio = int(num[-1]) % 12
            weight = 0.98 ** idx
            decay_scores[shio] += weight * 30
    last_seen = {}
    for idx, num in enumerate(data):
        if len(num) >= 4:
            shio = int(num[-1]) % 12
            if shio in last_seen:
                gap = idx - last_seen[shio]
                if gap > 15:
                    gap_scores[shio] += 20
                elif gap > 10:
                    gap_scores[shio] += 15
                elif gap > 5:
                    gap_scores[shio] += 10
            last_seen[shio] = idx
    streak_bonus = defaultdict(int)
    for i in range(len(data)-1):
        if len(data[i]) >= 4 and len(data[i+1]) >= 4:
            s1 = int(data[i][-1]) % 12
            s2 = int(data[i+1][-1]) % 12
            if s1 == s2:
                streak_bonus[s1] += 5
    final_scores = {}
    for shio in range(12):
        total = freq_scores[shio] + decay_scores[shio] + gap_scores[shio] + streak_bonus[shio]
        final_scores[shio] = min(100, total)
    sorted_shios = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)[:7]
    return [(idx, round(score, 2)) for idx, score in sorted_shios]

# ========== FUNGSI CONVERT ==========
def num_to_shio_simple(number):
    if len(number) < 4:
        return None, "Invalid"
    last_digit = int(number[-1]) % 12
    shio_name = SHIO_LIST[last_digit]
    element_idx = (last_digit // 2) % 5
    element = ELEMENT_COLOR[element_idx]
    return shio_name, element

# ========== MAIN MENU ==========
def main():
    os.system('clear')
    print("="*50)
    cprint("   🐲 SHIO PREDICTOR ADVANCED", Colors.CYAN + Colors.BOLD)
    print("="*50)
    print("\n1. Predict Shio dari Data CSV")
    print("2. Convert Angka Manual ke Shio")
    print("3. Exit")
    choice = input("\nPilih (1-3): ").strip()
    if choice == '1':
        dummy_data = ['3721','5614','3892','7145','3267','8153','3941','6728','3519','4236','1045','6283','9517','2364','7891']
        shio_results = predict_shio_hybrid(dummy_data)
        print("\n📊 HASIL PREDIKSI SHIO:")
        print("-"*50)
        for shio_idx, score in shio_results:
            shio_name = SHIO_LIST[shio_idx]
            element_idx = (shio_idx // 2) % 5
            element = ELEMENT_COLOR[element_idx]
            status_icon = "🔥" if score >= 60 else ("⭐" if score >= 40 else "⚪")
            bar_len = int(score / 2)
            bar = "█" * bar_len + "░" * (50 - bar_len)
            cprint(f"{status_icon} {shio_name:<10} [{bar}] {score:.1f}% {element}", 
                   Colors.GREEN if score >= 60 else Colors.YELLOW if score >= 40 else Colors.WHITE)
        input("\nTekan Enter kembali...")
    elif choice == '2':
        print("\n🔢 INPUT ANGKA MANUAL:")
        angka = input("Masukkan 4-digit angka: ").strip()
        if len(angka) != 4:
            cprint("❌ Harus 4 digit!", Colors.RED)
            return
        shio_name, element = num_to_shio_simple(angka)
        print("\n📄 HASIL CONVERT:")
        cprint(f"Angka          : {angka}", Colors.WHITE)
        cprint(f"Digit Terakhir : {angka[-1]}", Colors.WHITE)
        cprint(f"Shio           : {shio_name.upper()} {element}", Colors.MAGENTA)
        cprint(f"Nomor Shio     : {(int(angka[-1]) % 12) + 1}/12", Colors.CYAN)
        input("\nTekan Enter kembali...")
    elif choice == '3':
        pass

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDibatalkan")