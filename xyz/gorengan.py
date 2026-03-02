# File: saham_200_800.py
# Script khusus screening saham harga 200 - 800 rupiah

import requests
import pandas as pd
import numpy as np
from datetime import datetime
import time
import sys

class SahamHargaMurah:
    """
    Screener khusus saham harga 200 - 800 rupiah
    """
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # Hanya akan memproses saham dalam range ini
        self.HARGA_MIN = 200
        self.HARGA_MAX = 800
        
        # Dapatkan daftar semua saham BEI
        print("📋 Mengambil daftar saham BEI...")
        self.daftar_semua_saham = self.get_all_idx_stocks()
        print(f"✅ Total saham di BEI: {len(self.daftar_semua_saham)}")
    
    def get_all_idx_stocks(self):
        """
        Mendapatkan daftar semua saham BEI
        """
        try:
            # Coba ambil dari IDX
            url = "https://www.idx.co.id/umbraco/Surface/ListedCompany/GetCompanyProfiles?start=0&length=10000"
            response = requests.get(url, headers=self.headers, timeout=10)
            data = response.json()
            
            if 'data' in data:
                stocks = {}
                for item in data['data']:
                    kode = item.get('KodeEmitan', '').strip()
                    if kode and len(kode) <= 5:  # Filter kode valid
                        stocks[kode] = f"{kode}.JK"
                return stocks
            
        except Exception as e:
            print(f"⚠️ Gagal scraping IDX: {e}")
        
        # Backup list (saham-saham yang umum di harga 200-800)
        return self.get_backup_stocks()
    
    def get_backup_stocks(self):
        """
        Daftar backup saham-saham yang sering di harga 200-800
        """
        return {
            'ADRO': 'ADRO.JK', 'ANTM': 'ANTM.JK', 'BUMI': 'BUMI.JK',
            'CNKO': 'CNKO.JK', 'DEWA': 'DEWA.JK', 'ELSA': 'ELSA.JK',
            'ENRG': 'ENRG.JK', 'ERAA': 'ERAA.JK', 'FREN': 'FREN.JK',
            'GOLD': 'GOLD.JK', 'HRUM': 'HRUM.JK', 'INTA': 'INTA.JK',
            'ITMG': 'ITMG.JK', 'KIAS': 'KIAS.JK', 'KKGI': 'KKGI.JK',
            'LPKR': 'LPKR.JK', 'MAIN': 'MAIN.JK', 'MBAP': 'MBAP.JK',
            'MBSS': 'MBSS.JK', 'MDKA': 'MDKA.JK', 'MEDC': 'MEDC.JK',
            'MTEL': 'MTEL.JK', 'MYOH': 'MYOH.JK', 'PANS': 'PANS.JK',
            'PTBA': 'PTBA.JK', 'PWON': 'PWON.JK', 'SIDO': 'SIDO.JK',
            'SMDR': 'SMDR.JK', 'SRAJ': 'SRAJ.JK', 'SULI': 'SULI.JK',
            'TINS': 'TINS.JK', 'TOBA': 'TOBA.JK', 'UNTR': 'UNTR.JK',
            'WIKA': 'WIKA.JK', 'WSKT': 'WSKT.JK', 'ZINC': 'ZINC.JK',
            'BIPP': 'BIPP.JK', 'BOSS': 'BOSS.JK', 'CINT': 'CINT.JK',
            'DIGI': 'DIGI.JK', 'ENVY': 'ENVY.JK', 'FILM': 'FILM.JK',
            'GAMA': 'GAMA.JK', 'HADE': 'HADE.JK', 'INET': 'INET.JK',
            'JAVA': 'JAVA.JK', 'KBLV': 'KBLV.JK', 'LUCK': 'LUCK.JK',
            'MABA': 'MABA.JK', 'NUSA': 'NUSA.JK', 'OCAP': 'OCAP.JK',
            'PALM': 'PALM.JK', 'QORA': 'QORA.JK', 'RAJA': 'RAJA.JK',
            'SATU': 'SATU.JK', 'TAMA': 'TAMA.JK', 'UANG': 'UANG.JK',
            'VICI': 'VICI.JK', 'WGSH': 'WGSH.JK', 'YELO': 'YELO.JK',
            'ZBRA': 'ZBRA.JK'
        }
    
    def quick_check_price(self, kode):
        """
        Cek harga saham dengan cepat (hanya ambil data terbaru)
        """
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{kode}"
            params = {'range': '1d', 'interval': '1d'}  # Hanya 1 hari
            
            response = requests.get(url, headers=self.headers, params=params, timeout=5)
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            
            if 'chart' in data and 'result' in data['chart'] and data['chart']['result']:
                result = data['chart']['result'][0]
                quotes = result['indicators']['quote'][0]
                
                # Ambil harga terakhir
                if quotes['close'] and quotes['close'][-1] is not None:
                    harga = quotes['close'][-1]
                    volume = quotes['volume'][-1] if quotes['volume'] else 0
                    
                    # Cek apakah dalam range 200-800
                    if self.HARGA_MIN <= harga <= self.HARGA_MAX:
                        return {
                            'kode': kode.replace('.JK', ''),
                            'harga': harga,
                            'volume': volume,
                            'layak_analisis': True
                        }
                    else:
                        return {'layak_analisis': False}
            
            return None
            
        except Exception as e:
            return None
    
    def detailed_analysis(self, kode):
        """
        Analisis detail untuk saham yang sudah lolos filter harga
        """
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{kode}"
            params = {'range': '3mo', 'interval': '1d'}  # 3 bulan untuk analisis
            
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            data = response.json()
            
            if 'chart' in data and 'result' in data['chart'] and data['chart']['result']:
                result = data['chart']['result'][0]
                timestamps = result['timestamp']
                quotes = result['indicators']['quote'][0]
                
                # Kumpulkan data harga
                closes = []
                volumes = []
                for i in range(len(timestamps)):
                    if quotes['close'][i] is not None and quotes['volume'][i] is not None:
                        closes.append(quotes['close'][i])
                        volumes.append(quotes['volume'][i])
                
                if len(closes) < 20:
                    return None
                
                # Hitung indikator
                harga_terkini = closes[-1]
                harga_sebelum = closes[-2] if len(closes) > 1 else harga_terkini
                perubahan = ((harga_terkini - harga_sebelum) / harga_sebelum) * 100
                
                # RSI (14 hari)
                rsi = self.calculate_rsi(closes)
                
                # Moving Average
                ma20 = sum(closes[-20:]) / 20 if len(closes) >= 20 else harga_terkini
                ma50 = sum(closes[-50:]) / 50 if len(closes) >= 50 else harga_terkini
                
                # Volume
                volume_avg = sum(volumes[-20:]) / 20 if len(volumes) >= 20 else 1
                volume_terkini = volumes[-1]
                volume_ratio = volume_terkini / volume_avg if volume_avg > 0 else 1
                
                # Trend
                trend = "Uptrend" if harga_terkini > ma20 else "Downtrend"
                
                # Scoring
                score = 0
                
                # RSI score
                if rsi < 30:
                    score += 3  # Oversold - bagus untuk beli
                    rsi_status = "OVERSOLD 🔥"
                elif rsi < 40:
                    score += 2
                    rsi_status = "MENARIK 👍"
                elif rsi > 70:
                    score -= 2
                    rsi_status = "OVERBOUGHT ⚠️"
                elif rsi > 60:
                    score -= 1
                    rsi_status = "WASPADA 👀"
                else:
                    score += 1
                    rsi_status = "NETRAL ✨"
                
                # Volume score
                if volume_ratio > 2:
                    score += 2
                    volume_status = "VOLUME SPIKES 📊"
                elif volume_ratio > 1.5:
                    score += 1
                    volume_status = "VOLUME MENINGKAT 📈"
                else:
                    volume_status = "VOLUME NORMAL 📉"
                
                # Trend score
                if perubahan > 2:
                    score += 2
                    trend_status = "NAIK KUAT 🚀"
                elif perubahan > 0:
                    score += 1
                    trend_status = "NAIK 📈"
                elif perubahan > -2:
                    score -= 1
                    trend_status = "TURUN 📉"
                else:
                    score -= 2
                    trend_status = "TURUN KUAT 💥"
                
                # MA score
                if harga_terkini > ma20 and harga_terkini > ma50:
                    score += 2
                    ma_status = "DI ATAS MA20 & MA50 ✅"
                elif harga_terkini > ma20:
                    score += 1
                    ma_status = "DI ATAS MA20 ⬆️"
                else:
                    ma_status = "DI BAWAH MA20 ⬇️"
                
                return {
                    'kode': kode.replace('.JK', ''),
                    'harga': harga_terkini,
                    'perubahan': perubahan,
                    'rsi': rsi,
                    'rsi_status': rsi_status,
                    'volume_ratio': volume_ratio,
                    'volume_status': volume_status,
                    'trend': trend,
                    'trend_status': trend_status,
                    'ma_status': ma_status,
                    'score': score,
                    'rekomendasi': self.get_recommendation(score)
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
    
    def get_recommendation(self, score):
        """Dapatkan rekomendasi berdasarkan score"""
        if score >= 8:
            return "🔥🔥 STRONG BUY"
        elif score >= 6:
            return "✅✅ BUY"
        elif score >= 4:
            return "✅ WATCH"
        elif score >= 2:
            return "📊 HOLD"
        elif score >= 0:
            return "⚠️ CAUTION"
        else:
            return "❌ AVOID"
    
    def screen_stocks(self):
        """
        Screening saham harga 200-800
        """
        print("\n" + "="*80)
        print(f"🔍 SCREENING SAHAM HARGA Rp {self.HARGA_MIN} - Rp {self.HARGA_MAX}")
        print("="*80)
        
        # Tahap 1: Quick price check
        print("\n📡 Tahap 1: Quick price check (mencari saham dalam range harga)...")
        
        candidates = []
        total = len(self.daftar_semua_saham)
        
        for i, (kode, kode_lengkap) in enumerate(self.daftar_semua_saham.items(), 1):
            # Progress
            if i % 20 == 0 or i == total:
                print(f"\r   Progress: {i}/{total} | Ditemukan: {len(candidates)}", end='', flush=True)
            
            # Quick check
            result = self.quick_check_price(kode_lengkap)
            
            if result and result.get('layak_analisis'):
                candidates.append({
                    'kode': kode,
                    'kode_lengkap': kode_lengkap,
                    'harga': result['harga'],
                    'volume': result['volume']
                })
            
            # Delay kecil agar tidak kena block
            time.sleep(0.1)
        
        print(f"\n✅ Tahap 1 selesai! Ditemukan {len(candidates)} saham dalam range Rp {self.HARGA_MIN}-{self.HARGA_MAX}")
        
        if not candidates:
            print("\n❌ Tidak ada saham dalam rentang harga tersebut")
            return []
        
        # Tahap 2: Analisis detail
        print("\n📊 Tahap 2: Analisis teknikal detail...")
        
        results = []
        for i, cand in enumerate(candidates, 1):
            print(f"\r   Menganalisis {i}/{len(candidates)}: {cand['kode']}", end='', flush=True)
            
            analysis = self.detailed_analysis(cand['kode_lengkap'])
            if analysis:
                results.append(analysis)
            
            time.sleep(0.3)  # Delay untuk analisis detail
        
        print(f"\n✅ Tahap 2 selesai! {len(results)} saham berhasil dianalisis")
        
        return results
    
    def display_results(self, results):
        """
        Tampilkan hasil screening
        """
        if not results:
            return
        
        # Urutkan berdasarkan score
        results = sorted(results, key=lambda x: x['score'], reverse=True)
        
        print("\n" + "="*100)
        print(f"📊 HASIL SCREENING SAHAM HARGA Rp {self.HARGA_MIN} - Rp {self.HARGA_MAX}")
        print("="*100)
        
        # Header tabel
        print(f"{'No':<3} {'Kode':<6} {'Harga':>8} {'%Chg':>7} {'RSI':>6} {'Vol':>7} {'Score':>5} {'Rekomendasi'}")
        print("-"*100)
        
        for i, r in enumerate(results, 1):
            print(f"{i:<3} {r['kode']:<6} Rp {r['harga']:>6,.0f} {r['perubahan']:>6.1f}% {r['rsi']:>5.1f} {r['volume_ratio']:>6.1f}x {r['score']:>4}  {r['rekomendasi']}")
        
        print("="*100)
        
        # Detail untuk top 10
        print("\n🏆 TOP 10 REKOMENDASI TERBAIK:")
        print("-"*60)
        
        for i in range(min(10, len(results))):
            r = results[i]
            print(f"\n{i+1}. {r['kode']} - Rp {r['harga']:,.0f}")
            print(f"   ├─ RSI: {r['rsi']:.1f} - {r['rsi_status']}")
            print(f"   ├─ Volume: {r['volume_ratio']:.2f}x - {r['volume_status']}")
            print(f"   ├─ Pergerakan: {r['perubahan']:+.1f}% - {r['trend_status']}")
            print(f"   ├─ Trend: {r['trend']} - {r['ma_status']}")
            print(f"   └─ SCORE: {r['score']} - {r['rekomendasi']}")
        
        # Statistik
        print("\n" + "="*60)
        print("📈 STATISTIK HASIL SCREENING:")
        print(f"├─ Total saham dianalisis: {len(results)}")
        print(f"├─ Harga termurah: Rp {min(r['harga'] for r in results):,.0f}")
        print(f"├─ Harga termahal: Rp {max(r['harga'] for r in results):,.0f}")
        print(f"├─ Rata-rata RSI: {sum(r['rsi'] for r in results)/len(results):.1f}")
        print(f"└─ Rata-rata Score: {sum(r['score'] for r in results)/len(results):.1f}")
        
        return results

def main():
    print("="*80)
    print("   SCREENER KHUSUS SAHAM HARGA 200 - 800 RUPIAH")
    print("   (Optimasi request - hanya saham dalam range)")
    print("="*80)
    
    screener = SahamHargaMurah()
    
    while True:
        print("\n📌 MENU:")
        print("1. 🔍 Screening saham harga 200-800")
        print("2. 💾 Simpan hasil ke file")
        print("3. ❌ Keluar")
        
        pilihan = input("\nPilih menu (1-3): ").strip()
        
        if pilihan == '1':
            # Screening
            results = screener.screen_stocks()
            
            # Tampilkan hasil
            if results:
                screener.display_results(results)
                
                # Simpan otomatis
                save = input("\n💾 Simpan hasil ke file CSV? (y/n): ").lower()
                if save == 'y':
                    df = pd.DataFrame(results)
                    filename = f"screening_200_800_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
                    df.to_csv(filename, index=False)
                    print(f"✅ Tersimpan ke {filename}")
            
            input("\nTekan Enter untuk kembali ke menu...")
        
        elif pilihan == '2':
            print("\n📁 Menyimpan hasil terakhir...")
            # Implementasi save file
            pass
        
        elif pilihan == '3':
            print("\nTerima kasih! Happy investing! 🚀")
            break
        
        else:
            print("❌ Pilihan tidak valid")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProgram dihentikan oleh user")
    except Exception as e:
        print(f"\nError: {e}")