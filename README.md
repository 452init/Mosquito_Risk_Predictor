# Mosquito Risk Predictor

A full-stack web application that estimates mosquito activity risk for any city based on real-time weather and forecast data. Enter a city name, and the app geocodes the location, fetches weather from the Weather AI API, computes a risk score (0–3), and returns actionable recommendations.

The main aim of the application is to reduce the risk of getting Malaria through mosquito bites. The Malaria menace has been one of the biggest bottleneck in most African cities for a very long time. With the application in place, such cases can be reduced through smart prevention measures.

## Features

- **City-based risk assessment** — Search any city worldwide via Open-Meteo geocoding (no API key required)
- **Weather-driven scoring** — Combines temperature, humidity, and rain forecast into a 0–3 risk score
- **Risk categories** — LOW, MEDIUM, or HIGH with plain-language explanations
- **Actionable advice** — Tailored recommendations (e.g., use a mosquito net)
- **7-day forecast summary** — Temperature, precipitation, and conditions at a glance
- **Search history** — Last 10 assessments stored in the database
- **Modern UI** — React frontend with glassmorphism design and responsive layout

## Architecture

```
┌─────────────────┐     HTTP/JSON      ┌─────────────────┐
│                 │ ◄────────────────► │                 │
│ React Frontend  │                    │  Flask Backend  │
│                 │                    │                 │
└─────────────────┘                    └────────┬────────┘
                                                │
                      ┌─────────────────────────┼─────────────────────────┐
                      │                         │                         │
                      ▼                         ▼                         ▼
             ┌───────────────┐        ┌─────────────────┐        ┌───────────────┐
             │  Supabase     │        │  Weather AI API │        │  Open-Meteo   │
             │  PostgreSQL   │        │  (current +     │        │  Geocoding    │
             │  (history)    │        │   forecast)     │        │  (free)       │
             └───────────────┘        └─────────────────┘        └───────────────┘
```

### Request flow

1. User submits a city name from the frontend
2. Backend geocodes the city → latitude/longitude
3. Backend fetches current weather and 7-day forecast
4. Risk engine scores three factors (temperature, humidity, rain)
5. Category and advice are generated; result is saved to the database
6. JSON response is rendered in the UI (weather card + risk gauge)

## Tech Stack

### Frontend (`frontend/`)

