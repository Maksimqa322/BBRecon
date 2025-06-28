#!/bin/bash

# BagBountyAuto Wrapper Script
# Автоматически активирует виртуальное окружение и запускает основной скрипт

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функции для вывода
print_status() {
    echo -e "${BLUE}[*]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[+]${NC} $1"
}

print_error() {
    echo -e "${RED}[-]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

# Проверяем, что скрипт запущен из корневой директории проекта
if [ ! -f "bagbounty.py" ]; then
    print_error "Скрипт должен быть запущен из корневой директории проекта BagBountyAuto"
    exit 1
fi

# Проверяем наличие виртуального окружения
if [ ! -d "venv" ]; then
    print_warning "Виртуальное окружение не найдено. Создаем..."
    python3 -m venv venv
    print_success "Виртуальное окружение создано"
fi

# Активируем виртуальное окружение
print_status "Активация виртуального окружения..."
source venv/bin/activate

# Проверяем установленные пакеты
if ! pip show requests >/dev/null 2>&1; then
    print_warning "Python пакеты не установлены. Устанавливаем..."
    pip install -r requirements.txt 2>/dev/null || {
        print_error "Не удалось установить пакеты. Запустите ./install.sh"
        exit 1
    }
    print_success "Пакеты установлены"
fi

# Проверяем аргументы
if [ $# -eq 0 ]; then
    print_error "Использование: $0 <домен> [опции]"
    echo ""
    echo "Примеры:"
    echo "  $0 example.com"
    echo "  $0 example.com --recon-only"
    echo "  $0 example.com --skip-scan"
    echo "  $0 example.com --show-timing"
    echo "  $0 example.com --show-summary"
    echo ""
    echo "Опции:"
    echo "  --recon-only       Только разведка"
    echo "  --skip-scan        Пропустить активное сканирование"
    echo "  --show-timing      Показать статистику времени выполнения"
    echo "  --show-summary     Показать сводку отчетов"
    echo "  --cleanup-reports  Очистить старые отчеты"
    echo "  --threads N        Количество потоков (по умолчанию: 3)"
    exit 1
fi

# Запускаем основной скрипт с переданными аргументами
print_status "Запуск BagBountyAuto..."
python3 bagbounty.py "$@"

# Деактивируем виртуальное окружение
deactivate

print_success "BagBountyAuto завершен" 