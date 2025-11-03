# TRS Backend (Django + DRF + ML)

> A **Django REST API** with **machine learning-powered travel recommendations**.  
> Serves the [TRS Frontend](https://github.com/anujkaran027/TRS-frontend.git).

**Deployed:** Render

---

## Features

- **JWT Authentication** (SimpleJWT)
- **ML Recommendations** using TF-IDF + Cosine Similarity
- Like & track user preferences
- PostgreSQL-ready (Render)
- CORS configured for Netlify
- Static files via WhiteNoise

---

## Tech Stack

- **Django 5.1** + **Django REST Framework**
- **SimpleJWT** for auth
- **scikit-learn** + **TF-IDF** for recommendations
- **Pandas**, **NumPy**
- **WhiteNoise** for static files
- **Render** for hosting + PostgreSQL

---

## Local Development

### 1. Clone the repo
```bash
git clone https://github.com/anujkaran027/TRS-backend.git
```

### 2. Set up virtual environment
**Linux/Mac**
```bash
python -m venv venv
source venv/bin/activate
```

**Windows**
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up `.env`
```bash
DJANGO_SECRET_KEY=your-dev-secret-key
DEBUG=True 
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:5173
DATABASE_URL=sqlite:///db.sqlite3
```

### 5. Run migrations & load data
```bash
python manage.py migrate
python manage.py load_data
```

### 6. Run server
```bash
python manage.py runserver
```

---

## ML Model

### Train Model (Optional)
```bash
python manage.py shell
>>> from api.ml.train import train_model
>>> train_model()
```

>Not needed in production — recommendations are content-based (TF-IDF).

---

## Management Commands

| Command       | Description                          |
|-----------|-------------------------------------|
| `python manage.py load_data`  | Import dataset.csv into Database |
|  `python manage.py collectstatic`  | Collect static files   |

---

## Deployment (Render)

### Render Settings

**buildCommand**
```bash
pip install -r requirements.txt &&
python manage.py migrate &&
python manage.py load_data &&
python manage.py collectstatic --no-input
```

**startCommand**
```bash
gunicorn backend.wsgi:application --bind 0.0.0.0:$PORT
```

### Environment Variables (Render)
| Key       | Value                          |
|-----------|-------------------------------------|
| `DJANGO_SECRET_KEY`  | `your-secret-key` |
| `DEBUG`   | `False`   |
| `CORS_ALLOWED_ORIGINS` | `your_netlify_app_url` |
| `DATABASE_URL` | `Your_Postgresql_Url` |

---

## Database

* **Dev**: SQLite
* **Production**: PostgreSQL (Render)

---