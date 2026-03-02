#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📝 DAILY SUMMARY
Ringkasan harian untuk setiap hari
"""

import os
from datetime import datetime, timedelta
from collections import Counter
import re

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

class DailySummary:
    def __init__(self):
        self.summary_dir = '/sdcard/Prediktor_Summary'
        self.download_dir = '/sdcard/Download'
        
        # Buat direktori jika belum ada
        if not os.path.exists(self.summary_dir):
            os.makedirs(self.summary_dir)
        
        self.file_prefix = 'summary_'
    
    def generate_daily_summary(self):
        """Generate daily summary of predictions made"""
        
        # Get today's date
        today = datetime.now()
        today_str = today.strftime('%Y-%m-%d')
        
        # Cek direktori Download
        if not os.path.exists(self.download_dir):
            print(f"{Colors.YELLOW}⚠️ Direktori Download tidak ditemukan{Colors.RESET}")
            return self.get_empty_summary(today)
        
        # Count today's files
        pred_files = []
        try:
            for f in os.listdir(self.download_dir):
                if f.startswith(('prediktor_', 'shio_', 'confidence_')):
                    pred_files.append(f)
        except Exception as e:
            print(f"{Colors.RED}❌ Error membaca direktori: {e}{Colors.RESET}")
            return self.get_empty_summary(today)
        
        # Hitung berdasarkan jenis
        total_preds = len([f for f in pred_files if f.startswith('prediktor_')])
        total_shio = len([f for f in pred_files if f.startswith('shio_')])
        total_conf = len([f for f in pred_files if f.startswith('confidence_')])
        
        # Filter file hari ini
        today_only_preds = []
        for f in pred_files:
            try:
                # Extract timestamp dari nama file (format: nama_timestamp.txt)
                # Contoh: prediktor_20240315_143022.txt
                match = re.search(r'(\d{8})_(\d{6})', f)
                if match:
                    file_date_str = match.group(1)
                    file_date = datetime.strptime(file_date_str, '%Y%m%d')
                    if file_date.strftime('%Y-%m-%d') == today_str:
                        today_only_preds.append(f)
            except Exception as e:
                # Skip jika gagal parse
                continue
        
        total_today = len(today_only_preds)
        
        # Hitung berdasarkan jenis untuk hari ini
        today_preds = len([f for f in today_only_preds if f.startswith('prediktor_')])
        today_shio = len([f for f in today_only_preds if f.startswith('shio_')])
        today_conf = len([f for f in today_only_preds if f.startswith('confidence_')])
        
        summary = {
            'date': today.strftime('%d/%m/%Y'),
            'time': today.strftime('%H:%M:%S'),
            'total_predictions': total_preds,
            'total_shio': total_shio,
            'total_confidence': total_conf,
            'today_preds': today_preds,
            'today_shio': today_shio,
            'today_conf': today_conf,
            'today_count': total_today,
            'combo_estimate': total_today * 100,
            'budget_estimate': total_today * 50000,  # Rp 50.000 per sesi
            'files': today_only_preds
        }
        
        return summary
    
    def get_empty_summary(self, today):
        """Return empty summary when no data"""
        return {
            'date': today.strftime('%d/%m/%Y'),
            'time': today.strftime('%H:%M:%S'),
            'total_predictions': 0,
            'total_shio': 0,
            'total_confidence': 0,
            'today_preds': 0,
            'today_shio': 0,
            'today_conf': 0,
            'today_count': 0,
            'combo_estimate': 0,
            'budget_estimate': 0,
            'files': []
        }
    
    def display_summary(self, summary):
        """Display today's summary"""
        print("\n" + "="*50)
        print(f"{Colors.MAGENTA}📝 RINGKASAN HARIAN{Colors.RESET}")
        print("="*50)
        
        print(f"\n{Colors.WHITE}Tanggal: {summary['date']}{Colors.RESET}")
        print(f"{Colors.WHITE}Waktu  : {summary['time']}{Colors.RESET}")
        
        print("\n" + "-"*50)
        print(f"{Colors.CYAN}📊 STATISTIK PREDIKSI:{Colors.RESET}")
        print(f"Total Semua Prediktor : {summary['total_predictions']} file")
        print(f"Total Semua Shio      : {summary['total_shio']} file")
        print(f"Total Semua Confidence: {summary['total_confidence']} file")
        
        print("\n" + "-"*50)
        print(f"{Colors.GREEN}📈 PREDIKSI HARI INI:{Colors.RESET}")
        print(f"Prediktor     : {summary['today_preds']} file")
        print(f"Shio          : {summary['today_shio']} file")
        print(f"Confidence    : {summary['today_conf']} file")
        print(f"{Colors.YELLOW}Total File    : {summary['today_count']} file{Colors.RESET}")
        
        # Daftar file hari ini
        if summary['files']:
            print(f"\n{Colors.BLUE}📋 Daftar File:{Colors.RESET}")
            for i, f in enumerate(summary['files'][-10:], 1):  # Tampilkan max 10 file
                print(f"  {i}. {f}")
            if len(summary['files']) > 10:
                print(f"  ... dan {len(summary['files']) - 10} file lainnya")
        
        print("\n" + "-"*50)
        print(f"{Colors.YELLOW}💰 ESTIMASI BIAYA:{Colors.RESET}")
        print(f"Total Kombinasi: ~{summary['combo_estimate']:,} kombinasi")
        print(f"Estimasi Budget: Rp {summary['budget_estimate']:,}")
        
        # Weekly trend
        print("\n" + "-"*50)
        print(f"{Colors.BLUE}📅 TREND MINGGU INI:{Colors.RESET}")
        
        # Hitung total minggu ini
        week_start = datetime.now() - timedelta(days=datetime.now().weekday())
        week_total = self.get_week_total(week_start)
        
        print(f"Minggu ini    : {week_total} sesi prediksi")
        print(f"Target minggu : 20 sesi")
        
        progress = min(100, (week_total / 20 * 100)) if week_total > 0 else 0
        bar_len = int(progress / 10)
        bar = "█" * bar_len + "░" * (10 - bar_len)
        print(f"Progress      : {progress:.1f}% [{bar}]")
        
        # Recommendations
        print("\n" + "-"*50)
        print(f"{Colors.GREEN}💡 REKOMENDASI:{Colors.RESET}")
        
        if summary['today_count'] == 0:
            print("❌ Tidak ada prediksi hari ini - Siap untuk besok!")
            print("   Jalankan prediktor.py untuk memulai.")
        elif summary['today_count'] < 3:
            print("⚠️ Cukup - Tingkatkan lagi besok!")
            print("   Targetkan minimal 3-5 prediksi per hari.")
        elif summary['today_count'] < 6:
            print("✅ Baik - Pertahankan konsistensi!")
            print("   Anda sudah produktif hari ini.")
        else:
            print("🔥 Sangat produktif - Luar biasa!")
            print("   Pertahankan semangat ini!")
        
        print(f"\n{Colors.CYAN}💡 Tips: Gunakan kombinasi tools untuk hasil terbaik:")
        print("   • prediktor.py -> Angka main")
        print("   • shio.py -> Angka shio")
        print("   • confidence.py -> Skor keyakinan")
        print(f"   • pola.py -> Analisis pola{Colors.RESET}")
        
        # Save to file
        print("\n" + "="*50)
        save = input(f"{Colors.GREEN}💾 Simpan ringkasan ke file? (y/n): {Colors.RESET}").lower()
        
        if save == 'y':
            self.save_summary(summary)
    
    def get_week_total(self, week_start):
        """Get total predictions for current week"""
        total = 0
        week_end = week_start + timedelta(days=6)
        
        if not os.path.exists(self.download_dir):
            return 0
        
        try:
            for f in os.listdir(self.download_dir):
                if f.startswith(('prediktor_', 'shio_', 'confidence_')):
                    match = re.search(r'(\d{8})', f)
                    if match:
                        file_date = datetime.strptime(match.group(1), '%Y%m%d')
                        if week_start <= file_date <= week_end:
                            total += 1
        except:
            pass
        
        return total
    
    def save_summary(self, summary):
        """Save summary to file"""
        today = datetime.now()
        fname = f"{self.file_prefix}{today.strftime('%Y%m%d')}_{today.strftime('%H%M%S')}.txt"
        path = os.path.join(self.summary_dir, fname)
        
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write("="*50 + "\n")
                f.write("📝 DAILY SUMMARY - RINGKASAN HARIAN\n")
                f.write("="*50 + "\n\n")
                f.write(f"Tanggal: {summary['date']}\n")
                f.write(f"Waktu  : {summary['time']}\n\n")
                
                f.write("STATISTIK PREDIKSI:\n")
                f.write(f"Total Semua Prediktor : {summary['total_predictions']} file\n")
                f.write(f"Total Semua Shio      : {summary['total_shio']} file\n")
                f.write(f"Total Semua Confidence: {summary['total_confidence']} file\n\n")
                
                f.write("PREDIKSI HARI INI:\n")
                f.write(f"Prediktor     : {summary['today_preds']} file\n")
                f.write(f"Shio          : {summary['today_shio']} file\n")
                f.write(f"Confidence    : {summary['today_conf']} file\n")
                f.write(f"Total File    : {summary['today_count']} file\n\n")
                
                if summary['files']:
                    f.write("DAFTAR FILE:\n")
                    for i, file in enumerate(summary['files'], 1):
                        f.write(f"{i:3}. {file}\n")
                    f.write("\n")
                
                f.write("ESTIMASI BIAYA:\n")
                f.write(f"Total Kombinasi: {summary['combo_estimate']:,} kombinasi\n")
                f.write(f"Estimasi Budget: Rp {summary['budget_estimate']:,}\n\n")
                
                f.write("="*50 + "\n")
                f.write(f"Dibuat: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            
            print(f"\n{Colors.GREEN}✅ Tersimpan: {path}{Colors.RESET}")
        except Exception as e:
            print(f"{Colors.RED}❌ Gagal menyimpan: {e}{Colors.RESET}")
    
    def view_all_summaries(self):
        """View all past summaries"""
        if not os.path.exists(self.summary_dir):
            print(f"\n{Colors.YELLOW}⚠️ Belum ada ringkasan tersimpan{Colors.RESET}")
            return
        
        summaries = []
        try:
            for f in os.listdir(self.summary_dir):
                if f.startswith(self.file_prefix) and f.endswith('.txt'):
                    summaries.append(f)
        except Exception as e:
            print(f"{Colors.RED}❌ Error: {e}{Colors.RESET}")
            return
        
        if not summaries:
            print(f"\n{Colors.YELLOW}⚠️ Belum ada ringkasan tersimpan{Colors.RESET}")
            return
        
        # Urutkan berdasarkan tanggal (terbaru dulu)
        summaries.sort(reverse=True)
        
        print("\n" + "="*50)
        print(f"{Colors.BLUE}📜 RINGKASAN SEJARAH{Colors.RESET}")
        print("="*50)
        
        for i, f in enumerate(summaries[:10], 1):  # Tampilkan 10 terbaru
            # Extract tanggal dari nama file
            try:
                date_str = f.replace(self.file_prefix, '').split('_')[0]
                date_obj = datetime.strptime(date_str, '%Y%m%d')
                display_date = date_obj.strftime('%d/%m/%Y')
                print(f"{i:2}. {display_date} - {f}")
            except:
                print(f"{i:2}. {f}")
        
        if len(summaries) > 10:
            print(f"\n... dan {len(summaries) - 10} file lainnya")
        
        # Opsi untuk melihat detail
        print(f"\n{Colors.CYAN}Ketik nomor untuk melihat detail (0 untuk kembali):{Colors.RESET}")
        try:
            choice = int(input("> ").strip())
            if 1 <= choice <= min(10, len(summaries)):
                self.view_summary_detail(os.path.join(self.summary_dir, summaries[choice-1]))
        except ValueError:
            pass
        except Exception:
            pass
    
    def view_summary_detail(self, filepath):
        """View detail of a specific summary file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            print("\n" + "="*50)
            print(f"{Colors.MAGENTA}📄 DETAIL RINGKASAN{Colors.RESET}")
            print("="*50)
            print(content)
        except Exception as e:
            print(f"{Colors.RED}❌ Error membaca file: {e}{Colors.RESET}")


def main():
    summary = DailySummary()
    
    while True:
        os.system('clear' if os.name == 'posix' else 'cls')
        print("\n" + "="*50)
        print(f"{Colors.MAGENTA}📝 RINGKASAN HARIAN PREDIKTOR{Colors.RESET}")
        print("="*50)
        print("\n1. 📊 Generate Summary Hari Ini")
        print("2. 📜 Lihat Semua Ringkasan")
        print("3. 📅 Ringkasan Minggu Ini")
        print("4. 🗑️ Hapus Ringkasan Lama")
        print("5. Exit")
        
        choice = input(f"\n{Colors.GREEN}Pilih (1-5): {Colors.RESET}").strip()
        
        if choice == '1':
            today_summary = summary.generate_daily_summary()
            summary.display_summary(today_summary)
            input("\nTekan Enter untuk lanjut...")
        
        elif choice == '2':
            summary.view_all_summaries()
            input("\nTekan Enter untuk lanjut...")
        
        elif choice == '3':
            week_start = datetime.now() - timedelta(days=datetime.now().weekday())
            week_end = week_start + timedelta(days=6)
            
            print("\n" + "="*50)
            print(f"{Colors.CYAN}📅 RINGKASAN MINGGU INI{Colors.RESET}")
            print("="*50)
            print(f"\nPeriode: {week_start.strftime('%d/%m/%Y')} - {week_end.strftime('%d/%m/%Y')}")
            
            # Hitung progress
            summary_obj = summary.generate_daily_summary()
            week_total = summary.get_week_total(week_start)
            
            print(f"\nTotal Minggu Ini: {week_total} sesi prediksi")
            
            remaining = max(0, 20 - week_total)
            if remaining > 0:
                print(f"{Colors.GREEN}Sisa target: {remaining} sesi lagi untuk mencapai 20!{Colors.RESET}")
                
                # Estimasi per hari
                days_left = max(1, 7 - datetime.now().weekday())
                per_day = remaining / days_left
                print(f"Target per hari: {per_day:.1f} sesi/hari")
            else:
                print(f"{Colors.GREEN}✅ Target Mingguan Tercapai! ({week_total}/20){Colors.RESET}")
            
            input("\nTekan Enter untuk lanjut...")
        
        elif choice == '4':
            confirm = input(f"{Colors.RED}⚠️ Hapus semua ringkasan lama? (y/n): {Colors.RESET}").lower()
            if confirm == 'y':
                try:
                    for f in os.listdir(summary.summary_dir):
                        if f.startswith(summary.file_prefix):
                            os.remove(os.path.join(summary.summary_dir, f))
                    print(f"{Colors.GREEN}✅ Semua ringkasan telah dihapus{Colors.RESET}")
                except Exception as e:
                    print(f"{Colors.RED}❌ Error: {e}{Colors.RESET}")
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