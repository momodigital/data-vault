# File: saham_dari_csv_anda.py
# Script dengan link CSV: https://raw.githubusercontent.com/momodigital/data-vault/refs/heads/main/xyz/sahambsi.csv

import requests
import pandas as pd
import numpy as np
from datetime import datetime
import time
import io

class SahamDariCSVAnda:
    """
    Screener saham - Menggunakan CSV dari GitHub Anda
    """
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        self.HARGA_MIN = 200
        self.HARGA_MAX = 800
        
        # ========== LINK CSV ANDA ==========
        self.CSV_URL = "https://raw.githubusercontent.com/momodigital/data-vault/refs/heads/main/xyz/sahambsi.csv"
        # ===================================
        
        # Load daftar saham dari CSV
        self.daftar_saham = self.load_stocks_from_csv()
        
        # Inisialisasi foreign data (bisa diisi nanti)
        self.foreign_data = {}
        
        print(f"\n📋 Total saham dari CSV Anda: {len(self.daftar_saham)}")
        print(f"🔗 Sumber: {self.CSV_URL}")
    
    def load_stocks_from_csv(self):
        """
        Load daftar saham dari CSV GitHub Anda
        CSV hanya berisi kolom 'kode' dengan daftar saham
        """
        print(f"\n📡 Mengambil daftar saham dari GitHub...")
        
        try:
            response = requests.get(self.CSV_URL, timeout=10)
            
            if response.status_code == 200:
                # Baca CSV
                df = pd.read_csv(io.StringIO(response.text))
                print(f"✅ CSV loaded! Columns: {list(df.columns)}")
                print(f"📊 Total data: {len(df)} baris")
                print(f"📝 5 data pertama:\n{df.head()}")
                
                stocks = {}
                
                # CSV Anda hanya punya kolom 'kode'
                if 'kode' in df.columns:
                    for _, row in df.iterrows():
                        kode = str(row['kode']).strip().upper()
                        if kode and pd.notna(kode):
                            stocks[kode] = f"{kode}.JK"
                    
                    print(f"✅ Berhasil memuat {len(stocks)} kode saham")
                    return stocks
                else:
                    # Fallback: coba kolom pertama
                    kolom_pertama = df.columns[0]
                    for _, row in df.iterrows():
                        kode = str(row[kolom_pertama]).strip().upper()
                        if kode and pd.notna(kode):
                            stocks[kode] = f"{kode}.JK"
                    
                    print(f"✅ Menggunakan kolom '{kolom_pertama}' - {len(stocks)} saham")
                    return stocks
            
            else:
                print(f"❌ Gagal load CSV: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error load CSV: {e}")
        
        # Fallback ke beberapa sampel
        print("⚠️ Menggunakan daftar sampel kecil")
        return {
            'ADRO': 'ADRO.JK', 'ANTM': 'ANTM.JK', 'BBCA': 'BBCA.JK',
        }
    
    def update_foreign_data(self, kode, buy, sell):
        """Update data foreign manual"""
        self.foreign_data[kode] = {
            'buy': buy,
            'sell': sell,
            'net': buy - sell
        }
        print(f"✅ Foreign data {kode} updated: Net Rp {(buy-sell)/1e9:.1f}M")
    
    def get_stock_data(self, kode):
        """
        Ambil data saham dari Yahoo Finance untuk analisis
        """
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{kode}"
            params = {'range': '3mo', 'interval': '1d'}
            
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            
            if 'chart' in data and 'result' in data['chart'] and data['chart']['result']:
                result = data['chart']['result'][0]
                timestamps = result['timestamp']
                quotes = result['indicators']['quote'][0]
                
                # Kumpulkan data harga
                closes = []
                volumes = []
                for i in range(len(timestamps)):
                    if quotes['close'][i] is not None:
                        closes.append(quotes['close'][i])
                        volumes.append(quotes['volume'][i] if quotes['volume'][i] else 0)
                
                if len(closes) < 20:
                    return None
                
                # Data terkini
                harga = closes[-1]
                harga_sebelum = closes[-2] if len(closes) > 1 else harga
                perubahan = ((harga - harga_sebelum) / harga_sebelum) * 100
                
                # RSI
                rsi = self.calculate_rsi(closes)
                
                # Volume
                vol_avg = sum(volumes[-20:]) / 20
                vol_now = volumes[-1]
                vol_ratio = vol_now / vol_avg if vol_avg > 0 else 1
                
                # MA
                ma20 = sum(closes[-20:]) / 20
                
                return {
                    'harga': harga,
                    'perubahan': perubahan,
                    'rsi': rsi,
                    'vol_ratio': vol_ratio,
                    'ma20': ma20,
                    'trend': 'Uptrend' if harga > ma20 else 'Downtrend'
                }
            
            return None
            
        except Exception as e:
            return None
    
    def calculate_rsi(self, prices):
        """Hitung RSI"""
        if len(prices) < 15:
            return 50
        
        gains = []
        losses = []
        
        for i in range(1, 15):
            diff = prices[-i] - prices[-i-1]
            if diff > 0:
                gains.append(diff)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(diff))
        
        avg_gain = sum(gains) / 14
        avg_loss = sum(losses) / 14
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))
    
    def calculate_score(self, data_teknikal, foreign=None):
        """
        Hitung score berdasarkan teknikal + foreign
        """
        score = 0
        signals = []
        
        if not data_teknikal:
            return 0, []
        
        # ========== TEKNIKAL SCORING ==========
        
        # 1. RSI Score (40%)
        if data_teknikal['rsi'] < 30:
            score += 40
            signals.append(f"RSI OVERSOLD ({data_teknikal['rsi']:.1f}) +40")
        elif data_teknikal['rsi'] < 40:
            score += 30
            signals.append(f"RSI MENARIK ({data_teknikal['rsi']:.1f}) +30")
        elif data_teknikal['rsi'] < 50:
            score += 20
            signals.append(f"RSI NETRAL ({data_teknikal['rsi']:.1f}) +20")
        elif data_teknikal['rsi'] > 70:
            score -= 30
            signals.append(f"RSI OVERBOUGHT ({data_teknikal['rsi']:.1f}) -30")
        elif data_teknikal['rsi'] > 60:
            score -= 10
            signals.append(f"RSI WASPADA ({data_teknikal['rsi']:.1f}) -10")
        
        # 2. Volume Score (30%)
        if data_teknikal['vol_ratio'] > 2:
            score += 30
            signals.append(f"VOLUME SPIKES ({data_teknikal['vol_ratio']:.1f}x) +30")
        elif data_teknikal['vol_ratio'] > 1.5:
            score += 20
            signals.append(f"VOLUME MENINGKAT ({data_teknikal['vol_ratio']:.1f}x) +20")
        elif data_teknikal['vol_ratio'] > 1:
            score += 10
            signals.append(f"VOLUME NORMAL ({data_teknikal['vol_ratio']:.1f}x) +10")
        else:
            score -= 10
            signals.append(f"VOLUME TURUN ({data_teknikal['vol_ratio']:.1f}x) -10")
        
        # 3. Trend Score (30%)
        if data_teknikal['perubahan'] > 3:
            score += 30
            signals.append(f"TREND NAIK KUAT ({data_teknikal['perubahan']:+.1f}%) +30")
        elif data_teknikal['perubahan'] > 1:
            score += 20
            signals.append(f"TREND NAIK ({data_teknikal['perubahan']:+.1f}%) +20")
        elif data_teknikal['perubahan'] > 0:
            score += 10
            signals.append(f"TREND MULAI NAIK ({data_teknikal['perubahan']:+.1f}%) +10")
        elif data_teknikal['perubahan'] > -2:
            score -= 10
            signals.append(f"TREND TURUN ({data_teknikal['perubahan']:.1f}%) -10")
        else:
            score -= 20
            signals.append(f"TREND TURUN KUAT ({data_teknikal['perubahan']:.1f}%) -20")
        
        # ========== FOREIGN SCORING (BONUS) ==========
        if foreign:
            if foreign['net'] > 100_000_000_000:
                score += 30
                signals.append(f"FOREIGN NET BUY BESAR Rp {foreign['net']/1e9:.1f}M +30")
            elif foreign['net'] > 50_000_000_000:
                score += 20
                signals.append(f"FOREIGN NET BUY Rp {foreign['net']/1e9:.1f}M +20")
            elif foreign['net'] > 10_000_000_000:
                score += 10
                signals.append(f"FOREIGN NET BUY Rp {foreign['net']/1e9:.1f}M +10")
            elif foreign['net'] < -50_000_000_000:
                score -= 20
                signals.append(f"FOREIGN NET SELL BESAR Rp {abs(foreign['net'])/1e9:.1f}M -20")
            elif foreign['net'] < 0:
                score -= 10
                signals.append(f"FOREIGN NET SELL Rp {abs(foreign['net'])/1e9:.1f}M -10")
        
        return score, signals
    
    def get_recommendation(self, score):
        """Konversi score ke rekomendasi"""
        if score >= 80:
            return "🔥🔥 STRONG BUY", "BELI BESAR (Teknikal Super)"
        elif score >= 60:
            return "✅✅ BUY", "BELI (Teknikal Bagus)"
        elif score >= 40:
            return "✅ WATCH", "PANTAU (Berpotensi)"
        elif score >= 20:
            return "📊 HOLD", "Tahan (Belum Waktunya)"
        elif score >= 0:
            return "⚠️ CAUTION", "Hati-hati (Teknikal Melemah)"
        else:
            return "❌ AVOID", "Hindari (Teknikal Buruk)"
    
    def analyze_all_stocks(self):
        """
        Analisis semua saham dari CSV Anda
        """
        print("\n" + "="*100)
        print(f"🔍 ANALISIS {len(self.daftar_saham)} SAHAM DARI CSV ANDA")
        print(f"📊 Rentang Harga: Rp {self.HARGA_MIN} - Rp {self.HARGA_MAX}")
        print("="*100)
        
        results = []
        total = len(self.daftar_saham)
        
        for i, (kode, kode_lengkap) in enumerate(self.daftar_saham.items(), 1):
            # Progress
            print(f"\r⏳ Progress: {i}/{total} | Ditemukan: {len(results)}", end='', flush=True)
            
            try:
                # Quick price check
                url_check = f"https://query1.finance.yahoo.com/v8/finance/chart/{kode_lengkap}"
                params = {'range': '1d', 'interval': '1d'}
                response = requests.get(url_check, headers=self.headers, params=params, timeout=3)
                
                if response.status_code != 200:
                    continue
                
                data = response.json()
                if not data['chart']['result']:
                    continue
                
                quotes = data['chart']['result'][0]['indicators']['quote'][0]
                if not quotes['close'] or quotes['close'][-1] is None:
                    continue
                
                harga = quotes['close'][-1]
                
                # Filter harga 200-800
                if harga < self.HARGA_MIN or harga > self.HARGA_MAX:
                    continue
                
                # Ambil data teknikal
                data_teknikal = self.get_stock_data(kode_lengkap)
                if not data_teknikal:
                    continue
                
                # Data foreign (jika ada)
                foreign = self.foreign_data.get(kode, None)
                
                # Hitung score
                score, signals = self.calculate_score(data_teknikal, foreign)
                rekom, alasan = self.get_recommendation(score)
                
                results.append({
                    'kode': kode,
                    'harga': harga,
                    'perubahan': data_teknikal['perubahan'],
                    'rsi': data_teknikal['rsi'],
                    'volume_ratio': data_teknikal['vol_ratio'],
                    'trend': data_teknikal['trend'],
                    'score': score,
                    'rekomendasi': rekom,
                    'alasan': alasan,
                    'signals': ' | '.join(signals[:3])
                })
                
                time.sleep(0.05)  # Delay kecil
                
            except Exception:
                continue
        
        print(f"\n✅ Selesai! Ditemukan {len(results)} saham dalam range Rp {self.HARGA_MIN}-{self.HARGA_MAX}")
        
        return results
    
    def display_results(self, results):
        """
        Tampilkan hasil dengan rekomendasi
        """
        if not results:
            print("\n❌ Tidak ada saham dalam range harga")
            return
        
        # Urutkan berdasarkan score
        results = sorted(results, key=lambda x: x['score'], reverse=True)
        
        print("\n" + "="*120)
        print(f"📊 HASIL ANALISIS - REKOMENDASI BELI (Tertinggi ke Terendah)")
        print("="*120)
        
        # Header
        print(f"{'No':<3} {'Kode':<6} {'Harga':>8} {'%Chg':>7} {'RSI':>6} {'Vol':>6} {'Score':>6} {'Rekomendasi'}")
        print("-"*120)
        
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
            else:
                marker = "❌"
            
            print(f"{i:<3} {r['kode']:<6} Rp {r['harga']:>6,.0f} {r['perubahan']:>6.1f}% {r['rsi']:>5.1f} {r['volume_ratio']:>5.1f}x {r['score']:>5}  {marker} {r['rekomendasi']}")
        
        print("="*120)
        
        # Statistik
        print(f"\n📈 RINGKASAN DARI {len(results)} SAHAM:")
        strong_buy = sum(1 for r in results if 'STRONG BUY' in r['rekomendasi'])
        buy = sum(1 for r in results if 'BUY' in r['rekomendasi'] and 'STRONG' not in r['rekomendasi'])
        watch = sum(1 for r in results if 'WATCH' in r['rekomendasi'])
        hold = sum(1 for r in results if 'HOLD' in r['rekomendasi'])
        caution = sum(1 for r in results if 'CAUTION' in r['rekomendasi'])
        avoid = sum(1 for r in results if 'AVOID' in r['rekomendasi'])
        
        print(f"├─ 🔥 STRONG BUY: {strong_buy}")
        print(f"├─ ✅ BUY: {buy}")
        print(f"├─ 👀 WATCH: {watch}")
        print(f"├─ 📊 HOLD: {hold}")
        print(f"├─ ⚠️ CAUTION: {caution}")
        print(f"└─ ❌ AVOID: {avoid}")
        
        # TOP 10 REKOMENDASI
        print("\n🏆 TOP 10 REKOMENDASI BELI TERBAIK:")
        print("-"*60)
        
        for i in range(min(10, len(results))):
            r = results[i]
            print(f"\n{i+1}. {r['kode']} - Rp {r['harga']:,.0f} [SCORE: {r['score']}]")
            print(f"   ├─ {r['rekomendasi']}: {r['alasan']}")
            print(f"   ├─ RSI: {r['rsi']:.1f} | Volume: {r['volume_ratio']:.1f}x | Perubahan: {r['perubahan']:+.1f}%")
            print(f"   └─ Signals: {r['signals']}")
        
        return results

