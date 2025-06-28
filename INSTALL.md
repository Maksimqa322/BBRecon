# Установка инструментов для BagBountyAuto

## Требования
- Python 3.8+ и pip
- Go 1.16+
- Linux (рекомендуется Ubuntu/Debian)

## 1. Установка Python и pip
```bash
sudo apt update
sudo apt install python3 python3-pip
```

## 2. Установка Go
```bash
sudo apt install golang-go
```

## 3. Установка инструментов Recon
```bash
# Subfinder
GO111MODULE=on go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
# httpx
GO111MODULE=on go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest
# waybackurls
GO111MODULE=on go install github.com/tomnomnom/waybackurls@latest
# katana
GO111MODULE=on go install github.com/projectdiscovery/katana/cmd/katana@latest
# nuclei
GO111MODULE=on go install -v github.com/projectdiscovery/nuclei/v2/cmd/nuclei@latest
# nuclei templates
nuclei -update-templates

# Добавьте Go bin в PATH (добавьте в ~/.bashrc или ~/.zshrc):
export PATH=$PATH:$(go env GOPATH)/bin
```

## 4. Установка SQLMap
```bash
git clone --depth 1 https://github.com/sqlmapproject/sqlmap.git sqlmap-dev
cd sqlmap-dev
sudo ln -s $(pwd)/sqlmap.py /usr/local/bin/sqlmap
```

## 5. Установка TruffleHog
```bash
pip3 install truffleHog
# или через Go
GO111MODULE=on go install github.com/trufflesecurity/trufflehog/v3/cmd/trufflehog@latest
```

## 6. Установка системных утилит
```bash
sudo apt install wget grep sed curl
```

## 7. Проверка установки
```bash
subfinder --version
httpx --version
waybackurls --help
katana --version
nuclei --version
sqlmap --version
trufflehog --version
wget --version
curl --version
```

## Примечания
- Для ускорения работы используйте SSD и быстрый интернет.
- Для nuclei рекомендуется регулярно обновлять шаблоны.
- Для некоторых инструментов могут понадобиться API-ключи.

## Использование скриптов

### Основная разведка
```bash
# Запуск разведки для домена
python3 recon.py example.com
```

### Фильтрация результатов
```bash
# Базовая фильтрация
python3 filter_recon.py recon-example.com/urls/all_urls.txt -o filtered_urls.txt

# Только URL с параметрами
python3 filter_recon.py recon-example.com/urls/all_urls.txt -o param_urls.txt --params-only

# Исключить нестандартные порты
python3 filter_recon.py recon-example.com/urls/all_urls.txt -o filtered_urls.txt --exclude-non-std-ports
```

### Анализ уязвимостей
```bash
# Анализ собранных URL на уязвимости
python3 analyze.py recon-example.com
```

### Сканирование уязвимостей
```bash
# Полное сканирование уязвимостей
python3 vuln_scanner.py recon-example.com

# Сканирование без sqlmap
python3 vuln_scanner.py recon-example.com --skip-sqlmap

# Сканирование только секретов
python3 vuln_scanner.py recon-example.com --skip-nuclei --skip-sqlmap
```

## Структура результатов
После выполнения скрипта будет создана структура:
```
recon-example.com/
├── subdomains/
│   ├── subdomains.txt
│   └── alive.txt
├── urls/
│   ├── all_urls.txt
│   ├── filtered_urls.txt
│   ├── sensitive_files.txt
│   ├── param_urls.txt
│   ├── js_files.txt
│   ├── php_files.txt
│   └── api_endpoints.txt
├── files/
│   ├── sensitive/
│   ├── js/
│   └── php/
├── waybackurls/
│   └── waybackurls_urls.txt
├── katana/
│   └── katana_urls.txt
├── analysis/
│   ├── sqli_urls.txt
│   ├── xss_urls.txt
│   ├── lfi_urls.txt
│   ├── ssrf_urls.txt
│   ├── open_redirect_urls.txt
│   └── vulnerability_report.md
├── vuln_scan/
│   ├── secrets_found.txt
│   ├── nuclei_general_report.txt
│   ├── sqlmap_report_*.txt
│   ├── manual_payload_results.txt
│   └── vulnerability_scan_report_*.md
├── logs/
└── report_YYYYMMDD-HHMMSS.md
```

## Параметры фильтрации

Скрипт `filter_recon.py` поддерживает следующие параметры:

- `--params-only` - оставлять только URL с параметрами
- `--exclude-ports 8080,8443` - исключить указанные порты
- `--exclude-non-std-ports` - исключить нестандартные порты (не 80/443)
- `--max-url-len 2000` - максимальная длина URL

## Параметры сканера уязвимостей

Скрипт `vuln_scanner.py` поддерживает следующие параметры:

- `--urls` - файл с URL для тестирования
- `--files` - директория с файлами для сканирования секретов
- `--output` - директория для результатов
- `--threads` - количество потоков
- `--skip-secrets` - пропустить поиск секретов
- `--skip-sqlmap` - пропустить sqlmap
- `--skip-nuclei` - пропустить nuclei

## Примечания
- Убедитесь, что у вас есть разрешение на тестирование целевого домена
- Некоторые инструменты могут требовать API ключи для лучших результатов
- Скрипт создает подробный отчет в формате Markdown
- Фильтрация помогает очистить результаты от мусора и дубликатов
- Анализ уязвимостей выявляет потенциальные точки для тестирования
- Сканер уязвимостей использует лучшие инструменты для комплексного тестирования
- SQLMap может быть медленным, используйте с осторожностью
- Nuclei автоматически обновляет шаблоны уязвимостей 
- Nuclei автоматически обновляет шаблоны уязвимостей 