#!/bin/bash

# BagBountyAuto - Альтернативная установка зависимостей (глобальная)
# Для пользователей, которые хотят установить Python пакеты глобально

set -e  # Остановка при ошибке

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функции для вывода
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Установка Python пакетов глобально (с --break-system-packages)
install_python_packages_global() {
    print_status "Установка Python пакетов глобально..."
    print_warning "Используется --break-system-packages (может нарушить системный Python)"
    
    # Устанавливаем пакеты глобально
    pip3 install --break-system-packages \
        requests \
        httpx \
        beautifulsoup4 \
        lxml \
        colorama \
        tqdm
    
    print_success "Python пакеты установлены глобально"
    print_warning "Теперь можно использовать: python3 bagbounty.py example.com"
}

# Основная функция
main() {
    echo -e "${GREEN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                BagBountyAuto Legacy Installer                ║"
    echo "║           Глобальная установка Python пакетов                ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    print_warning "Этот скрипт устанавливает Python пакеты глобально"
    print_warning "Это может нарушить системный Python (PEP 668)"
    read -p "Продолжить? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_status "Установка отменена. Используйте ./install.sh для безопасной установки"
        exit 1
    fi
    
    install_python_packages_global
    
    echo
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗"
    echo "║                    Установка завершена!                        ║"
    echo "║                                                                  ║"
    echo "║  Для использования скриптов:                                    ║"
    echo "║  python3 bagbounty.py example.com                               ║"
    echo "║  python3 manage_reports.py summary                              ║"
    echo "║                                                                  ║"
    echo "║  ВНИМАНИЕ: Python пакеты установлены глобально                 ║"
    echo "║  Рекомендуется использовать ./install.sh для безопасной установки ║"
    echo "╚══════════════════════════════════════════════════════════════╝${NC}"
}

# Запуск основной функции
main "$@" 