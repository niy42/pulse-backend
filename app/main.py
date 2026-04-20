# from fastapi import FastAPI
# from app.bot import run_bot

# app = FastAPI()

# @app.get("/")
# def health():
#     return {"status": "running"}

# @app.on_event("startup")
# def startup():
#     run_bot()

# from app.bot import run_bot
# from dotenv import load_dotenv

# load_dotenv()

# if __name__ == "__main__":
#     run_bot()


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import threading
from dotenv import load_dotenv
from app.api.routes import user
from app.bot import run_bot
from app.api.routes.jobs import router as jobs_router

load_dotenv()

app = FastAPI()


# ✅ CORS (frontend connection)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ✅ Register routes
app.include_router(jobs_router)
app.include_router(user.router)


# ✅ Health check
@app.get("/")
def health():
    return {"status": "running"}


# 🤖 Run Telegram bot in background
# @app.on_event("startup")
# def start_bot():
#     thread = threading.Thread(target=run_bot, daemon=True)
#     thread.start()


# if __name__ == "__main__":
#     run_bot()
