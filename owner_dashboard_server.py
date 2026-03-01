#!/Users/lp1/clawd/landiq/venv/bin/python3
"""
Local server for Top 200 Citrus Owners Dashboard with editable Rv_Owner and Packer fields.
Saves edits to rv_owner_edits.json and packer_edits.json

Usage:
    cd /Users/lp1/clawd/landiq
    python3 owner_dashboard_server.py

Then open: http://localhost:8765
"""

import http.server
import json
import os
from urllib.parse import parse_qs
import pandas as pd

PORT = 8765
RV_OWNER_FILE = 'rv_owner_edits.json'
PACKER_FILE = 'packer_edits.json'
CSV_FILE = 'top200_citrus_owners.csv'

def load_edits(filepath):
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return json.load(f)
    return {}

def save_edits(filepath, edits):
    with open(filepath, 'w') as f:
        json.dump(edits, f, indent=2)

def generate_dashboard():
    top100 = pd.read_csv(CSV_FILE)
    rv_edits = load_edits(RV_OWNER_FILE)
    packer_edits = load_edits(PACKER_FILE)
    
    html = '''<!DOCTYPE html>
<html>
<head>
    <title>Top 200 California Citrus Owners</title>
    <style>
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #1a1a2e; 
            color: #eee;
            margin: 0;
            padding: 20px;
        }
        h1 { color: #ff9500; text-align: center; margin-bottom: 5px; }
        .subtitle { text-align: center; color: #888; margin-bottom: 20px; }
        .toolbar {
            text-align: center;
            margin-bottom: 15px;
        }
        .toolbar button {
            background: #0f3460;
            color: #fff;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            margin: 0 5px;
        }
        .toolbar button:hover { background: #1a4a80; }
        #saveStatus { color: #4ade80; margin-left: 15px; }
        .stats {
            display: flex;
            justify-content: center;
            gap: 40px;
            margin-bottom: 20px;
        }
        .stat-box {
            background: #16213e;
            padding: 15px 25px;
            border-radius: 8px;
            text-align: center;
        }
        .stat-value { font-size: 28px; font-weight: bold; color: #ff9500; }
        .stat-label { color: #888; font-size: 12px; }
        table { 
            width: 100%;
            max-width: 1400px;
            margin: 0 auto;
            border-collapse: collapse;
            background: #16213e;
            border-radius: 8px;
            overflow: hidden;
        }
        th { 
            background: #0f3460;
            color: #ff9500;
            padding: 12px 10px;
            text-align: left;
            font-weight: 600;
        }
        td { padding: 8px 10px; border-bottom: 1px solid #2a2a4a; }
        tr:hover { background: #1f2b4a; }
        .rank { color: #888; width: 40px; }
        .acres { text-align: right; font-weight: bold; color: #4ade80; }
        .parcels { text-align: right; color: #888; }
        .owner { max-width: 250px; font-size: 13px; }
        .address { color: #aaa; font-size: 12px; max-width: 200px; }
        .rv-owner { width: 160px; }
        .packer { width: 120px; }
        .rv-owner input, .packer input {
            width: 100%;
            background: #1a1a2e;
            border: 1px solid #444;
            color: #fff;
            padding: 5px 8px;
            border-radius: 4px;
            font-size: 13px;
        }
        .rv-owner input:focus, .packer input:focus { border-color: #ff9500; outline: none; }
        .rv-owner input.edited { border-color: #4ade80; background: #1a2e1a; }
        .packer input.edited { border-color: #60a5fa; background: #1a1a2e; }
        .top3 { background: #1f2b4a; }
        .top3 .rank { color: #ff9500; font-weight: bold; }
    </style>
</head>
<body>
    <h1>🍊 Top 200 California Citrus Owners</h1>
    <p class="subtitle">By total acreage • Edits saved to: rv_owner_edits.json & packer_edits.json</p>
    
    <div class="toolbar">
        <button onclick="saveAll()" style="background:#2e7d32; font-weight:bold;">💾 SAVE ALL</button>
        <button onclick="exportCSV()">📥 Export CSV</button>
        <button onclick="clearEdits()">🗑️ Clear All Edits</button>
        <span id="saveStatus"></span>
    </div>
    
    <div class="stats">
        <div class="stat-box">
            <div class="stat-value">''' + f"{int(top100['TOTAL_ACRE'].sum()):,}" + '''</div>
            <div class="stat-label">TOTAL ACRES (Top 200)</div>
        </div>
        <div class="stat-box">
            <div class="stat-value">''' + f"{top100['PARCEL_CNT'].sum():,}" + '''</div>
            <div class="stat-label">PARCELS</div>
        </div>
        <div class="stat-box">
            <div class="stat-value">''' + f"{len(rv_edits)}" + '''</div>
            <div class="stat-label">RV_OWNER EDITS</div>
        </div>
        <div class="stat-box">
            <div class="stat-value">''' + f"{len(packer_edits)}" + '''</div>
            <div class="stat-label">PACKER EDITS</div>
        </div>
    </div>
    
    <table>
        <tr>
            <th>#</th>
            <th>Owner Name</th>
            <th>Rv_Owner</th>
            <th>Packer</th>
            <th>Mailing Address</th>
            <th>Parcels</th>
            <th>Acres</th>
        </tr>
'''
    
    for i, row in top100.iterrows():
        row_class = 'top3' if i < 3 else ''
        mail_key = str(row['MAIL_STD']) if pd.notna(row['MAIL_STD']) else ''
        rv_value = rv_edits.get(mail_key, '')
        packer_value = packer_edits.get(mail_key, '')
        rv_edited_class = 'edited' if rv_value else ''
        packer_edited_class = 'edited' if packer_value else ''
        
        html += f'''        <tr class="{row_class}">
            <td class="rank">{i+1}</td>
            <td class="owner">{row['TOP_OWNER']}</td>
            <td class="rv-owner"><input type="text" class="{rv_edited_class}" data-key="{mail_key}" data-field="rv" value="{rv_value}" onchange="markUnsaved()"></td>
            <td class="packer"><input type="text" class="{packer_edited_class}" data-key="{mail_key}" data-field="packer" value="{packer_value}" onchange="markUnsaved()"></td>
            <td class="address">{mail_key}</td>
            <td class="parcels">{row['PARCEL_CNT']:,}</td>
            <td class="acres">{int(row['TOTAL_ACRE']):,}</td>
        </tr>
'''
    
    html += '''    </table>

<script>
function markUnsaved() {
    document.getElementById('saveStatus').textContent = '⚠️ Unsaved changes - click SAVE ALL';
    document.getElementById('saveStatus').style.color = '#ffcc00';
}

function saveAll() {
    const rvEdits = {};
    const packerEdits = {};
    
    document.querySelectorAll('input[data-field="rv"]').forEach(input => {
        const key = input.dataset.key;
        const value = input.value.trim();
        if (value) {
            rvEdits[key] = value;
            input.classList.add('edited');
        } else {
            input.classList.remove('edited');
        }
    });
    
    document.querySelectorAll('input[data-field="packer"]').forEach(input => {
        const key = input.dataset.key;
        const value = input.value.trim();
        if (value) {
            packerEdits[key] = value;
            input.classList.add('edited');
        } else {
            input.classList.remove('edited');
        }
    });
    
    fetch('/saveall', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({rv: rvEdits, packer: packerEdits})
    })
    .then(r => r.json())
    .then(data => {
        document.getElementById('saveStatus').textContent = '✓ Saved! (RV: ' + Object.keys(rvEdits).length + ', Packer: ' + Object.keys(packerEdits).length + ')';
        document.getElementById('saveStatus').style.color = '#4ade80';
    })
    .catch(err => {
        document.getElementById('saveStatus').textContent = '❌ Save failed';
        document.getElementById('saveStatus').style.color = '#ff6666';
    });
}

function clearEdits() {
    if (confirm('Clear ALL edits (Rv_Owner and Packer)?')) {
        fetch('/clear', {method: 'POST'})
        .then(() => location.reload());
    }
}

function exportCSV() {
    let csv = 'Rank,Owner,Rv_Owner,Packer,Mailing_Address,Parcels,Acres\\n';
    document.querySelectorAll('table tr').forEach((row, i) => {
        if (i === 0) return;
        const cells = row.querySelectorAll('td');
        const rvInput = row.querySelector('input[data-field="rv"]');
        const packerInput = row.querySelector('input[data-field="packer"]');
        const rvOwner = rvInput ? rvInput.value : '';
        const packer = packerInput ? packerInput.value : '';
        csv += `${cells[0].textContent},"${cells[1].textContent}","${rvOwner}","${packer}","${cells[4].textContent}",${cells[5].textContent},${cells[6].textContent}\\n`;
    });
    const blob = new Blob([csv], {type: 'text/csv'});
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'top200_citrus_owners_with_edits.csv';
    a.click();
}
</script>
</body>
</html>'''
    return html

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/dashboard':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(generate_dashboard().encode())
        else:
            self.send_error(404)
    
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length).decode()
        
        if self.path == '/saveall':
            data = json.loads(body)
            
            # If merge flag is set, merge with existing edits
            if data.get('merge'):
                existing_rv = load_edits(RV_OWNER_FILE)
                existing_packer = load_edits(PACKER_FILE)
                existing_rv.update(data.get('rv', {}))
                existing_packer.update(data.get('packer', {}))
                save_edits(RV_OWNER_FILE, existing_rv)
                save_edits(PACKER_FILE, existing_packer)
                print(f'Merged edits - RV: {len(existing_rv)}, Packer: {len(existing_packer)}')
            else:
                save_edits(RV_OWNER_FILE, data.get('rv', {}))
                save_edits(PACKER_FILE, data.get('packer', {}))
                print(f'Saved {len(data.get("rv", {}))} RV edits, {len(data.get("packer", {}))} Packer edits')
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'ok': True}).encode())
        
        elif self.path == '/clear':
            save_edits(RV_OWNER_FILE, {})
            save_edits(PACKER_FILE, {})
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'ok': True}).encode())
        
        else:
            self.send_error(404)
    
    def log_message(self, format, *args):
        pass  # Suppress logging

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    print(f'🍊 Citrus Owner Dashboard')
    print(f'   RV Edits: {os.path.abspath(RV_OWNER_FILE)}')
    print(f'   Packer Edits: {os.path.abspath(PACKER_FILE)}')
    print(f'   Open: http://localhost:{PORT}')
    print(f'   Press Ctrl+C to stop\n')
    
    server = http.server.HTTPServer(('localhost', PORT), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nStopped.')