def main():
    print("="*100)
    print("   ANALISIS SAHAM DARI CSV ANDA")
    print("   Sumber: https://raw.githubusercontent.com/momodigital/data-vault/refs/heads/main/xyz/sahambsi.csv")
    print("="*100)
    
    screener = SahamDariCSVAnda()
    
    while True:
        print("\n📌 MENU:")
        print("1. 🔍 Analisis semua saham (filter harga 200-800)")
        print("2. ⚙️ Ubah range harga")
        print("3. ✏️ Input data foreign manual (opsional)")
        print("4. 💾 Simpan hasil ke CSV")
        print("5. ❌ Keluar")
        
        pilihan = input("\nPilih menu: ").strip()
        
        if pilihan == '1':
            results = screener.analyze_all_stocks()
            if results:
                screener.display_results(results)
            input("\nTekan Enter...")
        
        elif pilihan == '2':
            try:
                min_h = float(input("Harga minimum (contoh: 200): "))
                max_h = float(input("Harga maksimum (contoh: 800): "))
                screener.HARGA_MIN = min_h
                screener.HARGA_MAX = max_h
                print(f"✅ Range harga diupdate: Rp {min_h:,.0f} - Rp {max_h:,.0f}")
            except:
                print("❌ Input tidak valid")
        
        elif pilihan == '3':
            print("\n✏️ INPUT DATA FOREIGN (Opsional)")
            kode = input("Kode saham: ").upper()
            try:
                buy = float(input("Foreign Buy (Rp): ").replace('.', ''))
                sell = float(input("Foreign Sell (Rp): ").replace('.', ''))
                screener.update_foreign_data(kode, buy, sell)
            except:
                print("❌ Input tidak valid")
        
        elif pilihan == '4':
            if hasattr(screener, 'last_results') and screener.last_results:
                df = pd.DataFrame(screener.last_results)
                filename = f"hasil_analisis_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
                df.to_csv(filename, index=False)
                print(f"✅ Tersimpan ke {filename}")
            else:
                print("❌ Belum ada hasil analisis. Jalankan menu 1 dulu.")
        
        elif pilihan == '5':
            break

