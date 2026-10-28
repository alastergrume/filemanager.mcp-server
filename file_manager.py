import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional
import json
from datetime import datetime
import hashlib


class FileManagerMCP:
    """MCP-сервер для управления файловой системой"""

    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.categories = {
            'food': ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'],
            'documents': ['pdf', 'doc', 'docx', 'txt', 'md', 'rtf'],
            'video': ['mp4', 'avi', 'mov', 'mkv', 'wmv'],
            'audio': ['mp3', 'wav', 'flac', 'aac', 'ogg'],
            'archives': ['zip', 'rar', '7z', 'tar', 'gz'],
            'other': []
        }

    def scan_directory(self, directory: str = None) -> Dict:
        """Сканирование директории и классификация файлов"""
        target = Path(directory) if directory else self.base_path
        results = {
            'files': [],
            'categories': {},
            'total_size': 0
        }

        for file_path in target.rglob('*'):
            if file_path.is_file():
                file_info = self._analyze_file(file_path)
                results['files'].append(file_info)
                results['total_size'] += file_info['size']

                category = self._classify_file(file_path)
                if category not in results['categories']:
                    results['categories'][category] = []
                results['categories'][category].append(str(file_path))

        return results

    def _analyze_file(self, file_path: Path) -> Dict:
        """Анализ файла для определения его характеристик"""
        stat = file_path.stat()
        return {
            'path': str(file_path),
            'name': file_path.name,
            'extension': file_path.suffix.lower(),
            'size': stat.st_size,
            'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'hash': self._calculate_hash(file_path)
        }

    def _classify_file(self, file_path: Path) -> str:
        """Классификация файла по категориям"""
        extension = file_path.suffix.lower().lstrip('.')

        for category, extensions in self.categories.items():
            if extension in extensions:
                return category
        return 'other'

    def _calculate_hash(self, file_path: Path) -> str:
        """Вычисление хэша файла для дедупликации"""
        hasher = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hasher.update(chunk)
        return hasher.hexdigest()

    def organize_files(self, directory: str = None) -> Dict:
        """Организация файлов по категориям"""
        target = Path(directory) if directory else self.base_path
        results = {
            'moved': [],
            'errors': [],
            'created_dirs': []
        }

        for file_path in target.iterdir():
            if file_path.is_file():
                category = self._classify_file(file_path)
                category_dir = target / category

                try:
                    if not category_dir.exists():
                        category_dir.mkdir()
                        results['created_dirs'].append(str(category_dir))

                    new_path = category_dir / file_path.name
                    shutil.move(str(file_path), str(new_path))
                    results['moved'].append({
                        'from': str(file_path),
                        'to': str(new_path)
                    })
                except Exception as e:
                    results['errors'].append({
                        'file': str(file_path),
                        'error': str(e)
                    })

        return results

    def find_duplicates(self, directory: str = None) -> Dict:
        """Поиск дубликатов файлов по хэшу"""
        target = Path(directory) if directory else self.base_path
        hash_map = {}

        for file_path in target.rglob('*'):
            if file_path.is_file():
                file_hash = self._calculate_hash(file_path)
                if file_hash not in hash_map:
                    hash_map[file_hash] = []
                hash_map[file_hash].append(str(file_path))

        duplicates = {h: paths for h, paths in hash_map.items() if len(paths) > 1}
        return {
            'duplicate_groups': duplicates,
            'total_duplicates': sum(len(v) - 1 for v in duplicates.values())
        }

    def generate_report(self, directory: str = None) -> str:
        """Генерация отчета о файловой системе"""
        scan_results = self.scan_directory(directory)

        report = []
        report.append("=" * 50)
        report.append("ОТЧЕТ О ФАЙЛОВОЙ СИСТЕМЕ")
        report.append(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 50)
        report.append(f"\nВсего файлов: {len(scan_results['files'])}")
        report.append(f"Общий размер: {self._format_size(scan_results['total_size'])}")

        report.append("\nРаспределение по категориям:")
        for category, files in scan_results['categories'].items():
            category_size = sum(
                self._get_file_size(f) for f in files
            )
            report.append(f"  {category}: {len(files)} файлов ({self._format_size(category_size)})")

        duplicates = self.find_duplicates(directory)
        report.append(f"\nДубликаты: {duplicates['total_duplicates']} файлов")

        return "\n".join(report)

    def _get_file_size(self, file_path: str) -> int:
        """Получение размера файла"""
        return Path(file_path).stat().st_size

    def _format_size(self, size: int) -> str:
        """Форматирование размера файла"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} TB"


# MCP Server Configuration
def create_mcp_server():
    """Создание MCP сервера"""
    server = FileManagerMCP(base_path="/path/to/your/directory")

    # Здесь можно добавить интеграцию с MCP протоколом
    # Например, через FastMCP или аналогичную библиотеку

    return server


if __name__ == "__main__":
    server = create_mcp_server()

    # Пример использования
    print(server.generate_report())

    # Организация файлов
    result = server.organize_files()
    print(f"\nПеремещено файлов: {len(result['moved'])}")