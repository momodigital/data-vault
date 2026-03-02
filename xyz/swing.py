# File: swing_trading_bsi.py
# Script Swing Trading untuk saham BSI dengan filter harga user

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import io
import os

class SwingTradingBSI:
    """
    Swing Trading Scanner untuk saham BSI
    - Mencari saham dalam tren naik (uptrend)
    - Deteksi pola teknikal teratur
    - Support/Resistance yang jelas
    - User bisa menentukan range harga
    """
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # Link CSV saham BSI Anda
        self.CSV_URL = "https://raw.githubusercontent.com/momodigital/data-vault/refs/heads/main/xyz/sahambsi.csv"
        
        # Load daftar saham
        self.daftar_saham = self.load_stocks_from_csv()
        
        # Default range harga
        self.HARGA_MIN = 200
        self.HARGA_MAX = 2000
        
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
    
    def get_stock_data(self, kode):
        """
        Ambil data historis untuk analisis swing trading
        """
        try:
            kode_lengkap = self.daftar_saham.get(kode, f"{kode}.JK")
            
            # Ambil data 3 bulan untuk analisis tren
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{kode_lengkap}"
            params = {'range': '3mo', 'interval': '1d'}  # Data harian
            
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            
            if 'chart' in data and 'result' in data['chart'] and data['chart']['result']:
                result = data['chart']['result'][0]
                timestamps = result['timestamp']
                quotes = result['indicators']['quote'][0]
                
                # Kumpulkan data harian
                dates = []
                closes = []
                highs = []
                lows = []
                volumes = []
                
                for i in range(len(timestamps)):
                    if (quotes['close'][i] is not None and 
                        quotes['high'][i] is not None and
                        quotes['low'][i] is not None and
                        quotes['volume'][i] is not None):
                        
                        dates.append(datetime.fromtimestamp(timestamps[i]))
                        closes.append(quotes['close'][i])
                        highs.append(quotes['high'][i])
                        lows.append(quotes['low'][i])
                        volumes.append(quotes['volume'][i])
                
                if len(closes) < 30:  # Butuh minimal 30 hari data
                    return None
                
                # Analisis Swing Trading
                swing_analysis = self.analyze_swing_trading(
                    kode, dates, closes, highs, lows, volumes
                )
                
                return swing_analysis
            
            return None
            
        except Exception as e:
            return None
    
    def analyze_swing_trading(self, kode, dates, closes, highs, lows, volumes):
        """
        Analisis lengkap untuk swing trading
        """
        # 1. Moving Averages untuk tren
        ma20 = self.calculate_ma(closes, 20)
        ma50 = self.calculate_ma(closes, 50)
        ma200 = self.calculate_ma(closes, 200) if len(closes) >= 200 else None
        
        # 2. Deteksi tren
        current_price = closes[-1]
        current_ma20 = ma20[-1] if ma20 else current_price
        current_ma50 = ma50[-1] if ma50 else current_price
        
        # Uptrend condition: harga di atas MA20 dan MA50
        uptrend = current_price > current_ma20 and current_price > current_ma50
        
        # 3. Support & Resistance dinamis
        lookback = 20
        recent_highs = highs[-lookback:]
        recent_lows = lows[-lookback:]
        
        resistance = max(recent_highs)
        support = min(recent_lows)
        
        # 4. Deteksi area support kuat (harga mendekati support)
        near_support = current_price <= support * 1.03  # 3% dari support
        
        # 5. RSI untuk overbought/oversold
        rsi = self.calculate_rsi(closes)
        
        # 6. Volume analysis
        avg_volume = np.mean(volumes[-20:])
        current_volume = volumes[-1]
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
        
        # 7. Pola candlestick (3 hari terakhir)
        last_3_closes = closes[-3:]
        last_3_highs = highs[-3:]
        last_3_lows = lows[-3:]
        
        # Deteksi bullish reversal pattern
        bullish_pattern = self.detect_bullish_pattern(last_3_closes, last_3_highs, last_3_lows)
        
        # 8. Scoring untuk Swing Trading
        swing_score = 0
        signals = []
        
        # Tren (bobot 40%)
        if uptrend:
            swing_score += 40
            signals.append("📈 UPTREND TERKONFIRMASI (+40)")
        else:
            swing_score -= 20
            signals.append("📉 DOWNTREND (-20)")
        
        # Support level (bobot 20%)
        if near_support and uptrend:
            swing_score += 20
            signals.append(f"💪 MENDEXAT SUPPORT KUAT Rp {support:,.0f} (+20)")
        elif near_support:
            swing_score += 10
            signals.append(f"⚡ MENDEXAT SUPPORT Rp {support:,.0f} (+10)")
        
        # RSI (bobot 15%)
        if 40 <= rsi <= 60:
            swing_score += 15
            signals.append(f"📊 RSI NETRAL {rsi:.1f} (+15)")
        elif 30 <= rsi < 40:
            swing_score += 10
            signals.append(f"🟢 RSI MENARIK {rsi:.1f} (+10)")
        elif rsi < 30:
            swing_score += 5
            signals.append(f"🔵 RSI OVERSOLD {rsi:.1f} (+5)")
        elif rsi > 70:
            swing_score -= 10
            signals.append(f"🔴 RSI OVERBOUGHT {rsi:.1f} (-10)")
        
        # Volume (bobot 15%)
        if volume_ratio > 1.5 and uptrend:
            swing_score += 15
            signals.append(f"🚀 VOLUME KONFIRMASI {volume_ratio:.1f}x (+15)")
        elif volume_ratio > 1.2:
            swing_score += 10
            signals.append(f"📊 VOLUME MENINGKAT {volume_ratio:.1f}x (+10)")
        
        # Pattern (bobot 10%)
        if bullish_pattern:
            swing_score += 10
            signals.append(f"🎯 BULLISH PATTERN TERDETEKSI (+10)")
        
        # 9. Target Price (untuk swing)
        swing_target = resistance * 1.05  # Target 5% di atas resistance
        stop_loss = support * 0.97  # Stop loss 3% di bawah support
        
        # 10. Risk/Reward Ratio
        risk = current_price - stop_loss
        reward = swing_target - current_price
        risk_reward = reward / risk if risk > 0 else 0
        
        return {
            'kode': kode,
            'harga': current_price,
            'ma20': current_ma20,
            'ma50': current_ma50,
            'support': support,
            'resistance': resistance,
            'rsi': rsi,
            'volume_ratio': volume_ratio,
            'uptrend': uptrend,
            'near_support': near_support,
            'bullish_pattern': bullish_pattern,
            'swing_target': swing_target,
            'stop_loss': stop_loss,
            'risk_reward': risk_reward,
            'swing_score': swing_score,
            'signals': signals,
            'rekomendasi': self.get_swing_recommendation(swing_score, uptrend, near_support, risk_reward)
        }
    
    def calculate_ma(self, prices, period):
        """Hitung Moving Average"""
        if len(prices) < period:
            return [prices[-1]] * len(prices)
        
        mas = []
        for i in range(len(prices)):
            if i < period - 1:
                mas.append(prices[i])
            else:
                ma = sum(prices[i-period+1:i+1]) / period
                mas.append(ma)
        return mas
    
    def calculate_rsi(self, prices, period=14):
        """Hitung RSI"""
        if len(prices) < period + 1:
            return 50
        
        gains = []
        losses = []
        
        for i in range(len(prices)-period, len(prices)-1):
            diff = prices[i+1] - prices[i]
            if diff > 0:
                gains.append(diff)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(diff))
        
        avg_gain = np.mean(gains)
        avg_loss = np.mean(losses)
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))
    
    def detect_bullish_pattern(self, closes, highs, lows):
        """
        Deteksi bullish reversal pattern:
        - Hammer
        - Bullish Engulfing
        - Morning Star
        """
        if len(closes) < 3:
            return False
        
        # Simple pattern: higher low + higher high
        if closes[-1] > closes[-2] and closes[-2] > closes[-3]:
            return True
        
        # Bullish engulfing
        if (closes[-2] < opens[-2] and  # Candlestick sebelumnya merah
            closes[-1] > highs[-2] and   # Candlestick sekarang menutup di atas high sebelumnya
            closes[-1] > opens[-1]):      # Candlestick sekarang hijau
            return True
        
        return False
    
    def get_swing_recommendation(self, score, uptrend, near_support, risk_reward):
        """Rekomendasi untuk swing trading"""
        if score >= 70 and uptrend and near_support:
            return "🔥 SWING BUY (TREN KUAT + SUPPORT)"
        elif score >= 60 and uptrend:
            return "✅ SWING BUY (TREN NAIK)"
        elif score >= 50:
            return "👀 WATCH (POTENSI SWING)"
        elif score >= 30:
            return "📊 HOLD (TUNGGU KONFIRMASI)"
        elif score >= 15:
            return "⚠️ CAUTION (BELUM IDEAL)"
        else:
            return "❌ AVOID (TREN TURUN)"
    
    def scan_swing_trading(self, harga_min, harga_max):
        """
        Scan semua saham dengan filter harga untuk swing trading
        """
        print("\n" + "="*100)
        print(f"🎯 SWING TRADING SCANNER")
        print(f"💰 RENTANG HARGA: Rp {harga_min:,.0f} - Rp {harga_max:,.0f}")
        print("="*100)
        
        results = []
        total = len(self.daftar_saham)
        
        print(f"\n⏳ Menganalisis {total} saham untuk swing trading...")
        
        for i, (kode, _) in enumerate(self.daftar_saham.items(), 1):
            # Progress
            progress = (i / total) * 100
            bar = '█' * int(progress/2) + '░' * (50 - int(progress/2))
            print(f"\r[{bar}] {i}/{total} ({progress:.1f}%) - {kode}", end='', flush=True)
            
            swing_data = self.get_stock_data(kode)
            
            if swing_data:
                # FILTER HARGA SESUAI INPUT USER
                if harga_min <= swing_data['harga'] <= harga_max:
                    results.append(swing_data)
            
            time.sleep(0.1)
        
        print(f"\n✅ Selesai! Ditemukan {len(results)} saham dalam rentang Rp {harga_min:,.0f} - Rp {harga_max:,.0f}")
        
        return results
    
    def display_swing_results(self, results):
        """
        Tampilkan hasil swing trading
        """
        if not results:
            print("❌ Tidak ada saham dalam range harga")
            return
        
        # Urutkan berdasarkan swing score
        results = sorted(results, key=lambda x: x['swing_score'], reverse=True)
        
        print("\n" + "="*130)
        print("📊 HASIL SWING TRADING - URUTAN TERBAIK")
        print("="*130)
        
        # Header
        print(f"{'No':<3} {'Kode':<6} {'Harga':>8} {'MA20':>8} {'MA50':>8} {'RSI':>6} {'Vol':>6} {'S/R':>12} {'Score':>6} {'Rekomendasi'}")
        print("-"*130)
        
        for i, r in enumerate(results[:50], 1):  # Top 50
            # Simbol tren
            trend_symbol = "📈" if r['uptrend'] else "📉"
            
            sr_info = f"{r['support']:.0f}/{r['resistance']:.0f}"
            
            print(f"{i:<3} {r['kode']:<6} Rp {r['harga']:>6,.0f} {r['ma20']:>6,.0f} {r['ma50']:>6,.0f} {r['rsi']:>5.1f} {r['volume_ratio']:>5.1f}x {sr_info:>12} {r['swing_score']:>5}  {trend_symbol} {r['rekomendasi']}")
        
        print("="*130)
        
        # Statistik
        swing_buy = sum(1 for r in results if 'SWING BUY' in r['rekomendasi'])
        watch = sum(1 for r in results if 'WATCH' in r['rekomendasi'])
        hold = sum(1 for r in results if 'HOLD' in r['rekomendasi'])
        caution = sum(1 for r in results if 'CAUTION' in r['rekomendasi'])
        avoid = sum(1 for r in results if 'AVOID' in r['rekomendasi'])
        
        print(f"\n📈 RINGKASAN SWING TRADING:")
        print(f"├─ 🔥 SWING BUY: {swing_buy}")
        print(f"├─ 👀 WATCH: {watch}")
        print(f"├─ 📊 HOLD: {hold}")
        print(f"├─ ⚠️ CAUTION: {caution}")
        print(f"└─ ❌ AVOID: {avoid}")
        
        # TOP 10 SWING CANDIDATES
        print("\n🏆 TOP 10 SWING TRADING CANDIDATES:")
        print("-"*80)
        
        for i, r in enumerate(results[:10], 1):
            print(f"\n{i}. {r['kode']} - Rp {r['harga']:,.0f} [Score: {r['swing_score']}]")
            print(f"   ├─ Trend: {'UPTREND' if r['uptrend'] else 'DOWNTREND'}")
            print(f"   ├─ Support: Rp {r['support']:,.0f} | Resistance: Rp {r['resistance']:,.0f}")
            print(f"   ├─ MA20: Rp {r['ma20']:,.0f} | MA50: Rp {r['ma50']:,.0f}")
            print(f"   ├─ RSI: {r['rsi']:.1f} | Volume: {r['volume_ratio']:.1f}x")
            print(f"   ├─ Target Swing: Rp {r['swing_target']:,.0f}")
            print(f"   ├─ Stop Loss: Rp {r['stop_loss']:,.0f}")
            print(f"   ├─ Risk/Reward: 1:{r['risk_reward']:.2f}")
            print(f"   ├─ {r['rekomendasi']}")
            if r['signals']:
                print(f"   └─ Signals: {', '.join(r['signals'][:2])}")
    
    def detail_swing(self, kode):
        """Lihat detail swing trading satu saham"""
        print(f"\n📊 DETAIL SWING TRADING: {kode}")
        print("="*60)
        
        swing_data = self.get_stock_data(kode)
        
        if not swing_data:
            print("❌ Tidak dapat mengambil data")
            return
        
        print(f"Harga Terkini  : Rp {swing_data['harga']:,.0f}")
        print(f"MA20           : Rp {swing_data['ma20']:,.0f}")
        print(f"MA50           : Rp {swing_data['ma50']:,.0f}")
        print(f"Support        : Rp {swing_data['support']:,.0f}")
        print(f"Resistance     : Rp {swing_data['resistance']:,.0f}")
        print(f"RSI (14)       : {swing_data['rsi']:.1f}")
        print(f"Volume Ratio   : {swing_data['volume_ratio']:.2f}x")
        print(f"Trend          : {'UPTREND' if swing_data['uptrend'] else 'DOWNTREND'}")
        print(f"Near Support   : {'Ya' if swing_data['near_support'] else 'Tidak'}")
        print(f"Bullish Pattern: {'Ya' if swing_data['bullish_pattern'] else 'Tidak'}")
        print(f"\n🎯 TARGET SWING : Rp {swing_data['swing_target']:,.0f}")
        print(f"🛑 STOP LOSS    : Rp {swing_data['stop_loss']:,.0f}")
        print(f"📈 Risk/Reward  : 1:{swing_data['risk_reward']:.2f}")
        print(f"\n💡 SWING SCORE   : {swing_data['swing_score']}")
        print(f"💬 REKOMENDASI  : {swing_data['rekomendasi']}")
        
        if swing_data['signals']:
            print("\nSinyal Terdeteksi:")
            for s in swing_data['signals']:
                print(f"  • {s}")

