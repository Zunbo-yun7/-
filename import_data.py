"""
数据导入脚本 - 从PDF提取单词和页码
请将PDF内容复制到 data.txt 文件中，格式：单词,页码
例如：abandon,1
"""
import sqlite3

DATABASE = 'words.db'

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS words (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            word TEXT NOT NULL UNIQUE,
            phonetic TEXT,
            definition TEXT,
            page INTEGER
        )
    ''')
    # 创建索引加速搜索
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_word ON words(word)')
    conn.commit()
    conn.close()
    print("数据库初始化完成")

def import_from_text(filename):
    """从文本文件导入数据"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    imported = 0
    skipped = 0
    issues = []

    with open(filename, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            # 只按第一个逗号分割 (格式: word,page)
            idx = line.find(',')
            if idx > 0:
                word = line[:idx].strip()
                page_str = line[idx+1:].strip()
                try:
                    page = int(page_str)
                    word_lower = word.lower()
                    cursor.execute(
                        "INSERT OR IGNORE INTO words (word, page) VALUES (?, ?)",
                        (word_lower, page)
                    )
                    if cursor.rowcount > 0:
                        imported += 1
                    else:
                        skipped += 1
                except ValueError:
                    issues.append(line)
            else:
                issues.append(line)

    conn.commit()
    conn.close()
    print(f"导入完成: {imported} 条新记录, {skipped} 条跳过")
    if issues:
        print(f"无法解析的行 ({len(issues)} 条):")
        for line in issues[:5]:
            print(f"  · {line}")
        if len(issues) > 5:
            print(f"  ... 还有 {len(issues) - 5} 条")

def export_sample():
    """导出示例数据用于测试"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # 插入一些常见GRE词汇作为示例
    sample_words = [
        ('aberrant', '1'),
    ]

    for word, page in sample_words:
        cursor.execute(
            "INSERT OR IGNORE INTO words (word, page) VALUES (?, ?)",
            (word, int(page))
        )

    conn.commit()
    conn.close()
    print(f"已导入 {len(sample_words)} 条示例词汇")

if __name__ == '__main__':
    import sys

    init_db()

    if len(sys.argv) > 1:
        if sys.argv[1] == 'sample':
            export_sample()
        elif sys.argv[1] == 'import':
            if len(sys.argv) > 2:
                import_from_text(sys.argv[2])
            else:
                print("用法: python import_data.py import <文件名>")
    else:
        print("用法:")
        print("  python import_data.py sample    - 导入示例数据")
        print("  python import_data.py import <文件名>  - 从文本文件导入")
