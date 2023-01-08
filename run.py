import os
from dotenv import load_dotenv
from waitress import serve
import app

load_dotenv()

PORT = os.getenv("PORT", 5000)
print("Waitress serving on port", PORT)

serve(app.app, host="0.0.0.0", port=PORT)
