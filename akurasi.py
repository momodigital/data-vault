#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔷 AKURASI TRACKER
Track akurasi prediksi vs hasil real
"""

import os
from datetime import datetime
from collections import defaultdict

class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'

def cprint(text, color=Colors.RESET):
    print(f"{color}{text}{Colors.RESET}")

class AkurasiTracker:
    def __init__(self):
        self.data_dir = '/sdcard/Prediktor_Akuras'
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def input_real_result(self):
        print("\n" + "="*50)
        print("   INPUT HASIL REAL")
        print("="*50)
        
        pasaran = input("\nPasaran (contoh: Cambodia): ").strip()
        tanggal = input("Tanggal (dd/mm/yyyy): ").strip() or datetime.now().strftime('%d/%m/%Y')
        angka = input("Hasil Real (4 digit): ").strip()
        
        if len(angka) != 4:
            cprint("❌ Masukkan 4 digit!", Colors.RED)
            return None
        
        return {'pasaran': pasaran, 'tanggal': tanggal, 'angka': angka}
    
    def track_prediction(self, result_data):
        files = [f for f in os.listdir(self.data_dir) if f.startswith('prediktor_') and f.endswith('.txt')]
        if not files:
            cprint("❌ Tidak ada file prediksi ditemukan", Colors.RED)
            return None
        latest = max(files)
        with open(os.path.join(self.data_dir, latest), 'r') as f:
            content = f.read()
        cprint("\n📄 PREDIKSI TERAKHIR:", Colors.CYAN)
        print(content[:500] + "...")
        return content
    
    def calculate_accuracy(self, prediksi, real):
        pred_list = set(prediksi.split('*')) if '*' in prediksi else set(prediksi)
        real_set = set(real)
        hit = len(pred_list & real_set)
        accuracy = (hit / 4 * 100) if hit > 0 else 0
        return {
            'hit': hit,
            'accuracy': min(accuracy, 100),
            'status': '✅ HIT' if hit >= 1 else '❌ TIDAK HIT'
        }
    
    def save_record(self, result_data, pred_content, accuracy):
        record_file = os.path.join(self.data_dir, f"record_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv")
        header_needed = not os.path.exists(record_file)
        with open(record_file, 'a') as f:
            if header_needed:
                f.write("PASARAN,TANGGAL,REAL_ANGKA,PREDIKSI,ACC,HIT,STATUS\n")
            pred_2d = ""
            pred_kepala_ekor = ""
            lines = pred_content.split('\n')
            for i, line in enumerate(lines):
                if '2D FILTERED' in line and i+1 < len(lines):
                    pred_2d = lines[i+1][:20]
                if 'KEPALA*EKOR' in line and i+1 < len(lines):
                    pred_kepala_ekor = lines[i+1][:20]
            f.write(f"{result_data['pasaran']},{result_data['tanggal']},{result_data['angka']},{pred_2d},{pred_kepala_ekor},{accuracy['accuracy']}%,{accuracy['status']}\n")
        return record_file
    
    def show_statistics(self):
        files = [f for f in os.listdir(self.data_dir) if f.startswith('record_') and f.endswith('.csv')]
        if not files:
            cprint("❌ Belum ada data akurasi", Colors.RED)
            return
        latest = max(files)
        with open(os.path.join(self.data_dir, latest), 'r') as f:
            lines = f.readlines()[1:]
        records = []
        for line in lines:
            parts = line.strip().split(',')
            if len(parts) >= 7:
                records.append({
                    'pasaran': parts[0],
                    'tanggal': parts[1],
                    'real': parts[2],
                    'acc': float(parts[5].replace('%','')) if '%' in parts[5] else 0,
                    'status': parts[6]
                })
        if not records:
            return
        hits = sum(1 for r in records if r['status'].strip() == '✅ HIT')
        total = len(records)
        avg_acc = sum(r['acc'] for r in records) / total if total > 0 else 0
        cprint("\n📊 STATISTIK AKURASI", Colors.GREEN)
        print("="*50)
        cprint(f"Total Prediksi : {total}", Colors.WHITE)
        cprint(f"⚡ Hit Rate     : {hits}/{total} ({hits/total*100:.1f}%)", Colors.YELLOW)
        cprint(f"🎯 Avg Accuracy : {avg_acc:.1f}%", Colors.YELLOW)
        print()
        pasars = {}
        for r in records:
            p = r['pasaran']
            if p not in pasars:
                pasars[p] = {'hits': 0, 'total': 0}
            pasars[p]['total'] += 1
            if r['status'].strip() == '✅ HIT':
                pasars[p]['hits'] += 1
        for p, d in pasars.items():
            rate = d['hits']/d['total']*100 if d['total'] > 0 else 0
            icon = "🔥" if rate >= 50 else "⚠️" if rate >= 25 else "💤"
            cprint(f"{icon} {p}: {d['hits']}/{d['total']} ({rate:.1f}%)",
                   Colors.GREEN if rate >= 50 else Colors.YELLOW if rate >= 25 else Colors.RED)

def main():
    tracker = AkurasiTracker()
    while True:
        os.system('clear')
        print("="*50)
        print("   🔷 AKURASI TRACKER")
        print("="*50)
        print("\n1. Input Hasil Real + Compare")
        print("2. Lihat Statistik")
        print("3. Exit")
        choice = input("\nPilih (1-3): ")
        if choice == '1':
            result_data = tracker.input_real_result()
            if result_data:
                pred_content = tracker.track_prediction(result_data)
                if pred_content:
                    accuracy = tracker.calculate_accuracy(pred_content, result_data['angka'])
                    save_path = tracker.save_record(result_data, pred_content, accuracy)
                    print(f"\n✅ Record tersimpan di: {save_path}")
                    input("\nTekan Enter lanjut...")
        elif choice == '2':
            tracker.show_statistics()
            input("\nTekan Enter lanjut...")
        elif choice == '3':
            break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDibatalkan")
    except Exception as e:
        print(f"❌ Error: {e}")