
# File: tape_reading_bsi.py
# Script Tape Reading untuk saham BSI dengan filter harga user

import requests
import pandas as pd
import numpy as np
from datetime import datetime
import time
import io
import json
import os

class TapeReadingBSI:
    """
    Tape Reading Scanner untuk saham BSI
    - User bisa menentukan range harga
    - Deteksi akumulasi/distribusi bandar
    - Real-time monitoring
    """
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # Link CSV saham BSI Anda
        self.CSV_URL = "https://raw.githubusercontent.com/momodigital/data-vault/refs/heads/main/xyz/sahambsi.csv"
        
        # Load daftar saham
        self.daftar_saham = self.load_stocks_from_csv()
        
        # Default range harga (bisa diubah user)
        self.HARGA_MIN = 50
        self.HARGA_MAX = 5000
        
        print(f"\n📋 Total saham BSI: {len(self.daftar_saham)}")
        print(f"🔗 Sumber CSV: {self.CSV_URL}")
    
    def load_stocks_from_csv(self):
        """Load daftar saham dari CSV"""
        try:
            response = requests.get(self.CSV_URL, timeout=10)
            if response.status_code == 200:
                df = pd.read_csv(io.StringIO(response.text))
                stocks = {}
                
                if 'kode' in df.columns:
                    for _, row in df.iterrows():
                        kode = str(row['kode']).strip().upper()
                        if kode and pd.notna(kode):
                            stocks[kode] = f"{kode}.JK"
                    
                    print(f"✅ Loaded {len(stocks)} saham dari CSV")
                    return stocks
            return {}
        except Exception as e:
            print(f"Error: {e}")
            return {}
    
    def get_order_book(self, kode):
        """
        Mendapatkan data untuk tape reading
        """
        try:
            kode_lengkap = self.daftar_saham.get(kode, f"{kode}.JK")
            
            # Ambil data 1 jam terakhir (60 menit)
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{kode_lengkap}"
            params = {'range': '1d', 'interval': '1m'}  # Data per menit
            
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            
            if 'chart' in data and 'result' in data['chart'] and data['chart']['result']:
                result = data['chart']['result'][0]
                timestamps = result['timestamp']
                quotes = result['indicators']['quote'][0]
                
                # Kumpulkan data per menit
                prices = []
                volumes = []
                for i in range(len(timestamps)):
                    if quotes['close'][i] is not None and quotes['volume'][i] is not None:
                        prices.append(quotes['close'][i])
                        volumes.append(quotes['volume'][i])
                
                if len(prices) < 30:
                    return None
                
                # Analisis Tape Reading
                tape_analysis = self.analyze_tape_reading(prices, volumes, kode)
                
                return tape_analysis
            
            return None
            
        except Exception as e:
            return None
    
    def analyze_tape_reading(self, prices, volumes, kode):
        """
        Analisis tape reading dari pergerakan harga dan volume
        """
        # 1. Hitung rata-rata volume
        avg_volume = np.mean(volumes[:-5]) if len(volumes) > 5 else np.mean(volumes)
        
        # 2. Deteksi volume spikes (5 menit terakhir)
        last_5_volumes = volumes[-5:]
        volume_spikes = [v for v in last_5_volumes if v > avg_volume * 1.8]
        
        # 3. Analisis candle pattern (5 menit terakhir)
        last_5_prices = prices[-5:]
        last_5_volumes = volumes[-5:]
        
        bullish_candles = 0
        bearish_candles = 0
        accumulation_signals = []
        distribution_signals = []
        
        for i in range(1, len(last_5_prices)):
            price_change = last_5_prices[i] - last_5_prices[i-1]
            volume_ratio = last_5_volumes[i] / avg_volume if avg_volume > 0 else 1
            
            # Bullish signal: harga naik + volume besar
            if price_change > 0 and volume_ratio > 1.5:
                bullish_candles += 1
                accumulation_signals.append({
                    'menit_ke': i,
                    'harga': last_5_prices[i],
                    'volume': last_5_volumes[i],
                    'volume_ratio': volume_ratio
                })
            
            # Bearish signal: harga turun + volume besar
            elif price_change < 0 and volume_ratio > 1.5:
                bearish_candles += 1
                distribution_signals.append({
                    'menit_ke': i,
                    'harga': last_5_prices[i],
                    'volume': last_5_volumes[i],
                    'volume_ratio': volume_ratio
                })
        
        # 4. Deteksi Support/Resistance
        recent_prices = prices[-20:]
        support = min(recent_prices)
        resistance = max(recent_prices)
        current_price = prices[-1]
        
        # Posisi harga
        if current_price <= support * 1.02:
            position = "NEAR SUPPORT"
        elif current_price >= resistance * 0.98:
            position = "NEAR RESISTANCE"
        else:
            position = "MIDDLE"
        
        # 5. Tape Reading Score
        tape_score = 0
        signals = []
        
        # Akumulasi signal
        if len(accumulation_signals) >= 3:
            tape_score += 4
            signals.append(f"🔥 AKUMULASI KUAT ({len(accumulation_signals)} candles)")
        elif len(accumulation_signals) >= 2:
            tape_score += 2
            signals.append(f"✅ AKUMULASI TERDETEKSI ({len(accumulation_signals)} candles)")
        elif len(accumulation_signals) >= 1:
            tape_score += 1
            signals.append(f"👀 MULAI AKUMULASI")
        
        # Distribusi signal
        if len(distribution_signals) >= 3:
            tape_score -= 4
            signals.append(f"💥 DISTRIBUSI KUAT ({len(distribution_signals)} candles)")
        elif len(distribution_signals) >= 2:
            tape_score -= 2
            signals.append(f"⚠️ DISTRIBUSI TERDETEKSI ({len(distribution_signals)} candles)")
        elif len(distribution_signals) >= 1:
            tape_score -= 1
            signals.append(f"📉 MULAI DISTRIBUSI")
        
        # Volume spike terakhir
        if volumes[-1] > avg_volume * 2.5:
            if prices[-1] > prices[-2]:
                tape_score += 3
                signals.append(f"🚀 VOLUME SPIKE BESAR + UPTICK (BUYING PRESSURE)")
            else:
                tape_score -= 3
                signals.append(f"💣 VOLUME SPIKE BESAR + DOWNTICK (SELLING PRESSURE)")
        elif volumes[-1] > avg_volume * 1.8:
            if prices[-1] > prices[-2]:
                tape_score += 2
                signals.append(f"📊 VOLUME SPIKE + UPTICK")
            else:
                tape_score -= 2
                signals.append(f"📉 VOLUME SPIKE + DOWNTICK")
        elif volumes[-1] > avg_volume * 1.3:
            if prices[-1] > prices[-2]:
                tape_score += 1
                signals.append(f"📈 VOLUME MENINGKAT + UPTICK")
            else:
                tape_score -= 1
                signals.append(f"📉 VOLUME MENINGKAT + DOWNTICK")
        
        # Price action terhadap support/resistance
        if position == "NEAR SUPPORT":
            if tape_score > 0:
                tape_score += 1
                signals.append(f"💪 SUPPORT TERUJI (+1)")
            else:
                signals.append(f"⚡ SUPPORT DIUJI")
        elif position == "NEAR RESISTANCE":
            if tape_score < 0:
                tape_score -= 1
                signals.append(f"🧱 RESISTANCE TERUJI (-1)")
            else:
                signals.append(f"⚡ RESISTANCE DIUJI")
        
        return {
            'kode': kode,
            'harga_terkini': current_price,
            'support': support,
            'resistance': resistance,
            'position': position,
            'avg_volume': avg_volume,
            'volume_terakhir': volumes[-1],
            'volume_ratio': volumes[-1] / avg_volume if avg_volume > 0 else 1,
            'bullish_candles': bullish_candles,
            'bearish_candles': bearish_candles,
            'accumulation_count': len(accumulation_signals),
            'distribution_count': len(distribution_signals),
            'tape_score': tape_score,
            'signals': signals,
            'rekomendasi': self.get_tape_recommendation(tape_score, position, current_price)
        }
    
    def get_tape_recommendation(self, tape_score, position, harga):
        """Rekomendasi berdasarkan tape reading"""
        if tape_score >= 6:
            return "🔥🔥 STRONG BUY (AKUMULASI BANDAR BESAR)"
        elif tape_score >= 4:
            return "✅✅ BUY (AKUMULASI TERKONFIRMASI)"
        elif tape_score >= 2:
            return "✅ WATCH (AKUMULASI AWAL)"
        elif tape_score >= -1:
            return "📊 HOLD (NETRAL)"
        elif tape_score >= -3:
            return "⚠️ CAUTION (DISTRIBUSI AWAL)"
        elif tape_score >= -5:
            return "⚠️⚠️ SELL (DISTRIBUSI TERKONFIRMASI)"
        else:
            return "❌ AVOID (DISTRIBUSI BANDAR BESAR)"
    
    def scan_tape_reading(self, harga_min, harga_max):
        """
        Scan semua saham dengan filter harga dari USER
        """
        print("\n" + "="*100)
        print(f"🎯 TAPE READING SCANNER")
        print(f"💰 RENTANG HARGA: Rp {harga_min:,.0f} - Rp {harga_max:,.0f}")
        print("="*100)
        
        results = []
        total = len(self.daftar_saham)
        
        print(f"\n⏳ Menganalisis {total} saham...")
        
        for i, (kode, _) in enumerate(self.daftar_saham.items(), 1):
            # Progress bar sederhana
            progress = (i / total) * 100
            bar = '█' * int(progress/2) + '░' * (50 - int(progress/2))
            print(f"\r[{bar}] {i}/{total} ({progress:.1f}%) - {kode}", end='', flush=True)
            
            tape_data = self.get_order_book(kode)
            
            if tape_data:
                # FILTER HARGA SESUAI INPUT USER
                if harga_min <= tape_data['harga_terkini'] <= harga_max:
                    results.append(tape_data)
            
            time.sleep(0.15)  # Delay
        
        print(f"\n✅ Selesai! Ditemukan {len(results)} saham dalam rentang Rp {harga_min:,.0f} - Rp {harga_max:,.0f}")
        
        return results
    
    def display_tape_results(self, results):
        """
        Tampilkan hasil tape reading
        """
        if not results:
            print("❌ Tidak ada data")
            return
        
        # Urutkan berdasarkan tape score (akumulasi terkuat di atas)
        results = sorted(results, key=lambda x: x['tape_score'], reverse=True)
        
        print("\n" + "="*130)
        print("📊 HASIL TAPE READING - URUTAN AKUMULASI TERKUAT")
        print("="*130)
        
        # Header
        print(f"{'No':<3} {'Kode':<6} {'Harga':>8} {'S/R':>12} {'Vol':>8} {'Bull':>5} {'Bear':>5} {'Score':>6} {'Rekomendasi'}")
        print("-"*130)
        
        for i, r in enumerate(results[:50], 1):  # Top 50
            # Simbol berdasarkan rekomendasi
            if 'STRONG BUY' in r['rekomendasi']:
                marker = "🔥"
            elif 'BUY' in r['rekomendasi']:
                marker = "✅"
            elif 'WATCH' in r['rekomendasi']:
                marker = "👀"
            elif 'HOLD' in r['rekomendasi']:
                marker = "📊"
            elif 'CAUTION' in r['rekomendasi']:
                marker = "⚠️"
            elif 'SELL' in r['rekomendasi']:
                marker = "📉"
            else:
                marker = "❌"
            
            sr_info = f"{r['support']:.0f}/{r['resistance']:.0f}"
            
            print(f"{i:<3} {r['kode']:<6} Rp {r['harga_terkini']:>6,.0f} {sr_info:>12} {r['volume_ratio']:>7.1f}x {r['bullish_candles']:>5} {r['bearish_candles']:>5} {r['tape_score']:>5}  {marker} {r['rekomendasi']}")
        
        print("="*130)
        
        # Statistik
        strong_buy = sum(1 for r in results if 'STRONG BUY' in r['rekomendasi'])
        buy = sum(1 for r in results if 'BUY' in r['rekomendasi'] and 'STRONG' not in r['rekomendasi'])
        watch = sum(1 for r in results if 'WATCH' in r['rekomendasi'])
        hold = sum(1 for r in results if 'HOLD' in r['rekomendasi'])
        caution = sum(1 for r in results if 'CAUTION' in r['rekomendasi'])
        sell = sum(1 for r in results if 'SELL' in r['rekomendasi'])
        avoid = sum(1 for r in results if 'AVOID' in r['rekomendasi'])
        
        print(f"\n📈 RINGKASAN STATISTIK:")
        print(f"├─ 🔥 STRONG BUY: {strong_buy}")
        print(f"├─ ✅ BUY: {buy}")
        print(f"├─ 👀 WATCH: {watch}")
        print(f"├─ 📊 HOLD: {hold}")
        print(f"├─ ⚠️ CAUTION: {caution}")
        print(f"├─ 📉 SELL: {sell}")
        print(f"└─ ❌ AVOID: {avoid}")
        
        # TOP 10 AKUMULASI
        print("\n🏆 TOP 10 AKUMULASI TERKUAT (REKOMENDASI BELI):")
        print("-"*70)
        
        top_accum = [r for r in results if r['tape_score'] >= 2][:10]
        for i, r in enumerate(top_accum, 1):
            print(f"\n{i}. {r['kode']} - Rp {r['harga_terkini']:,.0f} [Score: {r['tape_score']}]")
            print(f"   ├─ Support: Rp {r['support']:,.0f} | Resistance: Rp {r['resistance']:,.0f}")
            print(f"   ├─ Volume: {r['volume_ratio']:.1f}x dari rata-rata")
            print(f"   ├─ Bullish/Bearish: {r['bullish_candles']}/{r['bearish_candles']}")
            print(f"   ├─ Posisi: {r['position']}")
            print(f"   ├─ {r['rekomendasi']}")
            if r['signals']:
                print(f"   └─ Signals: {', '.join(r['signals'][:2])}")
        
        # TOP 10 DISTRIBUSI
        print("\n💣 TOP 10 DISTRIBUSI TERKUAT (HINDARI/JUAL):")
        print("-"*70)
        
        top_distrib = [r for r in results if r['tape_score'] <= -2][:10]
        for i, r in enumerate(top_distrib, 1):
            print(f"\n{i}. {r['kode']} - Rp {r['harga_terkini']:,.0f} [Score: {r['tape_score']}]")
            print(f"   ├─ {r['rekomendasi']}")
            print(f"   ├─ Volume: {r['volume_ratio']:.1f}x dari rata-rata")
            print(f"   └─ Signals: {', '.join(r['signals'][:2])}")
        
        return results
    
    def detail_saham(self, kode):
        """Lihat detail tape reading satu saham"""
        print(f"\n📊 DETAIL TAPE READING: {kode}")
        print("="*50)
        
        tape_data = self.get_order_book(kode)
        
        if not tape_data:
            print("❌ Tidak dapat mengambil data")
            return
        
        print(f"Harga Terkini : Rp {tape_data['harga_terkini']:,.0f}")
        print(f"Support Level : Rp {tape_data['support']:,.0f}")
        print(f"Resistance    : Rp {tape_data['resistance']:,.0f}")
        print(f"Posisi        : {tape_data['position']}")
        print(f"Volume Ratio  : {tape_data['volume_ratio']:.2f}x")
        print(f"Bullish Candle: {tape_data['bullish_candles']} (5 menit)")
        print(f"Bearish Candle: {tape_data['bearish_candles']} (5 menit)")
        print(f"Tape Score    : {tape_data['tape_score']}")
        print(f"Rekomendasi   : {tape_data['rekomendasi']}")
        
        if tape_data['signals']:
            print("\nSinyal Terdeteksi:")
            for s in tape_data['signals']:
                print(f"  • {s}")

