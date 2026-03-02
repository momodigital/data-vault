import time
import random
import sys

def print_slow(text):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(0.03)
    print()

def hacking_game():
    print_slow("=" * 50)
    print_slow("     WELCOME TO HACKER SIMULATOR")
    print_slow("=" * 50)
    print_slow("\nAnda adalah seorang hacker yang mencoba")
    print_slow("menembus sistem keamanan perusahaan X")
    
    # Sistem target
    targets = {
        "1": {"name": "Server Database", "difficulty": 3, "hacked": False},
        "2": {"name": "Firewall Utama", "difficulty": 5, "hacked": False},
        "3": {"name": "Email Server", "difficulty": 2, "hacked": False},
        "4": {"name": "System Admin", "difficulty": 4, "hacked": False}
    }
    
    player_level = 1
    hacking_tools = ["password cracker", "port scanner"]
    score = 0
    
    while True:
        print_slow(f"\n[Level Keahlian: {player_level}]")
        print_slow(f"[Skor: {score}]")
        print_slow("\nPilih target untuk di-hack:")
        
        for key, target in targets.items():
            status = "[HACKED]" if target["hacked"] else "[LOCKED]"
            print_slow(f"{key}. {target['name']} {status}")
        
        print_slow("4. Keluar dari game")
        
        choice = input("\nPilih target (1-4): ")
        
        if choice == "4":
            print_slow("\nAnda keluar dari sistem...")
            print_slow(f"Skor akhir: {score}")
            break
            
        if choice in targets and not targets[choice]["hacked"]:
            target = targets[choice]
            print_slow(f"\nMencoba menghack {target['name']}...")
            
            # Simulasi proses hacking
            for i in range(3):
                print_slow(f"Loading{'.' * (i+1)}")
                time.sleep(1)
            
            # Chance berdasarkan level dan kesulitan
            success_chance = (player_level * 20) - (target["difficulty"] * 10)
            success_chance = max(10, min(90, success_chance))  # Batasi antara 10-90%
            
            if random.randint(1, 100) <= success_chance:
                print_slow("\n[BERHASIL] Sistem berhasil ditembus!")
                targets[choice]["hacked"] = True
                
                # Dapatkan point
                points = target["difficulty"] * 10
                score += points
                print_slow(f"[INFO] Mendapatkan {points} point!")
                
                # Naik level
                if score >= player_level * 30:
                    player_level += 1
                    print_slow(f"\n[LEVEL UP] Anda sekarang level {player_level}!")
                    if player_level % 2 == 0:
                        new_tool = random.choice(["exploit toolkit", "packet sniffer", "rootkit", "encryption breaker"])
                        hacking_tools.append(new_tool)
                        print_slow(f"[TOOL BARU] Mendapatkan: {new_tool}")
                        
            else:
                print_slow("\n[GAGAL] Sistem mendeteksi percobaan hacking!")
                print_slow("[WARNING] Meninggalkan jejak digital...")
                
        elif choice in targets and targets[choice]["hacked"]:
            print_slow("\n[Sistem ini sudah di-hack sebelumnya]")
        else:
            print_slow("\n[Pilihan tidak valid]")
        
        # Cek apakah semua sudah di-hack
        if all(target["hacked"] for target in targets.values()):
            print_slow("\n" + "=" * 50)
            print_slow("     SELAMAT! ANDA BERHASIL MERETAS SEMUA SISTEM!")
            print_slow("=" * 50)
            print_slow(f"\nSkor Akhir: {score}")
            print_slow(f"Level Akhir: {player_level}")
            print_slow(f"Tools yang dimiliki: {', '.join(hacking_tools)}")
            break

# Menjalankan game
if __name__ == "__main__":
    try:
        hacking_game()
    except KeyboardInterrupt:
        print_slow("\n\nProgram dihentikan...")
        sys.exit(0)
