FROM ubuntu:24.04

# Установка переменных окружения
ENV DEBIAN_FRONTEND=noninteractive
ENV GO111MODULE=on
ENV GOPROXY=direct
ENV BAGBOUNTY_REPORTS_DIR=/app/reports

# Обновление системы и установка базовых пакетов
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    unzip \
    build-essential \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release \
    python3 \
    python3-pip \
    python3-venv \
    python3-full \
    ruby \
    ruby-dev \
    ruby-bundler \
    && rm -rf /var/lib/apt/lists/*

# Установка Go
RUN wget https://go.dev/dl/go1.22.0.linux-amd64.tar.gz \
    && tar -C /usr/local -xzf go1.22.0.linux-amd64.tar.gz \
    && rm go1.22.0.linux-amd64.tar.gz

# Настройка PATH
ENV PATH=$PATH:/usr/local/go/bin

# Установка Go инструментов
RUN go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest \
    && go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest \
    && go install github.com/tomnomnom/waybackurls@latest \
    && go install github.com/projectdiscovery/katana/cmd/katana@latest \
    && go install -v github.com/projectdiscovery/nuclei/v2/cmd/nuclei@latest \
    && go install github.com/trufflesecurity/trufflehog/v3/cmd/trufflehog@latest

# Добавление Go bin в PATH
ENV PATH=$PATH:/root/go/bin

# Установка SQLMap
RUN git clone --depth 1 https://github.com/sqlmapproject/sqlmap.git /opt/sqlmap \
    && ln -sf /opt/sqlmap/sqlmap.py /usr/local/bin/sqlmap

# Установка wayback_machine_downloader
RUN gem install wayback_machine_downloader

# Создание рабочей директории
WORKDIR /app

# Копирование исходного кода
COPY . .

# Создание виртуального окружения и установка Python пакетов
RUN python3 -m venv venv \
    && . venv/bin/activate \
    && pip install --upgrade pip \
    && pip install \
        requests \
        httpx \
        beautifulsoup4 \
        lxml \
        colorama \
        tqdm \
    && deactivate

# Создание скрипта-обертки для Docker
RUN echo '#!/bin/bash' > bagbounty_docker.sh && \
    echo '# Обертка для запуска BagBountyAuto в Docker' >> bagbounty_docker.sh && \
    echo '' >> bagbounty_docker.sh && \
    echo 'SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"' >> bagbounty_docker.sh && \
    echo 'VENV_PATH="$SCRIPT_DIR/venv"' >> bagbounty_docker.sh && \
    echo '' >> bagbounty_docker.sh && \
    echo '# Активируем виртуальное окружение и запускаем скрипт' >> bagbounty_docker.sh && \
    echo 'source "$VENV_PATH/bin/activate"' >> bagbounty_docker.sh && \
    echo 'python3 "$SCRIPT_DIR/bagbounty.py" "$@"' >> bagbounty_docker.sh

# Создание структуры директорий для отчетов
RUN mkdir -p /app/reports/{recon_reports,analysis_reports,vuln_scan_reports,filtered_reports,logs}

# Обновление nuclei templates
RUN nuclei -update-templates

# Установка прав на выполнение
RUN chmod +x *.py *.sh

# Создание volume для отчетов
VOLUME ["/app/reports"]

# Точка входа
ENTRYPOINT ["./bagbounty_docker.sh"]
CMD ["--help"] 