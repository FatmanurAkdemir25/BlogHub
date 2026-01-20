from app import create_app

app = create_app()#uygulama factory fonksiyonunu çağır

if __name__ == '__main__': #bu dosya doğrudan çalıştırılıyorsa yani python run.py olur import run olmaz
    app.run(debug=True) #development server başlat