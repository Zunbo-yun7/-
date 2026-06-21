from flask import Flask, request, jsonify, send_from_directory
import urllib.request
import urllib.parse
import json
import os

app = Flask(__name__, static_folder='.')

WORDS_LIST = []

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def load_words_from_file():
    """从 data.txt 加载单词列表到内存"""
    txt_file = os.path.join(BASE_DIR, 'data.txt')
    
    if not os.path.exists(txt_file):
        print(f"[警告] 未找到数据文件 {txt_file}，词库为空")
        return
    
    words = []
    with open(txt_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            idx = line.find(',')
            if idx > 0:
                word = line[:idx].strip()
                page_str = line[idx+1:].strip()
                try:
                    page = int(page_str)
                    words.append({
                        'word': word.lower(),
                        'page': page,
                        'definition': None,
                        'phonetic': None
                    })
                except ValueError:
                    continue
    
    global WORDS_LIST
    WORDS_LIST = words
    print(f"[数据] 已从 data.txt 加载 {len(words)} 条单词记录")


def levenshtein_distance(s1, s2):
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)
    
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]


def search_exact(word):
    word = word.lower()
    for w in WORDS_LIST:
        if w['word'] == word:
            return w
    return None


def search_prefix(word):
    word = word.lower()
    results = []
    for w in WORDS_LIST:
        if w['word'].startswith(word):
            results.append(w)
            if len(results) >= 15:
                break
    return sorted(results, key=lambda x: x['word'])


def search_contains(word):
    word = word.lower()
    results = []
    for w in WORDS_LIST:
        if word in w['word']:
            results.append(w)
            if len(results) >= 15:
                break
    return sorted(results, key=lambda x: x['word'])


def search_similar(word, limit=10):
    word_lower = word.lower()
    max_distance = 1 if len(word) <= 3 else 2 if len(word) <= 6 else 3
    
    scored = []
    for w in WORDS_LIST:
        dist = levenshtein_distance(word_lower, w['word'])
        if dist <= max_distance and dist > 0:
            scored.append((dist, w))
    
    scored.sort(key=lambda x: (x[0], x[1]['word']))
    return [w for _, w in scored[:limit]]


def get_network_definition(word):
    try:
        url = f"https://dict.youdao.com/jsonapi?q={urllib.parse.quote(word)}"
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
        
        if 'ec' in data and 'word' in data['ec']:
            word_data = data['ec']['word']
            if word_data and len(word_data) > 0:
                trs = word_data[0].get('trs', [])
                if trs:
                    definitions = []
                    for tr in trs[:3]:
                        if 'tr' in tr and 'l' in tr['tr'] and 'i' in tr['tr']['l']:
                            defn = tr['tr']['l']['i']
                            if isinstance(defn, list):
                                defn = '; '.join([d.get('#text', '') for d in defn if '#text' in d])
                            elif isinstance(defn, dict) and '#text' in defn:
                                defn = defn['#text']
                            definitions.append(str(defn))
                    if definitions:
                        return '; '.join(definitions)
    except Exception as e:
        print(f"Network definition error: {e}")
    return None


@app.route('/')
def index():
    return send_from_directory('.', 'index.html')


@app.route('/api/search')
def api_search():
    query = request.args.get('q', '').strip().lower()
    
    if not query:
        return jsonify({
            'query': query,
            'found': False,
            'exact': [],
            'prefix': [],
            'contains': [],
            'similar': [],
            'network_definition': None
        })
    
    exact = search_exact(query)
    prefix = search_prefix(query)
    contains = search_contains(query)
    similar = search_similar(query)
    
    exact_list = [exact] if exact else []
    
    prefix_filtered = [w for w in prefix if w['word'].lower() != query.lower()]
    
    contains_filtered = [w for w in contains if w['word'].lower() != query.lower()
                          and not any(w['word'].lower() == p['word'].lower() for p in prefix_filtered)]
    
    existing_words = set()
    if exact:
        existing_words.add(exact['word'].lower())
    for w in prefix_filtered + contains_filtered:
        existing_words.add(w['word'].lower())
    
    similar_filtered = [w for w in similar if w['word'].lower() not in existing_words]
    
    total = len(exact_list) + len(prefix_filtered) + len(contains_filtered) + len(similar_filtered)
    
    network_def = None
    if total == 0:
        network_def = get_network_definition(query)
    
    return jsonify({
        'query': query,
        'found': total > 0,
        'total': total,
        'exact': exact_list,
        'prefix': prefix_filtered,
        'contains': contains_filtered,
        'similar': similar_filtered,
        'network_definition': network_def
    })


if __name__ == '__main__':
    load_words_from_file()
    
    import socket
    lan_ip = "127.0.0.1"
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        lan_ip = s.getsockname()[0]
        s.close()
    except Exception:
        pass
    
    print("=" * 50)
    print("  红宝书词典服务器已启动")
    print("=" * 50)
    print()
    print(f"  本机访问:  http://localhost:5000")
    print(f"  手机访问:  http://{lan_ip}:5000")
    print()
    print("  提示: 手机和电脑需在同一 WiFi 网络下")
    print("=" * 50)
    print()
    
    app.run(host='0.0.0.0', port=5000)