def main():
    # Bersihkan layar
    os.system('clear' if os.name == 'posix' else 'cls')
    
    print("="*100)
    print("   SWING TRADING SCANNER - DENGAN FILTER HARGA USER")
    print("   Mencari Saham dengan Tren Jelas & Pola Teknikal Teratur")
    print("   Khusus Saham BSI dari CSV Anda")
    print("="*100)
    
    scanner = SwingTradingBSI()
    
    while True:
        print("\n📌 MENU SWING TRADING:")
        print("1. 🎯 Scan berdasarkan RENTANG HARGA (input user)")
        print("2. 🔍 Detail swing trading satu saham")
        print("3. 📈 Top 20 Swing Candidates")
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
                
                # Scan dengan filter harga
                results = scanner.scan_swing_trading(harga_min, harga_max)
                
                if results:
                    scanner.display_swing_results(results)
                    
                    # Opsi simpan hasil
                    save = input("\n💾 Simpan hasil ke CSV? (y/n): ").lower()
                    if save == 'y':
                        df_simple = pd.DataFrame([{
                            'kode': r['kode'],
                            'harga': r['harga'],
                            'support': r['support'],
                            'resistance': r['resistance'],
                            'ma20': r['ma20'],
                            'ma50': r['ma50'],
                            'rsi': r['rsi'],
                            'volume_ratio': r['volume_ratio'],
                            'uptrend': r['uptrend'],
                            'swing_score': r['swing_score'],
                            'target': r['swing_target'],
                            'stop_loss': r['stop_loss'],
                            'risk_reward': r['risk_reward'],
                            'rekomendasi': r['rekomendasi']
                        } for r in results])
                        
                        filename = f"swing_trading_{harga_min:.0f}_{harga_max:.0f}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
                        df_simple.to_csv(filename, index=False)
                        print(f"✅ Tersimpan ke {filename}")
                
                input("\nTekan Enter untuk kembali ke menu...")
                
            except ValueError:
                print("❌ Input harus berupa angka")
        
        elif pilihan == '2':
            kode = input("Masukkan kode saham: ").upper()
            if kode in scanner.daftar_saham:
                scanner.detail_swing(kode)
            else:
                print("❌ Kode tidak ditemukan dalam daftar")
            input("\nTekan Enter...")
        
        elif pilihan == '3':
            print("\n🏆 TOP 20 SWING CANDIDATES (SEMUA HARGA)")
            results = scanner.scan_swing_trading(0, 1000000)  # Scan semua harga
            if results:
                # Ambil top 20
                top20 = sorted(results, key=lambda x: x['swing_score'], reverse=True)[:20]
                scanner.display_swing_results(top20)
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
            print("\nTerima kasih! Happy swing trading! 🚀")
            break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProgram dihentikan user")
    except Exception as e:
        print(f"\nError: {e}")