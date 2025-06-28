FROM ubuntu:22.04

# Установка переменных окружения
ENV DEBIAN_FRONTEND=noninteractive
ENV GO111MODULE=on
ENV GOPROXY=direct

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
    && rm -rf /var/lib/apt/lists/*

# Установка Go
RUN wget https://go.dev/dl/go1.21.5.linux-amd64.tar.gz \
    && tar -C /usr/local -xzf go1.21.5.linux-amd64.tar.gz \
    && rm go1.21.5.linux-amd64.tar.gz

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

# Установка Python пакетов
RUN pip3 install --no-cache-dir \
    requests \
    httpx \
    beautifulsoup4 \
    lxml \
    colorama \
    tqdm

# Обновление nuclei templates
RUN nuclei -update-templates

# Создание рабочей директории
WORKDIR /app

# Копирование скриптов
COPY *.py ./
COPY *.md ./
COPY install.sh ./

# Создание директории для результатов
RUN mkdir -p /app/results

# Установка прав на выполнение
RUN chmod +x *.py install.sh

# Точка входа
ENTRYPOINT ["python3"]
CMD ["run_all.py"] 