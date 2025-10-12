#!/bin/bash
#@doliyevuz manba bilan oling

# ┌──────────────────────────────────────────────────────────────┐
# │             REAL SMS BOMBER — TERMUX:API EDITION             │
# │             YOUR PHONE NUMBER — REAL SMS SENT                │
# │             REQUIRES TERMUX:API APP INSTALLED                │
# └──────────────────────────────────────────────────────────────┘

#@doliyevuz manba bilan oling
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

CONFIG="$HOME/.realsms.conf"
LOG="$HOME/real_sms.log"
LANGUAGE="uz"
TARGET=""
MESSAGE="Salom, bu test xabari!"
COUNT=1
DELAY=2
PROFILE="default"

#@doliyevuz manba bilan oling
load_config() {
    [ -f "$CONFIG" ] && source "$CONFIG"
}

#@doliyevuz manba bilan oling
save_config() {
    cat > "$CONFIG" <<EOF
LANGUAGE="$LANGUAGE"
PROFILE="$PROFILE"
EOF
}

#@doliyevuz manba bilan oling
log() {
    echo "[$(date)] $1" >> "$LOG"
}

#@doliyevuz manba bilan oling
animate_shax_mobi() {
    clear
    text="@shax_mobi"
    for ((i=0; i<${#text}; i++)); do
        echo -ne "${GREEN}${text:0:i+1}${NC}\r"
        sleep 0.1
    done
    echo -e "\n"
    sleep 0.5
}

#@doliyevuz manba bilan oling
banner() {
    clear
    echo -e "${GREEN}
  ██████╗ ███████╗██╗  ██╗    ███╗   ███╗██████╗ ██╗   ██╗███████╗
 ██╔════╝ ██╔════╝██║  ██║    ████╗ ████║██╔══██╗██║   ██║██╔════╝
 ██║  ███╗███████╗███████║    ██╔████╔██║██████╔╝██║   ██║█████╗
 ██║   ██║╚════██║██╔══██║    ██║╚██╔╝██║██╔══██╗██║   ██║██╔══╝
 ╚██████╔╝███████║██║  ██║    ██║ ╚═╝ ██║██████╔╝╚██████╔╝███████╗
  ╚═════╝ ╚══════╝╚═╝  ╚═╝    ╚═╝     ╚═╝╚═════╝  ╚═════╝ ╚══════╝
          ${YELLOW}Haqiqiy SMS Jo'natuvchi — Sizning Raqamingizdan${NC}
          ${BLUE}@doliyevuz uchun maxsus tayyorlandi${NC}
          ${RED}Faqat ta'lim maqsadida!${NC}
"
}

#@doliyevuz manba bilan oling
menu() {
    banner
    echo -e "${YELLOW}=== Asosiy Menyu (@doliyevuz) ===${NC}"
    echo "1. SMS Yuborish"
    echo "2. Sozlamalar"
    echo "3. Profil"
    echo "4. Statistika"
    echo "5. Ornatishni Tekshirish"
    echo "6. Kodni yangilash"
    echo "7. Haqida"
    echo "8. Chiqish"
    read -p "Tanlov: " ch

    case $ch in
        1) send_sms ;;
        2) settings ;;
        3) profile ;;
        4) stats ;;
        5) check_install ;;
        6) update_code ;;
        7) about ;;
        8) exit 0 ;;
        *) echo -e "${RED}Noto'g'ri!${NC}"; sleep 1; menu ;;
    esac
}

#@doliyevuz manba bilan oling
send_sms() {
    banner
    echo -e "${YELLOW}=== SMS Yuborish (@doliyevuz) ===${NC}"

    if ! command -v termux-sms-send >/dev/null 2>&1; then
        echo -e "${RED}Xato: termux-api o'rnatilmagan!${NC}"
        echo "Iltimos, 'pkg install termux-api' ni ishlating."
        read -p "Davom etish uchun ENTER bosing..."
        menu
        return
    fi

    read -p "Qabul qiluvchi raqam (+998...): " TARGET
    if [[ ! $TARGET =~ ^\+998[0-9]{9}$ ]]; then
        echo -e "${RED}Raqam noto'g'ri formatda! (+998XXXXXXXXX)${NC}"
        read -p "Davom etish uchun ENTER..."
        send_sms
        return
    fi

    read -p "Xabar matni (Enter — standart): " MSG
    MESSAGE="${MSG:-$MESSAGE}"

    read -p "Nechta SMS yuborilsin? (default: 1): " CNT
    COUNT="${CNT:-1}"

    read -p "Har bir SMS oralig'i (sekund, default: 2): " DL
    DELAY="${DL:-2}"

    echo -e "\n${GREEN}Boshlanmoqda... (@doliyevuz)${NC}"
    echo -e "Raqam: $TARGET"
    echo -e "Xabar: $MESSAGE"
    echo -e "Soni: $COUNT ta"
    echo -e "Oraliq: $DELAY sekund"

    for i in $(seq 1 $COUNT); do
        echo -e "\n${BLUE}[$i/$COUNT] SMS yuborilmoqda... (@doliyevuz)${NC}"
        termux-sms-send -n "$TARGET" "$MESSAGE"
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ Yuborildi${NC}"
            log "SUCCESS | $TARGET | $MESSAGE"
        else
            echo -e "${RED}❌ Xato yuz berdi${NC}"
            log "FAILED | $TARGET | $MESSAGE"
        fi
        if [ $i -lt $COUNT ]; then
            sleep $DELAY
        fi
    done

    echo -e "\n${GREEN}✅ Jarayon tugadi! (@doliyevuz)${NC}"
    read -p "Menyuga qaytish uchun ENTER..."
    menu
}

