#!/bin/bash

# BagBountyAuto - Автоматическая установка зависимостей
# Для Ubuntu/Debian серверов

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

# Проверка на root права
check_root() {
    if [[ $EUID -eq 0 ]]; then
        print_warning "Скрипт запущен с root правами. Рекомендуется запускать от обычного пользователя."
        read -p "Продолжить? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# Определение версии Ubuntu
get_ubuntu_version() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        UBUNTU_VERSION=$VERSION_CODENAME
        UBUNTU_MAJOR_VERSION=$(echo $VERSION_ID | cut -d. -f1)
        echo "Ubuntu $VERSION_ID ($VERSION_CODENAME)"
    else
        print_error "Не удалось определить версию Ubuntu"
        exit 1
    fi
}

# Очистка проблемных репозиториев
cleanup_repositories() {
    print_status "Очистка проблемных репозиториев..."
    
    # Удаляем старые репозитории HashiCorp если они есть
    if [ -f /etc/apt/sources.list.d/hashicorp.list ]; then
        sudo rm -f /etc/apt/sources.list.d/hashicorp.list
        print_status "Удален старый репозиторий HashiCorp"
    fi
    
    # Очищаем кэш apt
    sudo apt clean
    print_success "Репозитории очищены"
}

# Обновление системы
update_system() {
    print_status "Обновление системы..."
    
    # Очищаем проблемные репозитории перед обновлением
    cleanup_repositories
    
    # Обновляем список пакетов
    sudo apt update || {
        print_warning "Обновление apt завершилось с предупреждениями, продолжаем..."
    }
    
    # Обновляем пакеты
    sudo apt upgrade -y
    print_success "Система обновлена"
}

# Установка базовых пакетов
install_basic_packages() {
    print_status "Установка базовых пакетов..."
    sudo apt install -y \
        curl \
        wget \
        git \
        unzip \
        build-essential \
        software-properties-common \
        apt-transport-https \
        ca-certificates \
        gnupg \
        lsb-release
    print_success "Базовые пакеты установлены"
}

# Установка Python
install_python() {
    print_status "Проверка Python..."
    if ! command -v python3 &> /dev/null; then
        print_status "Установка Python 3..."
        sudo apt install -y python3 python3-pip python3-venv
    else
        print_success "Python 3 уже установлен"
    fi
    
    # Обновление pip
    python3 -m pip install --upgrade pip
    print_success "Python настроен"
}

# Установка Go
install_go() {
    print_status "Проверка Go..."
    if ! command -v go &> /dev/null; then
        print_status "Установка Go..."
        # Удаляем старую версию если есть
        sudo apt remove -y golang-go 2>/dev/null || true
        
        # Устанавливаем последнюю версию
        GO_VERSION="1.22.0"
        wget https://go.dev/dl/go${GO_VERSION}.linux-amd64.tar.gz
        sudo rm -rf /usr/local/go
        sudo tar -C /usr/local -xzf go${GO_VERSION}.linux-amd64.tar.gz
        rm go${GO_VERSION}.linux-amd64.tar.gz
        
        # Добавляем в PATH
        echo 'export PATH=$PATH:/usr/local/go/bin' >> ~/.bashrc
        echo 'export PATH=$PATH:/usr/local/go/bin' >> ~/.zshrc
        export PATH=$PATH:/usr/local/go/bin
    else
        print_success "Go уже установлен"
    fi
    
    # Настройка Go
    go env -w GO111MODULE=on
    go env -w GOPROXY=direct
    print_success "Go настроен"
}

# Установка Go инструментов
install_go_tools() {
    print_status "Установка Go инструментов..."
    
    # Создаем директорию для Go bin если её нет
    mkdir -p ~/go/bin
    
    # Добавляем в PATH
    echo 'export PATH=$PATH:~/go/bin' >> ~/.bashrc
    echo 'export PATH=$PATH:~/go/bin' >> ~/.zshrc
    export PATH=$PATH:~/go/bin
    
    # Устанавливаем инструменты
    tools=(
        "github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest"
        "github.com/projectdiscovery/httpx/cmd/httpx@latest"
        "github.com/tomnomnom/waybackurls@latest"
        "github.com/projectdiscovery/katana/cmd/katana@latest"
        "github.com/projectdiscovery/nuclei/v2/cmd/nuclei@latest"
        "github.com/trufflesecurity/trufflehog/v3/cmd/trufflehog@latest"
    )
    
    for tool in "${tools[@]}"; do
        print_status "Установка $tool..."
        go install -v $tool
    done
    
    print_success "Go инструменты установлены"
}

# Установка SQLMap
install_sqlmap() {
    print_status "Проверка SQLMap..."
    if ! command -v sqlmap &> /dev/null; then
        print_status "Установка SQLMap..."
        cd ~
        git clone --depth 1 https://github.com/sqlmapproject/sqlmap.git sqlmap-dev
        sudo ln -sf ~/sqlmap-dev/sqlmap.py /usr/local/bin/sqlmap
        print_success "SQLMap установлен"
    else
        print_success "SQLMap уже установлен"
    fi
}

