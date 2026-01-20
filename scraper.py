from playwright.sync_api import sync_playwright
import time

class AmazonSession:
    def __init__(self):
        self.url = "https://hiring.amazon.com/search/warehouse-jobs"

    def get_fresh_token(self):
        """Opens a headless browser to intercept the AppSync Bearer token."""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            page = context.new_page()

            captured_token = {"token": None}

            def handle_request(request):
                if "appsync-api" in request.url:
                    auth = request.headers.get("authorization")
                    if auth and "Bearer" in auth and len(auth) > 200:
                        captured_token["token"] = auth
                        print(f"Found token: {auth}")
                    else:
                        print("Authorization header missing or invalid in AppSync request.")

            page.on("request", handle_request)
            
            try:
                # Wait until network is quiet to ensure GraphQL calls have fired
                page.goto(self.url, wait_until="networkidle", timeout=60000)
                time.sleep(5) 
            except Exception as e:
                print(f"Browser error: {e}")
            
            browser.close()
            
            return captured_token["token"]
