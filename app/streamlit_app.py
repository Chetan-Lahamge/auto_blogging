import streamlit as st
import os
import logging
import re
import sys
from dotenv import load_dotenv

load_dotenv() # Moved to the very top

# Add the project root to the sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.trend_scraper import get_trending_topics
from src.blog_writer import generate_blog, generate_attractive_title, generate_blog_from_content
from src.blogger_api import post_to_blogger
from src.blog_db import init_db, blog_exists, add_blog_entry, get_recent_topics, get_all_normalized_titles
from src.config import BLOGGER_BLOG_ID

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def normalize_title(title: str) -> str:
    """Normalizes a title for consistent database lookup."""
    return re.sub(r'[^a-z0-9]', '', title.lower())

def run_auto_blogger(generation_mode, provided_content, custom_title):
    st.write("Initializing...")
    init_db()

    if not BLOGGER_BLOG_ID:
        st.error("BLOGGER_BLOG_ID environment variable not set in config.py or .env. Please set it up.")
        logging.error("BLOGGER_BLOG_ID environment variable not set.")
        return

    blog_title = ""
    blog_content = ""
    original_topic_for_db = "" # To store the original topic or a derived one for DB tracking

    all_existing_titles = get_all_normalized_titles() # Fetch all existing titles once

    MAX_TITLE_RETRIES = 5 # Max attempts to generate a unique title

    if generation_mode == "From Trending Topic":
        st.write("Fetching trending topics...")
        try:
            topics = get_trending_topics()
            if not topics:
                st.info("No trending topics found.")
                logging.info("No trending topics found.")
                return
        except Exception as e:
            st.error(f"Error fetching trending topics: {e}")
            logging.error(f"Error fetching trending topics: {e}")
            return

        # Example of Trend Topic Filtering:
        filtered_topics = [topic for topic in topics if "news" not in topic.lower()]
        if not filtered_topics:
            st.info("No relevant trending topics after filtering.")
            logging.info("No relevant trending topics after filtering.")
            return

        recent_topics = get_recent_topics(limit=5) # Get last 5 posted topics
        logging.info(f"Recent topics: {recent_topics}")

        def is_similar(topic1: str, topic2: str) -> bool:
            """Checks if two topics are similar based on keyword overlap."""
            words1 = set(topic1.lower().split())
            words2 = set(topic2.lower().split())
            return bool(words1.intersection(words2))

        selected_topic = None
        for topic in filtered_topics:
            is_new_theme = True
            for recent_topic in recent_topics:
                if is_similar(topic, recent_topic):
                    is_new_theme = False
                    break
            if is_new_theme:
                selected_topic = topic
                break

        if selected_topic is None and filtered_topics: # If all topics are similar to recent ones, just pick the first available
            selected_topic = filtered_topics[0]
            st.info("All trending topics are similar to recently posted ones. Selecting the first available topic.")

        if selected_topic is None:
            st.info("No suitable topic found to generate a blog.")
            return

        original_topic_for_db = selected_topic
        st.write(f"Processing topic: {selected_topic}")

        # Title generation retry loop for Trending Topic
        for attempt in range(MAX_TITLE_RETRIES):
            try:
                st.write(f"Attempt {attempt + 1}/{MAX_TITLE_RETRIES} to generate unique title...")
                blog_title = generate_attractive_title(selected_topic, all_existing_titles)
                normalized_attractive_title = normalize_title(blog_title)

                if not blog_exists(normalized_attractive_title): # Check against DB
                    st.info(f"Generated unique title: {blog_title}")
                    break # Unique title found
                else:
                    st.warning(f"Generated title '{blog_title}' already exists. Retrying...")
                    # Add the generated title to all_existing_titles to avoid generating it again in this run
                    all_existing_titles.append(normalized_attractive_title)
            except Exception as e:
                st.error(f"Failed to generate attractive title for topic '{selected_topic}' (Attempt {attempt + 1}): {e}")
                logging.error(f"Failed to generate attractive title for topic '{selected_topic}' (Attempt {attempt + 1}): {e}")
                blog_title = "" # Reset to ensure it's empty if generation fails
                break # Exit loop on error

        if not blog_title:
            st.error(f"Could not generate a unique attractive title after {MAX_TITLE_RETRIES} attempts. Aborting.")
            return

        st.write(f"Generating blog content for '{blog_title}'...")
        try:
            blog_content = generate_blog(blog_title)
        except Exception as e:
            st.error(f"Failed to generate blog content for '{blog_title}': {e}")
            logging.error(f"Failed to generate blog content for '{blog_title}': {e}")
            return

    elif generation_mode == "From Provided Content":
        original_content_to_process = provided_content
        if provided_content.startswith("http://") or provided_content.startswith("https://"):
            st.write(f"Fetching content from URL: {provided_content}")
            try:
                fetch_result = default_api.web_fetch(prompt=f"Extract main content from: {provided_content}")
                if fetch_result and fetch_result.get('content'):
                    original_content_to_process = fetch_result['content']
                    st.write("Content fetched successfully.")
                else:
                    st.error(f"Failed to fetch content from URL: {provided_content}")
                    logging.error(f"Failed to fetch content from URL: {provided_content}")
                    return
            except Exception as e:
                st.error(f"Error during web_fetch: {e}")
                logging.error(f"Error during web_fetch: {e}")
                return
        
        if not original_content_to_process:
            st.warning("No content to process.")
            return

        original_topic_for_db = custom_title if custom_title else original_content_to_process[:50] # Use custom title or first 50 chars for DB tracking

        if custom_title:
            blog_title = custom_title
            st.write(f"Using provided custom title: {blog_title}")
            # Check if custom title exists
            normalized_attractive_title = normalize_title(blog_title)
            if blog_exists(normalized_attractive_title):
                st.info(f"Blog with custom title '{blog_title}' (normalized: '{normalized_attractive_title}') already exists in DB. Skipping.")
                logging.info(f"Blog with custom title '{blog_title}' (normalized: '{normalized_attractive_title}') already exists in DB. Skipping.")
                return
        else:
            st.write("Generating attractive title from provided content...")
            # Title generation retry loop for Provided Content
            for attempt in range(MAX_TITLE_RETRIES):
                try:
                    st.write(f"Attempt {attempt + 1}/{MAX_TITLE_RETRIES} to generate unique title...")
                    blog_title = generate_attractive_title(original_content_to_process, all_existing_titles) # Generate title from content
                    normalized_attractive_title = normalize_title(blog_title)

                    if not blog_exists(normalized_attractive_title): # Check against DB
                        st.info(f"Generated unique title: {blog_title}")
                        break # Unique title found
                    else:
                        st.warning(f"Generated title '{blog_title}' already exists. Retrying...")
                        all_existing_titles.append(normalized_attractive_title)
                except Exception as e:
                    st.error(f"Failed to generate attractive title from provided content (Attempt {attempt + 1}): {e}")
                    logging.error(f"Failed to generate attractive title from provided content (Attempt {attempt + 1}): {e}")
                    blog_title = "" # Reset to ensure it's empty if generation fails
                    break # Exit loop on error

            if not blog_title:
                st.error(f"Could not generate a unique attractive title after {MAX_TITLE_RETRIES} attempts. Aborting.")
                return

        st.write(f"Generating detailed blog from provided content with title: {blog_title}...")
        try:
            blog_content = generate_blog_from_content(original_content_to_process, blog_title)
        except Exception as e:
            st.error(f"Failed to generate blog from provided content: {e}")
            logging.error(f"Failed to generate blog from provided content: {e}")
            return

    # Common logic for both modes
    if not blog_title or not blog_content:
        st.warning("Blog title or content could not be generated. Skipping post.")
        return

    # Final check before posting (in case of custom title or last-minute race condition)
    normalized_attractive_title = normalize_title(blog_title)
    if blog_exists(normalized_attractive_title):
        st.info(f"Blog with title '{blog_title}' (normalized: '{normalized_attractive_title}') already exists in DB. Skipping final post.")
        logging.info(f"Blog with title '{blog_title}' (normalized: '{normalized_attractive_title}') already exists in DB. Skipping final post.")
        return

    st.write("Content generated. Posting to Blogger...")
    try:
        post_to_blogger(title=blog_title, content=blog_content, blog_id=BLOGGER_BLOG_ID)
        add_blog_entry(title=normalized_attractive_title, status="posted")
        st.success(f"Successfully posted blog with title: {blog_title}")
        logging.info(f"Successfully posted blog with title: {blog_title}")
    except Exception as e:
        st.error(f"Failed to post blog with title '{blog_title}': {e}")
        add_blog_entry(title=normalized_attractive_title, status="failed")
        logging.error(f"Failed to post blog with title '{blog_title}': {e}")

st.title("Auto-Blogger Application")

# Blog Generation Mode Selection
generation_mode = st.radio(
    "Choose Blog Generation Mode:",
    ("From Trending Topic", "From Provided Content"),
    index=0 # Default to Trending Topic
)

provided_content = ""
custom_title = ""

if generation_mode == "From Provided Content":
    provided_content = st.text_area(
        "Paste Blog Content or URL Here:",
        height=200,
        help="Paste the full content of a blog post or a URL to an article. The LLM will use this as context."
    )
    custom_title = st.text_input(
        "Optional: Provide a Custom Title (Leave blank for AI-generated title)",
        help="If you provide content, you can also suggest a title. If left blank, an attractive title will be generated from the content."
    )

if st.button("Generate & Post Blog"):
    if generation_mode == "From Provided Content" and not provided_content:
        st.warning("Please provide content or a URL to generate a blog from.")
    else:
        run_auto_blogger(generation_mode, provided_content, custom_title)