# Установка Python пакетов
install_python_packages() {
    print_status "Установка Python пакетов..."
    
    # Проверяем, есть ли python3-full
    if ! dpkg -l | grep -q python3-full; then
        print_status "Установка python3-full..."
        sudo apt install -y python3-full
    fi
    
    # Создаем виртуальное окружение для проекта
    print_status "Создание виртуального окружения..."
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    
    # Активируем виртуальное окружение
    source venv/bin/activate
    
    # Обновляем pip в виртуальном окружении
    pip install --upgrade pip
    
    # Устанавливаем пакеты в виртуальное окружение
    pip install \
        requests \
        httpx \
        beautifulsoup4 \
        lxml \
        colorama \
        tqdm
    
    # Деактивируем виртуальное окружение
    deactivate
    
    # Создаем скрипт-обертку для запуска с виртуальным окружением
    cat > bagbounty_wrapper.sh << 'EOF'
#!/bin/bash
# Обертка для запуска BagBountyAuto с виртуальным окружением

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="$SCRIPT_DIR/venv"

if [ ! -d "$VENV_PATH" ]; then
    echo "Виртуальное окружение не найдено. Запустите ./install.sh"
    exit 1
fi

# Активируем виртуальное окружение и запускаем скрипт
source "$VENV_PATH/bin/activate"
python3 "$SCRIPT_DIR/bagbounty.py" "$@"
EOF
    
    chmod +x bagbounty_wrapper.sh
    
    print_success "Python пакеты установлены в виртуальное окружение"
    print_warning "Используйте ./bagbounty_wrapper.sh вместо python3 bagbounty.py"
}

# Обновление nuclei templates
update_nuclei_templates() {
    print_status "Обновление nuclei templates..."
    if command -v nuclei &> /dev/null; then
        nuclei -update-templates
        print_success "Nuclei templates обновлены"
    else
        print_warning "Nuclei не найден, пропускаем обновление templates"
    fi
}

# Создание конфигурационных файлов
create_configs() {
    print_status "Создание конфигурационных файлов..."
    
    # Создаем .bashrc если его нет
    touch ~/.bashrc
    
    # Добавляем переменные окружения
    if ! grep -q "export PATH.*go/bin" ~/.bashrc; then
        echo 'export PATH=$PATH:/usr/local/go/bin:~/go/bin' >> ~/.bashrc
    fi
    
    # Создаем .zshrc если используем zsh
    if [ -f ~/.zshrc ]; then
        if ! grep -q "export PATH.*go/bin" ~/.zshrc; then
            echo 'export PATH=$PATH:/usr/local/go/bin:~/go/bin' >> ~/.zshrc
        fi
    fi
    
    print_success "Конфигурационные файлы созданы"
}

# Проверка установки
verify_installation() {
    print_status "Проверка установки..."
    
    tools=(
        "python3"
        "go"
        "subfinder"
        "httpx"
        "waybackurls"
        "katana"
        "nuclei"
        "sqlmap"
        "trufflehog"
        "wget"
        "curl"
        "git"
    )
    
    failed_tools=()
    
    for tool in "${tools[@]}"; do
        if command -v $tool &> /dev/null; then
            print_success "$tool - OK"
        else
            print_error "$tool - НЕ НАЙДЕН"
            failed_tools+=($tool)
        fi
    done
    
    # Проверяем виртуальное окружение и pip
    if [ -d "venv" ]; then
        if [ -f "venv/bin/pip" ]; then
            print_success "pip (в venv) - OK"
        else
            print_error "pip (в venv) - НЕ НАЙДЕН"
            failed_tools+=("pip")
        fi
    else
        print_warning "Виртуальное окружение не найдено"
        failed_tools+=("venv")
    fi
    
    if [ ${#failed_tools[@]} -eq 0 ]; then
        print_success "Все инструменты установлены успешно!"
    else
        print_warning "Следующие инструменты не найдены: ${failed_tools[*]}"
        print_warning "Попробуйте перезапустить терминал или выполнить: source ~/.bashrc"
    fi
}

# Основная функция
main() {
    echo -e "${GREEN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    BagBountyAuto Installer                   ║"
    echo "║              Автоматическая установка зависимостей           ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    check_root
    
    # Определяем версию Ubuntu
    get_ubuntu_version
    
    print_status "Начало установки BagBountyAuto зависимостей..."
    
    update_system
    install_basic_packages
    install_python
    install_go
    install_go_tools
    install_sqlmap
    install_python_packages
    update_nuclei_templates
    create_configs
    
    echo
    print_success "Установка завершена!"
    print_status "Перезапустите терминал или выполните: source ~/.bashrc"
    echo
    
    verify_installation
    
    echo
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗"
    echo "║                        Установка завершена!                        ║"
    echo "║                                                                  ║"
    echo "║  Для использования скриптов:                                    ║"
    echo "║  ./bagbounty_wrapper.sh example.com                             ║"
    echo "║  python3 manage_reports.py summary                              ║"
    echo "║                                                                  ║"
    echo "║  Документация: README.md и INSTALL.md                           ║"
    echo "║                                                                  ║"
    echo "║  Примечание: Python пакеты установлены в виртуальное окружение  ║"
    echo "║  Используйте bagbounty_wrapper.sh для запуска основного скрипта ║"
    echo "╚══════════════════════════════════════════════════════════════╝${NC}"
}

# Запуск основной функции
main "$@" 