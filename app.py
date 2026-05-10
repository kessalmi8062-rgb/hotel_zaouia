from flask import Flask, render_template, request, jsonify
import sqlite3
import os
from datetime import datetime
import traceback

app = Flask(_name_)

# ==================== إعداد اتصال قاعدة البيانات SQLite ====================
DATABASE = 'hotel_zaouia.db'

def get_db_connection():
    """إنشاء اتصال بقاعدة البيانات SQLite"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # للتعامل مع النتائج كقاموس
    return conn

# ==================== إنشاء الجداول ====================
def create_tables():
    """إنشاء الجداول إذا لم تكن موجودة"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # جدول حجوزات الإقامة
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reservations_sejour (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type_chambre TEXT NOT NULL,
                nombre_chambres INTEGER NOT NULL,
                adultes INTEGER NOT NULL,
                enfants INTEGER NOT NULL,
                date_arrivee TEXT NOT NULL,
                date_depart TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # جدول حجوزات المطعم
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reservations_table (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                restaurant TEXT NOT NULL,
                nom_complet TEXT NOT NULL,
                email TEXT NOT NULL,
                telephone TEXT,
                date_reservation TEXT NOT NULL,
                nombre_personnes INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # جدول حجوزات الفعاليات
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reservations_evenement (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type_evenement TEXT NOT NULL,
                nom TEXT NOT NULL,
                prenom TEXT NOT NULL,
                email TEXT NOT NULL,
                pays TEXT NOT NULL,
                ville TEXT NOT NULL,
                societe TEXT NOT NULL,
                telephone TEXT NOT NULL,
                commentaires TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        print("✓ الجداول تم إنشاؤها بنجاح (أو موجودة مسبقاً)")
    except Exception as e:
        print(f"✗ خطأ في إنشاء الجداول: {e}")
    finally:
        conn.close()

# ==================== الصفحة الرئيسية ====================
@app.route('/')
def index():
    """عرض صفحة HTML الرئيسية"""
    return render_template('index.html')

# ==================== API حجز الإقامة ====================
@app.route('/api/reserver/sejour', methods=['POST'])
def reserver_sejour():
    """معالجة طلب حجز الإقامة"""
    try:
        data = request.json
        print("بيانات الحجز المستلمة:", data)
        
        # التحقق من صحة البيانات
        required_fields = ['type_chambre', 'nombre_chambres', 'adultes', 'enfants', 'date_arrivee', 'date_depart']
        for field in required_fields:
            if field not in data:
                return jsonify({"success": False, "message": f"الحقل {field} مطلوب"}), 400
        
        # حفظ في قاعدة البيانات
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO reservations_sejour 
            (type_chambre, nombre_chambres, adultes, enfants, date_arrivee, date_depart)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            data['type_chambre'],
            data['nombre_chambres'],
            data['adultes'],
            data['enfants'],
            data['date_arrivee'],
            data['date_depart']
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            "success": True, 
            "message": f"تم حجز {data['nombre_chambres']} غرفة من نوع {data['type_chambre']} بتاريخ {data['date_arrivee']} إلى {data['date_depart']}"
        })
            
    except Exception as e:
        print("خطأ:", traceback.format_exc())
        return jsonify({"success": False, "message": str(e)}), 500

# ==================== API حجز المطعم ====================
@app.route('/api/reserver/table', methods=['POST'])
def reserver_table():
    """معالجة طلب حجز المطعم"""
    try:
        data = request.json
        print("بيانات حجز المطعم:", data)
        
        required_fields = ['restaurant', 'nom_complet', 'email', 'date_reservation', 'nombre_personnes']
        for field in required_fields:
            if field not in data:
                return jsonify({"success": False, "message": f"الحقل {field} مطلوب"}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO reservations_table 
            (restaurant, nom_complet, email, telephone, date_reservation, nombre_personnes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            data['restaurant'],
            data['nom_complet'],
            data['email'],
            data.get('telephone', ''),
            data['date_reservation'],
            data['nombre_personnes']
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": f"تم حجز طاولة في مطعم {data['restaurant']} لـ {data['nombre_personnes']} أشخاص بتاريخ {data['date_reservation']}"
        })
            
    except Exception as e:
        print("خطأ:", traceback.format_exc())
        return jsonify({"success": False, "message": str(e)}), 500

# ==================== API حجز الفعاليات ====================
@app.route('/api/reserver/evenement', methods=['POST'])
def reserver_evenement():
    """معالجة طلب حجز الفعالية"""
    try:
        data = request.json
        print("بيانات الفعالية:", data)
        
        required_fields = ['type_evenement', 'nom', 'prenom', 'email', 'pays', 'ville', 'societe', 'telephone', 'commentaires']
        for field in required_fields:
            if field not in data:
                return jsonify({"success": False, "message": f"الحقل {field} مطلوب"}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO reservations_evenement 
            (type_evenement, nom, prenom, email, pays, ville, societe, telephone, commentaires)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data['type_evenement'],
            data['nom'],
            data['prenom'],
            data['email'],
            data['pays'],
            data['ville'],
            data['societe'],
            data['telephone'],
            data['commentaires']
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": f"تم استلام طلب فعالية {data['type_evenement']} من {data['prenom']} {data['nom']}. سنتواصل معكم قريباً."
        })
            
    except Exception as e:
        print("خطأ:", traceback.format_exc())
        return jsonify({"success": False, "message": str(e)}), 500

# ==================== API للإحصائيات (اختياري) ====================
@app.route('/api/statistiques', methods=['GET'])
def get_statistiques():
    """الحصول على إحصائيات الحجوزات"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) as count FROM reservations_sejour")
        sejour_count = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM reservations_table")
        table_count = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM reservations_evenement")
        evenement_count = cursor.fetchone()['count']
        
        conn.close()
        
        return jsonify({
            "success": True,
            "data": {
                "sejour": sejour_count,
                "table": table_count,
                "evenement": evenement_count,
                "total": sejour_count + table_count + evenement_count
            }
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# ==================== تشغيل التطبيق ====================
if _name_ == '_main_':
    # إنشاء الجداول عند بدء التشغيل
    print("=== فندق الزاوية - نظام الحجوزات ===")
    print("جاري تجهيز قاعدة البيانات...")
    create_tables()
    print("\n✓ الخادم يعمل على http://localhost:5000")
    print("✓ اضغط Ctrl+C لإيقاف الخادم\n")
    app.run(debug=False, host='0.0.0.0', port=5000)
