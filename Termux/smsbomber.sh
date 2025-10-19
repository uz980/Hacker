#!/bin/bash
# =============================================
# 🤖 AI Chat Terminal (Google Gemini Assistant)
# Yaratuvchi: @doliyevuz
# =============================================

# Ranglar
RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
BLUE='\033[1;34m'
RESET='\033[0m'

# API kalit
API_KEY="API_KIRITING"
MODEL="gemini-2.5-flash"
CHAT_FILE="yozishma.txt"

# Chat faylni yaratish
[[ ! -f "$CHAT_FILE" ]] && echo "" > "$CHAT_FILE"

# Gemini javobi olish
ask_gemini() {
  question="$1"
  history=$(cat "$CHAT_FILE")

  # "Seni kim yaratgan" so‘roviga maxsus javob
  if echo "$question" | grep -iq "kim yaratgan"; then
    echo "@doliyevuz"
    return
  fi

  # So‘rov JSON
  json=$(jq -n --arg hist "$history" --arg q "$question" \
  '{contents:[{parts:[{text:$hist}]},{parts:[{text:$q}]}]}')

  # APIga yuborish
  response=$(curl -s -X POST \
    "https://generativelanguage.googleapis.com/v1beta/models/${MODEL}:generateContent?key=${API_KEY}" \
    -H "Content-Type: application/json" \
    -d "$json")

  # Xatolikni tekshirish
  if [[ $(echo "$response" | jq -r '.error.message' 2>/dev/null) != "null" ]]; then
    echo -e "${RED}❌ Xatolik: API javob bermadi yoki noto‘g‘ri kalit.${RESET}"
    return
  fi

  # Javobni ajratib olish
  text=$(echo "$response" | jq -r '.candidates[0].content.parts[0].text')

  # Kodlarni ajratish (``` orasidagi matn)
  echo "$text" | awk '
  BEGIN {inblock=0}
  /```/ {
    if (inblock==0) {
      inblock=1
      print "\033[1;33m"  # sariq rang - kod boshi
    } else {
      inblock=0
      print "\033[0m"     # rangni tiklash
    }
    next
  }
  {print}
  '
}

# Asosiy menyu
while true; do
  clear
  echo -e "${CYAN}╔════════════════════════════════════╗"
  echo -e "║       🤖 AI Terminal Assistant      ║"
  echo -e "║    Model: ${YELLOW}${MODEL}${CYAN}             ║"
  echo -e "╚════════════════════════════════════╝${RESET}"
  echo ""
  echo -e "${GREEN}[1]${RESET} AI bilan gaplashish"
  echo -e "${GREEN}[2]${RESET} So‘nggi yozishmalarni ko‘rish"
  echo -e "${GREEN}[3]${RESET} API kalitni o‘zgartirish"
  echo -e "${GREEN}[0]${RESET} Chiqish"
  echo ""
  read -p "Tanlov (0-3): " tanlov
  echo ""

  case $tanlov in
    1)
      clear
      echo -e "${YELLOW}💬 AI bilan suhbat boshlandi. (0 - chiqish)${RESET}"
      echo ""
      while true; do
        read -p "$(echo -e ${BLUE}Siz:${RESET} )" user_msg
        if [[ "$user_msg" == "0" ]]; then
          echo -e "${CYAN}📴 Suhbat tugatildi.${RESET}"
          break
        fi

        echo -e "${YELLOW}AI javob yozmoqda...${RESET}"
        reply=$(ask_gemini "$user_msg")

        # Agar bo‘sh javob bo‘lsa yoki API ishlamasa
        if [[ -z "$reply" ]]; then
          echo -e "${RED}❌ Xatolik: javob olinmadi.${RESET}"
        else
          echo -e "${GREEN}AI:${RESET} $reply"
          echo "Siz: $user_msg" >> "$CHAT_FILE"
          echo "AI: $reply" >> "$CHAT_FILE"
          echo "" >> "$CHAT_FILE"
        fi
      done
      ;;
    2)
      clear
      echo -e "${CYAN}📜 So‘nggi yozishmalar:${RESET}"
      echo ""
      cat "$CHAT_FILE" | fold -s -w 80
      echo ""
      read -p "Davom etish uchun [Enter] bosing..."
      ;;
    3)
      read -p "Yangi API kalit: " newkey
      API_KEY="$newkey"
      echo -e "${GREEN}✅ API kalit yangilandi.${RESET}"
      sleep 1
      ;;
    0)
      echo -e "${YELLOW}Chiqilmoqda...${RESET}"
      exit 0
      ;;
    *)
      echo -e "${RED}❌ Noto‘g‘ri tanlov.${RESET}"
      ;;
  esac
done
