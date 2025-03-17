import scrapy
import requests
import json

class AirbnbSpider(scrapy.Spider):
    name = "airbnb"

    def start_requests(self):
        url = "https://www.airbnb.com/s/{location}/homes"
        params = {
            'checkin': self.checkin,
            'checkout': self.checkout,
            'adults': self.guests
        }
        yield scrapy.Request(url.format(location=self.location), self.parse, cb_kwargs={'params': params})

    def parse(self, response, params):
        listings = response.css('div._8ssblpx')
        for listing in listings:
            data = {
                "title": listing.css('span._1whrsux9::text').get(),
                "location": self.location,
                "price_per_night": listing.css('span._olc9rf0::text').get(),
                "ratings": listing.css('span._10fy1f8::text').get(),
                "image_urls": listing.css('img::attr(src)').getall()
            }
            headers = {"Content-Type": "application/json"}
            requests.post("http://localhost:8000/api/add_listing", json=data, headers=headers)

# ===============================
# Backend: Django REST Framework
# ===============================

# models.py
from django.db import models

class Listing(models.Model):
    title = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    ratings = models.FloatField()
    image_urls = models.JSONField()

# serializers.py
from rest_framework import serializers
from .models import Listing

class ListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Listing
        fields = '__all__'

# views.py
from rest_framework import generics
from .models import Listing
from .serializers import ListingSerializer

class ListingCreateView(generics.CreateAPIView):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer

class ListingListView(generics.ListAPIView):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer

# urls.py
from django.urls import path
from .views import ListingCreateView, ListingListView

urlpatterns = [
    path('api/add_listing', ListingCreateView.as_view(), name='add_listing'),
    path('api/listings', ListingListView.as_view(), name='listings'),
]

# ===============================
# Frontend: Next.js with Tailwind CSS
# ===============================

// pages/index.js
import { useState, useEffect } from 'react'

export default function Home() {
    const [listings, setListings] = useState([])

    useEffect(() => {
        fetch('http://localhost:8000/api/listings')
            .then(res => res.json())
            .then(data => setListings(data))
    }, [])

    return (
        <div className="p-5">
            <h1 className="text-2xl font-bold">Airbnb Listings</h1>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-5">
                {listings.map((listing, index) => (
                    <div key={index} className="border p-4 rounded shadow-md">
                        <img src={listing.image_urls[0]} alt={listing.title} className="w-full h-48 object-cover rounded" />
                        <h2 className="text-xl font-semibold mt-2">{listing.title}</h2>
                        <p>{listing.location}</p>
                        <p>Price: ${listing.price_per_night}</p>
                        <p>Ratings: {listing.ratings}</p>
                    </div>
                ))}
            </div>
        </div>
    )
}

// tailwind.config.js
module.exports = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,ts,jsx,tsx}"
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}

// postcss.config.js
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}

// styles/globals.css
@tailwind base;
@tailwind components;
@tailwind utilities;

# ===============================
# Environment Configuration
# ===============================

# .env (for Django)
DATABASE_URL=mysql://user:password@localhost:3306/airbnb_db
SECRET_KEY=your_secret_key

# ===============================
# Instructions to Run
# ===============================
1. Install dependencies for each module (backend, frontend, and scraper).
2. Run MySQL server and create a database `airbnb_db`.
3. Run Django backend:
   - python manage.py makemigrations
   - python manage.py migrate
   - python manage.py runserver
4. Run Scrapy scraper:
   - scrapy crawl airbnb -a location='New York' -a checkin='2025-03-20' -a checkout='2025-03-25' -a guests=2
5. Run Next.js frontend:
   - npm run dev
