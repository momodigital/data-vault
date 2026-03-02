#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📅 HISTORY ANALYZER v3.0 - DUOPLEX EDITION (FIXED)
Dual Analysis: GitHub Market History + Your Personal Accuracy Tracking
"""

import os
import csv
import requests
import re
from datetime import datetime
from collections import Counter, defaultdict

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

class HistoryAnalyzer:
    def __init__(self):
        self.db_dir = '/sdcard/Prediktor_Akurasi_DB'
        self.db_dir_2 = '/sdcard/Prediktor_History'
        self.export_dir = '/sdcard/Download/History_Reports'
        
        # Create directories
        for directory in [self.db_dir, self.db_dir_2, self.export_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)
    
    class Colors:
        RESET = '\033[0m'
        GREEN = '\033[92m'
        YELLOW = '\033[93m'
        BLUE = '\033[94m'
        CYAN = '\033[96m'
        WHITE = '\033[97m'
        MAGENTA = '\033[95m'
        RED = '\033[91m'
        BOLD = '\033[1m'
    
    @staticmethod
    def cprint(text, color=None, end='\n'):
        try:
            if color:
                formatted = f"{color}{text}{HistoryAnalyzer.Colors.RESET}"
            else:
                formatted = str(text)
            print(formatted, end=end)
        except Exception:
            print(str(text), end=end)
    
    # ========== FUNGSI GITHUB INTEGRATION ==========
    def fetch_github_csv(self, market_key):
        file_info = MARKET_FILES.get(market_key)
        if not file_info:
            return None
        
        url = f"https://raw.githubusercontent.com/{GITHUB_CONFIG['username']}/{GITHUB_CONFIG['repo']}/{GITHUB_CONFIG['branch']}/{GITHUB_CONFIG['path']}/{file_info[1]}"
        
        try:
            r = requests.get(url, timeout=30)
            r.raise_for_status()
            return r.text
        except Exception as e:
            self.cprint(f"❌ Error GitHub: {e}", self.Colors.RED)
            return None
    
    def parse_csv_data(self, text):
        if not text:
            return []
        results = []
        lines = text.strip().split('\n')[1:]
        for line in lines:
            if not line: continue
            parts = line.split(',')
            if len(parts) >= 2:
                match = re.search(r'\d{4}', parts[1].strip())
                if match and len(match.group()) == 4:
                    results.append(match.group())
        return results
    
    def analyze_market_history(self, market_key):
        """Analyze historical patterns from GitHub CSV"""
        m_name = MARKET_NAMES.get(market_key, f"Market {market_key}")
        
        self.cprint(f"\n{'='*50}", self.Colors.CYAN)
        self.cprint(f"[{market_key}/10] Mengambil Data {m_name}...", self.Colors.BLUE)
        self.cprint('='*50, self.Colors.CYAN)
        
        csv_text = self.fetch_github_csv(market_key)
        if not csv_text:
            return None
        
        data = self.parse_csv_data(csv_text)
        
        if len(data) < 50:
            self.cprint(f"⚠️ Data kurang ({len(data)}). Minimum 50 putaran.", self.Colors.YELLOW)
            return None
        
        self.cprint(f"✅ Analisa {len(data)} riwayat pasar...", self.Colors.GREEN)
        
        # Analyze digit frequency
        all_digits = [d for num in data for d in num]
        digit_freq = Counter(all_digits).most_common(10)
        
        # Odd/Even ratio
        odd_count = sum(1 for d in all_digits if int(d) % 2 == 1)
        even_count = len(all_digits) - odd_count
        odd_rate = odd_count / len(all_digits) * 100 if len(all_digits) > 0 else 0
        
        # Hot/Cold digits
        hot = digit_freq[:5]
        cold = digit_freq[-5:] if len(digit_freq) >= 5 else digit_freq
        
        # Last digit frequency
        last_digits = [int(d[-1]) for d in data if len(d) == 4]
        last_digit_freq = Counter(last_digits).most_common(5)
        
        return {
            'name': m_name,
            'count': len(data),
            'digit_freq': dict(digit_freq),
            'hot_digits': hot,
            'cold_digits': cold,
            'odd': {'count': odd_count, 'even': even_count, 'rate': odd_rate},
            'odd_rate': odd_rate,
            'even': even_count,
            'last_digit': last_digit_freq
        }
    
    # ========== FUNGSI PERSONAL ACCURACY ==========
    def load_personal_records(self):
        records_file = os.path.join(self.db_dir, 'records.csv')
        if not os.path.exists(records_file):
            return []
        
        records = []
        try:
            with open(records_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                records = [row for row in reader]
        except Exception as e:
            self.cprint(f"Error membaca records: {e}", self.Colors.RED)
        return records
    
    def calculate_accuracy_stats(self, records):
        total = len(records)
        hits = sum(1 for r in records if r.get('Status', '').strip() == '✅ HIT')
        partials = sum(1 for r in records if r.get('Status', '').strip() == '⚠️ PARTIAL')
        
        return {
            'total': total,
            'hits': hits,
            'partials': partials,
            'misses': total - hits - partials,
            'hit_rate': (hits / total * 100) if total > 0 else 0
        }
    
    # ========== DISPLAY FUNCTION ==========
    def display_comprehensive_report(self, github_analyses, personal_stats):
        """Display complete dual analysis report"""
        
        print("\n" + "="*60)
        self.cprint("📊 REPORT LENGKAP - MARKET + PERSONAL", self.Colors.MAGENTA + self.Colors.BOLD)
        print("="*60)
        
        # ===== PERSONAL STATS =====
        print("\n" + "-"*60)
        self.cprint("👤 AKURASI PRIBADI ANDA", self.Colors.GREEN)
        print("-"*60)
        self.cprint(f"Total Prediksi : {personal_stats['total']} x", self.Colors.WHITE)
        self.cprint(f"✅ Hit          : {personal_stats['hits']} ({personal_stats['hit_rate']:.1f}%)", self.Colors.GREEN)
        self.cprint(f"⚠️ Partial      : {personal_stats['partials']} x", self.Colors.YELLOW)
        self.cprint(f"❌ Miss         : {personal_stats['misses']} x", self.Colors.RED)
        
        # ===== MARKET ANALYSIS SUMMARY =====
        print("\n" + "-"*60)
        self.cprint("📈 HISTORI PASARAN (Dari GitHub)", self.Colors.CYAN)
        print("-"*60)
        
        if github_analyses:
            valid_analyses = [a for a in github_analyses.values() if a]
            for i, analysis in enumerate(valid_analyses, 1):
                self.cprint(f"\n[{i}] {analysis['name']} ({analysis['count']} putaran)", self.Colors.BLUE)
                
                # Hot/Cold digits
                hot_str = ', '.join([str(t[0]) for t in analysis['hot_digits']])
                cold_str = ', '.join([str(c[0]) for c in analysis['cold_digits']])
                
                self.cprint(f"   🔥 Hot Digits : {hot_str}", self.Colors.GREEN)
                self.cprint(f"   ❄️ Cold Digits: {cold_str}", self.Colors.YELLOW)
                
                # Odd/Even rate
                self.cprint(f"   G/E Ratio     : {analysis['odd']['count']}:{analysis['even']} ({analysis['odd_rate']:.1f}%)", self.Colors.WHITE)
                
                # Last digit trend
                self.cprint(f"   👉 Terakhir   : ", end="")
                items = ', '.join([f"{d}({c})" for d, c in analysis['last_digit'][:3]])
                self.cprint(items, self.Colors.CYAN)
        else:
            self.cprint("Tidak ada data pasar berhasil diunduh", self.Colors.RED)
        
        # ===== COMPARISON & INSIGHTS =====
        print("\n" + "="*60)
        self.cprint("💡 INSIGHT & REKOMENDASI", self.Colors.MAGENTA + self.Colors.BOLD)
        print("="*60)
        
        # Overall assessment
        self.cprint(f"\n🎯 Performance Summary:", self.Colors.CYAN)
        if personal_stats['hit_rate'] >= 60:
            self.cprint("• Skill Anda TINGGI! Pertahankan!", self.Colors.GREEN)
        elif personal_stats['hit_rate'] >= 40:
            self.cprint("• Cukup baik, tingkatkan lagi!", self.Colors.YELLOW)
        else:
            self.cprint("• Perlu evaluasi strategi prediksi!", self.Colors.RED)
        
        # Top performing market
        if github_analyses:
            valid_with_data = [(k, v) for k, v in github_analyses.items() if v]
            top_markets = sorted(valid_with_data, 
                              key=lambda x: x[1]['count'] if x[1] else 0, 
                              reverse=True)[:3]
            
            self.cprint("\n🏆 3 Pasar dengan Data Terlengkap:", self.Colors.CYAN)
            for idx, (key, val) in enumerate(top_markets, 1):
                if val:
                    self.cprint(f"  {idx}. {val['name']} ({val['count']} putaran)", self.Colors.WHITE)
        
        # Hot digits recommendation
        all_hot = {}
        if github_analyses:
            for market, analysis in github_analyses.items():
                if analysis:
                    for digit, count in analysis['hot_digits']:
                        all_hot[digit] = all_hot.get(digit, 0) + count
            
            if all_hot:
                sorted_hot = sorted(all_hot.items(), key=lambda x: x[1], reverse=True)[:5]
                self.cprint("\n🔥 Digit Paling Sering Muncul Across Markets:", self.Colors.MAGENTA)
                for digit, count in sorted_hot:
                    self.cprint(f"  • {digit}: muncul di {count} pasar panas", self.Colors.YELLOW)
    
    # ========== SAVE REPORT ==========
    def save_full_report(self, filename, data, personal):
        path = os.path.join(self.export_dir, filename)
        
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write("="*60 + "\n")
                f.write("📊 LAPORAN LENGKAP - MARKET HISTORY + PERSONAL\n")
                f.write("="*60 + "\n\n")
                f.write(f"Generated: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n")
                
                f.write("PERSONAL ACCURACY:\n")
                f.write(f"  Total Predictions: {personal['total']}\n")
                f.write(f"  Hits: {personal['hits']} ({personal['hit_rate']:.1f}%)\n")
                f.write(f"  Partials: {personal['partials']}\n")
                f.write(f"  Misses: {personal['misses']}\n\n")
                
                f.write("MARKET HISTORY (GitHub):\n")
                for market, analysis in data.items():
                    if analysis:
                        f.write(f"\n  [{market}] {analysis['name']}:\n")
                        f.write(f"    Data Count: {analysis['count']}\n")
                        f.write(f"    Hot Digits: {[t[0] for t in analysis['hot_digits']]}\n")
                        f.write(f"    Cold Digits: {[c[0] for c in analysis['cold_digits']]}\n")
                
                f.write("\n" + "="*60 + "\n")
            return path
        except Exception as e:
            self.cprint(f"Error menyimpan file: {e}", self.Colors.RED)
            return None


def main():
    analyzer = HistoryAnalyzer()
    
    while True:
        os.system('clear' if os.name == 'posix' else 'cls')
        print("\n" + "="*60)
        analyzer.cprint("📅 HISTORY ANALYZER v3.0 - DUOPLEX EDITION", analyzer.Colors.MAGENTA + analyzer.Colors.BOLD)
        print("="*60)
        
        print("\n1️⃣ Lihat Akurasi Personal (Local DB)")
        print("2️⃣ Ambil Data Pasar (GitHub - Single)")
        print("3️⃣ Semua Pasar Otomatis (GitHub - All 10)")
        print("4️⃣ Report Lengkap (Both)")
        print("X Exit")
        
        choice = input(f"\n{analyzer.Colors.GREEN}Pilih (1-4/X): {analyzer.Colors.RESET}").strip().upper()
        
        if choice == 'X':
            analyzer.cprint("\n✅ Keluar. Sampai jumpa!", analyzer.Colors.WHITE)
            break
        
        elif choice == '1':
            # Show personal stats only
            records = analyzer.load_personal_records()
            stats = analyzer.calculate_accuracy_stats(records)
            
            print("\n" + "-"*60)
            analyzer.cprint("👤 AKURASI PRIBADI ANDA", analyzer.Colors.GREEN)
            print("-"*60)
            analyzer.cprint(f"Total Prediksi : {stats['total']} x", analyzer.Colors.WHITE)
            analyzer.cprint(f"✅ Hit          : {stats['hits']} ({stats['hit_rate']:.1f}%)", analyzer.Colors.GREEN)
            analyzer.cprint(f"⚠️ Partial      : {stats['partials']} x", analyzer.Colors.YELLOW)
            analyzer.cprint(f"❌ Miss         : {stats['misses']} x", analyzer.Colors.RED)
            
            input("\nTekan Enter untuk lanjut...")
        
        elif choice == '2':
            # Manual select one market
            print("\nPilih Pasar:")
            for k, v in MARKET_NAMES.items():
                analyzer.cprint(f"{k}. {v}", analyzer.Colors.WHITE)
            
            try:
                sel = int(input(analyzer.Colors.GREEN + "➤ Pilihan (1-10): " + analyzer.Colors.RESET))
                analysis = analyzer.analyze_market_history(sel)
                
                if analysis:
                    print("\nHot Digits:", [str(t[0]) for t in analysis['hot_digits']])
                    print("Cold Digits:", [str(c[0]) for c in analysis['cold_digits']])
                    
                    save = input(analyzer.Colors.GREEN + "\nSimpan laporan? (y/n): " + analyzer.Colors.RESET).lower()
                    if save == 'y':
                        path = os.path.join(analyzer.export_dir, f"market_{sel}_{datetime.now().strftime('%Y%m%d%H%M%S')}.txt")
                        with open(path, 'w') as f:
                            f.write(f"Pasar: {analysis['name']}\n")
                            f.write(f"Data: {analysis['count']} putaran\n")
                            f.write(f"Hot: {[t[0] for t in analysis['hot_digits']]}\n")
                            f.write(f"Cold: {[c[0] for c in analysis['cold_digits']]}\n")
                        
                        analyzer.cprint(f"✅ Tersimpan di: {path}", analyzer.Colors.GREEN)
            except ValueError:
                analyzer.cprint("❌ Input tidak valid", analyzer.Colors.RED)
            
            input("\nTekan Enter untuk lanjut...")
        
        elif choice == '3':
            # Auto process all 10 markets
            analyzer.cprint("\n▶️ FULL AUTO - ALL MARKETS FROM GITHUB", analyzer.Colors.CYAN)
            
            analyses = {}
            for m_choice in MARKET_FILES.keys():
                analysis = analyzer.analyze_market_history(m_choice)
                if analysis:
                    analyses[m_choice] = analysis
                
                if m_choice < max(MARKET_FILES.keys()):
                    cont = input(analyzer.Colors.CYAN + "\nLanjut? (Enter) / N exit: " + analyzer.Colors.RESET).lower()
                    if cont == 'n':
                        break
            
            analyzer.cprint("\n✅ Semua pasar selesai di-analisa!", analyzer.Colors.GREEN)
            input("Tekan Enter untuk lanjut...")
        
        elif choice == '4':
            # Complete report
            # First get market analysis
            analyses = {}
            analyzer.cprint("\nMengambil data pasar dari GitHub...", analyzer.Colors.CYAN)
            
            for m_choice in MARKET_FILES.keys():
                analysis = analyzer.analyze_market_history(m_choice)
                if analysis:
                    analyses[m_choice] = analysis
            
            # Then get personal stats
            records = analyzer.load_personal_records()
            personal = analyzer.calculate_accuracy_stats(records)
            
            # Display comprehensive report
            analyzer.display_comprehensive_report(analyses, personal)
            
            # Save option
            save = input(f"\n{analyzer.Colors.GREEN}💾 Simpan report lengkap? (y/n): {analyzer.Colors.RESET}").lower()
            if save == 'y':
                path = analyzer.save_full_report(
                    f"full_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    analyses, personal
                )
                if path:
                    analyzer.cprint(f"✅ Laporan tersimpan di: {path}", analyzer.Colors.GREEN)
            
            input("\nTekan Enter untuk lanjut...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{HistoryAnalyzer.Colors.YELLOW}⚠️ Dibatalkan.{HistoryAnalyzer.Colors.RESET}")
    except Exception as e:
        print(f"\n{HistoryAnalyzer.Colors.RED}❌ Error utama: {e}{HistoryAnalyzer.Colors.RESET}")
        import traceback
        traceback.print_exc()