#@doliyevuz manba bilan oling
settings() {
    banner
    echo -e "${YELLOW}=== Sozlamalar (@doliyevuz) ===${NC}"
    echo "1. Tilni o'zgartirish (Hozir: $LANGUAGE)"
    echo "2. Standart xabarni o'zgartirish"
    echo "3. Standart kechikish ($DELAY sekund)"
    echo "4. Orqaga"
    read -p "Tanlov: " s

    case $s in
        1)
            read -p "Til (uz/en): " LANGUAGE
            LANGUAGE=$(echo "$LANGUAGE" | tr '[:upper:]' '[:lower:]')
            if [[ "$LANGUAGE" != "uz" && "$LANGUAGE" != "en" ]]; then
                LANGUAGE="uz"
            fi
            save_config
            echo -e "${GREEN}Til o'zgartirildi! (@doliyevuz)${NC}"
            ;;
        2)
            read -p "Yangi standart xabar: " MESSAGE
            MESSAGE="${MESSAGE:-Salom, bu test xabari!}"
            echo -e "${GREEN}Xabar o'rnatildi! (@doliyevuz)${NC}"
            ;;
        3)
            read -p "Standart kechikish (sekund): " DELAY
            DELAY="${DELAY:-2}"
            echo -e "${GREEN}Kechikish o'rnatildi! (@doliyevuz)${NC}"
            ;;
        4) menu; return ;;
        *) echo -e "${RED}Noto'g'ri! (@doliyevuz)${NC}" ;;
    esac
    save_config
    sleep 1
    settings
}

#@doliyevuz manba bilan oling
profile() {
    banner
    echo -e "${YELLOW}=== Profil (@doliyevuz) ===${NC}"
    echo "Hozirgi profil: $PROFILE"
    read -p "Yangi profil nomi (bo'sh — o'zgartirmaslik): " P
    if [ -n "$P" ]; then
        PROFILE="$P"
        save_config
        echo -e "${GREEN}Profil yangilandi! (@doliyevuz)${NC}"
    fi
    sleep 1
    menu
}

#@doliyevuz manba bilan oling
stats() {
    banner
    echo -e "${YELLOW}=== Statistika (@doliyevuz) ===${NC}"
    if [ ! -f "$LOG" ]; then
        echo "Hali hech qanday SMS yuborilmagan."
    else
        total=$(wc -l < "$LOG")
        success=$(grep -c "SUCCESS" "$LOG")
        failed=$(grep -c "FAILED" "$LOG")
        echo "Jami urinishlar: $total"
        echo "Muvaffaqiyatli: $success"
        echo "Xatoliklar: $failed"
        echo
        echo -e "${BLUE}Oxirgi 5 ta yozuv:${NC}"
        tail -5 "$LOG"
    fi
    read -p "Orqaga qaytish uchun ENTER..."
    menu
}

#@doliyevuz manba bilan oling
check_install() {
    banner
    echo -e "${YELLOW}=== O'RNATISHNI TEKSHIRISH (@doliyevuz) ===${NC}"

    if command -v termux-sms-send >/dev/null 2>&1; then
        echo -e "${GREEN}✅ termux-api o'rnatilgan (@doliyevuz)${NC}"
    else
        echo -e "${RED}❌ termux-api topilmadi! (@doliyevuz)${NC}"
        echo "Iltimos, Termuxda quyidagini ishlating:"
        echo -e "${BLUE}pkg install termux-api${NC}"
    fi

    echo -e "\n${YELLOW}⚠️  Birinchi marta ishlatganda Termux:API ilovasi"
    echo -e "   sizdan SMS jo'natish ruxsatini so'raydi — uni bering! (@doliyevuz)${NC}"

    read -p "Menyuga qaytish uchun ENTER..."
    menu
}

