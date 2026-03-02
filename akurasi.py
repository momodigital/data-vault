#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 AKURASI TRACKER - Termux Edition
Track hasil prediksi vs kenyataan
"""

import os
import re
import csv
from datetime import datetime
from collections import Counter

# ========== WARNA ANSI ==========
class Colors:
    RESET = '\033[0m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'

class AkurasiTracker:
    def __init__(self):
        self.db_dir = '/sdcard/Prediktor_Akurasi_DB'
        if not os.path.exists(self.db_dir):
            os.makedirs(self.db_dir)
        self.records_file = os.path.join(self.db_dir, 'records.csv')
        self._init_db()
    
    def _init_db(self):
        """Initialize database file"""
        if not os.path.exists(self.records_file):
            with open(self.records_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['ID', 'Pasaran', 'Tanggal', 'Real_Result', 
                               'Predict_6A', 'Predict_2D', 'Predict_Shio',
                               'Hit_Total', 'ACC_Persen', 'Status'])
    
    def input_real_result(self):
        """Input hasil real dari pasaran"""
        print("\n" + "="*50)
        print(f"{Colors.MAGENTA}   INPUT HASIL REAL{Colors.RESET}")
        print("="*50)
        
        pasaran = input("\n➤ Pasaran: ").strip()
        tanggal = input("📅 Tanggal (dd/mm/yyyy): ").strip() or datetime.now().strftime('%d/%m/%Y')
        angka = input("🎯 Hasil Real (4 digit): ").strip()
        
        if len(angka) != 4 or not angka.isdigit():
            print(f"{Colors.RED}❌ Masukkan tepat 4 digit angka!{Colors.RESET}")
            input("\nTekan Enter untuk kembali...")
            return None
        
        # Input prediksi manual
        print(f"\n{Colors.YELLOW}📝 Masukkan prediksi (kosongkan jika tidak ada):{Colors.RESET}")
        
        pred_6a = input("6 Angka (pisahkan spasi): ").strip().split()
        pred_2d = input("2D Combo (pisahkan spasi): ").strip().split()
        pred_shio = input("Shio: ").strip()
        
        return {
            'pasaran': pasaran,
            'tanggal': tanggal,
            'angka': angka,
            'pred_6a': [p for p in pred_6a if p.isdigit()][:6],
            'pred_2d': [p for p in pred_2d if p][:10],
            'pred_shio': pred_shio
        }
    
    def calculate_accuracy(self, record_data):
        """Hitung akurasi dari real result vs prediksi"""
        real_digits = list(record_data['angka'])
        hit_6a = hit_2d = 0
        
        # Cek 6A
        pred_6a_set = set(int(d) for d in record_data['pred_6a'] if d.isdigit())
        real_set = set(int(d) for d in real_digits)
        common_6a = pred_6a_set & real_set
        hit_6a = len(common_6a)
        
        # Cek 2D
        for p2d in record_data['pred_2d']:
            if len(p2d) == 2 and p2d.isdigit():
                if p2d[0] in real_digits and p2d[1] in real_digits:
                    hit_2d += 1
        
        # Hitung akurasi total
        total_score = (hit_6a * 10) + (hit_2d * 5)
        max_score = (len(record_data['pred_6a']) * 10) + (len(record_data['pred_2d']) * 5)
        accuracy = (total_score / max_score * 100) if max_score > 0 else 0
        accuracy = min(100, max(0, round(accuracy, 1)))
        
        if hit_6a >= 3:
            status = "✅ HIGH HIT"
        elif hit_6a >= 1 or hit_2d >= 2:
            status = "⚠️ PARTIAL"
        else:
            status = "❌ MISS"
        
        return {
            'hit_6a': hit_6a,
            'hit_2d': hit_2d,
            'accuracy': accuracy,
            'status': status
        }
    
    def save_record(self, record_data, accuracy_data):
        """Simpan rekaman hasil"""
        # Baca file untuk mendapatkan ID terakhir
        try:
            with open(self.records_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                last_id = len(lines) - 1  # Kurangi 1 untuk header
        except:
            last_id = 0
        
        id_num = last_id
        
        with open(self.records_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                id_num + 1,
                record_data['pasaran'],
                record_data['tanggal'],
                record_data['angka'],
                '|'.join(record_data['pred_6a']),
                '|'.join(record_data['pred_2d']),
                record_data['pred_shio'],
                str(accuracy_data['hit_6a']),
                str(accuracy_data['accuracy']) + '%',
                accuracy_data['status']
            ])
        return self.records_file
    
    def show_statistics(self):
        """Tampilkan statistik akurasi"""
        records = []
        
        try:
            with open(self.records_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                records = [row for row in reader]
        except Exception as e:
            print(f"{Colors.RED}❌ Error membaca database: {e}{Colors.RESET}")
            return
        
        if not records:
            print(f"\n{Colors.RED}❌ Belum ada data akurasi{Colors.RESET}")
            return
        
        total = len(records)
        hits = sum(1 for r in records if 'HIGH' in r['Status'])
        partials = sum(1 for r in records if 'PARTIAL' in r['Status'])
        misses = total - hits - partials
        
        acc_scores = []
        for r in records:
            try:
                acc = float(r['ACC_Persen'].replace('%', ''))
                acc_scores.append(acc)
            except:
                pass
        
        avg_acc = sum(acc_scores) / len(acc_scores) if acc_scores else 0
        
        print("\n" + "="*50)
        print(f"{Colors.GREEN}📊 STATISTIK AKURASI{Colors.RESET}")
        print("="*50)
        print(f"{Colors.WHITE}Total Prediksi      : {total}{Colors.RESET}")
        print(f"{Colors.GREEN}✅ HIGH HIT          : {hits}/{total} ({hits/total*100:.1f}%){Colors.RESET}")
        print(f"{Colors.YELLOW}⚠️ PARTIAL            : {partials}/{total} ({partials/total*100:.1f}%){Colors.RESET}")
        print(f"{Colors.RED}❌ MISS               : {misses}/{total} ({misses/total*100:.1f}%){Colors.RESET}")
        print(f"{Colors.CYAN}🎯 Average Acc        : {avg_acc:.1f}%{Colors.RESET}")
        
        # Per pasaran
        pasars = {}
        for r in records:
            p = r['Pasaran']
            if p not in pasars:
                pasars[p] = {'hits': 0, 'partial': 0, 'miss': 0, 'acc': []}
            
            if 'HIGH' in r['Status']:
                pasars[p]['hits'] += 1
            elif 'PARTIAL' in r['Status']:
                pasars[p]['partial'] += 1
            else:
                pasars[p]['miss'] += 1
            
            try:
                pasars[p]['acc'].append(float(r['ACC_Persen'].replace('%', '')))
            except:
                pass
        
        print("\n" + "-"*50)
        print(f"{Colors.BLUE}PERFORMA PER PASARAN:{Colors.RESET}")
        for p, d in sorted(pasars.items(), key=lambda x: x[1]['hits'], reverse=True)[:5]:
            total_p = d['hits'] + d['partial'] + d['miss']
            rate = d['hits']/total_p*100 if total_p > 0 else 0
            avg = sum(d['acc'])/len(d['acc']) if d['acc'] else 0
            icon = "🔥" if rate >= 50 else "⭐" if rate >= 25 else "⚪"
            print(f"  {icon} {p}: {d['hits']}/{total_p} ({rate:.1f}%) | Acc: {avg:.1f}%")
        
        # Top performa
        print("\n" + "-"*50)
        print(f"{Colors.MAGENTA}🏆 TOP 5 PREDIKSI TERAKURAT:{Colors.RESET}")
        
        valid_records = []
        for r in records:
            try:
                acc = float(r['ACC_Persen'].replace('%', ''))
                valid_records.append((r['Pasaran'], acc, r['Status']))
            except:
                continue
        
        top_acc = sorted(valid_records, key=lambda x: x[1], reverse=True)[:5]
        
        for i, (pasaran, acc, status) in enumerate(top_acc, 1):
            icon = "🔥" if acc >= 80 else "⭐" if acc >= 60 else "⚪"
            print(f"  {i}. {icon} {pasaran} - {acc:.1f}% ({status})")
    
    def clear_database(self):
        """Hapus semua data"""
        confirm = input(f"{Colors.RED}⚠️ Yakin hapus semua data? (y/n): {Colors.RESET}").lower()
        if confirm == 'y':
            # Buat file baru dengan header
            with open(self.records_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['ID', 'Pasaran', 'Tanggal', 'Real_Result', 
                               'Predict_6A', 'Predict_2D', 'Predict_Shio',
                               'Hit_Total', 'ACC_Persen', 'Status'])
            print(f"{Colors.GREEN}✅ Database cleared.{Colors.RESET}")
        else:
            print(f"{Colors.YELLOW}⚠️ Dibatalkan.{Colors.RESET}")
    
    def export_csv(self):
        """Export data ke file terpisah"""
        export_file = os.path.join(self.db_dir, f'akurasi_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv')
        try:
            import shutil
            shutil.copy2(self.records_file, export_file)
            print(f"{Colors.GREEN}✅ Exported to: {export_file}{Colors.RESET}")
        except Exception as e:
            print(f"{Colors.RED}❌ Error: {e}{Colors.RESET}")


def main():
    tracker = AkurasiTracker()
    
    while True:
        os.system('clear' if os.name == 'posix' else 'cls')
        print("\n" + "="*50)
        print(f"{Colors.MAGENTA}   🎯 AKURASI TRACKER{Colors.RESET}")
        print("="*50)
        print("\n1. ✅ Input Hasil Real + Compare")
        print("2. 📊 Lihat Statistik")
        print("3. 🗑️ Clear Database")
        print("4. 📤 Export CSV")
        print("5. Exit")
        
        choice = input(f"\n{Colors.GREEN}Pilih (1-5): {Colors.RESET}").strip()
        
        if choice == '1':
            record_data = tracker.input_real_result()
            if record_data:
                accuracy_data = tracker.calculate_accuracy(record_data)
                tracker.save_record(record_data, accuracy_data)
                
                print(f"\n{'-'*50}")
                print(f"📄 HASIL ANALISA:")
                print(f"{Colors.CYAN}• Real Result    : {record_data['angka']}{Colors.RESET}")
                print(f"• Hit 6 Angka    : {accuracy_data['hit_6a']} dari {len(record_data['pred_6a'])}")
                print(f"• Hit 2D Combo   : {accuracy_data['hit_2d']} kombinasi")
                print(f"• Akurasi Total  : {accuracy_data['accuracy']}%")
                print(f"• Status         : {accuracy_data['status']}")
                print(f"{'-'*50}")
                print(f"{Colors.GREEN}✅ Record tersimpan di database{Colors.RESET}")
                input("\nTekan Enter untuk lanjut...")
        
        elif choice == '2':
            tracker.show_statistics()
            input("\nTekan Enter untuk lanjut...")
        
        elif choice == '3':
            tracker.clear_database()
            input("\nTekan Enter untuk lanjut...")
        
        elif choice == '4':
            tracker.export_csv()
            input("\nTekan Enter untuk lanjut...")
        
        elif choice == '5':
            print(f"\n{Colors.YELLOW}👋 Sampai jumpa!{Colors.RESET}")
            break
        
        else:
            print(f"{Colors.RED}❌ Pilihan tidak valid!{Colors.RESET}")
            input("\nTekan Enter untuk lanjut...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}⚠️ Dibatalkan.{Colors.RESET}")
    except Exception as e:
        print(f"{Colors.RED}❌ Error: {e}{Colors.RESET}")
        import traceback
        traceback.print_exc()