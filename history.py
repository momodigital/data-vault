#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📅 HISTORY ANALYZER
Analisis pola dari semua prediksi + hasil real
"""

import os
import csv
from datetime import datetime
from collections import Counter, defaultdict

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

class HistoryAnalyzer:
    def __init__(self):
        self.db_dir = '/sdcard/Prediktor_Akurasi_DB'
        self.db_dir_2 = '/sdcard/Prediktor_History'
        
        # Buat direktori jika belum ada
        if not os.path.exists(self.db_dir):
            os.makedirs(self.db_dir)
        if not os.path.exists(self.db_dir_2):
            os.makedirs(self.db_dir_2)
            
        self.records_file = os.path.join(self.db_dir, 'records.csv')
        self.history_file = os.path.join(self.db_dir_2, 'prediction_history.txt')
    
    def load_records(self):
        """Load all records from akurasi tracker"""
        if not os.path.exists(self.records_file):
            print(f"{Colors.YELLOW}⚠️ File records.csv belum ada. Jalankan Akurasi Tracker dulu.{Colors.RESET}")
            return []
        
        records = []
        try:
            with open(self.records_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Bersihkan data
                    cleaned_row = {}
                    for key, value in row.items():
                        cleaned_row[key.strip()] = value.strip() if value else ''
                    records.append(cleaned_row)
        except Exception as e:
            print(f"{Colors.RED}❌ Error membaca records: {e}{Colors.RESET}")
            return []
        
        return records
    
    def analyze_digit_frequency(self, records):
        """Analyze which digits appear most frequently"""
        all_hits = []
        for r in records:
            if r.get('Real_Result'):
                for digit in r['Real_Result']:
                    if digit.isdigit():
                        all_hits.append(digit)
        
        freq = Counter(all_hits)
        return freq.most_common(10)
    
    def analyze_position_frequency(self, records):
        """Analyze digit frequency by position (AS, KOP, KEPALA, EKOR)"""
        positions = {'AS': [], 'KOP': [], 'KEPALA': [], 'EKOR': []}
        
        for r in records:
            if r.get('Real_Result') and len(r['Real_Result']) == 4:
                digits = r['Real_Result']
                positions['AS'].append(digits[0])
                positions['KOP'].append(digits[1])
                positions['KEPALA'].append(digits[2])
                positions['EKOR'].append(digits[3])
        
        result = {}
        for pos, digits in positions.items():
            if digits:
                result[pos] = Counter(digits).most_common(5)
            else:
                result[pos] = []
        
        return result
    
    def analyze_weekday_performance(self, records):
        """Analyze performance per weekday"""
        weekday_perfs = defaultdict(lambda: {'total': 0, 'hits': 0, 'partial': 0})
        
        for r in records:
            if r.get('Tanggal'):
                try:
                    date = datetime.strptime(r['Tanggal'], '%d/%m/%Y')
                    weekday = date.strftime('%A')
                    weekday_perfs[weekday]['total'] += 1
                    
                    status = r.get('Status', '').strip()
                    if 'HIGH HIT' in status:
                        weekday_perfs[weekday]['hits'] += 1
                    elif 'PARTIAL' in status:
                        weekday_perfs[weekday]['partial'] += 1
                except Exception as e:
                    # Skip jika format tanggal salah
                    continue
        
        return dict(weekday_perfs)
    
    def analyze_time_periods(self, records):
        """Analyze performance by time period"""
        period_perf = defaultdict(lambda: {'total': 0, 'hits': 0, 'partial': 0})
        
        for r in records:
            if r.get('Tanggal'):
                try:
                    date = datetime.strptime(r['Tanggal'], '%d/%m/%Y')
                    
                    if date.weekday() < 5:  # Weekday
                        period = 'Weekday (Senin-Jumat)'
                    else:
                        period = 'Weekend (Sabtu-Minggu)'
                    
                    period_perf[period]['total'] += 1
                    
                    status = r.get('Status', '').strip()
                    if 'HIGH HIT' in status:
                        period_perf[period]['hits'] += 1
                    elif 'PARTIAL' in status:
                        period_perf[period]['partial'] += 1
                except:
                    pass
        
        return dict(period_perf)
    
    def analyze_monthly_trend(self, records):
        """Analyze monthly performance trends"""
        monthly = defaultdict(lambda: {'total': 0, 'hits': 0})
        
        for r in records:
            if r.get('Tanggal'):
                try:
                    date = datetime.strptime(r['Tanggal'], '%d/%m/%Y')
                    month_key = date.strftime('%B %Y')
                    
                    monthly[month_key]['total'] += 1
                    
                    status = r.get('Status', '').strip()
                    if 'HIGH HIT' in status:
                        monthly[month_key]['hits'] += 1
                except:
                    pass
        
        return dict(monthly)
    
    def get_top_pasaran(self, records):
        """Get top performing markets"""
        pasaran_stats = defaultdict(lambda: {'total': 0, 'hits': 0, 'acc_total': 0})
        
        for r in records:
            pasaran = r.get('Pasaran', 'Unknown')
            pasaran_stats[pasaran]['total'] += 1
            
            status = r.get('Status', '').strip()
            if 'HIGH HIT' in status:
                pasaran_stats[pasaran]['hits'] += 1
            
            try:
                acc = float(r.get('ACC_Persen', '0').replace('%', ''))
                pasaran_stats[pasaran]['acc_total'] += acc
            except:
                pasaran_stats[pasaran]['acc_total'] += 0
        
        # Hitung rata-rata akurasi
        result = []
        for pasaran, stats in pasaran_stats.items():
            if stats['total'] > 0:
                avg_acc = stats['acc_total'] / stats['total']
                hit_rate = (stats['hits'] / stats['total'] * 100) if stats['total'] > 0 else 0
                result.append({
                    'pasaran': pasaran,
                    'total': stats['total'],
                    'hits': stats['hits'],
                    'hit_rate': hit_rate,
                    'avg_acc': avg_acc
                })
        
        return sorted(result, key=lambda x: x['hit_rate'], reverse=True)
    
    def show_analysis(self):
        """Show complete analysis"""
        records = self.load_records()
        
        if not records:
            print(f"{Colors.RED}❌ Tidak ada data untuk dianalisis{Colors.RESET}")
            return
        
        print("\n" + "="*50)
        print(f"{Colors.MAGENTA}📅 HISTORY ANALYZER - COMPLETE REPORT{Colors.RESET}")
        print("="*50)
        
        # Overall Stats
        total = len(records)
        hits = sum(1 for r in records if 'HIGH HIT' in r.get('Status', ''))
        partials = sum(1 for r in records if 'PARTIAL' in r.get('Status', ''))
        misses = total - hits - partials
        
        hit_rate = (hits / total * 100) if total > 0 else 0
        
        print(f"\n{Colors.WHITE}Total Data       : {total}{Colors.RESET}")
        print(f"{Colors.GREEN}HIGH HIT          : {hits} ({hit_rate:.1f}%){Colors.RESET}")
        print(f"{Colors.YELLOW}PARTIAL           : {partials}{Colors.RESET}")
        print(f"{Colors.RED}MISS              : {misses}{Colors.RESET}")
        
        # Digit Frequency by Position
        print("\n" + "-"*50)
        print(f"{Colors.CYAN}🔢 FREKUENSI DIGIT PER POSISI:{Colors.RESET}")
        pos_freq = self.analyze_position_frequency(records)
        
        for pos, digits in pos_freq.items():
            print(f"\n{Colors.YELLOW}{pos}:{Colors.RESET}")
            for digit, count in digits[:3]:
                bar_len = int(count / digits[0][1] * 30) if digits else 0
                bar = "█" * bar_len
                print(f"  Digit {digit}: {count}x [{bar}]")
        
        # Overall Digit Frequency
        print("\n" + "-"*50)
        print(f"{Colors.CYAN}🔢 FREKUENSI DIGIT KESELURUHAN:{Colors.RESET}")
        digit_freq = self.analyze_digit_frequency(records)
        
        if digit_freq:
            max_count = digit_freq[0][1]
            for digit, count in digit_freq:
                bar_len = int(count / max_count * 40)
                bar = "█" * bar_len
                print(f"Digit {digit}: {count}x [{bar}]")
        
        # Top Pasaran
        print("\n" + "-"*50)
        print(f"{Colors.GREEN}🏆 TOP 5 PASARAN TERBAIK:{Colors.RESET}")
        top_pasaran = self.get_top_pasaran(records)[:5]
        
        for i, p in enumerate(top_pasaran, 1):
            icon = "🔥" if p['hit_rate'] >= 50 else "⭐" if p['hit_rate'] >= 30 else "⚪"
            print(f"{i}. {icon} {p['pasaran']}: {p['hits']}/{p['total']} ({p['hit_rate']:.1f}%) | Acc: {p['avg_acc']:.1f}%")
        
        # Weekday Performance
        print("\n" + "-"*50)
        print(f"{Colors.BLUE}📅 KINERJA PER HARI:{Colors.RESET}")
        weekday_perf = self.analyze_weekday_performance(records)
        
        # Urutkan berdasarkan hari
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_names = {
            'Monday': 'Senin', 'Tuesday': 'Selasa', 'Wednesday': 'Rabu',
            'Thursday': 'Kamis', 'Friday': 'Jumat', 'Saturday': 'Sabtu', 'Sunday': 'Minggu'
        }
        
        for day in day_order:
            if day in weekday_perf:
                perf = weekday_perf[day]
                rate = perf['hits']/perf['total']*100 if perf['total'] > 0 else 0
                icon = "🔥" if rate >= 50 else "⭐" if rate >= 30 else "⚪"
                print(f"{icon} {day_names[day]}: {perf['hits']}/{perf['total']} ({rate:.1f}%)")
        
        # Time Period
        print("\n" + "-"*50)
        print(f"{Colors.YELLOW}⏰ KINERJA PER MASA:{Colors.RESET}")
        period_perf = self.analyze_time_periods(records)
        
        for period, perf in period_perf.items():
            rate = perf['hits']/perf['total']*100 if perf['total'] > 0 else 0
            icon = "🔥" if rate >= 50 else "⭐" if rate >= 30 else "⚪"
            print(f"{icon} {period}: {perf['hits']}/{perf['total']} ({rate:.1f}%)")
        
        # Monthly Trend
        print("\n" + "-"*50)
        print(f"{Colors.MAGENTA}📈 TREN BULANAN:{Colors.RESET}")
        monthly = self.analyze_monthly_trend(records)
        
        # Ambil 3 bulan terakhir
        recent_months = sorted(monthly.keys())[-3:]
        for month in recent_months:
            if month in monthly:
                m = monthly[month]
                rate = m['hits']/m['total']*100 if m['total'] > 0 else 0
                trend = "📈" if rate >= 40 else "📉" if rate < 30 else "➡️"
                print(f"{trend} {month}: {m['hits']}/{m['total']} ({rate:.1f}%)")
        
        # Rekomendasi
        print("\n" + "="*50)
        print(f"{Colors.GREEN}📋 REKOMENDASI BERDASARKAN DATA:{Colors.RESET}")
        print("-"*50)
        
        # Best days
        best_days = []
        for day in day_order:
            if day in weekday_perf and weekday_perf[day]['total'] >= 2:
                rate = weekday_perf[day]['hits']/weekday_perf[day]['total']*100
                best_days.append((day_names[day], rate))
        
        best_days = sorted(best_days, key=lambda x: x[1], reverse=True)[:3]
        if best_days:
            print(f"{Colors.GREEN}✅ Hari Terbaik: {', '.join([d[0] for d in best_days])}{Colors.RESET}")
        
        # Hot digits
        if digit_freq:
            hot_digits = [d[0] for d in digit_freq[:3]]
            print(f"{Colors.CYAN}🔥 Digit Terpanas: {', '.join(hot_digits)}{Colors.RESET}")
        
        # Best market
        if top_pasaran:
            best_market = top_pasaran[0]
            print(f"{Colors.YELLOW}🎯 Pasaran Terbaik: {best_market['pasaran']} ({best_market['hit_rate']:.1f}%){Colors.RESET}")
        
        # Save to file
        save = input(f"\n{Colors.GREEN}💾 Simpan laporan ke file? (y/n): {Colors.RESET}").lower()
        if save == 'y':
            self.save_report(records, digit_freq, weekday_perf, period_perf, top_pasaran)
    
    def save_report(self, records, digit_freq, weekday_perf, period_perf, top_pasaran):
        """Save analysis report to file"""
        fname = f"history_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        path = os.path.join(self.db_dir_2, fname)
        
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write("="*50 + "\n")
                f.write("📅 HISTORY ANALYZER - LAPORAN LENGKAP\n")
                f.write("="*50 + "\n\n")
                f.write(f"Tanggal Report: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                f.write(f"Total Data     : {len(records)}\n\n")
                
                f.write("FREKUENSI DIGIT:\n")
                for digit, count in digit_freq:
                    f.write(f"  Digit {digit}: {count}x\n")
                
                f.write("\nKINERJA PER HARI:\n")
                day_names = {
                    'Monday': 'Senin', 'Tuesday': 'Selasa', 'Wednesday': 'Rabu',
                    'Thursday': 'Kamis', 'Friday': 'Jumat', 'Saturday': 'Sabtu', 'Sunday': 'Minggu'
                }
                for day, id_day in day_names.items():
                    if day in weekday_perf:
                        perf = weekday_perf[day]
                        rate = perf['hits']/perf['total']*100 if perf['total'] > 0 else 0
                        f.write(f"  {id_day}: {perf['hits']}/{perf['total']} ({rate:.1f}%)\n")
                
                f.write("\nTOP PASARAN:\n")
                for p in top_pasaran[:5]:
                    f.write(f"  {p['pasaran']}: {p['hits']}/{p['total']} ({p['hit_rate']:.1f}%) - Acc: {p['avg_acc']:.1f}%\n")
            
            print(f"\n{Colors.GREEN}✅ Laporan tersimpan: {path}{Colors.RESET}")
        except Exception as e:
            print(f"{Colors.RED}❌ Gagal menyimpan laporan: {e}{Colors.RESET}")


def main():
    analyzer = HistoryAnalyzer()
    
    while True:
        os.system('clear' if os.name == 'posix' else 'cls')
        print("\n" + "="*50)
        print(f"{Colors.MAGENTA}📅 HISTORY ANALYZER{Colors.RESET}")
        print("="*50)
        print("\n1. 📊 Analisis Lengkap")
        print("2. 🔢 Pola Digit per Posisi")
        print("3. 📅 Performa Harian")
        print("4. 🏆 Top Pasaran")
        print("5. 📤 Export Laporan")
        print("6. Exit")
        
        choice = input(f"\n{Colors.GREEN}Pilih (1-6): {Colors.RESET}").strip()
        
        if choice == '1':
            analyzer.show_analysis()
            input("\nTekan Enter untuk lanjut...")
        
        elif choice == '2':
            records = analyzer.load_records()
            if records:
                pos_freq = analyzer.analyze_position_frequency(records)
                
                print("\n" + "="*50)
                print(f"{Colors.CYAN}🔢 POLA DIGIT PER POSISI{Colors.RESET}")
                print("="*50)
                
                for pos, digits in pos_freq.items():
                    print(f"\n{Colors.YELLOW}{pos}:{Colors.RESET}")
                    if digits:
                        max_count = digits[0][1]
                        for digit, count in digits:
                            bar_len = int(count / max_count * 30)
                            bar = "█" * bar_len
                            print(f"  Digit {digit}: {count}x [{bar}]")
                    else:
                        print("  Belum ada data")
            else:
                print(f"{Colors.RED}❌ Tidak ada data{Colors.RESET}")
            input("\nTekan Enter untuk lanjut...")
        
        elif choice == '3':
            records = analyzer.load_records()
            if records:
                weekday_perf = analyzer.analyze_weekday_performance(records)
                period_perf = analyzer.analyze_time_periods(records)
                
                print("\n" + "="*50)
                print(f"{Colors.BLUE}📅 KINERJA PER WAKTU{Colors.RESET}")
                print("="*50)
                
                print(f"\n{Colors.YELLOW}Per Hari:{Colors.RESET}")
                day_names = {
                    'Monday': 'Senin', 'Tuesday': 'Selasa', 'Wednesday': 'Rabu',
                    'Thursday': 'Kamis', 'Friday': 'Jumat', 'Saturday': 'Sabtu', 'Sunday': 'Minggu'
                }
                day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                
                for day in day_order:
                    if day in weekday_perf:
                        perf = weekday_perf[day]
                        rate = perf['hits']/perf['total']*100 if perf['total'] > 0 else 0
                        icon = "🔥" if rate >= 50 else "⭐" if rate >= 30 else "⚪"
                        print(f"  {icon} {day_names[day]}: {perf['hits']}/{perf['total']} ({rate:.1f}%)")
                
                print(f"\n{Colors.YELLOW}Per Periode:{Colors.RESET}")
                for period, perf in period_perf.items():
                    rate = perf['hits']/perf['total']*100 if perf['total'] > 0 else 0
                    icon = "🔥" if rate >= 50 else "⭐" if rate >= 30 else "⚪"
                    print(f"  {icon} {period}: {perf['hits']}/{perf['total']} ({rate:.1f}%)")
            else:
                print(f"{Colors.RED}❌ Tidak ada data{Colors.RESET}")
            input("\nTekan Enter untuk lanjut...")
        
        elif choice == '4':
            records = analyzer.load_records()
            if records:
                top_pasaran = analyzer.get_top_pasaran(records)
                
                print("\n" + "="*50)
                print(f"{Colors.GREEN}🏆 TOP PASARAN{Colors.RESET}")
                print("="*50)
                
                for i, p in enumerate(top_pasaran, 1):
                    icon = "🔥" if p['hit_rate'] >= 50 else "⭐" if p['hit_rate'] >= 30 else "⚪"
                    print(f"{i}. {icon} {p['pasaran']}")
                    print(f"   • Hit Rate: {p['hits']}/{p['total']} ({p['hit_rate']:.1f}%)")
                    print(f"   • Avg Acc : {p['avg_acc']:.1f}%")
            else:
                print(f"{Colors.RED}❌ Tidak ada data{Colors.RESET}")
            input("\nTekan Enter untuk lanjut...")
        
        elif choice == '5':
            analyzer.show_analysis()
            input("\nTekan Enter untuk lanjut...")
        
        elif choice == '6':
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