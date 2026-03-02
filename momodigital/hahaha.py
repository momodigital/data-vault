import time
import random
import sys
import hashlib

def print_slow(text, delay=0.02):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def loading_animation(text="Mengakses sistem", duration=2):
    print_slow(f"\n{text}", 0.05)
    for i in range(duration):
        print_slow("." * (i+1), 0.3)
        time.sleep(0.5)

def mini_game_password():
    """Mini-game tebak password sederhana"""
    print_slow("\n[MINI-GAME: CRACK PASSWORD]")
    print_slow("Tebak password 3 digit (angka 0-9)")
    
    password = str(random.randint(100, 999))
    attempts = 3
    
    while attempts > 0:
        print_slow(f"\nKesempatan tersisa: {attempts}")
        guess = input("Masukkan tebakan (3 digit): ")
        
        if len(guess) != 3 or not guess.isdigit():
            print_slow("[!] Masukkan 3 digit angka!")
            continue
            
        if guess == password:
            print_slow("[✓] PASSWORD BENAR! Akses diberikan.")
            return True
        
        # Beri petunjuk
        correct_pos = 0
        for i in range(3):
            if guess[i] == password[i]:
                correct_pos += 1
        
        print_slow(f"[!] Salah! {correct_pos} digit berada di posisi yang benar")
        attempts -= 1
    
    print_slow("\n[✗] Gagal! Password tidak ditemukan.")
    return False

def mini_game_port_scan():
    """Mini-game scan port"""
    print_slow("\n[MINI-GAME: PORT SCANNING]")
    print_slow("Cari port yang terbuka (1-10)")
    
    open_port = random.randint(1, 10)
    attempts = 3
    
    while attempts > 0:
        print_slow(f"\nPort yang belum di-scan: {attempts}")
        try:
            guess = int(input("Masukkan nomor port (1-10): "))
            
            if guess < 1 or guess > 10:
                print_slow("[!] Port harus antara 1-10!")
                continue
                
            if guess == open_port:
                print_slow(f"[✓] Port {guess} TERBUKA! Akses diberikan.")
                return True
            else:
                if guess < open_port:
                    print_slow(f"[!] Port {guess} tertutup. Coba port yang lebih tinggi")
                else:
                    print_slow(f"[!] Port {guess} tertutup. Coba port yang lebih rendah")
                attempts -= 1
                
        except ValueError:
            print_slow("[!] Masukkan angka!")
    
    print_slow("\n[✗] Gagal menemukan port terbuka!")
    return False

def mini_game_firewall():
    """Mini-game bypass firewall"""
    print_slow("\n[MINI-GAME: BYPASS FIREWALL]")
    print_slow("Pilih urutan protokol yang benar:")
    print_slow("1. HTTP - 2. TCP - 3. UDP - 4. ICMP")
    
    correct_sequence = random.sample([1, 2, 3, 4], 3)
    attempts = 2
    
    while attempts > 0:
        print_slow(f"\nTebak 3 urutan protokol (contoh: 1 2 3)")
        print_slow(f"Kesempatan: {attempts}")
        
        try:
            guesses = list(map(int, input("Masukkan 3 angka (pisah spasi): ").split()))
            
            if len(guesses) != 3:
                print_slow("[!] Masukkan tepat 3 angka!")
                continue
                
            if guesses == correct_sequence:
                print_slow("[✓] FIREWALL BERHASIL DIBYPASS!")
                return True
            else:
                # Hitung berapa yang benar
                correct = sum(1 for i in range(3) if guesses[i] == correct_sequence[i])
                print_slow(f"[!] Urutan salah! {correct} posisi benar")
                attempts -= 1
                
        except ValueError:
            print_slow("[!] Format salah!")
    
    print_slow("\n[✗] Firewall mendeteksi intrusi!")
    return False

def mini_game_decrypt():
    """Mini-game dekripsi sederhana"""
    print_slow("\n[MINI-GAME: DEKRIPSI DATA]")
    
    # Buat kode sederhana
    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    message = "HACK"
    encrypted = ""
    key = random.randint(1, 5)
    
    for char in message:
        if char in chars:
            idx = chars.index(char)
            encrypted += chars[(idx + key) % 26]
    
    print_slow(f"Pesan terenkripsi: {encrypted}")
    print_slow(f"Kunci geser: {key}")
    print_slow("Dekripsi dengan menggeser huruf ke kiri")
    
    answer = input("Masukkan pesan asli: ").upper()
    
    if answer == message:
        print_slow("[✓] DEKRIPSI BERHASIL!")
        return True
    else:
        print_slow("[✗] Dekripsi gagal!")
        return False