if __name__ == "__main__":
    screener = SahamDariCSVAnda()
    screener.last_results = None
    
    while True:
        print("\n📌 MENU:")
        print("1. 🔍 Analisis semua saham (filter harga 200-800)")
        print("2. ⚙️ Ubah range harga")
        print("3. ✏️ Input data foreign manual (opsional)")
        print("4. 💾 Simpan hasil ke CSV")
        print("5. ❌ Keluar")
        
        pilihan = input("\nPilih menu: ").strip()
        
        if pilihan == '1':
            results = screener.analyze_all_stocks()
            if results:
                screener.last_results = results
                screener.display_results(results)
            input("\nTekan Enter...")
        
        elif pilihan == '2':
            try:
                min_h = float(input("Harga minimum (contoh: 200): "))
                max_h = float(input("Harga maksimum (contoh: 800): "))
                screener.HARGA_MIN = min_h
                screener.HARGA_MAX = max_h
                print(f"✅ Range harga diupdate: Rp {min_h:,.0f} - Rp {max_h:,.0f}")
            except:
                print("❌ Input tidak valid")
        
        elif pilihan == '3':
            print("\n✏️ INPUT DATA FOREIGN (Opsional)")
            kode = input("Kode saham: ").upper()
            try:
                buy = float(input("Foreign Buy (Rp): ").replace('.', ''))
                sell = float(input("Foreign Sell (Rp): ").replace('.', ''))
                screener.update_foreign_data(kode, buy, sell)
            except:
                print("❌ Input tidak valid")
        
        elif pilihan == '4':
            if screener.last_results:
                df = pd.DataFrame(screener.last_results)
                filename = f"hasil_analisis_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
                df.to_csv(filename, index=False)
                print(f"✅ Tersimpan ke {filename}")
            else:
                print("❌ Belum ada hasil analisis. Jalankan menu 1 dulu.")
            input("\nTekan Enter...")
        
        elif pilihan == '5':
            print("\nTerima kasih! Happy investing! 🚀")
            break