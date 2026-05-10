from flask import Flask, render_template, request, jsonify
import pymysql
from datetime import datetime
import traceback

app = Flask(__name__)

# ==================== إعداد اتصال قاعدة البيانات ====================
def get_db_connection():
    """إنشاء اتصال بقاعدة البيانات"""
    return pymysql.connect(
        host='localhost',
        user='root',
        password='',  # اتركها فارغة في XAMPP، أو ضع كلمة المرور الخاصة بك
        database='hotel_zaouia',
        cursorclass=pymysql.cursors.DictCursor,
        charset='utf8mb4'
    )

# ==================== إنشاء الجداول ====================
def create_tables():
    """إنشاء الجداول إذا لم تكن موجودة"""
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # جدول حجوزات الإقامة
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS reservations_sejour (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    type_chambre VARCHAR(50) NOT NULL,
                    nombre_chambres INT NOT NULL,
                    adultes INT NOT NULL,
                    enfants INT NOT NULL,
                    date_arrivee DATE NOT NULL,
                    date_depart DATE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # جدول حجوزات المطعم
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS reservations_table (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    restaurant VARCHAR(50) NOT NULL,
                    nom_complet VARCHAR(100) NOT NULL,
                    email VARCHAR(100) NOT NULL,
                    telephone VARCHAR(20),
                    date_reservation DATE NOT NULL,
                    nombre_personnes INT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # جدول حجوزات الفعاليات
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS reservations_evenement (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    type_evenement VARCHAR(50) NOT NULL,
                    nom VARCHAR(50) NOT NULL,
                    prenom VARCHAR(50) NOT NULL,
                    email VARCHAR(100) NOT NULL,
                    pays VARCHAR(50) NOT NULL,
                    ville VARCHAR(50) NOT NULL,
                    societe VARCHAR(100) NOT NULL,
                    telephone VARCHAR(20) NOT NULL,
                    commentaires TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
        connection.commit()
        print("✓ الجداول تم إنشاؤها بنجاح (أو موجودة مسبقاً)")
    except Exception as e:
        print(f"✗ خطأ في إنشاء الجداول: {e}")
    finally:
        connection.close()

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
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = """
                    INSERT INTO reservations_sejour 
                    (type_chambre, nombre_chambres, adultes, enfants, date_arrivee, date_depart)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (
                    data['type_chambre'],
                    data['nombre_chambres'],
                    data['adultes'],
                    data['enfants'],
                    data['date_arrivee'],
                    data['date_depart']
                ))
            connection.commit()
            return jsonify({
                "success": True, 
                "message": f"تم حجز {data['nombre_chambres']} غرفة من نوع {data['type_chambre']} بتاريخ {data['date_arrivee']} إلى {data['date_depart']}"
            })
        finally:
            connection.close()
            
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
        
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = """
                    INSERT INTO reservations_table 
                    (restaurant, nom_complet, email, telephone, date_reservation, nombre_personnes)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (
                    data['restaurant'],
                    data['nom_complet'],
                    data['email'],
                    data.get('telephone', ''),
                    data['date_reservation'],
                    data['nombre_personnes']
                ))
            connection.commit()
            return jsonify({
                "success": True,
                "message": f"تم حجز طاولة في مطعم {data['restaurant']} لـ {data['nombre_personnes']} أشخاص بتاريخ {data['date_reservation']}"
            })
        finally:
            connection.close()
            
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
        
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = """
                    INSERT INTO reservations_evenement 
                    (type_evenement, nom, prenom, email, pays, ville, societe, telephone, commentaires)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (
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
            connection.commit()
            return jsonify({
                "success": True,
                "message": f"تم استلام طلب فعالية {data['type_evenement']} من {data['prenom']} {data['nom']}. سنتواصل معكم قريباً."
            })
        finally:
            connection.close()
            
    except Exception as e:
        print("خطأ:", traceback.format_exc())
        return jsonify({"success": False, "message": str(e)}), 500

# ==================== API للإحصائيات (اختياري) ====================
@app.route('/api/statistiques', methods=['GET'])
def get_statistiques():
    """الحصول على إحصائيات الحجوزات"""
    try:
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) as count FROM reservations_sejour")
                sejour_count = cursor.fetchone()['count']
                
                cursor.execute("SELECT COUNT(*) as count FROM reservations_table")
                table_count = cursor.fetchone()['count']
                
                cursor.execute("SELECT COUNT(*) as count FROM reservations_evenement")
                evenement_count = cursor.fetchone()['count']
                
            return jsonify({
                "success": True,
                "data": {
                    "sejour": sejour_count,
                    "table": table_count,
                    "evenement": evenement_count,
                    "total": sejour_count + table_count + evenement_count
                }
            })
        finally:
            connection.close()
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# ==================== تشغيل التطبيق ====================
if __name__ == '__main__':
    # إنشاء الجداول عند بدء التشغيل
    print("=== فندق الزاوية - نظام الحجوزات ===")
    print("جاري تجهيز قاعدة البيانات...")
    create_tables()
    print("\n✓ الخادم يعمل على http://localhost:5000")
    print("✓ اضغط Ctrl+C لإيقاف الخادم\n")
    app.run(debug=False, host='0.0.0.0', port=5000)