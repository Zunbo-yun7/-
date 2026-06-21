import json

# 读取 words.js 中的数据
with open('words.js', 'r', encoding='utf-8') as f:
    content = f.read()
# 提取 JSON 部分
json_start = content.index('[')
json_end = content.rindex(']') + 1
words_data = json.loads(content[json_start:json_end])

print(f'词库大小: {len(words_data)} 条')
print(f'前 5 条: {words_data[:5]}')
print()

# 预处理
WORDS = [{
    'word': w[0],
    'wordLower': w[0].lower(),
    'page': w[1]
} for w in words_data]

def levenshtein_distance(s1, s2):
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)
    previous_row = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]

def search_exact(query):
    q = query.lower()
    for w in WORDS:
        if w['wordLower'] == q:
            return w
    return None

def search_prefix(query, limit=15):
    q = query.lower()
    results = []
    for w in WORDS:
        if w['wordLower'].startswith(q):
            results.append(w)
            if len(results) >= limit:
                break
    results.sort(key=lambda x: x['wordLower'])
    return results

def search_contains(query, limit=15):
    q = query.lower()
    results = []
    for w in WORDS:
        if q in w['wordLower']:
            results.append(w)
            if len(results) >= limit:
                break
    results.sort(key=lambda x: x['wordLower'])
    return results

def search_similar(query, limit=10):
    q = query.lower()
    max_dist = 1 if len(q) <= 3 else (2 if len(q) <= 6 else 3)
    scored = []
    for w in WORDS:
        dist = levenshtein_distance(q, w['wordLower'])
        if dist <= max_dist and dist > 0:
            scored.append({'dist': dist, 'word': w})
    scored.sort(key=lambda x: (x['dist'], x['word']['wordLower']))
    return [s['word'] for s in scored[:limit]]

def perform_search(query):
    exact = search_exact(query)
    prefix = search_prefix(query, 15)
    contains = search_contains(query, 15)
    similar = search_similar(query, 10)

    exact_list = [exact] if exact else []
    q_lower = query.lower()

    prefix_filtered = [w for w in prefix if w['wordLower'] != q_lower]
    existing = set()
    if exact:
        existing.add(exact['wordLower'])
    for w in prefix_filtered:
        existing.add(w['wordLower'])

    contains_filtered = []
    for w in contains:
        if w['wordLower'] not in existing:
            contains_filtered.append(w)
            existing.add(w['wordLower'])

    similar_filtered = []
    for w in similar:
        if w['wordLower'] not in existing:
            similar_filtered.append(w)
            existing.add(w['wordLower'])

    total = len(exact_list) + len(prefix_filtered) + len(contains_filtered) + len(similar_filtered)

    return {
        'query': query,
        'found': total > 0,
        'total': total,
        'exact': exact_list,
        'prefix': prefix_filtered,
        'contains': contains_filtered,
        'similar': similar_filtered
    }

# 测试
for test_query in ['abandon', 'aberr', 'acqui', 'ambigu', 'python', 'xxx']:
    print(f'--- 查询: {test_query} ---')
    r = perform_search(test_query)
    print(f'找到: {r["found"]}, 总数: {r["total"]}')
    if r['exact']:
        print(f'  精确: {[(w["word"], w["page"]) for w in r["exact"][:3]]}')
    if r['prefix']:
        print(f'  前缀: {[(w["word"], w["page"]) for w in r["prefix"][:3]]}')
    if r['contains']:
        print(f'  包含: {[(w["word"], w["page"]) for w in r["contains"][:3]]}')
    if r['similar']:
        print(f'  相近: {[(w["word"], w["page"]) for w in r["similar"][:3]]}')
    print()

print('✅ 搜索逻辑测试完成')
