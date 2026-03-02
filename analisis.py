#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 ANALISIS POLA
Deteksi pola dari hasil undian
"""

import os
import requests
import re
from collections import Counter, defaultdict
from datetime import datetime
import time

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

class PatternAnalyzer:
    def __init__(self):
        self.GITHUB_CONFIG = {
            'username': 'MOMODIGITAL',
            'repo': 'data-vault',
            'branch': 'main',
            'path': 'data'
        }
        
        # Daftar pasaran yang tersedia
        self.MARKET_FILES = {
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
        
        self.MARKET_NAMES = {
            1: 'Magnum Cambodia',
            2: 'Sydney Pools',
            3: 'Sydney Lotto',
            4: 'China Pools',
            5: 'Singapore',
            6: 'Taiwan',
            7: 'Hongkong Pools',
            8: 'Hongkong Lotto',
            9: 'New York Evening',
            10: 'Kentucky Evening'
        }
        
        self.PATTERN_DIR = '/sdcard/Prediktor_Pola'
        if not os.path.exists(self.PATTERN_DIR):
            os.makedirs(self.PATTERN_DIR)
    
    def fetch_csv(self, market_key):
        """Fetch CSV data from GitHub"""
        if market_key not in self.MARKET_FILES:
            print(f"{Colors.RED}❌ Pasaran tidak valid!{Colors.RESET}")
            return None
            
        url = f"https://raw.githubusercontent.com/{self.GITHUB_CONFIG['username']}/{self.GITHUB_CONFIG['repo']}/{self.GITHUB_CONFIG['branch']}/{self.GITHUB_CONFIG['path']}/{self.MARKET_FILES[market_key][1]}"
        
        try:
            print(f"{Colors.CYAN}📡 Mengambil data dari GitHub...{Colors.RESET}")
            r = requests.get(url, timeout=30)
            r.raise_for_status()
            return r.text
        except requests.exceptions.ConnectionError:
            print(f"{Colors.RED}❌ Gagal koneksi ke GitHub. Periksa internet Anda.{Colors.RESET}")
            return None
        except requests.exceptions.Timeout:
            print(f"{Colors.RED}❌ Timeout. Server terlalu lambat.{Colors.RESET}")
            return None
        except requests.exceptions.HTTPError as e:
            print(f"{Colors.RED}❌ HTTP Error: {e}{Colors.RESET}")
            return None
        except Exception as e:
            print(f"{Colors.RED}❌ Error: {e}{Colors.RESET}")
            return None
    
    def parse_csv(self, text):
        """Parse CSV data"""
        if not text:
            return []
        
        results = []
        lines = text.strip().split('\n')
        
        # Skip header if exists
        start_idx = 0
        if lines and 'date' in lines[0].lower():
            start_idx = 1
        
        for line in lines[start_idx:]:
            if not line.strip():
                continue
            parts = line.split(',')
            if len(parts) >= 2:
                # Cari angka 4 digit di kolom kedua
                match = re.search(r'(\d{4})', parts[1].strip())
                if match:
                    results.append(match.group(1))
        
        return results
    
    def detect_patterns(self, data):
        """Detect various patterns in data"""
        patterns = {}
        
        if len(data) < 10:
            return patterns
        
        # 1. Ganjil/Genap Pattern
        odd_even = []
        odd_positions = []
        even_positions = []
        
        for num in data[-30:]:  # Gunakan 30 data terakhir
            odds = sum(int(c) % 2 for c in num)
            evens = 4 - odds
            odd_even.append('GANJIL' if odds > evens else 'GENAP' if evens > odds else 'SEIMBANG')
            
            # Hitung per posisi
            pos_odd = [i for i, c in enumerate(num) if int(c) % 2 == 1]
            odd_positions.extend(pos_odd)
        
        patterns['odd_even'] = odd_even
        patterns['odd_positions'] = Counter(odd_positions)
        
        # 2. Pola Naik/Turun (berdasarkan digit terakhir)
        rise_down = []
        for i in range(len(data)-1):
            prev = int(data[i][3])
            curr = int(data[i+1][3])
            if curr > prev:
                rise_down.append('NAIK')
            elif curr < prev:
                rise_down.append('TURUN')
            else:
                rise_down.append('SAMA')
        
        patterns['rise_down'] = rise_down[-20:]
        
        # 3. Pola Kembaran (double digit)
        kembar_types = []
        for num in data[-30:]:
            counts = Counter(num)
            pairs = [d for d, c in counts.items() if c >= 2]
            if len(pairs) >= 2:
                kembar_types.append('DOBEL KEMBAR')
            elif len(pairs) == 1:
                if counts[pairs[0]] == 2:
                    kembar_types.append('KEMBAR 2')
                elif counts[pairs[0]] == 3:
                    kembar_types.append('KEMBAR 3')
                elif counts[pairs[0]] == 4:
                    kembar_types.append('KEMBAR 4')
            else:
                kembar_types.append('NORMAL')
        
        patterns['kembar'] = kembar_types
        
        # 4. Pola Posisi
        pos_patterns = defaultdict(list)
        for num in data[-50:]:  # Gunakan 50 data terakhir
            for pos in range(4):
                pos_patterns[pos].append(int(num[pos]))
        
        patterns['positions'] = dict(pos_patterns)
        
        # 5. Pola 2D Berulang (2 digit terakhir)
        two_d_counter = Counter([d[-2:] for d in data[-50:]])
        patterns['two_d_top'] = two_d_counter.most_common(10)
        
        # 6. Pola 3D Berulang (3 digit pertama)
        three_d_counter = Counter([d[:3] for d in data[-50:]])
        patterns['three_d_top'] = three_d_counter.most_common(10)
        
        # 7. Pola Gap (selisih antar digit)
        gaps = []
        for num in data[-30:]:
            digits = [int(d) for d in num]
            max_gap = max(digits) - min(digits)
            gaps.append(max_gap)
        patterns['gaps'] = Counter(gaps)
        
        # 8. Pola AS (digit pertama) terakhir
        as_counter = Counter([d[0] for d in data[-30:]])
        patterns['as_top'] = as_counter.most_common(5)
        
        # 9. Pola EKOR (digit terakhir) terakhir
        ekor_counter = Counter([d[3] for d in data[-30:]])
        patterns['ekor_top'] = ekor_counter.most_common(5)
        
        return patterns
    
    def analyze_trend(self, data):
        """Analyze trends in data"""
        trends = {}
        
        if len(data) < 20:
            return trends
        
        # Moving average of last digits
        last_digits = [int(d[3]) for d in data[-20:]]
        ma5 = sum(last_digits[-5:]) / 5 if len(last_digits) >= 5 else 0
        ma10 = sum(last_digits[-10:]) / 10 if len(last_digits) >= 10 else 0
        
        trends['ma5'] = ma5
        trends['ma10'] = ma10
        
        # Volatility
        if len(last_digits) > 1:
            changes = [abs(last_digits[i] - last_digits[i-1]) for i in range(1, len(last_digits))]
            trends['volatility'] = sum(changes) / len(changes)
        
        # Hot and cold numbers
        all_digits = [d for num in data[-50:] for d in num]
        digit_counts = Counter(all_digits)
        
        trends['hot'] = [d for d, c in digit_counts.most_common(3)]
        trends['cold'] = [d for d, c in sorted(digit_counts.items(), key=lambda x: x[1])[:3]]
        
        return trends
    
    def display_patterns(self, patterns, trends, market_name):
        """Display detected patterns"""
        print("\n" + "="*50)
        print(f"{Colors.MAGENTA}🔍 ANALISIS POLA: {market_name}{Colors.RESET}")
        print("="*50)
        
        if not patterns:
            print(f"{Colors.RED}❌ Tidak cukup data untuk analisis{Colors.RESET}")
            return
        
        # Odd/Even Summary
        if 'odd_even' in patterns:
            oe = patterns['odd_even']
            o_cnt = oe.count('GANJIL')
            e_cnt = oe.count('GENAP')
            s_cnt = oe.count('SEIMBANG')
            
            print(f"\n{Colors.YELLOW}📊 POLA GANJIL/GENAP:{Colors.RESET}")
            print(f"  Ganjil   : {o_cnt} ({o_cnt/len(oe)*100:.1f}%)")
            print(f"  Genap    : {e_cnt} ({e_cnt/len(oe)*100:.1f}%)")
            print(f"  Seimbang : {s_cnt} ({s_cnt/len(oe)*100:.1f}%)")
        
        # Rise/Down
        if 'rise_down' in patterns:
            rd = patterns['rise_down']
            na = rd.count('NAIK')
            tu = rd.count('TURUN')
            sa = rd.count('SAMA')
            
            print(f"\n{Colors.CYAN}📈 POLA NAIK/TURUN:{Colors.RESET}")
            print(f"  Naik  : {na} ({na/len(rd)*100:.1f}%)")
            print(f"  Turun : {tu} ({tu/len(rd)*100:.1f}%)")
            print(f"  Sama  : {sa} ({sa/len(rd)*100:.1f}%)")
        
        # Kembar Patterns
        if 'kembar' in patterns:
            k = patterns['kembar']
            kembar_count = sum(1 for x in k if 'KEMBAR' in x)
            normal_count = k.count('NORMAL')
            
            print(f"\n{Colors.GREEN}🎯 POLA KEMBARAN:{Colors.RESET}")
            print(f"  Kembar : {kembar_count} ({kembar_count/len(k)*100:.1f}%)")
            print(f"  Normal : {normal_count} ({normal_count/len(k)*100:.1f}%)")
            
            # Detail jenis kembar
            kembar_types = Counter(k)
            for ktype in ['KEMBAR 2', 'KEMBAR 3', 'KEMBAR 4', 'DOBEL KEMBAR']:
                if ktype in kembar_types:
                    print(f"    {ktype}: {kembar_types[ktype]}x")
        
        # Top 2D and 3D
        print(f"\n{Colors.BLUE}🔢 TOP 5 2D TERAKHIR:{Colors.RESET}")
        if 'two_d_top' in patterns:
            for num, count in patterns['two_d_top'][:5]:
                bar_len = int(count / patterns['two_d_top'][0][1] * 20)
                bar = "█" * bar_len
                print(f"  {num}: {count}x [{bar}]")
        
        print(f"\n{Colors.MAGENTA}🔢 TOP 5 3D TERAKHIR:{Colors.RESET}")
        if 'three_d_top' in patterns:
            for num, count in patterns['three_d_top'][:5]:
                bar_len = int(count / patterns['three_d_top'][0][1] * 20)
                bar = "█" * bar_len
                print(f"  {num}: {count}x [{bar}]")
        
        # Position stats
        if 'positions' in patterns:
            position_names = ['AS (Ribuan)', 'KOP (Ratusan)', 'KEPALA (Puluhan)', 'EKOR (Satuan)']
            print(f"\n{Colors.YELLOW}📊 STATISTIK PER POSISI:{Colors.RESET}")
            
            for pos, nums in patterns['positions'].items():
                if pos < len(position_names):
                    most_common = Counter(nums).most_common(3)
                    print(f"\n  {position_names[pos]}:")
                    for digit, count in most_common:
                        bar_len = int(count / most_common[0][1] * 20)
                        bar = "█" * bar_len
                        print(f"    Digit {digit}: {count}x [{bar}]")
        
        # AS and EKOR trends
        if 'as_top' in patterns:
            print(f"\n{Colors.CYAN}🎯 TOP 5 ANGKA AS:{Colors.RESET}")
            for digit, count in patterns['as_top']:
                print(f"  Digit {digit}: {count}x")
        
        if 'ekor_top' in patterns:
            print(f"\n{Colors.GREEN}🎯 TOP 5 ANGKA EKOR:{Colors.RESET}")
            for digit, count in patterns['ekor_top']:
                print(f"  Digit {digit}: {count}x")
        
        # Trends
        if trends:
            print(f"\n{Colors.MAGENTA}📈 TREN TERKINI:{Colors.RESET}")
            if 'ma5' in trends:
                print(f"  MA5 Ekor  : {trends['ma5']:.1f}")
            if 'ma10' in trends:
                print(f"  MA10 Ekor : {trends['ma10']:.1f}")
            if 'volatility' in trends:
                vol_status = "Tinggi" if trends['volatility'] > 3 else "Sedang" if trends['volatility'] > 2 else "Rendah"
                print(f"  Volatilitas: {trends['volatility']:.2f} ({vol_status})")
            if 'hot' in trends:
                print(f"  Hot Digits : {', '.join(trends['hot'])}")
            if 'cold' in trends:
                print(f"  Cold Digits: {', '.join(trends['cold'])}")
        
        # Gap analysis
        if 'gaps' in patterns:
            print(f"\n{Colors.YELLOW}📊 ANALISIS GAP (Selisih Max-Min):{Colors.RESET}")
            total_gaps = sum(patterns['gaps'].values())
            for gap in range(10):
                if gap in patterns['gaps']:
                    count = patterns['gaps'][gap]
                    pct = count/total_gaps*100
                    bar_len = int(pct / 2)
                    bar = "█" * bar_len
                    print(f"  Gap {gap}: {count}x ({pct:.1f}%) [{bar}]")
    
    def save_patterns(self, patterns, trends, market_name):
        """Save pattern analysis to file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        fname = f"pola_{market_name.replace(' ', '_')}_{timestamp}.txt"
        path = os.path.join(self.PATTERN_DIR, fname)
        
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write("="*50 + "\n")
                f.write(f"🔍 ANALISIS POLA: {market_name}\n")
                f.write("="*50 + "\n")
                f.write(f"Tanggal: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n")
                
                if patterns:
                    if 'odd_even' in patterns:
                        oe = patterns['odd_even']
                        o_cnt = oe.count('GANJIL')
                        e_cnt = oe.count('GENAP')
                        f.write(f"GANJIL/GENAP: {o_cnt}/{e_cnt}\n")
                    
                    if 'two_d_top' in patterns:
                        f.write("\nTOP 5 2D:\n")
                        for num, count in patterns['two_d_top'][:5]:
                            f.write(f"  {num}: {count}x\n")
                    
                    if 'three_d_top' in patterns:
                        f.write("\nTOP 5 3D:\n")
                        for num, count in patterns['three_d_top'][:5]:
                            f.write(f"  {num}: {count}x\n")
                    
                    if 'as_top' in patterns:
                        f.write("\nTOP AS:\n")
                        for digit, count in patterns['as_top']:
                            f.write(f"  Digit {digit}: {count}x\n")
                    
                    if 'ekor_top' in patterns:
                        f.write("\nTOP EKOR:\n")
                        for digit, count in patterns['ekor_top']:
                            f.write(f"  Digit {digit}: {count}x\n")
                
                f.write("\n" + "="*50 + "\n")
                f.write("Analisis selesai. Gunakan dengan bijak.\n")
            
            print(f"\n{Colors.GREEN}✅ Tersimpan di: {path}{Colors.RESET}")
        except Exception as e:
            print(f"{Colors.RED}❌ Gagal menyimpan: {e}{Colors.RESET}")


