#!/bin/bash
echo "🚀 RoccoZoom Kurulumu Başlıyor..."

# 1. Gerekli bağımlılıkları yükle
echo "📦 Paketler yükleniyor..."
npm install

# 2. Veritabanı şemasını oluştur
echo "🗄️ Veritabanı kontrolü..."
npx prisma generate

# 3. Next.js projesini derle (Build)
echo "🏗️ Proje derleniyor (Build)..."
npm run build

# 4. Eğer PM2'de zaten çalışıyorsa durdur ve sil
pm2 delete roccozoom 2>/dev/null

# 5. PM2 ile projeyi başlat (Port 3002)
echo "🟢 Proje PM2 ile başlatılıyor (Port: 3002)..."
PORT=3002 pm2 start npm --name "roccozoom" -- start

# 6. PM2 ayarlarını kaydet
pm2 save

echo "✅ RoccoZoom başarıyla 3002 portunda yayına alındı!"