| Technology | Purpose |
|------------|---------|
| [React 19](https://react.dev/) | UI framework |
| [Vite 8](https://vite.dev/) | Build tool and dev server |
| [Axios](https://axios-http.com/) | HTTP client for API calls |
| [Oxlint](https://oxc.rs/) | Linting |
| CSS (custom design system) | Dark theme, glassmorphism, risk color tokens |

### Backend (`backend/`)

| Technology | Purpose |
|------------|---------|
| [Python 3.11+](https://www.python.org/) | Runtime |
| [Flask 3](https://flask.palletsprojects.com/) | Web framework and REST API |
| [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/) | ORM and database integration |
| [Flask-CORS](https://flask-cors.readthedocs.io/) | Cross-origin requests from the frontend |
| [Requests](https://requests.readthedocs.io/) | External API calls (weather, geocoding) |
| [Gunicorn](https://gunicorn.org/) | Production WSGI server |
| [python-dotenv](https://github.com/theskumar/python-dotenv) | Environment variable loading |
| [pytest](https://docs.pytest.org/) | Testing (development) |

### Database

| Technology | Purpose |
|------------|---------|
| [Supabase PostgreSQL](https://supabase.com/) | Hosted PostgreSQL for production (recommended) |
| PostgreSQL (local) | Alternative local development database |
| SQLite | Supported for local testing (in-memory or file-based) |

**Schema:** Single table `risk_reports` stores city, coordinates, weather snapshot, risk score/category, reasons, advice, and timestamp.

### External APIs

| Service | Auth | Usage |
|---------|------|--------|
| [Weather AI](https://weather-ai.co/) | API key (`WEATHER_API_KEY`) | Current weather and 7-day forecast |
| [Open-Meteo Geocoding](https://open-meteo.com/en/docs/geocoding-api) | None | Resolve city names to coordinates |

## Risk Scoring Model

The score is the sum of three binary factors (0–3 total):

| Factor | Condition | Points |
|--------|-----------|--------|
| Temperature | 20°C – 30°C (ideal mosquito range) | +1 |
| Humidity | ≥ 60% | +1 |
| Rain | Precipitation or rain in forecast within 48 hours | +1 |

**Categories:**

| Score | Category |
|-------|----------|
| 3 | HIGH |
| 2 | MEDIUM |
| 0–1 | LOW |

Constants are defined in `backend/app/utils/constants.py`.

## Project Structure

```
Mosquito_Risk_Predictor/
├── README.md                 # This file
├── backend/
│   ├── app/
│   │   ├── __init__.py       # Flask app factory
│   │   ├── config.py         # Environment-based configuration
│   │   ├── extensions.py     # SQLAlchemy, CORS
│   │   ├── models.py         # RiskReport model
│   │   ├── routes/
│   │   │   └── api.py        # REST endpoints
│   │   ├── services/
│   │   │   ├── geocoding.py  # City → coordinates
│   │   │   ├── weather.py    # Weather AI integration
│   │   │   └── risk.py       # Scoring logic
│   │   └── utils/
│   │       └── constants.py  # Risk thresholds
│   ├── tests/                # pytest suite
│   ├── .env.example          # Environment template
│   ├── requirements.txt
│   ├── render.yaml           # Render.com deployment config
│   └── run.py                # Dev entry point
└── frontend/
    ├── src/
    │   ├── App.jsx           # Main application shell
    │   ├── components/       # CityInput, WeatherCard, RiskDisplay, Loader
    │   └── services/
    │       └── api.js        # Backend API client
    ├── package.json
    └── vite.config.js
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/health` | Health check |
| `POST` | `/api/risk` | Full risk assessment (body: `{ "city_name": "Nairobi" }`) |
| `GET` | `/api/history` | Last 10 stored risk reports |

### Example: POST `/api/risk`

**Request:**
```json
{
  "city_name": "Nairobi"
}
```

**Response (200):**
```json
{
  "city_name": "Nairobi, KE",
  "location": { "latitude": -1.28, "longitude": 36.82, "country": "KE", "region": "Nairobi City" },
  "current_weather": {
    "temperature": 24.5,
    "humidity": 72,
    "condition": "Partly cloudy",
    "wind_speed": 12,
    "feels_like": 25.1
  },
  "risk": {
    "score": 3,
    "max_score": 3,
    "category": "HIGH",
    "reasons": ["Temperature is in the ideal range...", "High humidity...", "Recent or upcoming rain..."],
    "advice": "Use a mosquito net tonight. Clear any standing water near your home."
  },
  "forecast_summary": [...]
}
```

## Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.11+
- **Weather AI API key** — [Sign up free](https://weather-ai.co/)
- **PostgreSQL database** — [Supabase](https://supabase.com/) (recommended) or local PostgreSQL

## Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd Mosquito_Risk_Predictor
```

### 2. Backend setup

```bash
cd backend

# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
```

Edit `backend/.env`:

```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@db.YOUR_PROJECT_REF.supabase.co:5432/postgres
WEATHER_API_KEY=wai_your_api_key_here
FRONTEND_URL=http://localhost:5173
FLASK_ENV=development
SECRET_KEY=your-random-secret-key
```

**Local development without PostgreSQL:** use SQLite instead:

```env
DATABASE_URL=sqlite:///mosquito_risk.db
```

Start the backend:

```bash
python run.py
```

The API runs at **http://localhost:5000**.

### 3. Frontend setup

In a new terminal:

```bash
cd frontend

npm install

# Optional: point to a non-default API URL
# echo "VITE_API_URL=http://localhost:5000/api" > .env

npm run dev
```

The app runs at **http://localhost:5173**.

## Environment Variables

### Backend (`backend/.env`)

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | PostgreSQL or SQLite connection string |
| `WEATHER_API_KEY` | Yes | Weather AI API bearer token |
| `FRONTEND_URL` | No | Allowed CORS origin (default: `http://localhost:5173`) |
| `FLASK_ENV` | No | `development` or `production` |
| `SECRET_KEY` | Yes (prod) | Flask secret key |

### Frontend (`frontend/.env`)

| Variable | Required | Description |
|----------|----------|-------------|
| `VITE_API_URL` | No | Backend API base URL (default: `http://localhost:5000/api`) |

## Testing

### Backend tests

```bash
cd backend
source .venv/bin/activate
pip install -r requirements-dev.txt
pytest tests/ -v
```

The test suite includes:

- **Risk service unit tests** — scoring, categories, rain detection, advice
- **Input validation unit tests** — city name sanitization and length limits
- **API integration tests** — health check, validation, history (uses in-memory SQLite)

### Frontend checks

```bash
cd frontend
npm run lint    # Oxlint
npm run build   # Production build verification
```

### Manual smoke test

With the backend running:

```bash
curl http://localhost:5000/api/health
curl http://localhost:5000/api/history
curl -X POST http://localhost:5000/api/risk \
  -H "Content-Type: application/json" \
  -d '{"city_name": "Nairobi"}'
```

## Production Deployment

### Backend (Render)

The backend includes a [Render](https://render.com/) blueprint (`backend/render.yaml`):

- **Service:** `mosquito-risk-api`
- **Build:** `pip install -r requirements.txt`
- **Start:** `gunicorn -c gunicorn.conf.py run:app`
- **Health check:** `/api/health`
- **Python:** 3.11 (`runtime.txt`)

In the Render dashboard, set:

| Variable | Value |
|----------|-------|
| `DATABASE_URL` | Supabase PostgreSQL connection string |
| `WEATHER_API_KEY` | Your Weather AI API key |
| `FRONTEND_URL` | Deployed frontend URL (e.g. `https://your-app.netlify.app`) |
| `FLASK_ENV` | `production` (set automatically by blueprint) |
| `SECRET_KEY` | Auto-generated by Render, or set manually |

### Frontend (Netlify or Vercel)

Deploy from the `frontend/` directory:

**Netlify** — uses `frontend/netlify.toml` automatically.

**Vercel** — uses `frontend/vercel.json` automatically.

Set the build environment variable:

```env
VITE_API_URL=https://your-api.onrender.com/api
```

Then build and deploy:

```bash
cd frontend
npm run build
```

### Git push checklist

Before pushing to GitHub, confirm:

1. **Never commit secrets** — `.env` files are gitignored; only `.env.example` is tracked
2. **Dependencies are lockfile-backed** — `package-lock.json` and `requirements.txt` are committed
3. **Generated folders are ignored** — `node_modules/`, `.venv/`, `dist/`, `__pycache__/`, `instance/`

```bash
git add .
git status   # verify no .env, node_modules, or .venv files are staged
git commit -m "Prepare Mosquito Risk Predictor for deployment"
git push origin main
```

## Security

The application includes these security measures:

| Area | Implementation |
|------|----------------|
| **Secrets** | All API keys and DB credentials loaded from environment variables only |
| **Production validation** | App refuses to start without `SECRET_KEY`, `WEATHER_API_KEY`, and a non-localhost `FRONTEND_URL` |
| **CORS** | Restricted to `FRONTEND_URL` in production; localhost allowed only in development |
| **Security headers** | `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, `Strict-Transport-Security` (production) |
| **Input validation** | City names are trimmed, length-limited (100 chars), and checked for control characters |
| **Request limits** | 16 KB max request body size |
| **Error handling** | Internal errors are logged server-side; generic messages returned to clients |
| **Debug mode** | Disabled automatically when `FLASK_ENV=production` |

**Recommendations for production:**

- Generate a strong `SECRET_KEY`: `python -c "import secrets; print(secrets.token_hex(32))"`
- Use Supabase PostgreSQL with SSL (included in connection string)
- Keep `WEATHER_API_KEY` server-side only — never expose it in frontend env vars
- Enable HTTPS on both frontend and backend hosts (Render/Netlify/Vercel provide this)

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `Weather API returned status...` | Verify `WEATHER_API_KEY` in `.env` |
| `City not recognized` | Try a different spelling or include country (e.g., "Paris, France") |
| CORS errors in browser | Ensure `FRONTEND_URL` matches your frontend origin |
| Database connection refused | Check `DATABASE_URL`; use SQLite for quick local testing |
| `connection to server at localhost:5432 failed` | PostgreSQL is not running; use Supabase or SQLite |

## License

This project is provided as-is for educational and demonstration purposes.
