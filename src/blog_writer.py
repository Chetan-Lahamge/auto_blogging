import os
import logging
import re
from datetime import date
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_fixed

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@retry(stop_after_attempt(3), wait_fixed(2))
def generate_image(client, prompt: str) -> str:
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        image_url = response.data[0].url
        return image_url
    except Exception as e:
        logging.error(f"Error generating image: {e}")
        raise  # Re-raise the exception to allow retry

@retry(stop_after_attempt(3), wait_fixed(2))
def generate_attractive_title(topic: str, titles_to_avoid: list[str] = None) -> str:
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    current_date = date.today().strftime("%B %d, %Y")
    avoid_prompt = ""
    if titles_to_avoid:
        avoid_prompt = f"\nAvoid generating titles similar to or containing keywords from: {', '.join(titles_to_avoid)}"
    prompt = f"""Generate 5 highly attractive, clickbait-style, and SEO-friendly blog post titles based on the following topic: "{topic}". Today's date is {current_date}. The titles should be concise, engaging, and make readers want to click immediately. Provide only the titles, one per line, without any additional text or numbering.{avoid_prompt}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150 # Increased max_tokens to allow for multiple titles
        )
        raw_titles = response.choices[0].message.content.strip().split('\n')
        # Select the first non-empty title as the attractive title
        attractive_title = next((title.strip() for title in raw_titles if title.strip()), topic) # Fallback to original topic if no attractive title is generated
        attractive_title = re.sub(r"^\d+\.\s*", "", attractive_title) # Remove leading numbers and periods
        attractive_title = re.sub(r"^\d+\.\s*", "", attractive_title) # Remove leading numbers and periods
        logging.info(f"Generated attractive title for '{topic}': {attractive_title}")
        return attractive_title
    except Exception as e:
        logging.error(f"Error generating attractive title for '{topic}': {e}")
        raise

@retry(stop_after_attempt(3), wait_fixed(2))
def generate_blog(title: str) -> str:
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    current_date = date.today().strftime("%B %d, %Y")
    prompt = f"""Write a 1000-word SEO blog post titled: "{title}". Today's date is {current_date}.
    The post should be in HTML format, suitable for a blog.
    It should be written in a human-like, engaging, and first-person style, as if a person is writing it.
    It should include:
    - An engaging intro
    - Use of headings (h2, h3) and paragraphs (<p>)
    - Bullet points (<ul><li>) and examples
    - A call to action at the end.
    - Absolutely do NOT include any personal information, email addresses, or names.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
        )
        raw_content = response.choices[0].message.content
    except Exception as e:
        logging.error(f"Error generating blog content: {e}")
        raise  # Re-raise the exception to allow retry

    image_prompt = f"A relevant image for a blog post titled: {title}"
    image_url = generate_image(client, image_prompt)

    if image_url:
        # Embed the image at the beginning of the blog post
        raw_content = f'<img src="{image_url}" alt="{title}" style="width:100%; max-width:600px; height:auto;"><br>' + raw_content

    return raw_content

@retry(stop_after_attempt(3), wait_fixed(2))
def generate_blog_from_content(original_content: str, title: str) -> str:
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    current_date = date.today().strftime("%B %d, %Y")
    prompt = f"""Rewrite and expand the following content into a 1000-word SEO blog post titled: "{title}". Today's date is {current_date}.
    The post should be in HTML format, suitable for a blog.
    It should be written in a human-like, engaging, and first-person style, as if a person is writing it.
    It should include:
    - An engaging intro
    - Use of headings (h2, h3) and paragraphs (<p>)
    - Bullet points (<ul><li>) and examples
    - A call to action at the end.
    - Absolutely do NOT include any personal information, email addresses, or names.

    Original Content to Expand/Rewrite:
    {original_content}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
        )
        raw_content = response.choices[0].message.content
    except Exception as e:
        logging.error(f"Error generating blog from provided content: {e}")
        raise  # Re-raise the exception to allow retry

    image_prompt = f"A relevant image for a blog post titled: {title}"
    image_url = generate_image(client, image_prompt)

    if image_url:
        raw_content = f'<img src="{image_url}" alt="{title}" style="width:100%; max-width:600px; height:auto;"><br>' + raw_content

    return raw_content
