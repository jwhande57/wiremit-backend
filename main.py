from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from models import UserCreate, Token, RateOut, HistoricalRate, User, Rate
from auth import get_password_hash, get_user, create_access_token, verify_password
from rates import fetch_and_store_rates
from dependencies import get_db, get_current_user
from database import engine, Base, SessionLocal
import time
import threading
from typing import List

app = FastAPI()

# Create DB tables
Base.metadata.create_all(bind=engine)

# Constants
MARKUP = 0.10  # 10% markup

@app.post("/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user(db, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = get_password_hash(user.password)
    new_user = User(username=user.username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    return {"msg": "User created"}

@app.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = get_user(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/rates", response_model=RateOut)
def get_latest_rates(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    latest_rate = db.query(Rate).order_by(Rate.timestamp.desc()).first()
    if not latest_rate:
        raise HTTPException(status_code=404, detail="No rates available")
    return {
        "usd_to_gbp": latest_rate.usd_gbp * (1 + MARKUP),
        "usd_to_zar": latest_rate.usd_zar * (1 + MARKUP),
        "zar_to_gbp": latest_rate.zar_gbp * (1 + MARKUP),
    }

@app.get("/rates/{currency}")
def get_specific_rate(currency: str, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    latest_rate = db.query(Rate).order_by(Rate.timestamp.desc()).first()
    if not latest_rate:
        raise HTTPException(status_code=404, detail="No rates available")
    pair = currency.lower().replace("-", "").replace("_", "")
    if pair == "usdgbp":
        return {"rate": latest_rate.usd_gbp * (1 + MARKUP)}
    elif pair == "usdzar":
        return {"rate": latest_rate.usd_zar * (1 + MARKUP)}
    elif pair == "zargbp":
        return {"rate": latest_rate.zar_gbp * (1 + MARKUP)}
    else:
        raise HTTPException(status_code=400, detail="Invalid currency pair. Use e.g., 'usd-gbp'")

@app.get("/historical/rates", response_model=List[HistoricalRate])
def get_historical_rates(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    rates = db.query(Rate).order_by(Rate.timestamp.desc()).all()
    return [
        {
            "timestamp": r.timestamp.isoformat(),
            "usd_gbp": r.usd_gbp,
            "usd_zar": r.usd_zar,
            "zar_gbp": r.zar_gbp,
        }
        for r in rates
    ]

@app.on_event("startup")
def startup_event():
    with SessionLocal() as session:
        fetch_and_store_rates(session)
    def refresh_loop():
        while True:
            time.sleep(3600)
            with SessionLocal() as session:
                fetch_and_store_rates(session)
    thread = threading.Thread(target=refresh_loop, daemon=True)
    thread.start()