#@doliyevuz manba bilan oling
update_code() {
    banner
    echo -e "${YELLOW}=== Kodni yangilash (@doliyevuz) ===${NC}"
    REMOTE_URL="https://raw.githubusercontent.com/uz980/Hacker/main/smsbomber.sh"
    TMP=$(mktemp /tmp/smsupdate.XXXXXX) || TMP="/tmp/smsupdate.$$"
    BACKUP="$HOME/$(basename "$0").bak.$(date +%Y%m%d%H%M%S)"

    echo "Manba: $REMOTE_URL"
    echo -n "Yangilashni boshlaysizmi? (y/N): "
    read -r yn
    yn=$(echo "$yn" | tr '[:upper:]' '[:lower:]')
    if [[ "$yn" != "y" && "$yn" != "yes" ]]; then
        echo "Yangilash bekor qilindi."
        sleep 1
        menu
        return
    fi

    echo "Yuklanmoqda..."
    if command -v curl >/dev/null 2>&1; then
        curl -fsSL "$REMOTE_URL" -o "$TMP"
        status=$?
    elif command -v wget >/dev/null 2>&1; then
        wget -qO "$TMP" "$REMOTE_URL"
        status=$?
    else
        echo -e "${RED}curl yoki wget topilmadi. Iltimos, birini o'rnating.${NC}"
        sleep 2
        menu
        return
    fi

    if [ $status -ne 0 ] || [ ! -s "$TMP" ]; then
        echo -e "${RED}❌ Yuklashda xato yuz berdi.${NC}"
        rm -f "$TMP"
        sleep 2
        menu
        return
    fi

    if ! grep -qE "REAL SMS BOMBER|@doliyevuz|Haqiqiy SMS Jo'natuvchi" "$TMP"; then
        echo -e "${RED}❌ Yuklangan fayl kutilgan tarkibga mos kelmadi.${NC}"
        echo "Faylni ko'rib chiqing: $TMP"
        read -p "Menyuga qaytish uchun ENTER..."
        rm -f "$TMP"
        menu
        return
    fi

    echo "Joriy fayl zaxiralanmoqda: $BACKUP"
    cp -p "$0" "$BACKUP" || {
        echo -e "${RED}❌ Zaxira olishda xato.${NC}"
        rm -f "$TMP"
        sleep 2
        menu
        return
    }

    echo "Skript yangilanmoqda..."
    cat "$TMP" > "$0" || {
        echo -e "${RED}❌ Skriptni yangilashda xato.${NC}"
        echo "Zaxiradan tiklashga harakat qilinmoqda..."
        cp -p "$BACKUP" "$0"
        rm -f "$TMP"
        sleep 2
        menu
        return
    }

    chmod +x "$0"
    rm -f "$TMP"
    log "UPDATE | $REMOTE_URL | OK"
    echo -e "${GREEN}✅ Yangilash muvaffaqiyatli yakunlandi. Zaxira: $BACKUP${NC}"
    echo "Skript darhol qayta ishga tushiriladi..."
    sleep 1
    exec "$0" "$@"
}

#@doliyevuz manba bilan oling
about() {
    banner
    echo -e "
${GREEN}HAQIQIY SMS BOMBER — TERMUX:API (@doliyevuz)${NC}
Versiya: 1.0
Muallif: @doliyevuz uchun maxsus tayyorlandi
Maqsad: Ta'limiy — o'zingizning raqamingizdan SMS jo'natish

${YELLOW}TALABLAR (@doliyevuz):${NC}
- Termux ilovasi
- Termux:API ilovasi (Fdroid)
- 'pkg install termux-api'
- Birinchi marta ruxsatni bering!

${RED}DIQQAT (@doliyevuz):${NC}
- Bu script faqat o'zingizning telefon raqamingizdan ishlaydi.
- Boshqa raqamlarga spam qilish — qonunbuzarlik!
- Faqat o'zingizga yoki ruxsat bergan do'stlaringizga sinab ko'ring.

${BLUE}YARATILGAN: 2025-yil — @doliyevuz uchun maxsus${NC}
"
    read -p "Menyuga qaytish uchun ENTER..."
    menu
}

#@doliyevuz manba bilan oling
# DASTURNI ISHGA TUSHIRISH
clear
animate_shax_mobi
sleep 1

load_config
menu