def main_game():
    # Storyline ringan
    print_slow("=" * 60)
    print_slow("     ░░░░░░░░░░░░░ HACKER ODYSSEY ░░░░░░░░░░░░░")
    print_slow("=" * 60)
    time.sleep(1)
    
    print_slow("\nAnda adalah 'Cipher' - seorang hacker legendaris yang sudah pensiun.")
    print_slow("Tapi hidup tenang Anda terusik ketika menerima pesan misterius:")
    print_slow("\n'CIPHER... MEREKA AKAN MENGHANCURKAN KOTA...")
    print_slow("HENTIKAN PROYEK NIGHTFALL SEBELUM TERLAMBAT...'")
    print_slow("\n[!] Anda memutuskan untuk menyelidiki lebih dalam...")
    
    # Database target dengan storyline
    missions = {
        "phase1": {
            "name": "FASE 1: INFILTRASI AWAL",
            "targets": [
                {
                    "id": 1,
                    "name": "Server Perimeter",
                    "desc": "Server keamanan lapisan pertama",
                    "difficulty": 1,
                    "mini_game": mini_game_password,
                    "hacked": False,
                    "story": "Anda berhasil mengakses server perimeter. Ada email mencurigakan tentang 'Proyek Nightfall'..."
                },
                {
                    "id": 2,
                    "name": "Database Karyawan",
                    "desc": "Database berisi data karyawan",
                    "difficulty": 1,
                    "mini_game": mini_game_port_scan,
                    "hacked": False,
                    "story": "Data karyawan menunjukkan beberapa nama terlibat dalam proyek rahasia..."
                }
            ]
        },
        "phase2": {
            "name": "FASE 2: MENGGALI INFORMASI",
            "targets": [
                {
                    "id": 3,
                    "name": "Server Proyek Nightfall",
                    "desc": "Server khusus proyek misterius",
                    "difficulty": 2,
                    "mini_game": mini_game_password,
                    "hacked": False,
                    "story": "Anda menemukan dokumen: 'Proyek Nightfall - Sistem kontrol cuaca berbahaya...'"
                },
                {
                    "id": 4,
                    "name": "Komunikasi Internal",
                    "desc": "Server email dan chat internal",
                    "difficulty": 2,
                    "mini_game": mini_game_firewall,
                    "hacked": False,
                    "story": "Percakapan karyawan: 'Bos bilang sistemnya tidak stabil. Bisa membahayakan kota!'"
                },
                {
                    "id": 5,
                    "name": "Ruang Server Utama",
                    "desc": "Server pusat perusahaan",
                    "difficulty": 2,
                    "mini_game": mini_game_port_scan,
                    "hacked": False,
                    "story": "Anda menemukan jadwal aktivasi: 3 HARI LAGI!"
                }
            ]
        },
        "phase3": {
            "name": "FASE 3: MENGUNGKAP KEJAHATAN",
            "targets": [
                {
                    "id": 6,
                    "name": "Database Rahasia",
                    "desc": "Database terenkripsi",
                    "difficulty": 3,
                    "mini_game": mini_game_decrypt,
                    "hacked": False,
                    "story": "Data terdekripsi: 'Proyek Nightfall - Akan menghancurkan distrik selatan kota!'"
                },
                {
                    "id": 7,
                    "name": "Sistem Kontrol Utama",
                    "desc": "Sistem yang mengontrol proyek",
                    "difficulty": 3,
                    "mini_game": mini_game_firewall,
                    "hacked": False,
                    "story": "Akses ke sistem kontrol... Anda bisa menghentikannya!"
                },
                {
                    "id": 8,
                    "name": "Server CEO",
                    "desc": "Komputer pribadi CEO",
                    "difficulty": 3,
                    "mini_game": mini_game_password,
                    "hacked": False,
                    "story": "Email CEO ke investor: 'Proyek Nightfall akan membuat kita kaya. Korban jiwa? Efek samping...'"
                }
            ]
        }
    }
    
    player_stats = {
        "level": 1,
        "hacking_skill": 50,
        "tools": ["Password Cracker Basic"],
        "discoveries": []
    }
    
    current_phase = "phase1"
    
    while True:
        phase = missions[current_phase]
        
        print_slow("\n" + "=" * 60)
        print_slow(f"     {phase['name']}")
        print_slow("=" * 60)
        print_slow(f"\n[STATS] Level: {player_stats['level']} | Skill: {player_stats['hacking_skill']}")
        print_slow(f"[TOOLS] {', '.join(player_stats['tools'])}")
        
        # Tampilkan target yang tersedia
        print_slow("\n[ TARGET TERSEDIA ]:")
        available_targets = [t for t in phase["targets"] if not t["hacked"]]
        
        if not available_targets:
            if current_phase == "phase1":
                current_phase = "phase2"
                print_slow("\n[!] FASE 1 SELESAI! Melanjutkan ke penyelidikan lebih dalam...")
                continue
            elif current_phase == "phase2":
                current_phase = "phase3"
                print_slow("\n[!] FASE 2 SELESAI! Waktunya mengungkap kebenaran...")
                continue
            else:
                # Game selesai
                print_slow("\n" + "=" * 60)
                print_slow("     ░░░░░ SEMUA SISTEM BERHASIL DIHACK! ░░░░░")
                print_slow("=" * 60)
                print_slow("\nAnda berhasil menghentikan Proyek Nightfall!")
                print_slow("Kota selamat dari bencana. Media memberitakan:")
                print_slow("'Hacker Misterius Selamatkan Kota dari Bencana'")
                print_slow(f"\n[STATS AKHIR]")
                print_slow(f"Level: {player_stats['level']}")
                print_slow(f"Skill: {player_stats['hacking_skill']}")
                print_slow(f"Tools: {', '.join(player_stats['tools'])}")
                print_slow(f"Rahasia terungkap: {len(player_stats['discoveries'])}")
                
                play_again = input("\nMain lagi? (y/n): ").lower()
                if play_again == 'y':
                    return main_game()
                else:
                    print_slow("\nTerima kasih telah bermain! - Cipher")
                    return
        
        for i, target in enumerate(available_targets, 1):
            print_slow(f"{i}. {target['name']} (Kesulitan: {target['difficulty']})")
            print_slow(f"   > {target['desc']}")
        
        print_slow(f"{len(available_targets)+1}. Lihat catatan penemuan")
        print_slow(f"{len(available_targets)+2}. Tingkatkan skill (10 point)")
        print_slow(f"{len(available_targets)+3}. Keluar dari sistem")
        
        try:
            choice = int(input("\nPilih target/menu: "))
            
            if 1 <= choice <= len(available_targets):
                target = available_targets[choice-1]
                
                print_slow(f"\n[!] Mencoba hack: {target['name']}")
                loading_animation("Menyusup ke sistem")
                
                # Cek keberhasilan berdasarkan skill
                success_chance = player_stats['hacking_skill'] - (target['difficulty'] * 10)
                success_chance = max(30, min(90, success_chance))
                
                if random.randint(1, 100) <= success_chance:
                    print_slow(f"\n[✓] Koneksi berhasil! Memulai proses hacking...")
                    
                    # Jalankan mini-game
                    if target['mini_game']():
                        target['hacked'] = True
                        player_stats['discoveries'].append(target['story'])
                        
                        print_slow(f"\n[STORY] {target['story']}")
                        
                        # Dapatkan reward
                        reward = target['difficulty'] * 15
                        player_stats['hacking_skill'] = min(100, player_stats['hacking_skill'] + 5)
                        
                        print_slow(f"\n[+] Skill meningkat! (+5)")
                        
                        # Dapatkan tool baru secara random
                        if random.random() < 0.3:  # 30% chance
                            new_tools = ["Port Scanner Pro", "Firewall Breaker", "Encryption Tool", "Rootkit", "Packet Sniffer"]
                            new_tool = random.choice(new_tools)
                            if new_tool not in player_stats['tools']:
                                player_stats['tools'].append(new_tool)
                                print_slow(f"[+] Tool baru: {new_tool}!")
                        
                        # Naik level setiap 3 target
                        if len([t for phase in missions.values() for t in phase['targets'] if t['hacked']]) % 3 == 0:
                            player_stats['level'] += 1
                            print_slow(f"\n[★] LEVEL UP! Sekarang level {player_stats['level']}!")
                            
                    else:
                        print_slow("\n[✗] Hacking gagal! Sistem waspada.")
                        player_stats['hacking_skill'] = max(20, player_stats['hacking_skill'] - 3)
                        print_slow("[-] Skill menurun! (-3)")
                else:
                    print_slow("\n[✗] Gagal terkoneksi! Sistem terlalu aman.")
                    
            elif choice == len(available_targets)+1:
                # Lihat penemuan
                if player_stats['discoveries']:
                    print_slow("\n[ CATATAN PENEMUAN ]:")
                    for i, discovery in enumerate(player_stats['discoveries'], 1):
                        print_slow(f"{i}. {discovery}")
                else:
                    print_slow("\n[!] Belum ada penemuan.")
                    
            elif choice == len(available_targets)+2:
                # Upgrade skill
                if player_stats['level'] > 1 or len(player_stats['discoveries']) >= 2:
                    player_stats['hacking_skill'] = min(100, player_stats['hacking_skill'] + 10)
                    print_slow(f"\n[+] Skill ditingkatkan! (+10) Sekarang: {player_stats['hacking_skill']}")
                else:
                    print_slow("\n[!] Butuh lebih banyak pengalaman untuk upgrade!")
                    
            elif choice == len(available_targets)+3:
                print_slow("\n[!] Memutuskan koneksi... Sampai jumpa, Cipher!")
                break
            else:
                print_slow("\n[!] Pilihan tidak valid!")
                
        except ValueError:
            print_slow("\n[!] Masukkan angka yang valid!")
        except KeyboardInterrupt:
            print_slow("\n\n[!] Koneksi terputus paksa!")
            break

if __name__ == "__main__":
    try:
        main_game()
    except Exception as e:
        print_slow(f"\n[ERROR] Sistem crash: {e}")
    finally:
        print_slow("\n[System shutdown]")
