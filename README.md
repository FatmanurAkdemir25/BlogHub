#  BlogHub - Modern Blog Platformu

Modern, güvenli ve ölçeklenebilir bir blog platformu. Flask framework'ü kullanılarak geliştirilmiştir.

##  İçindekiler

- [Özellikler](#-özellikler)
- [Teknolojiler](#-teknolojiler)
- [Kurulum](#-kurulum)
- [Kullanım](#-kullanım)
- [Proje Yapısı](#-proje-yapısı)
- [API Dokümantasyonu](#-api-dokümantasyonu)
- [Veritabanı Şeması](#-veritabanı-şeması)
- [Güvenlik](#-güvenlik)



##  Özellikler

###  Kullanıcı Yönetimi
-  Güvenli kullanıcı kaydı ve girişi (PBKDF2 hash)
-  Profil yönetimi (avatar, bio)
-  Takip sistemi (kullanıcılar birbirini takip edebilir)
-  Rol tabanlı yetkilendirme (Admin/User)

###  İçerik Yönetimi
-  Markdown desteği ile zengin metin editörü
-  Kategori bazlı yazılar
-  Taslak ve yayınlanmış durum yönetimi
-  Resim yükleme ve otomatik optimizasyon
-  Okuma süresi hesaplama
-  Görüntülenme sayısı takibi

###  Etkileşim Özellikleri
-  Yorum sistemi (iç içe yorumlar/replies)
-  Beğeni sistemi
-  Yer imi (bookmark) özelliği
-  Gerçek zamanlı bildirimler
-  İletişim formu

###  Arama ve Filtreleme
-  Tam metin araması
-  Kategori filtreleme
-  Popüler yazılar
-  Takip edilen yazarların feed'i
-  Sayfalama (pagination)

###  Admin Paneli
-  Kapsamlı dashboard (istatistikler)
-  Kullanıcı yönetimi
-  İçerik moderasyonu
-  Mesaj yönetimi ve cevaplama
-  Yorum yönetimi

##  Teknolojiler

### Backend
- **Flask 3.0.0** - Web framework
- **SQLAlchemy** - ORM (Object-Relational Mapping)
- **PostgreSQL** - İlişkisel veritabanı
- **Flask-Login** - Kullanıcı oturum yönetimi
- **Werkzeug** - Şifre hashleme ve güvenlik
- **Pillow** - Resim işleme

### Frontend
- **HTML5/CSS3** - Modern web standartları
- **JavaScript (Vanilla)** - Client-side interactivity
- **Font Awesome 6** - İkonlar
- **Google Fonts** - Tipografi

### Mimari Desenler
- **Application Factory Pattern** - Modüler uygulama yapısı
- **Blueprint Pattern** - Route organizasyonu
- **Repository Pattern** - Veritabanı soyutlama
- **MVC Pattern** - Model-View-Controller

##  Kurulum

### Gereksinimler
- Python 3.8 veya üzeri
- PostgreSQL 13 veya üzeri
- pip (Python paket yöneticisi)
- virtualenv (önerilir)

### Adım 1: Projeyi Klonlayın
```bash
git clone https://github.com/FatmanurAkdemir25/bloghub.git
cd bloghub
```

### Adım 2: Virtual Environment Oluşturun
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Adım 3: Bağımlılıkları Yükleyin
```bash
pip install -r requirements.txt
```

### Adım 4: PostgreSQL Veritabanı Oluşturun
```sql
-- PostgreSQL'e bağlanın
psql -U postgres

-- Yeni veritabanı oluşturun
CREATE DATABASE blog_db_new;

-- Çıkış
\q
```


### Adım 5: Veritabanını Başlatın
```bash
# Flask shell'de
python
>>> from app import create_app, db
>>> app = create_app()
>>> with app.app_context():
...     db.create_all()
>>> exit()
```

### Adım 6: Admin Kullanıcı Oluşturun
```bash
python create_admin.py
```
Veya manuel:
```python
python
>>> from app import create_app, db
>>> from app.models import User
>>> app = create_app()
>>> with app.app_context():
...     admin = User(username='admin', email='admin@blog.com', is_admin=True)
...     admin.set_password('admin123')
...     db.session.add(admin)
...     db.session.commit()
>>> exit()
```

### Adım 8: Uygulamayı Başlatın
```bash
python run.py
```

Tarayıcıda açın: `http://localhost:5000`

##  Kullanım

### İlk Giriş
1. `http://localhost:5000/login` adresine gidin
2. Admin bilgileriyle giriş yapın:
   - Kullanıcı adı: `admin`
   - Şifre: `admin123`

### Yeni Yazı Oluşturma
1. Navbar'dan **"Yeni Yazı"** butonuna tıklayın
2. Başlık, içerik, özet ve kategori girin
3. İsteğe bağlı resim yükleyin
4. **"Yayınla"** veya **"Taslak Olarak Kaydet"**

### Admin Paneli
1. Navbar'dan **"Admin"** linkine tıklayın
2. Dashboard'da istatistikleri görün
3. Kullanıcıları, yazıları ve yorumları yönetin

### Bildirimler
- Sağ üstteki bildirimler ikonuna tıklayarak bildirimleri görün
- Otomatik olarak 30 saniyede bir güncellenir
- Beğeni, yorum, takip bildirimleri

##  Proje Yapısı

```
bloghub/
├── app/
│   ├── __init__.py              # Uygulama fabrikası
│   ├── models.py                # Veritabanı modelleri
│   │
│   ├── routes/                  # Route'lar (Blueprint)
│   │   ├── __init__.py
│   │   ├── auth.py              # Kimlik doğrulama (login, register)
│   │   ├── main.py              # Ana sayfalar (index, about, contact)
│   │   ├── posts.py             # Yazı CRUD işlemleri
│   │   ├── user.py              # Kullanıcı profil ve ayarları
│   │   └── admin.py             # Admin paneli
│   │
│   ├── utils/                   # Yardımcı fonksiyonlar
│   │   ├── __init__.py
│   │   ├── decorators.py        # Özel decorator'lar (@admin_required)
│   │   └── helpers.py           # Yardımcı fonksiyonlar (resim kaydetme vb.)
│   │
│   ├── templates/               # HTML şablonları
│   │   ├── base.html            # Ana şablon
│   │   ├── index.html           # Ana sayfa
│   │   ├── post.html            # Yazı detay
│   │   ├── profile.html         # Kullanıcı profili
│   │   ├── notifications.html   # Bildirimler
│   │   └── admin/               # Admin şablonları
│   │       ├── dashboard.html
│   │       ├── users.html
│   │       └── ...
│   │
│   └── static/                  # Statik dosyalar
│       ├── css/
│       │   └── style.css
│       ├── js/
│       │   └── main.js
│       └── uploads/             # Yüklenen resimler
│
├── config.py                    # Yapılandırma
├── run.py                       # Uygulama başlatıcı
├── requirements.txt             # Python bağımlılıkları
├── create_admin.py              # Admin oluşturma script'i
├── seed_database.py             # Test verileri script'i
└── README.md                    # Bu dosya
```

##  API Dokümantasyonu

### Kimlik Doğrulama

#### POST /register
Yeni kullanıcı kaydı
```json
Request:
{
  "username": "fatmanur",
  "email": "fatmanur@example.com",
  "password": "sifre123"
}

Response: 302 Redirect → /login
```

#### POST /login
Kullanıcı girişi
```json
Request:
{
  "username": "fatmanur",
  "password": "sifre123"
}

Response: 302 Redirect → /
Set-Cookie: session=...
```

### Yazılar

#### GET /
Ana sayfa - Tüm yazıları listele
```
Query Params:
- page: Sayfa numarası (default: 1)
- category: Kategori filtresi
- search: Arama terimi

Response: HTML
```

#### GET /post/:id
Yazı detayı
```
Response: HTML
Side Effects: views += 1
```

#### POST /post/:id/like
Yazıyı beğen/beğenme toggle
```json
Response:
{
  "liked": true,
  "likes_count": 42
}
```

#### POST /post/:id/bookmark
Yer imlerine ekle/çıkar
```json
Response:
{
  "bookmarked": true
}
```

#### POST /post/:id/comment
Yorum ekle
```json
Request:
{
  "content": "Harika yazı!",
  "parent_id": null  // Opsiyonel (reply için)
}

Response: 302 Redirect → /post/:id
```

### Kullanıcı

#### GET /profile/:username
Kullanıcı profili
```
Response: HTML
```

#### POST /follow/:username
Kullanıcıyı takip et/etme
```json
Response:
{
  "following": true,
  "followers_count": 156
}
```

#### GET /notifications/unread-count
Okunmamış bildirim sayısı
```json
Response:
{
  "count": 5
}
```

## 🗄️ Veritabanı Şeması

### Users Tablosu
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    bio TEXT,
    avatar VARCHAR(255) DEFAULT 'default-avatar.jpg',
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_email (email)
);
```

### Posts Tablosu
```sql
CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    summary VARCHAR(300),
    image VARCHAR(255),
    category VARCHAR(50),
    views INTEGER DEFAULT 0,
    is_published BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_category (category),
    INDEX idx_is_published (is_published)
);
```

### İlişkiler
- **User → Posts**: One-to-Many (Cascade Delete)
- **User → Comments**: One-to-Many (Cascade Delete)
- **Post → Comments**: One-to-Many (Cascade Delete)
- **User ↔ Post (Likes)**: Many-to-Many
- **User ↔ Post (Bookmarks)**: Many-to-Many
- **User ↔ User (Follow)**: Self-referential Many-to-Many
- **Comment → Comment**: Self-referential (Replies)

### ER Diagram
```
┌──────────┐       ┌──────────┐       ┌──────────┐
│  User    │──1:N──│  Post    │──1:N──│ Comment  │
└──────────┘       └──────────┘       └──────────┘
     │                   │                   │
     │                   │                   │
     └──────N:M──────────┤                   │
     │    (Like)         │                   │
     │                   │                   │
     └──────N:M──────────┤                   │
     │  (Bookmark)       │                   │
     │                   │                   │
     └──────N:M──────────┘                   │
        (Follow)                             │
                                             │
                    ┌────────────────────────┘
                    │ (Self-reference: Replies)
                    ▼
```

##  Güvenlik

### Uygulanan Güvenlik Önlemleri

#### 1. Şifre Güvenliği
- **PBKDF2-SHA256** hash algoritması
- **150,000+ iterasyon** (brute-force saldırılarına karşı)
- **Otomatik salt** (her şifre için benzersiz)
```python
# Şifre hashleme
password_hash = pbkdf2:sha256:150000$salt$hash
```

#### 2. SQL Injection Koruması
- SQLAlchemy ORM kullanımı
- Parametreli sorgular
```python
#  GÜVENLİ
User.query.filter_by(username=username).first()

#  GÜVENSİZ (Kullanılmıyor)
db.session.execute(f"SELECT * FROM users WHERE username='{username}'")
```

#### 3. XSS Koruması
- Jinja2 otomatik escape
- `|safe` filtresi dikkatli kullanımı
```html
<!--  GÜVENLİ: Otomatik escape -->
{{ user.username }}

<!--  DİKKAT: Manuel kontrol gerekli -->
{{ post.content | markdown | safe }}
```

#### 4. CSRF Koruması
- Session tabanlı doğrulama
- Cookie güvenlik ayarları
```python
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
```

#### 5. Dosya Yükleme Güvenliği
- Uzantı kontrolü (whitelist)
- Dosya adı sanitizasyonu
- Boyut sınırlaması (16MB)
```python
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024
```

#### 6. Yetkilendirme
- Decorator'lar ile route koruması
- Rol tabanlı erişim kontrolü
```python
@login_required
@admin_required
def admin_dashboard():
    # Sadece admin'ler erişebilir
```

### Güvenlik Tavsiyeleri

#### Production Ortamı İçin
```python
# config.py
class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ.get('SECRET_KEY')  # Güçlü, rastgele key
    SESSION_COOKIE_SECURE = True  # Sadece HTTPS
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
```

#### Ortam Değişkenleri
```bash
export SECRET_KEY="$(openssl rand -hex 32)"
export DATABASE_URL="postgresql://user:pass@host/db"
export FLASK_ENV="production"
```

##  Test

### Manuel Test
```bash
# Test verileri oluştur
python seed_database.py

# Admin oluştur
python create_admin.py
```

### Postman ile API Testi
1. Collection'ı import edin
2. Login request'i gönderin (cookie alın)
3. Diğer endpoint'leri test edin

##  Performans

### Optimizasyon Teknikleri

#### 1. Database Indexing
```python
# Sık kullanılan kolonlara index
username = db.Column(db.String(80), index=True)
created_at = db.Column(db.DateTime, index=True)
```

#### 2. Query Optimization
```python
#  N+1 Problem
posts = Post.query.all()
for post in posts:
    print(post.author.username)  # Her post için ayrı sorgu!

#  Eager Loading
posts = Post.query.options(joinedload(Post.author)).all()
```

#### 3. Pagination
```python
# Tüm veriyi çekme, sayfalandır
posts = Post.query.paginate(page=1, per_page=6)
```

#### 4. Caching (Gelecek Özellik)
```python
# Redis ile caching planlanıyor
@cache.cached(timeout=300)
def get_popular_posts():
    return Post.query.order_by(Post.views.desc()).limit(10).all()
```

##  Bilinen Sorunlar ve Sınırlamalar

- [ ] Real-time bildirimler WebSocket yerine polling kullanıyor
- [ ] Resim yüklemede WebP formatı tarayıcı desteğine bağlı
- [ ] Admin paneli mobil responsive iyileştirme gerekiyor
- [ ] Unit test coverage %0 (test eklenecek)

##  Yazar

- **Fatmanur** - *Initial work* - [GitHub](https://github.com/FatmanurAkdemir25)
