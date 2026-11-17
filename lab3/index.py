"""Build an atomic, versioned FTS5 index from the checked-in knowledge base."""
import hashlib, json, os, re, sqlite3, subprocess, sys, tempfile
from pathlib import Path
import snowballstemmer
ROOT = Path(__file__).resolve().parent
CORPUS = Path(os.getenv('CORPUS_PATH', str(ROOT / 'corpus.json')))
INDEX = Path(os.getenv('INDEX_PATH', str(ROOT / 'index.sqlite')))
STEM = snowballstemmer.stemmer('russian')
def normalize(text):
    words = re.findall(r'[a-zа-я0-9]+', text.lower().replace('ё', 'е'))
    return ' '.join(STEM.stemWord(w) if re.search('[а-я]', w) else w for w in words)
def build():
    subprocess.run([sys.executable, str(ROOT/'validate_corpus.py')], check=True)
    raw = CORPUS.read_bytes(); corpus = json.loads(raw)
    fd, filename = tempfile.mkstemp(prefix='index-', suffix='.sqlite', dir=INDEX.parent); os.close(fd)
    try:
        db = sqlite3.connect(filename)
        db.executescript('''CREATE TABLE meta (digest TEXT NOT NULL);
        CREATE TABLE chunks (id INTEGER PRIMARY KEY, doc_id TEXT NOT NULL, version TEXT NOT NULL,
          title TEXT NOT NULL, status TEXT NOT NULL, visibility TEXT NOT NULL, path TEXT NOT NULL,
          anchor TEXT NOT NULL, section_title TEXT NOT NULL, chunk_id INTEGER NOT NULL, body TEXT NOT NULL);
        CREATE VIRTUAL TABLE search USING fts5(tokens, content='', tokenize='unicode61');''')
        db.execute('INSERT INTO meta VALUES (?)',(hashlib.sha256(raw).hexdigest(),))
        for group in corpus['sections']:
            for subgroup in group['subsections']:
                for d in subgroup['documents']:
                    for section in d['sections']:
                        words = ' '.join(section['body']).split()
                        for i in range(0,len(words),150):
                            body=' '.join(words[i:i+150]); path=' / '.join(d['path'])
                            cur=db.execute('INSERT INTO chunks (doc_id,version,title,status,visibility,path,anchor,section_title,chunk_id,body) VALUES (?,?,?,?,?,?,?,?,?,?)', (d['id'],d['version'],d['title'],d['status'],d['visibility'],path,section['anchor'],section['title'],i//150,body))
                            terms=normalize(' '.join([d['id'],d['title'],path,section['title'],body]))
                            db.execute('INSERT INTO search(rowid,tokens) VALUES (?,?)',(cur.lastrowid,terms))
        db.commit()
        assert db.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
        print('Indexed chunks:',db.execute('SELECT count(*) FROM chunks').fetchone()[0]); db.close()
        os.replace(filename,INDEX)
    finally:
        if os.path.exists(filename): os.unlink(filename)
if __name__ == '__main__': build()
