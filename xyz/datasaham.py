import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import seaborn as sns
import akshare as ak
import warnings
warnings.filterwarnings('ignore')

class StockbitAnalyticsWithAKShare:
    def __init__(self):
        # Daftar saham LQ45 dengan kode yang benar untuk AKShare
        self.sahams = {
            'BBCA': 'BBCA.JK',  # Bank Central Asia
            'BBRI': 'BBRI.JK',  # Bank Rakyat Indonesia
            'BMRI': 'BMRI.JK',  # Bank Mandiri
            'TLKM': 'TLKM.JK',  # Telkom Indonesia
            'ASII': 'ASII.JK',  # Astra International
            'UNVR': 'UNVR.JK',  # Unilever Indonesia
            'GGRM': 'GGRM.JK',  # Gudang Garam
            'ICBP': 'ICBP.JK',  # Indofood CBP
            'INDF': 'INDF.JK',  # Indofood Sukses Makmur
            'KLBF': 'KLBF.JK'   # Kalbe Farma
        }
        
    def get_real_stock_data(self, symbol, start_date=None, end_date=None):
        """
        Mengambil data saham real dari AKShare
        """
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
        if end_date is None:
            end_date = datetime.now().strftime('%Y%m%d')
        
        try:
            # Ambil data historis dari AKShare
            df = ak.stock_zh_a_hist(symbol=symbol, 
                                     start_date=start_date, 
                                     end_date=end_date,
                                     adjust="qfq")  # qfq = forward adjusted
            return df
        except Exception as e:
            print(f"Error mengambil data {symbol}: {e}")
            return None
    
    def get_multiple_stocks_data(self, period='1y'):
        """
        Mengambil data multiple saham
        """
        end_date = datetime.now()
        if period == '1y':
            start_date = end_date - timedelta(days=365)
        elif period == '6m':
            start_date = end_date - timedelta(days=180)
        elif period == '3m':
            start_date = end_date - timedelta(days=90)
        else:
            start_date = end_date - timedelta(days=365)
        
        start_str = start_date.strftime('%Y%m%d')
        end_str = end_date.strftime('%Y%m%d')
        
        all_data = {}
        for name, code in self.sahams.items():
            print(f"Mengambil data {name}...")
            df = self.get_real_stock_data(code, start_str, end_str)
            if df is not None and not df.empty:
                all_data[name] = df
        
        return all_data
    
    def calculate_returns(self, stock_data):
        """
        Menghitung return dari data real
        """
        returns = {}
        for name, df in stock_data.items():
            if df is not None and len(df) > 0:
                # Ambil harga pertama dan terakhir
                first_price = float(df['收盘'].iloc[0])  # Harga penutupan pertama
                last_price = float(df['收盘'].iloc[-1])  # Harga penutupan terakhir
                total_return = ((last_price - first_price) / first_price) * 100
                returns[name] = total_return
        return returns
    
    def analyze_sentiment_vs_price(self):
        """
        Analisis korelasi dengan data real + simulasi sentiment
        (karena AKShare tidak punya data sentiment)
        """
        # Ambil data real
        print("Mengambil data saham real dari AKShare...")
        stock_data = self.get_multiple_stocks_data('1y')
        
        # Hitung return real
        real_returns = self.calculate_returns(stock_data)
        
        # Buat dataframe untuk analisis
        sentiment_data = []
        for name in self.sahams.keys():
            if name in real_returns:
                # Generate sentiment random (karena tidak tersedia di AKShare)
                # Ini bisa diganti dengan data real dari sumber lain
                data = {
                    'saham': name,
                    'bullish': np.random.randint(30, 80),
                    'bearish': np.random.randint(10, 40),
                    'netral': 100 - np.random.randint(40, 120),  # Sisanya
                    'total_diskusi': np.random.randint(100, 5000),
                    'return_ytd': real_returns.get(name, 0),
                    'harga_terkini': float(stock_data[name]['收盘'].iloc[-1]) if name in stock_data else 0,
                    'volume': int(stock_data[name]['成交量'].iloc[-1]) if name in stock_data else 0
                }
                sentiment_data.append(data)
        
        sentiment_df = pd.DataFrame(sentiment_data)
        
        # Plot
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Scatter plot sentiment vs return
        axes[0, 0].scatter(sentiment_df['bullish'], sentiment_df['return_ytd'], 
                          alpha=0.6, s=100, c='blue')
        for i, saham in enumerate(sentiment_df['saham']):
            axes[0, 0].annotate(saham, (sentiment_df['bullish'].iloc[i], 
                                       sentiment_df['return_ytd'].iloc[i]))
        axes[0, 0].set_xlabel('Bullish Sentiment (%)')
        axes[0, 0].set_ylabel('Return YTD (%)')
        axes[0, 0].set_title('Korelasi Sentiment vs Return (Data Real)')
        axes[0, 0].grid(True, alpha=0.3)
        
        # Bar plot sentiment
        sentiment_df.set_index('saham')[['bullish', 'bearish']].plot(
            kind='bar', ax=axes[0, 1], color=['green', 'red'])
        axes[0, 1].set_title('Sentiment Per Saham')
        axes[0, 1].set_ylabel('Persentase (%)')
        axes[0, 1].legend()
        axes[0, 1].tick_params(axis='x', rotation=45)
        
        # Bar plot return real
        axes[1, 0].bar(sentiment_df['saham'], sentiment_df['return_ytd'], 
                      color=['green' if x > 0 else 'red' for x in sentiment_df['return_ytd']])
        axes[1, 0].set_title('Return YTD Real')
        axes[1, 0].set_ylabel('Return (%)')
        axes[1, 0].grid(True, alpha=0.3)
        axes[1, 0].tick_params(axis='x', rotation=45)
        
        # Harga terkini
        axes[1, 1].bar(sentiment_df['saham'], sentiment_df['harga_terkini'])
        axes[1, 1].set_title('Harga Terkini')
        axes[1, 1].set_ylabel('Harga (Rp)')
        axes[1, 1].grid(True, alpha=0.3)
        axes[1, 1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.show()
        
        print("\n=== Data Real dari AKShare ===")
        print(sentiment_df[['saham', 'harga_terkini', 'return_ytd', 'volume']].to_string(index=False))
        
        return sentiment_df
    
    def track_real_stock_price(self, saham, days=30):
        """
        Tracking harga real dari AKShare
        """
        if saham not in self.sahams:
            print(f"Saham {saham} tidak ditemukan")
            return None
        
        code = self.sahams[saham]
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Ambil data real
        df = self.get_real_stock_data(code, 
                                      start_date.strftime('%Y%m%d'),
                                      end_date.strftime('%Y%m%d'))
        
        if df is None or df.empty:
            print(f"Tidak ada data untuk {saham}")
            return None
        
        # Konversi tanggal
        df['日期'] = pd.to_datetime(df['日期'])
        df = df.sort_values('日期')
        
        # Plot
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8))
        
        # Candlestick-like chart (simplified)
        ax1.plot(df['日期'], df['收盘'], label='Close Price', color='black', linewidth=2)
        ax1.fill_between(df['日期'], df['最低'], df['最高'], alpha=0.3, color='gray')
        ax1.set_title(f'{saham} - Harga Real ({days} hari terakhir)')
        ax1.set_ylabel('Harga (Rp)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Volume
        ax2.bar(df['日期'], df['成交量'], color='blue', alpha=0.6)
        ax2.set_title('Volume Transaksi')
        ax2.set_ylabel('Volume')
        ax2.set_xlabel('Tanggal')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
        
        # Statistik
        print(f"\n=== Statistik {saham} ===")
        print(f"Harga Terendah: Rp {df['最低'].min():,.0f}")
        print(f"Harga Tertinggi: Rp {df['最高'].max():,.0f}")
        print(f"Harga Rata-rata: Rp {df['收盘'].mean():,.0f}")
        print(f"Total Volume: {df['成交量'].sum():,.0f}")
        print(f"Return periode: {(df['收盘'].iloc[-1]/df['收盘'].iloc[0] - 1)*100:.2f}%")
        
        return df
    
    def compare_stocks_performance(self):
        """
        Membandingkan performa multiple saham
        """
        stock_data = self.get_multiple_stocks_data('6m')
        
        plt.figure(figsize=(14, 8))
        
        for name, df in stock_data.items():
            if df is not None and len(df) > 0:
                # Normalisasi ke 100
                df['日期'] = pd.to_datetime(df['日期'])
                df = df.sort_values('日期')
                normalized = df['收盘'] / df['收盘'].iloc[0] * 100
                plt.plot(df['日期'], normalized, label=name, linewidth=2)
        
        plt.title('Perbandingan Performa Saham (Normalisasi 100)')
        plt.xlabel('Tanggal')
        plt.ylabel('Performansi (%)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.show()
        
        # Hitung return
        returns = {}
        for name, df in stock_data.items():
            if df is not None and len(df) > 0:
                ret = (df['收盘'].iloc[-1] / df['收盘'].iloc[0] - 1) * 100
                returns[name] = ret
        
        returns_df = pd.DataFrame(list(returns.items()), columns=['Saham', 'Return (%)'])
        returns_df = returns_df.sort_values('Return (%)', ascending=False)
        
        print("\n=== Ranking Performa Saham ===")
        print(returns_df.to_string(index=False))
        
        return returns_df
    
    def get_fundamental_data(self, saham):
        """
        Mencoba mengambil data fundamental (fitur terbatas di AKShare)
        """
        try:
            # AKShare juga punya beberapa data fundamental
            if saham in self.sahams:
                code = self.sahams[saham].replace('.JK', '')
                
                # Coba ambil data perusahaan
                stock_info = ak.stock_individual_info_em(symbol=code)
                print(f"\n=== Informasi Fundamental {saham} ===")
                print(stock_info)
                
                return stock_info
        except:
            print(f"Data fundamental untuk {saham} tidak tersedia")
            return None

# Contoh penggunaan
if __name__ == "__main__":
    analytics = StockbitAnalyticsWithAKShare()
    
    print("="*50)
    print("ANALISIS SAHAM INDONESIA DENGAN AKSHARE")
    print("="*50)
    
    # 1. Analisis sentiment vs return (dengan data real)
    print("\n1. Analisis Sentiment vs Return Real")
    print("-"*30)
    sentiment_df = analytics.analyze_sentiment_vs_price()
    
    # 2. Tracking harga real BBCA
    print("\n2. Tracking Harga Real BBCA")
    print("-"*30)
    trend_df = analytics.track_real_stock_price('BBCA', days=60)
    
    # 3. Perbandingan performa
    print("\n3. Perbandingan Performa Multiple Saham")
    print("-"*30)
    performance = analytics.compare_stocks_performance()
    
    # 4. Coba ambil data fundamental
    print("\n4. Data Fundamental (jika tersedia)")
    print("-"*30)
    analytics.get_fundamental_data('BBCA')