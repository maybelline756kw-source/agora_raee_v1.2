from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"status": "ok", "message": "¡El servidor en Vercel está vivo!"}