def main():
    # Bersihkan layar
    os.system('clear' if os.name == 'posix' else 'cls')
    
    print("="*90)
    print("   TAPE READING SCANNER - DENGAN FILTER HARGA USER")
    print("   Khusus Saham BSI dari CSV Anda")
    print("="*90)
    
    scanner = TapeReadingBSI()
    
    while True:
        print("\n📌 MENU TAPE READING:")
        print("1. 🎯 Scan berdasarkan RENTANG HARGA (input user)")
        print("2. 🔍 Detail satu saham")
        print("3. 📈 Monitor real-time (5 menit)")
        print("4. ⚙️ Ubah default range harga")
        print("5. ❌ Keluar")
        
        pilihan = input("\nPilih menu (1-5): ").strip()
        
        if pilihan == '1':
            print("\n💰 MASUKKAN RENTANG HARGA YANG DIINGINKAN:")
            try:
                harga_min = float(input("Harga minimum (Rp): ").replace('.', ''))
                harga_max = float(input("Harga maksimum (Rp): ").replace('.', ''))
                
                if harga_min >= harga_max:
                    print("❌ Harga minimum harus lebih kecil dari maksimum")
                    continue
                
                # Scan dengan filter harga dari user
                results = scanner.scan_tape_reading(harga_min, harga_max)
                
                if results:
                    scanner.display_tape_results(results)
                    
                    # Opsi simpan hasil
                    save = input("\n💾 Simpan hasil ke CSV? (y/n): ").lower()
                    if save == 'y':
                        # Buat dataframe tanpa kolom yang kompleks
                        df_simple = pd.DataFrame([{
                            'kode': r['kode'],
                            'harga': r['harga_terkini'],
                            'support': r['support'],
                            'resistance': r['resistance'],
                            'volume_ratio': r['volume_ratio'],
                            'tape_score': r['tape_score'],
                            'rekomendasi': r['rekomendasi']
                        } for r in results])
                        
                        filename = f"tape_reading_{harga_min:.0f}_{harga_max:.0f}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
                        df_simple.to_csv(filename, index=False)
                        print(f"✅ Tersimpan ke {filename}")
                else:
                    print(f"\n❌ Tidak ada saham dalam rentang Rp {harga_min:,.0f} - Rp {harga_max:,.0f}")
                
                input("\nTekan Enter untuk kembali ke menu...")
                
            except ValueError:
                print("❌ Input harus berupa angka")
        
        elif pilihan == '2':
            kode = input("Masukkan kode saham: ").upper()
            if kode in scanner.daftar_saham:
                scanner.detail_saham(kode)
            else:
                print("❌ Kode tidak ditemukan dalam daftar")
            input("\nTekan Enter...")
        
        elif pilihan == '3':
            kode = input("Masukkan kode saham: ").upper()
            if kode in scanner.daftar_saham:
                print(f"\n📡 MONITORING {kode} - Update setiap menit")
                print("Tekan Ctrl+C untuk berhenti")
                try:
                    for menit in range(5):
                        tape = scanner.get_order_book(kode)
                        if tape:
                            print(f"\n⏱️  Menit ke-{menit+1}:")
                            print(f"   Harga: Rp {tape['harga_terkini']:,.0f}")
                            print(f"   Volume: {tape['volume_ratio']:.1f}x")
                            print(f"   Score: {tape['tape_score']} - {tape['rekomendasi']}")
                            if tape['signals']:
                                print(f"   Signal: {tape['signals'][0]}")
                        time.sleep(60)
                except KeyboardInterrupt:
                    print("\n\nMonitoring dihentikan")
            else:
                print("❌ Kode tidak ditemukan")
            input("\nTekan Enter...")
        
        elif pilihan == '4':
            try:
                new_min = float(input("Default harga minimum baru: "))
                new_max = float(input("Default harga maksimum baru: "))
                scanner.HARGA_MIN = new_min
                scanner.HARGA_MAX = new_max
                print(f"✅ Default range diupdate: Rp {new_min:,.0f} - Rp {new_max:,.0f}")
            except:
                print("❌ Input tidak valid")
        
        elif pilihan == '5':
            print("\nTerima kasih! Happy tape reading! 🚀")
            break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProgram dihentikan user")
    except Exception as e:
        print(f"\nError: {e}")