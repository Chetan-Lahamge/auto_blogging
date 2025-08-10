# Auto-Blogger Application

## Project Overview

The Auto-Blogger is a Python-based application designed to automate the process of generating and posting blog content to Google Blogger. It leverages trending topics, AI-powered content generation, and intelligent topic selection to ensure fresh and relevant posts. The application is built with a Streamlit interface for easy local execution and is configured for seamless deployment on Streamlit Cloud.

### What's New?

*   **Automated Image Generation:** Now featuring automated image generation for blog posts using DALL-E 3, with images stored in a local `images` directory.
*   **Enhanced Error Handling:** Improved error handling with `tenacity` for robust retries on API calls and comprehensive logging for easier debugging.
*   **UI/UX Enhancements:** The Streamlit interface has been updated for a more intuitive user experience.
*   **Code Refactoring:** The codebase has been modularized for better readability and maintainability.

## Features

*   **Trending Topic Integration:** Fetches trending topics to inspire blog content.
*   **AI-Powered Content Generation:** Utilizes OpenAI's GPT-3.5 Turbo to generate engaging, SEO-friendly blog posts in HTML format.
*   **Attractive Title Generation:** Generates clickbait-style and SEO-friendly titles for blog posts.
*   **Duplicate Content Prevention:** Checks for existing blog posts (by normalized title) in a local SQLite database to avoid re-posting similar content.
*   **Smart Topic Selection:** Prioritizes trending topics that are not similar to recently posted blogs, ensuring diverse content.
*   **Image Generation:** Generates relevant images for blog posts using DALL-E 3.
*   **Robust Error Handling & Retries:** Implements `tenacity` for retrying failed API calls and comprehensive logging for better debugging.
*   **Streamlit User Interface:** Provides a simple web interface to trigger the auto-blogging process.

## Project Structure

The project is organized into the following directories:

*   `app/`: Contains the main Streamlit application file (`streamlit_app.py`).
*   `src/`: Houses the core Python logic and modules.
    *   `blog_writer.py`: Handles AI-powered blog and title generation.
    *   `blogger_api.py`: Manages interactions with the Google Blogger API.
    *   `trend_scraper.py`: Fetches trending topics.
    *   `blog_db.py`: Manages the local SQLite database for tracking blog posts.
    *   `config.py`: Stores application-wide configuration variables.
*   `images/`: Stores generated images for blog posts.
*   `requirements.txt`: Lists all Python dependencies.
*   `.gitignore`: Specifies files and directories to be ignored by Git.
*   `README.md`: This file.

## Local Setup Guide

This guide will walk you through setting up and running the Auto-Blogger application locally.

### Prerequisites

*   **Python 3.8+**: Download and install from [python.org](https://www.python.org/downloads/).
*   **Git**: Download and install from [git-scm.com](https://git-scm.com/downloads).

### Step 1: Clone the Repository

First, clone the project repository to your local machine:

```bash
git clone <your-repository-url>
cd auto_blogger
```

### Step 2: Set Up Python Virtual Environment

It's highly recommended to use a virtual environment to manage project dependencies.

```bash
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate
```

### Step 3: Install Dependencies

Install all required Python packages using `pip`:

```bash
pip install -r requirements.txt
```

### Step 4: Configure Google Blogger API Credentials

This application interacts with the Google Blogger API. You need to set up OAuth 2.0 credentials.

1.  **Create a Google Cloud Project:**
    *   Go to the [Google Cloud Console](https://console.cloud.google.com/).
    *   Create a new project.
2.  **Enable Blogger API:**
    *   In the Google Cloud Console, navigate to "APIs & Services" > "Enabled APIs & Services".
    *   Search for "Blogger API" and enable it.
3.  **Configure OAuth Consent Screen:**
    *   Go to "APIs & Services" > "OAuth consent screen".
    *   Configure it as "External" (unless you're part of a Google Workspace organization).
    *   Fill in the required fields (App name, User support email, Developer contact information).
    *   Add the scope: `https://www.googleapis.com/auth/blogger`
    *   Add test users if your app is not yet verified.
4.  **Create OAuth 2.0 Client ID:**
    *   Go to "APIs & Services" > "Credentials".
    *   Click "CREATE CREDENTIALS" > "OAuth client ID".
    *   Select "Desktop app" as the application type.
    *   Give it a name (e.g., `AutoBlogger Desktop`).
    *   Click "CREATE".
    *   **Download the `client_secret.json` file.** Save this file in the root directory of your project (e.g., `auto_blogger/client_secret.json`).
5.  **Generate `token.json`:**
    *   The project includes a utility script `auth_setup.py` (located in the root directory before project restructuring) to generate the `token.json` file, which stores your authentication tokens.
    *   Run this script from your project's root directory:
        ```bash
        python auth_setup.py
        ```
    *   This will open a browser window asking you to log in with your Google account and grant permissions. After successful authentication, `token.json` will be created in your project's root directory.

### Step 5: Set Up Environment Variables

The application uses environment variables for sensitive information and configuration. Create a file named `.env` in the root directory of your project and add the following:

```
OPENAI_API_KEY="your_openai_api_key_here"
BLOGGER_BLOG_ID="your_blogger_blog_id_here"
```

*   **`OPENAI_API_KEY`**: Obtain this from your [OpenAI API dashboard](https://platform.openai.com/account/api-keys).
*   **`BLOGGER_BLOG_ID`**: You can find your Blogger Blog ID in the URL when you are viewing your blog's dashboard. It's the long string of numbers after `/blogID/`.

### Step 6: Run the Streamlit Application

Once all the above steps are completed, you can run the Streamlit application:

```bash
streamlit run app/streamlit_app.py
```

This command will open the application in your default web browser. You can then click the "Run Auto-Blogger" button to start the blog generation process.

## Deployment to Streamlit Cloud

To deploy your Auto-Blogger application to Streamlit Cloud, follow these steps:

1.  **Git Repository:**
    *   Ensure your project is hosted on a public Git repository (e.g., GitHub).
    *   **Crucially, do NOT commit `token.json`, `client_secret.json`, or `.env` files to your Git repository.** These contain sensitive information and are already listed in `.gitignore`.

2.  **Streamlit Secrets:**
    *   Streamlit Cloud provides a secure way to manage sensitive information. You will need to add the following as secrets in your Streamlit Cloud app settings:
        *   `OPENAI_API_KEY`: Your OpenAI API key.
        *   `BLOGGER_BLOG_ID`: The ID of your Blogger blog.
        *   `GCP_TOKEN_JSON`: The *entire JSON content* of your `token.json` file. Copy the content of the file and paste it as a single string value for this secret.
        *   `GCP_CLIENT_SECRET_JSON`: The *entire JSON content* of your `client_secret.json` file. Copy the content of the file and paste it as a single string value for this secret.

    *   **How to add secrets in Streamlit Cloud:**
        1.  Go to your app's settings in Streamlit Cloud.
        2.  Navigate to "Secrets".
        3.  Add each of the above as a new secret, with the exact key names and their corresponding values.

3.  **Deploy on Streamlit Cloud:**
    *   Go to [Streamlit Cloud](https://share.streamlit.io/).
    *   Click "New app" and connect your Git repository.
    *   Select the branch and set the main file path to `app/streamlit_app.py`.
    *   Ensure you have configured the secrets as described above.
    *   Click "Deploy!".

Your Streamlit application should then deploy successfully, reading the necessary credentials and configurations from the environment variables you set as secrets.