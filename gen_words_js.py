import os
import json

words = []
with open('data.txt', 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        idx = line.rfind(',')
        if idx > 0:
            word = line[:idx].strip()
            try:
                page = int(line[idx+1:].strip())
                words.append([word, page])
            except ValueError:
                continue

js_content = 'window.WORDS_DATA = ' + json.dumps(words, ensure_ascii=False) + ';'
with open('words.js', 'w', encoding='utf-8') as f:
    f.write(js_content)

print('已生成 words.js，共 ' + str(len(words)) + ' 条单词记录')
print('文件大小: ' + str(os.path.getsize('words.js')) + ' bytes')
print('前5条: ' + str(words[:5]))
