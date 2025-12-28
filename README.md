🎓 Student Competency Analytics (Akademik OBS)
Student Competency Analytics, klasik notlandırma sistemlerinin ötesine geçerek, öğrencilerin akademik başarılarını Çıktı Temelli Eğitim (Outcome-Based Education) modeline göre analiz eden web tabanlı bir öğrenci bilgi sistemidir.

Bu proje, öğrencilerin sadece sınav puanlarını değil; Program Çıktıları (PO) ve Öğrenme Çıktıları (LO) bazındaki yetkinliklerini Radar Grafikleri ve detaylı veri analizleriyle görselleştirir.

🚀 Projenin Amacı
Üniversiteler ve eğitim kurumları için kritik olan "Hangi öğrenci, hangi yetkinliği ne kadar kazandı?" sorusuna dijital ve görsel bir çözüm sunmaktır.

🔐 Temel Özellikler
🏛️ Bölüm Başkanı Paneli (Yönetici)

Müfredat Yönetimi: Dönem, Ders ve Bölüm tanımlamaları.

Çıktı Tanımlama: Bölümün vizyonuna uygun Program Çıktılarını (PO) belirleme.

Genel Bakış: Toplam öğrenci, aktif ders ve sınav istatistiklerini dashboard üzerinden izleme.

Kullanıcı Yönetimi: Akademisyen ve öğrenci kayıtlarını yönetme.

👨‍🏫 Öğretmen Paneli

LO Yönetimi: Derslere özel Öğrenme Çıktıları (LO) oluşturma (Örn: "Algoritmik Düşünme").

Sınav Kurgusu: Sınav sorularını ilgili LO'lar ile eşleştirme ve ağırlıklandırma.

Analiz: Dersi alan öğrencilerin başarı dağılımını grafiklerle inceleme.

👨‍🎓 Öğrenci Paneli

Yetkinlik Karnesi: Klasik transkript yerine, hangi yetkinlikte ne kadar güçlü olduğunu gösteren Radar Grafikleri.

Başarım Takibi: Ders bazlı ve genel mezuniyet hedeflerine (PO) ulaşma oranları.

🛠️ Teknoloji Yığını
Alan	Teknoloji	Açıklama
Backend		Python tabanlı güçlü web çatısı.
Frontend		Responsive (Mobil uyumlu) arayüz tasarımı.
Veritabanı		Geliştirme ortamı veritabanı.
Görselleştirme		Radar ve Bar grafikleri.
📂 Proje Yapısı
Proje dosyaları, modüler Django mimarisine uygun olarak aşağıdaki gibi düzenlenmiştir:

Plaintext
SOFTWAREPROJECT/
├── .github/                   # GitHub Actions ve Konfigürasyonlar
├── obs_core/                  # Proje Ana Ayar Dosyaları
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py            # Veritabanı, Uygulama ve Middleware Ayarları
│   ├── urls.py                # Ana URL Yönlendirmeleri
│   └── wsgi.py
├── academic/                  # Ana Uygulama (App) Klasörü
│   ├── migrations/            # Veritabanı Değişiklik Geçmişi
│   ├── templates/             # HTML Arayüz Dosyaları
│   ├── templatetags/          # Özel Django Template Etiketleri
│   ├── __init__.py
│   ├── admin.py               # Admin Paneli Konfigürasyonu
│   ├── apps.py                # Uygulama Başlangıç Ayarları
│   ├── forms.py               # Form Tanımlamaları
│   ├── models.py              # Veritabanı Modelleri (Student, Course, PO, LO...)
│   ├── tests.py               # Birim Testler
│   └── views.py               # İş Mantığı ve View Fonksiyonları
├── venv/                      # Python Sanal Ortam Klasörü
├── .gitignore                 # Git Tarafından Takip Edilmeyecek Dosyalar
├── db.sqlite3                 # SQLite Veritabanı Dosyası
├── manage.py                  # Django Komut Satırı Aracı
└── requirements.txt           # Proje Kütüphane Bağımlılıkları
⚙️ Kurulum
Projeyi yerel ortamınızda çalıştırmak için aşağıdaki adımları izleyin:

1. Repoyu Kopyalayın:

Bash
git clone [https://github.com/kadirgullukaya/student-competency-analytics.git](https://github.com/kadirgullukaya/student-competency-analytics.git)
cd student-competency-analytics
2. Sanal Ortamı Kurun ve Başlatın:

Bash
# Windows için
python -m venv venv
venv\Scripts\activate

# Mac/Linux için
python3 -m venv venv
source venv/bin/activate
3. Gereksinimleri Yükleyin:

Bash
pip install -r requirements.txt
4. Veritabanını Hazırlayın:

Bash
python manage.py migrate
5. Yönetici Hesabı Oluşturun:

Bash
python manage.py createsuperuser
6. Projeyi Başlatın:

Bash
python manage.py runserver
🚀 Yol Haritası (Roadmap)
Projenin geliştirme süreci devam etmektedir. Aşağıdaki özelliklerin v2 sürümünde eklenmesi planlanmaktadır:

[ ] PDF Raporlama: Öğrencilerin yetkinlik karnelerinin (Radar Grafiklerinin) resmi transkript benzeri PDF formatında indirilebilmesi.

[ ] Toplu Veri Aktarımı: Öğrenci listelerinin ve sınav notlarının Excel/CSV formatında toplu olarak sisteme yüklenmesi (Import/Export).

[ ] Bildirim Sistemi: Sınav sonuçları açıklandığında veya ders duyurularında öğrencilere e-posta/sistem bildirimi gönderilmesi.

[ ] API Desteği: Mobil uygulama entegrasyonu için Django REST Framework ile API endpoint'lerinin yazılması.

[ ] Docker Entegrasyonu: Projenin konteynerize edilerek sunucu dağıtımının kolaylaştırılması.

Geliştiriciler: Kadir Güllükaya & Erdoğan Uludağ & Halil Samet Şen
