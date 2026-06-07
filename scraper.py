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
                # Look for the GraphQL endpoint instead of AppSync
                if "/graphql" in request.url and "hiring.amazon.com" in request.url:
                    print(f"[DEBUG] GraphQL request detected: {request.url}")
                    auth = request.headers.get("authorization")
                    if auth:
                        captured_token["token"] = auth
                        print(f"✓ Token captured successfully (length: {len(auth)})")
                    else:
                        print(f"[WARNING] No authorization header in GraphQL request")
                        print(f"[DEBUG] Headers: {list(request.headers.keys())}")
                elif "sts.us-east-1.amazonaws.com" in request.url or "cognito-identity" in request.url:
                    print(f"[DEBUG] AWS Auth request: {request.url[:80]}...")
                elif "authorize/api" in request.url:
                    print(f"[DEBUG] Authorize API: {request.url[:80]}...")

            page.on("request", handle_request)
            
            try:
                print(f"[DEBUG] Navigating to: {self.url}")
                # Wait until network is quiet to ensure GraphQL calls have fired
                page.goto(self.url, wait_until="networkidle", timeout=60000)
                print(f"[DEBUG] Page loaded, waiting 5s for API calls...")
                time.sleep(5)
                print(f"[DEBUG] Wait complete")
            except Exception as e:
                print(f"Browser error: {e}")
            
            browser.close()
            
            if captured_token["token"]:
                print(f"✓ Successfully captured token")
            else:
                print(f"✗ FAILED to capture token - The website structure may have changed")
            
            return captured_token["token"]
