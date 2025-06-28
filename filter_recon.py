#!/usr/bin/env python3
import os
import re
import sys
import argparse
from urllib.parse import urlparse, parse_qs

# Расширения, которые считаются неинтересными (статикой)
STATIC_EXT = re.compile(
    r"\.(?:jpg|jpeg|png|gif|svg|css|woff2?|ttf|eot|ico|mp4|webm|avi|mov|mp3|ogg|wav|zip|rar|7z|tar|gz|webp|bmp|pdf|swf|psd|exe|dmg|apk|bin|jar|m4a|m4v|csv|md|txt|xml|map|log|yml|yaml|rss|atom|cache|bak|backup|dll|dat|db|lock|sh|bat|out|tmp|sample|example|test|spec|conf|config|manifest|robots\.txt)$", 
    re.I
)

# Паттерны для фильтрации мусора и 404
TRASH_PATTERNS = [
    re.compile(r"/(?:404|not[-_]?found|error|invalid|doesnotexist|missing|unavailable)/?$", re.I),
    re.compile(r"[?&](?:error|msg|message|reason)=", re.I),
]

def normalize_url(url):
    """Нормализация URL для дедупликации"""
    parsed = urlparse(url)
    # Удаление фрагмента
    clean_url = parsed._replace(fragment="").geturl()
    return clean_url.lower()

def is_interesting(url, args):
    """Проверяет, интересен ли URL для багбаунти"""
    # Проверка длины URL
    if len(url) > args.max_url_len:
        return False
        
    # Проверка портов
    parsed = urlparse(url)
    if args.exclude_ports and parsed.port:
        if parsed.port in args.exclude_ports:
            return False
    if args.exclude_non_std_ports and parsed.port:
        if parsed.port not in [80, 443]:
            return False

    url_lower = url.lower()
    
    # Фильтрация статики (с исключением для API)
    if STATIC_EXT.search(url_lower):
        # Оставляем API endpoints
        if not ("/api/" in url_lower or "/v1/" in url_lower or "/v2/" in url_lower):
            return False

    # Фильтрация мусорных паттернов
    for pat in TRASH_PATTERNS:
        if pat.search(url_lower):
            return False
            
    return True

def has_params(url):
    """Есть ли параметры в URL"""
    parsed = urlparse(url)
    return bool(parse_qs(parsed.query))

def clean_urls(input_file, output_file, args):
    seen = set()
    for line in input_file:
        url = line.strip()
        if not url:
            continue
            
        # Нормализация для дедупликации
        norm_url = normalize_url(url)
        if norm_url in seen:
            continue
        seen.add(norm_url)
        
        if not is_interesting(url, args):
            continue
            
        if args.params_only and not has_params(url):
            continue
            
        output_file.write(url + '\n')
    
    return len(seen)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Фильтрация и очистка URL для багбаунти",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "input", 
        nargs='?', 
        type=argparse.FileType('r'), 
        default=sys.stdin,
        help="Входной файл с URL (используйте '-' для stdin)"
    )
    parser.add_argument(
        "-o", "--output", 
        type=argparse.FileType('w'), 
        default=sys.stdout,
        help="Файл для сохранения очищенных URL"
    )
    parser.add_argument(
        "--params-only", 
        action="store_true",
        help="Оставлять только URL с параметрами"
    )
    parser.add_argument(
        "--exclude-ports",
        type=lambda s: [int(p) for p in s.split(',')],
        help="Список портов для исключения (через запятую)"
    )
    parser.add_argument(
        "--exclude-non-std-ports", 
        action="store_true",
        help="Исключить URL с нестандартными портами (кроме 80 и 443)"
    )
    parser.add_argument(
        "--max-url-len",
        type=int, 
        default=2000,
        help="Максимальная длина URL"
    )
    
    args = parser.parse_args()
    unique_count = clean_urls(args.input, args.output, args)
    print(f"Обработка завершена. Уникальных URL: {unique_count}", file=sys.stderr)