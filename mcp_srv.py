from fastmcp import FastMCP, Context

from file_manager import FileManagerMCP

mcp = FastMCP("FileManager")

@mcp.tool()
def scan_files(directory: str = None) -> dict:
    """Сканирование файлов в указанной директории"""
    server = FileManagerMCP(base_path=directory or ".")
    return server.scan_directory()

@mcp.tool()
def organize_files(directory: str = None) -> dict:
    """Организация файлов по категориям"""
    server = FileManagerMCP(base_path=directory or ".")
    return server.organize_files()

@mcp.tool()
def find_duplicates(directory: str = None) -> dict:
    """Поиск дубликатов файлов"""
    server = FileManagerMCP(base_path=directory or ".")
    return server.find_duplicates()

@mcp.tool()
def generate_report(directory: str = None) -> str:
    """Генерация отчета о файловой системе"""
    server = FileManagerMCP(base_path=directory or ".")
    return server.generate_report()

if __name__ == "__main__":
    mcp.run(transport='streamable-http', host='100.111.202.65', port=80)
