from fastapi import FastAPI, Request  # <-- Ensure Request is imported
from mediaflow_proxy.main import app as mediaflow_app  # Import mediaflow app
import httpx
import re
import string

# Initialize the main FastAPI application
main_app = FastAPI()

# Middleware to log IPs
@main_app.middleware("http")
async def log_ip_middleware(request: Request, call_next):
    # First check for X-Viewer-IP, which should be set by AIOStreams
    viewer_ip = request.headers.get('X-Viewer-IP')
    if viewer_ip:
        # Log the forwarded viewer IP
        print(f"[FORWARDED IP] Viewer IP: {viewer_ip} streaming {request.url}")
    else:
        # Fallback to the IP in x-forwarded-for or the client's IP address
        client_ip = request.headers.get('x-forwarded-for', request.client.host)
        print(f"[IP LOG] {client_ip} requested {request.url}")
    
    response = await call_next(request)
    return response

# Manually add only non-static routes from mediaflow_app
for route in mediaflow_app.routes:
    if route.path != "/":  # Exclude the static file path
        main_app.router.routes.append(route)

# Run the main app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(main_app, host="0.0.0.0", port=8080)
