#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📝 DAILY SUMMARY v3.0 - GLOBAL REPORT EDITION (FIXED)
Comprehensive daily/weekly report with GitHub Market Data Integration
"""

import os
import csv
import requests
import re
from datetime import datetime, timedelta
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

class DailySummary:
    def __init__(self):
        self.summary_dir = '/sdcard/Prediktor_Summary'
        self.export_dir = '/sdcard/Download/Summary_Reports'
        
        # Create directories
        for directory in [self.summary_dir, self.export_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)
        
        self.file_prefix = 'summary_'
    
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
                formatted = f"{color}{text}{DailySummary.Colors.RESET}"
            else:
                formatted = str(text)
            print(formatted, end=end)
        except Exception:
            print(str(text), end=end)
    
    def fetch_market_stats(self, market_key):
        """Fetch current market statistics from GitHub"""
        file_info = MARKET_FILES.get(market_key)
        if not file_info:
            return None
        
        url = f"https://raw.githubusercontent.com/{GITHUB_CONFIG['username']}/{GITHUB_CONFIG['repo']}/{GITHUB_CONFIG['branch']}/{GITHUB_CONFIG['path']}/{file_info[1]}"
        
        try:
            r = requests.get(url, timeout=30)
            r.raise_for_status()
            
            data = []
            for line in r.text.strip().split('\n')[1:]:
                if not line: continue
                parts = line.split(',')
                if len(parts) >= 2:
                    match = re.search(r'\d{4}', parts[1].strip())
                    if match and len(match.group()) == 4:
                        data.append(match.group())
            
            if not data:
                return None
            
            # Last draw
            last_draw = data[-1] if data else "N/A"
            
            # Digit frequency
            all_digits = [d for num in data for d in num]
            digit_freq = Counter(all_digits)
            hot = [d for d, c in digit_freq.most_common(3)]
            freq = len(data)
            
            return {
                'last': last_draw,
                'hot_digits': hot,
                'freq': freq,
                'date': datetime.now().strftime('%Y-%m-%d')
            }
        except Exception as e:
            self.cprint(f"⚠️ Error fetch market {market_key}: {e}", self.Colors.YELLOW)
            return None
    
    def generate_daily_summary(self):
        today = datetime.now()
        today_str = today.strftime('%Y-%m-%d')
        
        # Count files created today
        files_today = []
        download_dir = '/sdcard/Download'
        
        if os.path.exists(download_dir):
            for f in os.listdir(download_dir):
                try:
                    file_path = os.path.join(download_dir, f)
                    if os.path.isfile(file_path):
                        # Check file modification time
                        mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                        if mod_time.strftime('%Y-%m-%d') == today_str:
                            files_today.append(f)
                except:
                    pass
        
        total_preds = len([f for f in files_today if f.lower().startswith('prediktor_')])
        total_shio = len([f for f in files_today if f.lower().startswith('shio_')])
        total_conf = len([f for f in files_today if f.lower().startswith('confidence_')])
        total_analysis = len([f for f in files_today if f.lower().startswith('pola_')])
        
        today_only = total_preds + total_shio + total_conf + total_analysis
        
        # Fetch global market stats
        global_markets = {}
        for m_key in MARKET_FILES.keys():
            stats = self.fetch_market_stats(m_key)
            if stats:
                global_markets[m_key] = stats
        
        return {
            'date': today.strftime('%d/%m/%Y'),
            'time': today.strftime('%H:%M'),
            'total_predictions': total_preds,
            'total_shio': total_shio,
            'total_confidence': total_conf,
            'total_analysis': total_analysis,
            'today_count': today_only,
            'combo_estimate': today_only * 100,
            'budget_estimate': today_only * 50,
            'global_markets': global_markets
        }
    
    def display_global_summary(self, summary):
        now = datetime.now()
        week_start = now - timedelta(days=now.weekday())
        
        print("\n" + "="*60)
        self.cprint("📝 GLOBAL SUMMARY - DAILY + MARKET STATUS", self.Colors.MAGENTA + self.Colors.BOLD)
        print("="*60)
        
        print(f"\n{self.Colors.WHITE}Tanggal: {summary['date']}{self.Colors.RESET}")
        print(f"{self.Colors.WHITE}Waktu  : {summary['time']}{self.Colors.RESET}")
        
        print("\n" + "-"*60)
        self.cprint("📊 PREDIKSI HARI INI:", self.Colors.CYAN)
        print(f"PREDIKTOR    : {summary['total_predictions']} file")
        print(f"SHIO         : {summary['total_shio']} file")
        print(f"CONFIDENCE   : {summary['total_confidence']} file")
        print(f"ANALISIS     : {summary['total_analysis']} file")
        print(f"\nTotal File   : {summary['today_count']}")
        
        print("\n" + "-"*60)
        self.cprint("💰 ESTIMASI BIAYA:", self.Colors.YELLOW)
        print(f"Kombo Total  : ~{summary['combo_estimate']} kombinasi")
        print(f"Estimasi Budget: Rp {summary['budget_estimate']:,}")
        
        # Weekly trend
        print("\n" + "-"*60)
        self.cprint("📅 TREND MINGGU INI:", self.Colors.BLUE)
        week_progress = min(summary['total_predictions'] / 20 * 100, 100)
        bar = "█" * int(week_progress/10) + "░" * (10 - int(week_progress/10))
        
        if summary['total_predictions'] < 20:
            remaining = 20 - summary['total_predictions']
            self.cprint(f"Target Minggu: {remaining} sesi lagi untuk mencapai 20!", self.Colors.GREEN)
        else:
            self.cprint("TARGET MINGGU TERCAPAI! ✅", self.Colors.GREEN)
        
        print(f"Maju         : {week_progress:.1f}% [{bar}]")
        
        # Global Markets Status
        print("\n" + "-"*60)
        self.cprint("🌐 STATUS PASARAN GLOBAL (GitHub):", self.Colors.MAGENTA)
        print("-"*60)
        
        if summary['global_markets']:
            displayed = 0
            sorted_markets = sorted(summary['global_markets'].items(), key=lambda x: x[1]['freq'], reverse=True)
            
            for m_key, stats in sorted_markets:
                if displayed >= 5:
                    self.cprint(f"... dan {len(summary['global_markets']) - 5} lainnya", self.Colors.CYAN)
                    break
                
                name = MARKET_NAMES.get(m_key, f"Market {m_key}")
                self.cprint(f"{name:<20} | Data: {stats['freq']:>4} | Hot: {', '.join(map(str, stats['hot_digits']))}", self.Colors.WHITE)
                displayed += 1
        else:
            self.cprint("Tidak ada data pasar terkini", self.Colors.RED)
        
        # Recommendations
        print("\n" + "-"*60)
        self.cprint("💡 REKOMENDASI:", self.Colors.GREEN)
        
        if summary['today_count'] < 1:
            self.cprint("• Tidak ada prediksi hari ini - Siap besok?", self.Colors.WHITE)
        elif summary['today_count'] < 5:
            self.cprint("• Cukup - Tingkatkan besok!", self.Colors.YELLOW)
        else:
            self.cprint("• Sangat produktif - Pertahankan!", self.Colors.GREEN)
        
        # Top performing markets
        if summary['global_markets']:
            top_markets = sorted(summary['global_markets'].items(), key=lambda x: x[1]['freq'], reverse=True)[:3]
            self.cprint("\n🏆 3 Pasar Teraktif Hari Ini:", self.Colors.CYAN)
            for i, (key, val) in enumerate(top_markets, 1):
                self.cprint(f"  {i}. {MARKET_NAMES[key]} ({val['freq']} putaran)", self.Colors.WHITE)
        
        # Save options
        save = input(f"\n{self.Colors.GREEN}💾 Simpan ringkasan lengkap? (y/n): {self.Colors.RESET}").lower()
        
        if save == 'y':
            fname = f"{self.file_prefix}{now.strftime('%Y%m%d')}_{now.strftime('%H%M%S')}_FULL.txt"
            path = os.path.join(self.export_dir, fname)
            
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write("="*60 + "\n")
                    f.write("GLOBAL SUMMARY - DAILY + MARKET STATUS\n")
                    f.write("="*60 + "\n\n")
                    f.write(f"Tanggal: {summary['date']}\nWaktu: {summary['time']}\n\n")
                    
                    f.write("PREDIKSI HARI INI:\n")
                    f.write(f"Prediktor: {summary['total_predictions']}\n")
                    f.write(f"Shio: {summary['total_shio']}\n")
                    f.write(f"Confidence: {summary['total_confidence']}\n")
                    f.write(f"Analysis: {summary['total_analysis']}\n\n")
                    
                    f.write("GLOBAL MARKETS (Last Update):\n")
                    for m_key, stats in summary['global_markets'].items():
                        f.write(f"- {MARKET_NAMES[m_key]}: {stats['freq']} puts, Hot: {stats['hot_digits']}\n")
                
                self.cprint(f"\n✅ Tersimpan: {path}", self.Colors.GREEN)
            except Exception as e:
                self.cprint(f"\n❌ Error menyimpan: {e}", self.Colors.RED)
    
    def view_all_summaries(self):
        summaries = []
        try:
            for f in os.listdir(self.export_dir):
                if f.startswith(self.file_prefix) and f.endswith('.txt'):
                    summaries.append(f)
        except:
            pass
        
        if not summaries:
            self.cprint("\nBelum ada ringkasan tersimpan", self.Colors.YELLOW)
            return
        
        print("\n" + "="*60)
        self.cprint("RINGKASAN SEJARAH", self.Colors.BLUE)
        print("="*60)
        
        # Sort by date (newest first)
        summaries.sort(reverse=True)
        
        for i, f in enumerate(summaries[:10], 1):
            print(f"{i}. {f}")
        
        input("\nTekan Enter untuk kembali...")


def main():
    summary = DailySummary()
    
    while True:
        os.system('clear' if os.name == 'posix' else 'cls')
        print("\n" + "="*60)
        summary.cprint("📝 RINGKASAN HARIAN v3.0", summary.Colors.MAGENTA + summary.Colors.BOLD)
        print("="*60)
        print("\n1. 📊 Generate Summary Global Hari Ini")
        print("2. 📜 Lihat Semua Ringkasan")
        print("3. 📅 Ringkasan Minggu Ini")
        print("4. 🔄 Update Data Pasar (GitHub)")
        print("X Exit")
        
        choice = input(f"\n{summary.Colors.GREEN}Pilih (1-4/X): {summary.Colors.RESET}").strip().upper()
        
        if choice == '1':
            today_summary = summary.generate_daily_summary()
            summary.display_global_summary(today_summary)
            input("\nTekan Enter lanjut...")
        
        elif choice == '2':
            summary.view_all_summaries()
        
        elif choice == '3':
            week_start = datetime.now() - timedelta(days=datetime.now().weekday())
            print(f"\n{summary.Colors.CYAN}Minggu Ini Dimulai: {week_start.strftime('%d/%m/%Y')}{summary.Colors.RESET}")
            print(f"Hari Ini           : {datetime.now().strftime('%d/%m/%Y')}\n")
            
            summary_obj = summary.generate_daily_summary()
            remaining = 20 - summary_obj['total_predictions']
            if remaining > 0:
                print(f"{summary.Colors.GREEN}Target Mingguan: {remaining} sesi lagi untuk mencapai 20!{summary.Colors.RESET}")
            else:
                print(f"{summary.Colors.GREEN}TARGET MINGGU TERCAPAI! ✅{summary.Colors.RESET}")
            
            input("Tekan Enter lanjut...")
        
        elif choice == '4':
            print(f"\n{summary.Colors.CYAN}Mengambil data terbaru dari GitHub...{summary.Colors.RESET}")
            count = 0
            for m_key in MARKET_FILES.keys():
                stats = summary.fetch_market_stats(m_key)
                if stats:
                    count += 1
                    print(f"  ✅ {MARKET_NAMES[m_key]}: {stats['freq']} data")
            print(f"\n{summary.Colors.GREEN}✅ Updated: {count} pasar berhasil refresh{summary.Colors.RESET}")
            input("Tekan Enter lanjut...")
        
        elif choice == 'X':
            break
        
        else:
            print("❌ Pilihan tidak valid")
            input("Tekan Enter lanjut...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{DailySummary.Colors.YELLOW}⚠️ Dibatalkan.{DailySummary.Colors.RESET}")
    except Exception as e:
        print(f"{DailySummary.Colors.RED}❌ Error: {e}{DailySummary.Colors.RESET}")
        import traceback
        traceback.print_exc()