def main():
    analyzer = PatternAnalyzer()
    
    while True:
        os.system('clear' if os.name == 'posix' else 'cls')
        print("\n" + "="*50)
        print(f"{Colors.MAGENTA}🔍 ANALISIS POLA PREDIKTOR{Colors.RESET}")
        print("="*50)
        
        print(f"\n{Colors.CYAN}📊 PILIH PASARAN:{Colors.RESET}")
        for k, v in analyzer.MARKET_NAMES.items():
            print(f"   {k}. {v}")
        print("   0. Keluar")
        
        try:
            choice = input(f"\n{Colors.GREEN}➤ Pilih pasaran (1-10): {Colors.RESET}").strip()
            if choice == '0':
                break
                
            choice = int(choice)
            if choice not in analyzer.MARKET_FILES:
                print(f"{Colors.RED}❌ Pilihan tidak valid!{Colors.RESET}")
                input("\nTekan Enter untuk melanjutkan...")
                continue
        except ValueError:
            print(f"{Colors.RED}❌ Masukkan angka yang valid!{Colors.RESET}")
            input("\nTekan Enter untuk melanjutkan...")
            continue
        
        market_name = analyzer.MARKET_NAMES[choice]
        print(f"\n{Colors.CYAN}🔄 Menganalisis {market_name}...{Colors.RESET}")
        
        # Fetch data
        data_text = analyzer.fetch_csv(choice)
        if not data_text:
            input("\nTekan Enter untuk melanjutkan...")
            continue
        
        data = analyzer.parse_csv(data_text)
        print(f"{Colors.GREEN}✅ Data dimuat: {len(data)} putaran{Colors.RESET}")
        
        if len(data) < 10:
            print(f"{Colors.YELLOW}⚠️ Data kurang, minimal 10 putaran untuk analisis{Colors.RESET}")
            input("\nTekan Enter untuk melanjutkan...")
            continue
        
        print(f"\n{Colors.CYAN}🔬 Mendeteksi pola...{Colors.RESET}")
        time.sleep(1)
        
        patterns = analyzer.detect_patterns(data)
        trends = analyzer.analyze_trend(data)
        analyzer.display_patterns(patterns, trends, market_name)
        
        # Save option
        save = input(f"\n{Colors.GREEN}💾 Simpan analisis? (y/n): {Colors.RESET}").lower()
        if save == 'y':
            analyzer.save_patterns(patterns, trends, market_name)
        
        input(f"\n{Colors.CYAN}Tekan Enter untuk analisis pasaran lain...{Colors.RESET}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}⚠️ Dibatalkan.{Colors.RESET}")
    except Exception as e:
        print(f"{Colors.RED}❌ Error: {e}{Colors.RESET}")
        import traceback
        traceback.print_exc()