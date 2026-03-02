# File: analisis_saham_manual.py
# Simpan dengan nama ini, lalu jalankan dengan: python analisis_saham_manual.py

import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import json
import sys
import os

# Cek versi
print(f"Python version: {sys.version}")
print(f"Pandas version: {pd.__version__}")
print(f"Requests version: {requests.__version__}")

class AnalisisSahamManual:
    """
    Analisis saham Indonesia dengan INPUT MANUAL
    User bisa memasukkan saham yang ingin dianalisis
    """
    def __init__(self):
        # Headers untuk request
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # Database saham populer (untuk referensi)
        self.referensi_saham = {
            'BBCA': 'Bank BCA',
            'BBRI': 'Bank BRI', 
            'BMRI': 'Bank Mandiri',
            'BNI': 'Bank BNI',
            'TLKM': 'Telkom Indonesia',
            'ASII': 'Astra International',
            'UNVR': 'Unilever Indonesia',
            'GGRM': 'Gudang Garam',
            'HMSP': 'HM Sampoerna',
            'ICBP': 'Indofood CBP',
            'INDF': 'Indofood Sukses Makmur',
            'KLBF': 'Kalbe Farma',
            'PGAS': 'Perusahaan Gas Negara',
            'ANTM': 'Aneka Tambang',
            'ADRO': 'Adaro Energy',
            'PTBA': 'Bukit Asam',
            'CPIN': 'Charoen Pokphand',
            'JPFA': 'Japfa Comfeed',
            'SMGR': 'Semen Indonesia',
            'WSKT': 'Waskita Karya',
            'WIKA': 'Wijaya Karya',
            'PTPP': 'PP Persero',
            'EXCL': 'XL Axiata',
            'ISAT': 'Indosat',
            'FREN': 'Smartfren',
        }
    
    def get_data_yahoo(self, kode_saham, periode='6m'):
        """
        Ambil data dari Yahoo Finance langsung via API
        """
        # Mapping periode
        period_map = {
            '1m': '1mo', '3m': '3mo', '6m': '6mo',
            '1y': '1y', '2y': '2y', '5y': '5y'
        }
        
        # Yahoo Finance API URL
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{kode_saham}"
        params = {
            'range': period_map.get(periode, '6mo'),
            'interval': '1d',
            'includePrePost': 'false'
        }
        
        try:
            print(f"  ⏳ Mengambil data {kode_saham}...")
            response = requests.get(url, headers=self.headers, params=params, timeout=15)
            
            if response.status_code != 200:
                print(f"  ❌ Gagal: HTTP {response.status_code}")
                return None
            
            data = response.json()
            
            # Parse data
            if 'chart' in data and 'result' in data['chart'] and data['chart']['result']:
                result = data['chart']['result'][0]
                
                # Ambil timestamp dan harga
                timestamps = result['timestamp']
                quotes = result['indicators']['quote'][0]
                
                # Buat DataFrame
                df = pd.DataFrame({
                    'Tanggal': pd.to_datetime(timestamps, unit='s'),
                    'Open': quotes['open'],
                    'High': quotes['high'],
                    'Low': quotes['low'], 
                    'Close': quotes['close'],
                    'Volume': quotes['volume']
                })
                
                # Bersihkan data
                df = df.dropna()
                df = df.set_index('Tanggal')
                
                print(f"  ✅ OK: {len(df)} data points")
                return df
            else:
                print(f"  ❌ Data tidak ditemukan untuk {kode_saham}")
                return None
                
        except requests.exceptions.Timeout:
            print(f"  ❌ Timeout untuk {kode_saham}")
            return None
        except Exception as e:
            print(f"  ❌ Error: {str(e)[:100]}")
            return None
    
    def format_kode_saham(self, kode):
        """
        Format kode saham untuk Yahoo Finance
        """
        kode = kode.upper().strip()
        
        # Hapus .JK jika sudah ada
        kode = kode.replace('.JK', '')
        
        # Untuk saham Indonesia, tambahkan .JK
        return f"{kode}.JK"
    
    def cek_ketersediaan(self, kode):
        """
        Cek apakah kode saham tersedia
        """
        kode_lengkap = self.format_kode_saham(kode)
        df = self.get_data_yahoo(kode_lengkap, '1m')  # Coba ambil 1 bulan
        
        return df is not None and not df.empty
    
    def lihat_saham(self, kode, periode='6m'):
        """
        Lihat detail satu saham
        """
        print(f"\n{'='*60}")
        print(f"📊 ANALISIS SAHAM: {kode.upper()}")
        print('='*60)
        
        # Format kode
        kode_lengkap = self.format_kode_saham(kode)
        
        # Ambil data
        df = self.get_data_yahoo(kode_lengkap, periode)
        
        if df is None or df.empty:
            print(f"\n❌ Tidak bisa mengambil data {kode}")
            print("   Kemungkinan penyebab:")
            print("   - Kode saham salah")
            print("   - Saham tidak terdaftar di Yahoo Finance")
            print("   - Masalah koneksi")
            return None
        
        # Hitung statistik
        harga_awal = df['Close'].iloc[0]
        harga_akhir = df['Close'].iloc[-1]
        harga_tertinggi = df['High'].max()
        harga_terendah = df['Low'].min()
        harga_rata = df['Close'].mean()
        volume_rata = df['Volume'].mean()
        volume_total = df['Volume'].sum()
        return_persen = ((harga_akhir / harga_awal) - 1) * 100
        
        # Hitung volatilitas (harian)
        daily_returns = df['Close'].pct_change().dropna()
        volatilitas_harian = daily_returns.std() * 100
        volatilitas_tahunan = volatilitas_harian * (252 ** 0.5)  # 252 hari trading
        
        # Tampilkan statistik dengan format yang rapi
        print(f"\n📈 DATA STATISTIK:")
        print(f"├─ Periode       : {df.index[0].strftime('%d %B %Y')} - {df.index[-1].strftime('%d %B %Y')}")
        print(f"├─ Hari Trading  : {len(df)} hari")
        print(f"├─ Harga Awal    : Rp {harga_awal:,.0f}")
        print(f"├─ Harga Akhir   : Rp {harga_akhir:,.0f}")
        print(f"├─ Harga Tertinggi: Rp {harga_tertinggi:,.0f}")
        print(f"├─ Harga Terendah : Rp {harga_terendah:,.0f}")
        print(f"├─ Harga Rata-rata: Rp {harga_rata:,.0f}")
        print(f"├─ Return Periode : {return_persen:+.2f}%")
        print(f"├─ Volatilitas Harian: {volatilitas_harian:.2f}%")
        print(f"├─ Volatilitas Tahunan: {volatilitas_tahunan:.2f}%")
        print(f"├─ Volume Rata-rata: {volume_rata:,.0f}")
        print(f"└─ Total Volume   : {volume_total:,.0f}")
        
        # Tampilkan 5 data terakhir
        print(f"\n📋 5 DATA TERAKHIR:")
        print(df[['Open', 'High', 'Low', 'Close', 'Volume']].tail().to_string())
        
        # Plot
        self.plot_saham(df, kode.upper())
        
        return df
    
    def plot_saham(self, df, judul):
        """
        Plot harga saham
        """
        try:
            fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10))
            
            # Plot harga candlestick sederhana
            ax1.plot(df.index, df['Close'], 'b-', linewidth=1.5, label='Close Price')
            ax1.fill_between(df.index, df['Low'], df['High'], alpha=0.2, color='blue')
            ax1.set_title(f'{judul} - Harga Saham', fontsize=14, fontweight='bold')
            ax1.set_ylabel('Harga (Rp)')
            ax1.grid(True, alpha=0.3)
            ax1.legend()
            
            # Plot volume
            colors = ['g' if df['Close'].iloc[i] >= df['Open'].iloc[i] else 'r' 
                     for i in range(len(df))]
            ax2.bar(df.index, df['Volume'], color=colors, alpha=0.7, width=0.8)
            ax2.set_title('Volume Transaksi', fontsize=12)
            ax2.set_ylabel('Volume')
            ax2.grid(True, alpha=0.3)
            
            # Plot return kumulatif
            cumulative_return = (df['Close'] / df['Close'].iloc[0] - 1) * 100
            ax3.plot(df.index, cumulative_return, 'g-', linewidth=1.5)
            ax3.fill_between(df.index, 0, cumulative_return, 
                            where=(cumulative_return > 0), color='g', alpha=0.3)
            ax3.fill_between(df.index, 0, cumulative_return, 
                            where=(cumulative_return < 0), color='r', alpha=0.3)
            ax3.set_title('Return Kumulatif (%)', fontsize=12)
            ax3.set_ylabel('Return (%)')
            ax3.set_xlabel('Tanggal')
            ax3.grid(True, alpha=0.3)
            ax3.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
            
            plt.tight_layout()
            plt.show()
            
        except Exception as e:
            print(f"Error plotting: {e}")
    
    def bandingkan_saham(self, daftar_kode, periode='6m'):
        """
        Bandingkan beberapa saham
        """
        print(f"\n{'='*60}")
        print("📊 PERBANDINGAN MULTIPLE SAHAM")
        print('='*60)
        print(f"Saham: {', '.join(daftar_kode)}")
        print(f"Periode: {periode}")
        print("-" * 40)
        
        # Kumpulkan data
        data_saham = {}
        for kode in daftar_kode:
            kode_lengkap = self.format_kode_saham(kode)
            df = self.get_data_yahoo(kode_lengkap, periode)
            if df is not None and not df.empty:
                data_saham[kode.upper()] = df
        
        if not data_saham:
            print("\n❌ Tidak ada data yang bisa diambil")
            return None
        
        # Plot perbandingan
        plt.figure(figsize=(14, 8))
        
        colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown', 'pink', 'gray']
        
        for i, (kode, df) in enumerate(data_saham.items()):
            # Normalisasi ke 100
            normal = (df['Close'] / df['Close'].iloc[0]) * 100
            color = colors[i % len(colors)]
            plt.plot(normal.index, normal.values, label=kode, color=color, linewidth=2)
        
        plt.title(f'Perbandingan Performa Saham (100 = awal periode)', fontsize=14, fontweight='bold')
        plt.xlabel('Tanggal')
        plt.ylabel('Performa (%)')
        plt.grid(True, alpha=0.3)
        plt.legend(loc='best')
        plt.axhline(y=100, color='black', linestyle='--', linewidth=0.5, alpha=0.5)
        plt.tight_layout()
        plt.show()
        
        # Tabel perbandingan
        print("\n📈 TABEL PERBANDINGAN:")
        print("-" * 60)
        print(f"{'Saham':<8} {'Return (%)':>12} {'Harga':>12} {'Volume':>15} {'Volatilitas':>12}")
        print("-" * 60)
        
        for kode, df in data_saham.items():
            ret = ((df['Close'].iloc[-1] / df['Close'].iloc[0]) - 1) * 100
            harga = df['Close'].iloc[-1]
            volume = df['Volume'].iloc[-1]
            volatilitas = df['Close'].pct_change().std() * 100
            
            arrow = "▲" if ret > 0 else "▼"
            print(f"{kode:<8} {arrow} {ret:>+10.2f}%  Rp {harga:>9,.0f}  {volume:>13,.0f}  {volatilitas:>10.2f}%")
        
        print("-" * 60)
        
        return data_saham
    
    def cari_saham_dari_daftar(self, daftar_kode, periode='1y'):
        """
        Cari saham terbaik dari daftar yang diberikan
        """
        print(f"\n{'='*60}")
        print("🔍 MENCARI SAHAM TERBAIK")
        print('='*60)
        print(f"Menganalisis {len(daftar_kode)} saham...")
        
        hasil = []
        for kode in daftar_kode:
            kode_lengkap = self.format_kode_saham(kode)
            df = self.get_data_yahoo(kode_lengkap, periode)
            
            if df is not None and len(df) > 20:
                ret = ((df['Close'].iloc[-1] / df['Close'].iloc[0]) - 1) * 100
                volatilitas = df['Close'].pct_change().std() * (252**0.5) * 100
                sharp_ratio = (ret/100) / (volatilitas/100) if volatilitas > 0 else 0
                
                hasil.append({
                    'Saham': kode.upper(),
                    'Return (%)': round(ret, 2),
                    'Volatilitas (%)': round(volatilitas, 2),
                    'Sharpe Ratio': round(sharp_ratio, 2),
                    'Harga': round(df['Close'].iloc[-1], 0),
                    'Volume': int(df['Volume'].iloc[-1])
                })
        
        if hasil:
            df_hasil = pd.DataFrame(hasil)
            
            # Urutkan berdasarkan return
            df_hasil_return = df_hasil.sort_values('Return (%)', ascending=False)
            
            print("\n🏆 RANKING BERDASARKAN RETURN:")
            print(df_hasil_return.to_string(index=False))
            
            # Urutkan berdasarkan Sharpe Ratio (risk-adjusted return)
            df_hasil_sharpe = df_hasil.sort_values('Sharpe Ratio', ascending=False)
            
            print("\n📊 RANKING BERDASARKAN SHARPE RATIO (Return per Risiko):")
            print(df_hasil_sharpe.to_string(index=False))
            
            # Plot
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
            
            # Plot return
            colors = ['g' if x > 0 else 'r' for x in df_hasil_return['Return (%)']]
            ax1.bar(df_hasil_return['Saham'], df_hasil_return['Return (%)'], color=colors)
            ax1.set_title('Return Saham', fontsize=12, fontweight='bold')
            ax1.set_ylabel('Return (%)')
            ax1.grid(True, alpha=0.3)
            ax1.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
            
            # Plot Sharpe Ratio
            colors2 = ['g' if x > 0.5 else 'orange' if x > 0 else 'r' 
                      for x in df_hasil_sharpe['Sharpe Ratio']]
            ax2.bar(df_hasil_sharpe['Saham'], df_hasil_sharpe['Sharpe Ratio'], color=colors2)
            ax2.set_title('Sharpe Ratio (Return per Unit Risiko)', fontsize=12, fontweight='bold')
            ax2.set_ylabel('Sharpe Ratio')
            ax2.set_xlabel('Saham')
            ax2.grid(True, alpha=0.3)
            ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
            ax2.axhline(y=0.5, color='orange', linestyle='--', linewidth=0.5, alpha=0.5, label='Good')
            ax2.axhline(y=1, color='green', linestyle='--', linewidth=0.5, alpha=0.5, label='Excellent')
            ax2.legend()
            
            plt.tight_layout()
            plt.show()
            
            return df_hasil
        else:
            print("\n❌ Tidak ada data yang valid")
            return None

