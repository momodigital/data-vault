#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 AKURASI TRACKER v3.0 - MARKET CONTEXT EDITION (FIXED)
Track hasil prediksi vs kenyataan dengan konteks pasar dari GitHub
"""

import os
import csv
import requests
import re
from datetime import datetime
from collections import Counter

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

class AkurasiTracker:
    def __init__(self):
        self.db_dir = '/sdcard/Prediktor_Akurasi_DB'
        if not os.path.exists(self.db_dir):
            os.makedirs(self.db_dir)
        self.records_file = os.path.join(self.db_dir, 'records.csv')
        self._init_db()
    
    class Colors:
        RESET = '\033[0m'
        RED = '\033[91m'
        GREEN = '\033[92m'
        YELLOW = '\033[93m'
        CYAN = '\033[96m'
        WHITE = '\033[97m'
        MAGENTA = '\033[95m'
        BOLD = '\033[1m'
        BLUE = '\033[94m'
    
    @staticmethod
    def cprint(text, color=None, end='\n'):
        try:
            if color:
                formatted = f"{color}{text}{AkurasiTracker.Colors.RESET}"
            else:
                formatted = str(text)
            print(formatted, end=end)
        except Exception:
            print(str(text), end=end)
    
    def _init_db(self):
        if not os.path.exists(self.records_file):
            with open(self.records_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['ID', 'Pasaran', 'Tanggal', 'Real_Result', 
                               'Pred_6A', 'Pred_2D', 'Pred_Shio', 'Status', 'Market_Context', 'ACC_Persen'])
    
    def fetch_market_context(self, market_key):
        """Fetch market statistics from GitHub CSV"""
        file_info = MARKET_FILES.get(market_key)
        if not file_info:
            return {'context_note': 'Market not found'}
        
        url = f"https://raw.githubusercontent.com/{GITHUB_CONFIG['username']}/{GITHUB_CONFIG['repo']}/{GITHUB_CONFIG['branch']}/{GITHUB_CONFIG['path']}/{file_info[1]}"
        
        try:
            r = requests.get(url, timeout=30)
            r.raise_for_status()
            text = r.text
            
            # Parse data
            data = []
            for line in text.strip().split('\n')[1:]:
                if not line: continue
                parts = line.split(',')
                if len(parts) >= 2:
                    match = re.search(r'\d{4}', parts[1].strip())
                    if match and len(match.group()) == 4:
                        data.append(match.group())
            
            # Calculate context stats
            if not data:
                return {'context_note': 'No data available'}
            
            all_digits = [d for num in data for d in num]
            digit_freq = Counter(all_digits)
            last_digit_freq = Counter(int(num[3]) for num in data if len(num) == 4)
            
            hot_digits = [d for d, c in digit_freq.most_common(5)]
            # Get cold digits properly
            all_items = list(digit_freq.items())
            cold_digits = [d for d, c in sorted(all_items, key=lambda x: x[1])[:5]] if len(all_items) >= 5 else [d for d, c in all_items[:len(all_items)]]
            last_digits_hot = [d for d, c in last_digit_freq.most_common(5)]
            
            return {
                'count': len(data),
                'hot': hot_digits,
                'cold': cold_digits,
                'last_hot': last_digits_hot,
                'total_data': len(data)
            }
        except Exception as e:
            self.cprint(f"⚠️ Cannot fetch: {e}", self.Colors.YELLOW)
            return {'context_note': f'Error: {str(e)[:50]}'}
    
    def input_real_result(self):
        print("\n" + "="*50)
        self.cprint("   INPUT HASIL REAL", self.Colors.MAGENTA + self.Colors.BOLD)
        print("="*50)
        
        pasaran = input("\n➤ Pasaran (1-10 atau nama): ").strip()
        tanggal = input("Tanggal (dd/mm/yyyy): ").strip() or datetime.now().strftime('%d/%m/%Y')
        angka = input("Hasil Real (4 digit): ").strip()
        
        if len(angka) != 4 or not angka.isdigit():
            self.cprint("❌ Masukkan tepat 4 digit angka!", self.Colors.RED)
            return None
        
        # Determine market key
        market_key = None
        for k, v in MARKET_NAMES.items():
            if str(k) == pasaran or v.lower() in pasaran.lower():
                market_key = k
                break
        
        # Get market context from GitHub
        context = self.fetch_market_context(market_key) if market_key else {'note': 'Custom Market'}
        
        pred_6a = input("Prediksi 6A (koma/enter skip): ").strip() or '-'
        pred_2d = input("Prediksi 2D (koma/enter skip): ").strip() or '-'
        pred_shio = input("Prediksi Shio (skip): ").strip() or '-'
        
        return {
            'pasaran': MARKET_NAMES.get(market_key, pasaran) if market_key else pasaran,
            'tanggal': tanggal,
            'angka': angka,
            'pred_6a': pred_6a,
            'pred_2d': pred_2d,
            'pred_shio': pred_shio,
            'market_context': str(context)
        }
    
    def calculate_accuracy(self, record_data):
        """Hitung akurasi dengan smart scoring"""
        real_digits = list(record_data['angka'])
        hit_score = 0
        
        # Check each position - digit match
        for i, digit in enumerate(real_digits):
            # Check if digit appears in predictions
            if record_data['pred_6a'] != '-':
                if digit in record_data['pred_6a']:
                    hit_score += 10
            
            if record_data['pred_2d'] != '-':
                pred_2d_list = [d.strip() for d in record_data['pred_2d'].split(',')]
                for p2d in pred_2d_list:
                    if len(p2d) == 2 and p2d[0] == digit:
                        hit_score += 5  # First digit match
                    if len(p2d) == 2 and p2d[1] == digit:
                        hit_score += 5  # Second digit match
        
        # Bonus for exact 2D match
        if record_data['pred_2d'] != '-':
            pred_2d_list = [d.strip() for d in record_data['pred_2d'].split(',')]
            real_2d = record_data['angka'][2:]
            if real_2d in pred_2d_list:
                hit_score += 30  # Big bonus for exact 2D
            elif real_2d[0] in [p[0] for p in pred_2d_list if len(p) == 2]:
                hit_score += 10  # Partial match first digit
            elif real_2d[1] in [p[1] for p in pred_2d_list if len(p) == 2]:
                hit_score += 10  # Partial match second digit
        
        # Convert to percentage
        accuracy = min(100, max(0, hit_score))
        
        # Status determination
        if hit_score >= 50:
            status = "✅ HIT"
        elif hit_score >= 25:
            status = "⚠️ PARTIAL"
        else:
            status = "❌ TIDAK HIT"
        
        return {
            'hit_count': hit_score,
            'accuracy': accuracy,
            'status': status
        }
    
    def save_record(self, record_data, accuracy_data):
        """Save dengan konteks pasar"""
        # Count existing records
        try:
            with open(self.records_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                id_num = len(lines) - 1  # Subtract header
        except:
            id_num = 0
        
        if id_num < 0: 
            id_num = 0
        
        with open(self.records_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                id_num + 1,
                record_data['pasaran'],
                record_data['tanggal'],
                record_data['angka'],
                record_data['pred_6a'],
                record_data['pred_2d'],
                record_data['pred_shio'],
                accuracy_data['status'],
                str(record_data['market_context'])[:100] if len(str(record_data['market_context'])) > 100 else str(record_data['market_context']),
                f"{accuracy_data['accuracy']}%"
            ])
        
        return self.records_file
    
    def show_statistics(self):
        """Show statistik lengkap dengan breakdown per pasar"""
        records = []
        
        try:
            with open(self.records_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                records = [row for row in reader]
        except Exception as e:
            self.cprint(f"❌ Error membaca database: {e}", self.Colors.RED)
            return
        
        if not records:
            self.cprint("\n❌ Belum ada data akurasi", self.Colors.RED)
            return
        
        total = len(records)
        hits = sum(1 for r in records if r['Status'].strip() == '✅ HIT')
        partials = sum(1 for r in records if r['Status'].strip() == '⚠️ PARTIAL')
        misses = total - hits - partials
        
        acc_scores = []
        for r in records:
            try:
                if 'ACC_Persen' in r and r['ACC_Persen']:
                    acc = float(r['ACC_Persen'].replace('%', ''))
                    acc_scores.append(acc)
            except:
                pass
        
        avg_acc = sum(acc_scores) / len(acc_scores) if acc_scores else 0
        
        # Per-market stats
        pasars = {}
        for r in records:
            p = r['Pasaran']
            if p not in pasars: 
                pasars[p] = {'hits': 0, 'partial': 0, 'miss': 0, 'total': 0}
            
            pasars[p]['total'] += 1
            if r['Status'].strip() == '✅ HIT': 
                pasars[p]['hits'] += 1
            elif r['Status'].strip() == '⚠️ PARTIAL': 
                pasars[p]['partial'] += 1
            else: 
                pasars[p]['miss'] += 1
        
        print("\n" + "="*50)
        self.cprint("📊 STATISTIK AKURASI LENGKAP", self.Colors.GREEN)
        print("="*50)
        print(f"Total Prediksi     : {total}")
        print(f"{self.Colors.GREEN}✅ Hit Rate         : {hits}/{total} ({hits/total*100:.1f}%){self.Colors.RESET}")
        print(f"{self.Colors.YELLOW}⚠️ Partials          : {partials}/{total} ({partials/total*100:.1f}%){self.Colors.RESET}")
        print(f"{self.Colors.RED}❌ Miss             : {misses}/{total} ({misses/total*100:.1f}%){self.Colors.RESET}")
        print(f"{self.Colors.CYAN}🎯 Average Acc      : {avg_acc:.1f}%{self.Colors.RESET}")
        
        print("\n" + "-"*50)
        self.cprint("PERFORMA PER PASARAN:", self.Colors.BLUE)
        for p, d in sorted(pasars.items(), key=lambda x: x[1]['hits'], reverse=True)[:5]:
            total_p = d['total']
            rate = d['hits']/total_p*100 if total_p > 0 else 0
            icon = "🔥" if rate >= 50 else "⭐" if rate >= 25 else "⚪"
            self.cprint(f"{icon} {p}: {d['hits']}/{total_p} ({rate:.1f}%)", self.Colors.WHITE)
        
        # Save report option
        save = input(f"\n{self.Colors.GREEN}💾 Simpan laporan? (y/n): {self.Colors.RESET}").lower()
        if save == 'y':
            path = os.path.join('/sdcard/Download', f"akurasi_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write("="*50 + "\n")
                    f.write("AKURASI TRACKER REPORT\n")
                    f.write("="*50 + "\n\n")
                    f.write(f"Total: {total}\n")
                    f.write(f"Hits: {hits} ({hits/total*100:.1f}%)\n")
                    f.write(f"Partials: {partials} ({partials/total*100:.1f}%)\n")
                    f.write(f"Misses: {misses} ({misses/total*100:.1f}%)\n\n")
                    f.write("Per Pasar:\n")
                    for p, d in pasars.items():
                        total_p = d['total']
                        rate = d['hits']/total_p*100 if total_p > 0 else 0
                        f.write(f"{p}: {d['hits']}/{total_p} ({rate:.1f}%)\n")
                self.cprint(f"✅ Tersimpan: {path}", self.Colors.GREEN)
            except Exception as e:
                self.cprint(f"❌ Error menyimpan: {e}", self.Colors.RED)


def main():
    tracker = AkurasiTracker()
    
    while True:
        os.system('clear' if os.name == 'posix' else 'cls')
        print("\n" + "="*50)
        tracker.cprint("   🎯 AKURASI TRACKER v3.0", tracker.Colors.MAGENTA + tracker.Colors.BOLD)
        print("="*50)
        print("\n1. Input Hasil Real + Compare")
        print("2. Lihat Statistik")
        print("3. Clear Database")
        print("4. Export All")
        print("X Exit")
        
        choice = input(f"\n{tracker.Colors.GREEN}Pilih (1-4/X): {tracker.Colors.RESET}").strip().upper()
        
        if choice == '1':
            record_data = tracker.input_real_result()
            if record_data:
                accuracy_data = tracker.calculate_accuracy(record_data)
                tracker.save_record(record_data, accuracy_data)
                
                print(f"\n{'-'*50}")
                print(f"📄 RESULT:")
                print(f"• Real Result   : {record_data['angka']}")
                print(f"• Pred 6A       : {record_data['pred_6a']}")
                print(f"• Pred 2D       : {record_data['pred_2d']}")
                print(f"• Akurasi Total : {accuracy_data['accuracy']}%")
                print(f"• Status        : {accuracy_data['status']}")
                print(f"{'-'*50}")
                print(f"{tracker.Colors.GREEN}✅ Record tersimpan{tracker.Colors.RESET}")
                input("\nTekan Enter lanjut...")
        
        elif choice == '2':
            tracker.show_statistics()
            input("\nTekan Enter lanjut...")
        
        elif choice == '3':
            confirm = input(f"{tracker.Colors.YELLOW}Hapus semua data? (y/n): {tracker.Colors.RESET}").lower()
            if confirm == 'y':
                # Create new file with header only
                with open(tracker.records_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['ID', 'Pasaran', 'Tanggal', 'Real_Result', 
                                   'Pred_6A', 'Pred_2D', 'Pred_Shio', 'Status', 'Market_Context', 'ACC_Persen'])
                print(f"{tracker.Colors.GREEN}Database cleared.{tracker.Colors.RESET}")
                input("Tekan Enter lanjut...")
        
        elif choice == '4':
            records = []
            try:
                with open(tracker.records_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    records = list(reader)
            except Exception as e:
                tracker.cprint(f"Error membaca: {e}", tracker.Colors.RED)
                records = []
            
            export_file = os.path.join('/sdcard/Download', f"akurasi_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
            try:
                with open(export_file, 'w', newline='', encoding='utf-8') as f:
                    if records:
                        writer = csv.DictWriter(f, fieldnames=['ID','Pasaran','Tanggal','Real_Result','Pred_6A','Pred_2D','Status','ACC_Persen'])
                        writer.writeheader()
                        # Write only selected fields
                        for r in records:
                            writer.writerow({
                                'ID': r.get('ID', ''),
                                'Pasaran': r.get('Pasaran', ''),
                                'Tanggal': r.get('Tanggal', ''),
                                'Real_Result': r.get('Real_Result', ''),
                                'Pred_6A': r.get('Pred_6A', ''),
                                'Pred_2D': r.get('Pred_2D', ''),
                                'Status': r.get('Status', ''),
                                'ACC_Persen': r.get('ACC_Persen', '')
                            })
                tracker.cprint(f"✅ Exported: {export_file}", tracker.Colors.GREEN)
            except Exception as e:
                tracker.cprint(f"❌ Error export: {e}", tracker.Colors.RED)
            input("Tekan Enter lanjut...")
        
        elif choice == 'X':
            break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{AkurasiTracker.Colors.YELLOW}⚠️ Dibatalkan.{AkurasiTracker.Colors.RESET}")
    except Exception as e:
        print(f"{AkurasiTracker.Colors.RED}❌ Error: {e}{AkurasiTracker.Colors.RESET}")
        import traceback
        traceback.print_exc()