import traceback
from fastapi import FastAPI, Response

try:
    from main import app
except Exception as e:
    # Si main.py falla al importar o iniciar, capturamos el error exacto
    app = FastAPI()
    error_trace = traceback.format_exc()

    @app.get("/{full_path:path}")
    @app.get("/")
    def show_error(full_path: str = ""):
        return Response(
            content=f"¡Atrapamos el error exacto que causa el 500!\n\n{error_trace}",
            media_type="text/plain",
            status_code=500
        )
