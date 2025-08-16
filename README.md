# Wiremit Forex Rates Backend Service


## How to Run the API
1. Install dependencies: `pip install fastapi uvicorn sqlalchemy requests pyjwt passlib[bcrypt] python-dotenv`
2. Create a `.env` file with:
   ```
   FASTFOREX_API_KEY=your_fastforex_key
   CURRENCYFREAKS_API_KEY=your_currencyfreaks_key
   EXCHANGERATES_API_KEY=your_exchangerates_key
   SECRET_KEY=your_jwt_secret_key_here
   DATABASE_URL=sqlite:///wiremit.db
   ```
3. Run: `uvicorn main:app --reload`
4. Access at http://127.0.0.1:8000/docs for interactive Swagger UI.

## Authentication Flow
- **Signup:** POST `/signup` with JSON `{"username": "...", "password": "..."}`. Passwords are hashed with bcrypt.
- **Login:** POST `/login` with form data (username, password). Returns JWT token.
- **Protected Endpoints:** Include `Authorization: Bearer <token>` header. JWT is verified (HS256 algorithm).
- **Justification:** JWT is secure, stateless, and scalable. Integrates well with FastAPI.

## Rate Aggregation Logic
- Fetches rates from FastForex, CurrencyFreaks, and ExchangeRatesAPI (USD→GBP, USD→ZAR).
- Calculates ZAR→GBP as (USD→GBP) / (USD→ZAR).
- Averages rates across successful API responses (skips failures).
- Stores averages in SQLite with timestamps.
- Refreshes on startup and every hour via a background thread.
- Serves rates with 10% markup: `customer_rate = average_rate * 1.10`.
- Historical rates are stored averages (no markup).