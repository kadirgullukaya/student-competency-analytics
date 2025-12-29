# 🎓 Student Competency Analytics (Akademik OBS)

**Student Competency Analytics**, klasik notlandırma sistemlerinin ötesine geçerek, öğrencilerin akademik başarılarını **Çıktı Temelli Eğitim (Outcome-Based Education)** modeline göre analiz eden web tabanlı bir öğrenci bilgi sistemidir.

Bu proje, öğrencilerin sadece sınav puanlarını değil; **Program Çıktıları (PO)** ve **Öğrenme Çıktıları (LO)** bazındaki yetkinliklerini **Radar Grafikleri** ve detaylı veri analizleriyle görselleştirir.

## 🚀 Projenin Amacı
Üniversiteler ve eğitim kurumları için kritik olan **"Hangi öğrenci, hangi yetkinliği ne kadar kazandı?"** sorusuna dijital ve görsel bir çözüm sunmaktır.

## 🔐 Temel Özellikler

### 🏛️ Bölüm Başkanı Paneli (Yönetici)
* **Müfredat Yönetimi**: Dönem, Ders ve Bölüm tanımlamaları.
* **Çıktı Tanımlama**: Bölümün vizyonuna uygun Program Çıktılarını (PO) belirleme.
* **Genel Bakış**: Toplam öğrenci, aktif ders ve sınav istatistiklerini dashboard üzerinden izleme.
* **Kullanıcı Yönetimi**: Akademisyen ve öğrenci kayıtlarını yönetme.

### 👨‍🏫 Öğretmen Paneli
* **LO Yönetimi**: Derslere özel Öğrenme Çıktıları (LO) oluşturma.
* **Sınav Kurgusu**: Sınav sorularını ilgili LO'lar ile eşleştirme ve ağırlıklandırma.
* **Analiz**: Dersi alan öğrencilerin başarı dağılımını grafiklerle inceleme.

### 👨‍🎓 Öğrenci Paneli
* **Yetkinlik Karnesi**: Klasik transkript yerine, hangi yetkinlikte ne kadar güçlü olduğunu gösteren Radar Grafikleri.
* **Başarım Takibi**: Ders bazlı ve genel mezuniyet hedeflerine (PO) ulaşma oranları.

## 🛠️ Teknoloji Yığını

| Alan | Teknoloji | Açıklama |
| :--- | :--- | :--- |
| **Backend** | Python & Django 5.0+ | Güçlü web mimarisi |
| **Frontend** | Bootstrap 5 | Modern ve duyarlı tasarım |
| **Veritabanı** | SQLite | Yerel geliştirme veritabanı |
| **Görselleştirme** | Chart.js 4.0 | Dinamik Radar ve Bar grafikleri |

## 📂 Proje Yapısı

Proje dosyaları, modüler Django mimarisine uygun olarak aşağıdaki gibi düzenlenmiştir:

```text
SOFTWAREPROJECT/
├── .github/                   # GitHub Actions ve Konfigürasyonlar
├── obs_core/                  # Proje Ana Ayar Dosyaları
│   ├── settings.py            # Uygulama ve Middleware Ayarları
│   ├── urls.py                # Ana URL Yönlendirmeleri
│   └── wsgi.py
├── academic/                  # Ana Uygulama (App) Klasörü
│   ├── migrations/            # Veritabanı Değişiklik Geçmişi
│   ├── templates/             # HTML Arayüz Dosyaları
│   ├── templatetags/          # Özel Django Template Etiketleri
│   ├── admin.py               # Admin Paneli Konfigürasyonu
│   ├── forms.py               # Form Tanımlamaları
│   ├── models.py              # Veritabanı Modelleri
│   └── views.py               # İş Mantığı ve Görünümler
├── manage.py                  # Django Komut Satırı Aracı
└── requirements.txt           # Bağımlılıklar





⚙️ Kurulum
Projeyi yerel ortamınızda çalıştırmak için aşağıdaki adımları izleyin:

1. Repoyu Kopyalayın:

```bash
git clone [https://github.com/kadirgullukaya/student-competency-analytics.git](https://github.com/kadirgullukaya/student-competency-analytics.git)
cd student-competency-analytics
```

2. Sanal Ortamı Kurun ve Başlatın:

```bash
# Windows için
python -m venv venv
venv\Scripts\activate

# Mac/Linux için
python3 -m venv venv
source venv/bin/activate
```

3. Gereksinimleri Yükleyin:

```bash
pip install -r requirements.txt
```

4. Veritabanını Hazırlayın:

```bash
python manage.py migrate
```

5. Yönetici Hesabı Oluşturun:

```bash
python manage.py createsuperuser
```

6. Projeyi Başlatın:

```bash
python manage.py runserver
```



🚀 Yol Haritası (Roadmap)
Projenin geliştirme süreci devam etmektedir. Aşağıdaki özelliklerin v2 sürümünde eklenmesi planlanmaktadır:

[ ] PDF Raporlama: Yetkinlik karnelerinin resmi belge formatında indirilmesi.

[ ] Toplu Veri Aktarımı: Excel/CSV formatında toplu not ve öğrenci yükleme.

[ ] Bildirim Sistemi: Sınav sonuçları açıklandığında otomatik e-posta bildirimi.

[ ] API Desteği: Mobil uygulama entegrasyonu için REST API desteği.



Geliştiriciler: Kadir Güllükaya & Erdoğan Uludağ & Halil Samet Şen