"""Backbone Core Dashboard - Python Backend (SQLite)"""
import sqlite3
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'backbone.db')

COLORS = [
    '#EF4444', '#F97316', '#F59E0B', '#84CC16', '#22C55E', '#10B981',
    '#14B8A6', '#06B6D4', '#0EA5E9', '#3B82F6', '#6366F1', '#8B5CF6',
]


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.executescript('''
        CREATE TABLE IF NOT EXISTS cables (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            total_core INTEGER NOT NULL,
            route TEXT,
            status TEXT DEFAULT 'active',
            created_at TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS tenants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            pic TEXT,
            contact TEXT,
            status TEXT DEFAULT 'active',
            created_at TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS cores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cable_id INTEGER NOT NULL,
            core_number INTEGER NOT NULL,
            status TEXT DEFAULT 'available',
            tenant_id INTEGER,
            color_code TEXT,
            allocated_at TEXT,
            FOREIGN KEY (cable_id) REFERENCES cables(id),
            FOREIGN KEY (tenant_id) REFERENCES tenants(id),
            UNIQUE(cable_id, core_number)
        );
        CREATE TABLE IF NOT EXISTS allocations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tenant_id INTEGER NOT NULL,
            cable_id INTEGER NOT NULL,
            core_number INTEGER NOT NULL,
            purpose TEXT,
            start_date TEXT,
            end_date TEXT,
            status TEXT DEFAULT 'active',
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (tenant_id) REFERENCES tenants(id),
            FOREIGN KEY (cable_id) REFERENCES cables(id),
            UNIQUE(cable_id, core_number)
        );
    ''')
    # Seed if empty
    count = c.execute('SELECT COUNT(*) AS c FROM cables').fetchone()['c']
    if count == 0:
        cables = [
            ('Backbone-Jakarta-Bandung', 96, 'Jakarta - Bandung via Purwakarta', 'active'),
            ('Backbone-Jakarta-Surabaya', 288, 'Jakarta - Surabaya via Semarang', 'active'),
            ('Backbone-Jakarta-Medan', 576, 'Jakarta - Medan via Palembang', 'active'),
            ('Backbone-Bandung-Yogyakarta', 96, 'Bandung - Yogyakarta via Cilacap', 'active'),
            ('Backbone-Surabaya-Denpasar', 288, 'Surabaya - Denpasar via Banyuwangi', 'active'),
        ]
        tenants = [
            ('PT Dark Fiber Indonesia', 'Andi Saputra', 'andi@dfi.co.id', 'active'),
            ('CV Kabel Nusantara', 'Budi Raharja', 'budi@kn.co.id', 'active'),
            ('PT Optik Sejahtera', 'Citra Lestari', 'citra@optik.co.id', 'active'),
            ('CV Jaringan Hijau', 'Dedi Kurniawan', 'dedi@jh.co.id', 'active'),
        ]
        cable_ids = []
        for name, total, route, status in cables:
            cur = c.execute(
                'INSERT INTO cables (name, total_core, route, status) VALUES (?, ?, ?, ?)',
                (name, total, route, status),
            )
            cable_ids.append(cur.lastrowid)
        tenant_ids = []
        for name, pic, contact, status in tenants:
            cur = c.execute(
                'INSERT INTO tenants (name, pic, contact, status) VALUES (?, ?, ?, ?)',
                (name, pic, contact, status),
            )
            tenant_ids.append(cur.lastrowid)
        for cid in cable_ids:
            total = c.execute('SELECT total_core FROM cables WHERE id = ?', (cid,)).fetchone()['total_core']
            for i in range(1, total + 1):
                color = COLORS[(i - 1) % len(COLORS)]
                c.execute(
                    'INSERT INTO cores (cable_id, core_number, status, color_code) VALUES (?, ?, ?, ?)',
                    (cid, i, 'available', color),
                )
        demo_allocs = [
            (tenant_ids[0], cable_ids[0], 1, 'Internet Dedicated', '2026-01-01', None),
            (tenant_ids[0], cable_ids[0], 2, 'Internet Dedicated', '2026-01-01', None),
            (tenant_ids[1], cable_ids[0], 10, 'VPN Corporate', '2026-02-15', None),
            (tenant_ids[2], cable_ids[1], 5, 'Dark Fiber Lease', '2026-03-01', None),
            (tenant_ids[2], cable_ids[1], 6, 'Dark Fiber Lease', '2026-03-01', None),
            (tenant_ids[3], cable_ids[2], 100, 'IP Transit', '2026-04-10', None),
        ]
        for tid, cid, cnum, purpose, start, end in demo_allocs:
            c.execute(
                'INSERT INTO allocations (tenant_id, cable_id, core_number, purpose, start_date, end_date, status) VALUES (?, ?, ?, ?, ?, ?, ?)',
                (tid, cid, cnum, purpose, start, end, 'active'),
            )
            c.execute(
                'UPDATE cores SET status = ?, tenant_id = ?, allocated_at = datetime("now") WHERE cable_id = ? AND core_number = ?',
                ('used', tid, cid, cnum),
            )
    conn.commit()
    conn.close()


