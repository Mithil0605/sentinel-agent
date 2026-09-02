import multiprocessing
import os

import uvicorn

if __name__ == "__main__":
    workers = int(os.getenv("UVICORN_WORKERS", "1"))
    uvicorn.run(
        "app.main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        workers=workers,
    )
