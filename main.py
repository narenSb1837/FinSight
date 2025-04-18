import os
import logging
from app import app

logging.basicConfig(level=logging.DEBUG)

# Vercel serverless handler
handler = app

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7001, debug=True)
