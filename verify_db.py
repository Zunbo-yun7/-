import sqlite3

conn = sqlite3.connect('words.db')
c = conn.cursor()

c.execute('SELECT COUNT(*) FROM words')
print(f"数据库总记录数: {c.fetchone()[0]}")

print("\n=== 前 10 条 ===")
c.execute('SELECT word, page FROM words LIMIT 10')
for word, page in c.fetchall():
    print(f"  {word:<25}  -> 第 {page} 页")

print("\n=== 搜索 'abandon' ===")
c.execute("SELECT word, page FROM words WHERE word LIKE ? LIMIT 10", ('%abandon%',))
for word, page in c.fetchall():
    print(f"  {word:<25}  -> 第 {page} 页")

print("\n=== 搜索 'aberr' (前缀) ===")
c.execute("SELECT word, page FROM words WHERE word LIKE ? LIMIT 10", ('aberr%',))
for word, page in c.fetchall():
    print(f"  {word:<25}  -> 第 {page} 页")

print("\n=== 含 'ment' 的单词 ===")
c.execute("SELECT word, page FROM words WHERE word LIKE ? LIMIT 10", ('%ment%',))
for word, page in c.fetchall():
    print(f"  {word:<25}  -> 第 {page} 页")

print("\n=== 第 24 页的所有单词 ===")
c.execute("SELECT word FROM words WHERE page = 24")
words_24 = [row[0] for row in c.fetchall()]
print(f"  共 {len(words_24)} 个: {', '.join(words_24)}")

print("\n=== 一些特殊单词 ===")
for w in ['a/an', 'according to', 'accommodation(s)']:
    c.execute("SELECT word, page FROM words WHERE word = ?", (w,))
    row = c.fetchone()
    if row:
        print(f"  {row[0]:<25}  -> 第 {row[1]} 页")
    else:
        print(f"  {w:<25}  -> 未找到")

conn.close()