def rows_to_list(rows):
    return [dict(r) for r in rows]


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        return  # silence logs

    def _send(self, code, data):
        body = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self):
        length = int(self.headers.get('Content-Length', 0))
        return self.rfile.read(length) if length else b''

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip('/')
        params = parse_qs(parsed.query)
        conn = get_conn()
        try:
            if path == '/api/health':
                self._send(200, {'ok': True})
            elif path == '/api/cables':
                rows = conn.execute('''
                    SELECT c.id, c.name, c.total_core, c.route, c.status, c.created_at,
                           SUM(CASE WHEN cr.status = 'used' THEN 1 ELSE 0 END) AS used_core,
                           SUM(CASE WHEN cr.status = 'available' THEN 1 ELSE 0 END) AS available_core
                    FROM cables c LEFT JOIN cores cr ON cr.cable_id = c.id
                    GROUP BY c.id ORDER BY c.name
                ''').fetchall()
                self._send(200, rows_to_list(rows))
            elif path == '/api/cables' and False:
                pass
            elif path.startswith('/api/cables/'):
                cid = int(path.split('/')[-1])
                row = conn.execute('SELECT * FROM cables WHERE id = ?', (cid,)).fetchone()
                if not row:
                    self._send(404, {'error': 'Cable not found'})
                else:
                    self._send(200, dict(row))
            elif path == '/api/cores':
                cable_id = params.get('cable_id', [None])[0]
                status = params.get('status', [None])[0]
                sql = '''
                    SELECT cr.id, cr.cable_id, cr.core_number, cr.status, cr.tenant_id,
                           cr.color_code, cr.allocated_at, t.name AS tenant_name
                    FROM cores cr LEFT JOIN tenants t ON t.id = cr.tenant_id WHERE 1=1
                '''
                args = []
                if cable_id:
                    sql += ' AND cr.cable_id = ?'; args.append(cable_id)
                if status:
                    sql += ' AND cr.status = ?'; args.append(status)
                sql += ' ORDER BY cr.core_number'
                rows = conn.execute(sql, args).fetchall()
                self._send(200, rows_to_list(rows))
            elif path.startswith('/api/cores/'):
                cid = int(path.split('/')[-1])
                row = conn.execute('''
                    SELECT cr.*, t.name AS tenant_name FROM cores cr
                    LEFT JOIN tenants t ON t.id = cr.tenant_id WHERE cr.id = ?
                ''', (cid,)).fetchone()
                if not row:
                    self._send(404, {'error': 'Core not found'})
                else:
                    self._send(200, dict(row))
            elif path == '/api/tenants':
                rows = conn.execute('SELECT * FROM tenants ORDER BY name').fetchall()
                self._send(200, rows_to_list(rows))
            elif path.startswith('/api/tenants/'):
                tid = int(path.split('/')[-1])
                row = conn.execute('SELECT * FROM tenants WHERE id = ?', (tid,)).fetchone()
                if not row:
                    self._send(404, {'error': 'Tenant not found'})
                else:
                    self._send(200, dict(row))
            elif path == '/api/allocations':
                tenant_id = params.get('tenant_id', [None])[0]
                cable_id = params.get('cable_id', [None])[0]
                sql = '''
                    SELECT a.id, a.tenant_id, a.cable_id, a.core_number, a.purpose,
                           a.start_date, a.end_date, a.status, a.created_at,
                           t.name AS tenant_name, c.name AS cable_name
                    FROM allocations a
                    LEFT JOIN tenants t ON t.id = a.tenant_id
                    LEFT JOIN cables c ON c.id = a.cable_id WHERE 1=1
                '''
                args = []
                if tenant_id:
                    sql += ' AND a.tenant_id = ?'; args.append(tenant_id)
                if cable_id:
                    sql += ' AND a.cable_id = ?'; args.append(cable_id)
                sql += ' ORDER BY a.created_at DESC'
                rows = conn.execute(sql, args).fetchall()
                self._send(200, rows_to_list(rows))
            else:
                self._send(404, {'error': 'Not found'})
        finally:
            conn.close()

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip('/')
        body = json.loads(self._read_body() or '{}')
        conn = get_conn()
        try:
            if path == '/api/cables':
                try:
                    cur = conn.execute(
                        'INSERT INTO cables (name, total_core, route, status) VALUES (?, ?, ?, ?)',
                        (body['name'], int(body['total_core']), body.get('route', ''), body.get('status', 'active')),
                    )
                    cid = cur.lastrowid
                    total = int(body['total_core'])
                    for i in range(1, total + 1):
                        color = COLORS[(i - 1) % len(COLORS)]
                        conn.execute(
                            'INSERT INTO cores (cable_id, core_number, status, color_code) VALUES (?, ?, ?, ?)',
                            (cid, i, 'available', color),
                        )
                    conn.commit()
                    row = conn.execute('SELECT * FROM cables WHERE id = ?', (cid,)).fetchone()
                    self._send(201, dict(row))
                except Exception as e:
                    self._send(400, {'error': str(e)})
            elif path == '/api/tenants':
                cur = conn.execute(
                    'INSERT INTO tenants (name, pic, contact, status) VALUES (?, ?, ?, ?)',
                    (body.get('name'), body.get('pic'), body.get('contact'), body.get('status', 'active')),
                )
                conn.commit()
                row = conn.execute('SELECT * FROM tenants WHERE id = ?', (cur.lastrowid,)).fetchone()
                self._send(201, dict(row))
            elif path == '/api/allocations':
                try:
                    conn.execute(
                        'INSERT INTO allocations (tenant_id, cable_id, core_number, purpose, start_date, end_date, status) VALUES (?, ?, ?, ?, ?, ?, ?)',
                        (int(body['tenant_id']), int(body['cable_id']), int(body['core_number']),
                         body.get('purpose'), body.get('start_date'), body.get('end_date'), 'active'),
                    )
                    conn.execute(
                        'UPDATE cores SET status = "used", tenant_id = ?, allocated_at = datetime("now") WHERE cable_id = ? AND core_number = ?',
                        (int(body['tenant_id']), int(body['cable_id']), int(body['core_number'])),
                    )
                    conn.commit()
                    row = conn.execute('SELECT * FROM allocations WHERE id = (SELECT last_insert_rowid())').fetchone()
                    self._send(201, dict(row))
                except Exception as e:
                    self._send(400, {'error': str(e)})
            else:
                self._send(404, {'error': 'Not found'})
        finally:
            conn.close()

    def do_PATCH(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip('/')
        body = json.loads(self._read_body() or '{}')
        conn = get_conn()
        try:
            if path.startswith('/api/cables/'):
                cid = int(path.split('/')[-1])
                conn.execute(
                    'UPDATE cables SET name = ?, total_core = ?, route = ?, status = ? WHERE id = ?',
                    (body.get('name'), int(body.get('total_core', 0)), body.get('route', ''), body.get('status', 'active'), cid),
                )
                conn.commit()
                row = conn.execute('SELECT * FROM cables WHERE id = ?', (cid,)).fetchone()
                if not row:
                    self._send(404, {'error': 'Cable not found'})
                else:
                    self._send(200, dict(row))
            elif path.startswith('/api/cores/'):
                cid = int(path.split('/')[-1])
                status = body.get('status')
                tenant_id = body.get('tenant_id')
                conn.execute(
                    'UPDATE cores SET status = ?, tenant_id = ?, allocated_at = CASE WHEN ? = "used" THEN datetime("now") ELSE allocated_at END WHERE id = ?',
                    (status, tenant_id, status, cid),
                )
                if status == 'used' and tenant_id:
                    core = conn.execute('SELECT * FROM cores WHERE id = ?', (cid,)).fetchone()
                    conn.execute(
                        'INSERT OR REPLACE INTO allocations (tenant_id, cable_id, core_number, status, created_at) VALUES (?, ?, ?, ?, datetime("now"))',
                        (tenant_id, core['cable_id'], core['core_number'], 'active'),
                    )
                conn.commit()
                row = conn.execute('SELECT * FROM cores WHERE id = ?', (cid,)).fetchone()
                self._send(200, dict(row))
            elif path.startswith('/api/tenants/'):
                tid = int(path.split('/')[-1])
                conn.execute(
                    'UPDATE tenants SET name = ?, pic = ?, contact = ?, status = ? WHERE id = ?',
                    (body.get('name'), body.get('pic'), body.get('contact'), body.get('status'), tid),
                )
                conn.commit()
                row = conn.execute('SELECT * FROM tenants WHERE id = ?', (tid,)).fetchone()
                if not row:
                    self._send(404, {'error': 'Tenant not found'})
                else:
                    self._send(200, dict(row))
            elif path.startswith('/api/allocations/'):
                aid = int(path.split('/')[-1])
                status = body.get('status')
                end_date = body.get('end_date')
                conn.execute(
                    'UPDATE allocations SET status = ?, end_date = COALESCE(?, end_date) WHERE id = ?',
                    (status, end_date, aid),
                )
                alloc = conn.execute('SELECT * FROM allocations WHERE id = ?', (aid,)).fetchone()
                if not alloc:
                    self._send(404, {'error': 'Allocation not found'})
                else:
                    if status == 'released':
                        conn.execute(
                            'UPDATE cores SET status = "available", tenant_id = NULL, allocated_at = NULL WHERE cable_id = ? AND core_number = ?',
                            (alloc['cable_id'], alloc['core_number']),
                        )
                    conn.commit()
                    row = conn.execute('SELECT * FROM allocations WHERE id = ?', (aid,)).fetchone()
                    self._send(200, dict(row))
            else:
                self._send(404, {'error': 'Not found'})
        finally:
            conn.close()

    def do_DELETE(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip('/')
        conn = get_conn()
        try:
            if path.startswith('/api/cables/'):
                cid = int(path.split('/')[-1])
                conn.execute('DELETE FROM cables WHERE id = ?', (cid,))
                conn.commit()
                self._send(200, {'ok': True})
            elif path.startswith('/api/tenants/'):
                tid = int(path.split('/')[-1])
                conn.execute('DELETE FROM tenants WHERE id = ?', (tid,))
                conn.commit()
                self._send(200, {'ok': True})
            elif path.startswith('/api/allocations/'):
                aid = int(path.split('/')[-1])
                alloc = conn.execute('SELECT * FROM allocations WHERE id = ?', (aid,)).fetchone()
                if alloc:
                    conn.execute(
                        'UPDATE cores SET status = "available", tenant_id = NULL, allocated_at = NULL WHERE cable_id = ? AND core_number = ?',
                        (alloc['cable_id'], alloc['core_number']),
                    )
                    conn.execute('DELETE FROM allocations WHERE id = ?', (aid,))
                    conn.commit()
                self._send(200, {'ok': True})
            else:
                self._send(404, {'error': 'Not found'})
        finally:
            conn.close()


if __name__ == '__main__':
    init_db()
    server = HTTPServer(('0.0.0.0', 4000), Handler)
    print('Server running on http://localhost:4000')
    server.serve_forever()
