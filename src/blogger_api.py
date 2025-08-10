from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import logging
import os
import json
from tenacity import retry, stop_after_attempt, wait_fixed

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@retry(stop_after_attempt(3), wait_fixed(2))
def post_to_blogger(title, content, blog_id):
    try:
        token_json_str = os.environ.get("GCP_TOKEN_JSON")
        if not token_json_str:
            raise ValueError("GCP_TOKEN_JSON environment variable not set.")
        
        creds_info = json.loads(token_json_str)
        creds = Credentials.from_authorized_user_info(creds_info, ["https://www.googleapis.com/auth/blogger"])
        
        service = build("blogger", "v3", credentials=creds)
        body = {
            "title": title,
            "content": content
        }
        response = service.posts().insert(blogId=blog_id, body=body, isDraft=True).execute()
        logging.info(f"Successfully posted blog: {title}")
        return response
    except Exception as e:
        logging.error(f"Error posting blog '{title}' to Blogger: {e}")
        raise