# Menu utama dengan input manual
def main():
    # Bersihkan layar
    os.system('clear' if os.name == 'posix' else 'cls')
    
    print("=" * 60)
    print("   ANALISIS SAHAM INDONESIA - INPUT MANUAL")
    print("   Khusus Termux - Tanpa Upgrade Pip")
    print("=" * 60)
    
    analyzer = AnalisisSahamManual()
    
    print("\n📌 SAHAM POPULER (referensi):")
    # Tampilkan 10 saham pertama sebagai referensi
    for i, (kode, nama) in enumerate(list(analyzer.referensi_saham.items())[:10]):
        print(f"   {kode:<6} - {nama}")
    print("   (dan masih banyak lagi...)")
    
    while True:
        print("\n" + "=" * 60)
        print("📌 MENU UTAMA:")
        print("=" * 60)
        print("1. 🔍 Analisis 1 saham")
        print("2. 📊 Bandingkan beberapa saham")
        print("3. 🏆 Cari saham terbaik dari daftar")
        print("4. 💾 Simpan daftar saham favorit")
        print("5. 📖 Lihat daftar saham referensi")
        print("6. ❌ Keluar")
        
        pilihan = input("\nPilih menu (1-6): ").strip()
        
        if pilihan == '1':
            print("\n" + "-" * 40)
            print("🔍 ANALISIS 1 SAHAM")
            print("-" * 40)
            
            kode = input("Masukkan kode saham (contoh: BBCA): ").strip().upper()
            if not kode:
                print("❌ Kode saham tidak boleh kosong!")
                continue
            
            print("\nPilih periode:")
            print("1m = 1 bulan")
            print("3m = 3 bulan")
            print("6m = 6 bulan")
            print("1y = 1 tahun")
            print("2y = 2 tahun")
            print("5y = 5 tahun")
            
            periode = input("Periode [default: 6m]: ").strip() or '6m'
            
            analyzer.lihat_saham(kode, periode)
            
            input("\nTekan Enter untuk kembali ke menu...")
            
        elif pilihan == '2':
            print("\n" + "-" * 40)
            print("📊 BANDINGKAN BEBERAPA SAHAM")
            print("-" * 40)
            print("Contoh: BBCA, BBRI, BMRI, TLKM")
            
            kodes = input("Masukkan kode saham (pisah dengan koma): ").strip().upper()
            if not kodes:
                print("❌ Tidak ada saham yang dimasukkan!")
                continue
            
            daftar = [k.strip() for k in kodes.split(',') if k.strip()]
            
            print("\nPilih periode:")
            print("1m/3m/6m/1y/2y/5y")
            periode = input("Periode [default: 6m]: ").strip() or '6m'
            
            analyzer.bandingkan_saham(daftar, periode)
            
            input("\nTekan Enter untuk kembali ke menu...")
            
        elif pilihan == '3':
            print("\n" + "-" * 40)
            print("🏆 CARI SAHAM TERBAIK")
            print("-" * 40)
            print("Masukkan daftar saham yang ingin dianalisis")
            print("Contoh: BBCA, BBRI, BMRI, TLKM, ASII, UNVR")
            
            kodes = input("Daftar saham: ").strip().upper()
            if not kodes:
                print("❌ Tidak ada saham yang dimasukkan!")
                continue
            
            daftar = [k.strip() for k in kodes.split(',') if k.strip()]
            
            print("\nPilih periode:")
            print("1m/3m/6m/1y/2y/5y")
            periode = input("Periode [default: 1y]: ").strip() or '1y'
            
            analyzer.cari_saham_dari_daftar(daftar, periode)
            
            input("\nTekan Enter untuk kembali ke menu...")
            
        elif pilihan == '4':
            print("\n" + "-" * 40)
            print("💾 SIMPAN DAFTAR SAHAM FAVORIT")
            print("-" * 40)
            
            # Simpan ke file teks sederhana
            favorit_file = "saham_favorit.txt"
            
            if os.path.exists(favorit_file):
                with open(favorit_file, 'r') as f:
                    existing = f.read().strip()
                print(f"Daftar favorit saat ini: {existing}")
            
            kodes = input("Masukkan daftar saham favorit (pisah koma): ").strip().upper()
            
            if kodes:
                with open(favorit_file, 'w') as f:
                    f.write(kodes)
                print(f"✅ Daftar saham favorit tersimpan: {kodes}")
            else:
                print("❌ Tidak ada yang disimpan")
            
            input("\nTekan Enter untuk kembali ke menu...")
            
        elif pilihan == '5':
            print("\n" + "-" * 40)
            print("📖 DAFTAR SAHAM REFERENSI")
            print("-" * 40)
            
            # Tampilkan dalam format tabel
            items = list(analyzer.referensi_saham.items())
            for i in range(0, len(items), 5):
                batch = items[i:i+5]
                for kode, nama in batch:
                    print(f"{kode:<6} - {nama:<30}")
                print()
            
            input("\nTekan Enter untuk kembali ke menu...")
            
        elif pilihan == '6':
            print("\n" + "=" * 60)
            print("   Terima kasih telah menggunakan program ini!")
            print("   Happy Investing! 📈")
            print("=" * 60)
            break
        
        else:
            print("\n❌ Pilihan tidak valid!")
            input("Tekan Enter untuk melanjutkan...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProgram dihentikan oleh user")
    except Exception as e:
        print(f"\nError: {e}")
        print("Program mengalami error")