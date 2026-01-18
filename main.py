from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
import sqlite3
import datetime
import qrcode
import io
import base64
import barcode
from barcode.writer import ImageWriter
from contextlib import contextmanager

app = Flask(__name__)
app.secret_key = 'daycare_secret_key_2024'

# Database setup
def init_db():
    with sqlite3.connect('daycare.db') as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS children (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                parent_name TEXT NOT NULL,
                parent_phone TEXT,
                card_id TEXT UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS cards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                card_code TEXT UNIQUE NOT NULL,
                is_assigned BOOLEAN DEFAULT FALSE,
                child_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (child_id) REFERENCES children (id)
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                child_id INTEGER NOT NULL,
                card_code TEXT NOT NULL,
                action TEXT NOT NULL CHECK (action IN ('drop_off', 'pick_up')),
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notes TEXT,
                FOREIGN KEY (child_id) REFERENCES children (id)
            )
        ''')
        
        conn.commit()

@contextmanager
def get_db():
    conn = sqlite3.connect('daycare.db')
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def generate_barcode(data):
    CODE128 = barcode.get_barcode_class('code128')
    bar = CODE128(data, writer=ImageWriter())
    img_io = io.BytesIO()
    bar.write(img_io)
    img_io.seek(0)
    img_base64 = base64.b64encode(img_io.getvalue()).decode()
    return f"data:image/png;base64,{img_base64}"

@app.route('/')
def index():
    with get_db() as conn:
        children = conn.execute('''
            SELECT c.*, cards.card_code 
            FROM children c 
            LEFT JOIN cards ON c.id = cards.child_id AND cards.is_assigned = 1
            ORDER BY c.name
        ''').fetchall()
        
        unassigned_cards = conn.execute('''
            SELECT * FROM cards WHERE is_assigned = 0 ORDER BY card_code
        ''').fetchall()
    
    return render_template('index.html', children=children, unassigned_cards=unassigned_cards)

@app.route('/add_child', methods=['POST'])
def add_child():
    name = request.form['name']
    parent_name = request.form['parent_name']
    parent_phone = request.form['parent_phone']
    
    with get_db() as conn:
        conn.execute('''
            INSERT INTO children (name, parent_name, parent_phone)
            VALUES (?, ?, ?)
        ''', (name, parent_name, parent_phone))
        conn.commit()
    
    flash('Child added successfully!')
    return redirect(url_for('index'))

@app.route('/edit_child/<int:child_id>', methods=['GET', 'POST'])
def edit_child(child_id):
    with get_db() as conn:
        child = conn.execute('SELECT * FROM children WHERE id = ?', (child_id,)).fetchone()
        if not child:
            flash("Child not found!", "danger")
            return redirect(url_for('index'))
        
        if request.method == 'POST':
            name = request.form['name']
            parent_name = request.form['parent_name']
            parent_phone = request.form['parent_phone']
            
            conn.execute('''
                UPDATE children SET name = ?, parent_name = ?, parent_phone = ?
                WHERE id = ?
            ''', (name, parent_name, parent_phone, child_id))
            conn.commit()
            
            flash("Child details updated successfully!", "success")
            return redirect(url_for('index'))
    
    return render_template('edit_child.html', child=child)

@app.route('/delete_child/<int:child_id>', methods=['POST', 'GET'])
def delete_child(child_id):
    with get_db() as conn:
        conn.execute('DELETE FROM children WHERE id = ?', (child_id,))
        conn.execute('UPDATE cards SET is_assigned = 0, child_id = NULL WHERE child_id = ?', (child_id,))
        conn.commit()
    
    flash("Child deleted successfully!", "danger")
    return redirect(url_for('index'))

@app.route('/generate_card')
def generate_card():
    import uuid
    card_code = str(uuid.uuid4())[:8].upper()
    
    with get_db() as conn:
        conn.execute('INSERT INTO cards (card_code) VALUES (?)', (card_code,))
        conn.commit()
    
    flash(f'New card generated: {card_code}')
    return redirect(url_for('index'))

@app.route('/assign_card', methods=['POST'])
def assign_card():
    child_id = request.form['child_id']
    card_code = request.form['card_code']
    
    with get_db() as conn:
        # Unassign any existing card for this child
        conn.execute('''
            UPDATE cards SET is_assigned = 0, child_id = NULL 
            WHERE child_id = ?
        ''', (child_id,))
        
        # Assign the new card
        conn.execute('''
            UPDATE cards SET is_assigned = 1, child_id = ? 
            WHERE card_code = ?
        ''', (child_id, card_code))
        conn.commit()
    
    flash('Card assigned successfully!')
    return redirect(url_for('index'))

@app.route('/unassign_card/<int:child_id>')
def unassign_card(child_id):
    with get_db() as conn:
        conn.execute('''
            UPDATE cards SET is_assigned = 0, child_id = NULL 
            WHERE child_id = ?
        ''', (child_id,))
        conn.commit()
    
    flash('Card unassigned successfully!')
    return redirect(url_for('index'))

@app.route('/scan')
def scan_page():
    return render_template('scan.html')

@app.route('/process_scan', methods=['POST'])
def process_scan():
    card_code = request.form['card_code'].strip().upper()
    action = request.form['action']
    notes = request.form.get('notes', '')
    
    with get_db() as conn:
        # Find the child associated with this card
        card_info = conn.execute('''
            SELECT c.id, c.name, cards.card_code 
            FROM children c 
            JOIN cards ON c.id = cards.child_id 
            WHERE cards.card_code = ? AND cards.is_assigned = 1
        ''', (card_code,)).fetchone()
        
        if not card_info:
            flash('Invalid card code or card not assigned!')
            return redirect(url_for('scan_page'))
        
        # Record the attendance
        conn.execute('''
            INSERT INTO attendance (child_id, card_code, action, notes)
            VALUES (?, ?, ?, ?)
        ''', (card_info['id'], card_code, action, notes))
        conn.commit()
        
        action_text = "dropped off" if action == "drop_off" else "picked up"
        flash(f'{card_info["name"]} has been {action_text} successfully!')
    
    return redirect(url_for('scan_page'))

@app.route('/reports')
def reports() -> str:
    month = request.args.get('month', datetime.datetime.now().strftime('%Y-%m'))
    
    with get_db() as conn:
        # Get attendance records for the month
        attendance_data = conn.execute('''
            SELECT 
                c.name,
                c.parent_name,
                a.action,
                a.timestamp,
                a.notes,
                DATE(a.timestamp) as date
            FROM attendance a
            JOIN children c ON a.child_id = c.id
            WHERE strftime('%Y-%m', a.timestamp) = ?
            ORDER BY c.name, a.timestamp
        ''', (month,)).fetchall()
        
        # Group by child and date
        report_data = {}
        for record in attendance_data:
            child_name = record['name']
            date = record['date']
            
            if child_name not in report_data:
                report_data[child_name] = {
                    'parent_name': record['parent_name'],
                    'days': {}
                }
            
            if date not in report_data[child_name]['days']:
                report_data[child_name]['days'][date] = {
                    'drop_off': None,
                    'pick_up': None
                }
            
            report_data[child_name]['days'][date][record['action']] = record['timestamp']
    
    return render_template('reports.html', report_data=report_data, month=month)

@app.route('/card_qr/<card_code>')  # type: ignore
def card_barcode(card_code):
    barcode_img = generate_barcode(card_code)
    return render_template('card_barcode.html', card_code=card_code, barcode_img=barcode_img)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5002, debug=True)
