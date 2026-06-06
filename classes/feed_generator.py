import time
import os
import json
import requests
from flask import flash
from database.apis import Api, ApiField
from bs4 import BeautifulSoup
from rfeed import Feed, Item, Guid
from classes.chroma_database import ChromaDatabase
from classes.model_utils import ModelUtils
# from playwright.sync_api import sync_playwright

class FeedGenerator(ChromaDatabase):

  """ def scrape_x_feed(url):
    # X uses `article` elements to contain each post
    POST_SELECTOR = "article[data-testid='tweet']"

    with sync_playwright() as p:
      # Launch browser. You can use 'chromium', 'firefox', or 'webkit'
      # To use your actual logged-in account, pass your browser's user data directory
      browser = p.chromium.launch(headless=False)
      context = browser.new_context()
      page = context.new_page()

      page.goto(url)
      print("Waiting for feed to load...")
      page.wait_for_selector(POST_SELECTOR)

      # Scroll down a few times to force X to load more posts
      for _ in range(3):
          page.mouse.wheel(0, 5000)
          time.sleep(2) # Allow network request time

      # Extract the page HTML and parse with BeautifulSoup
      html = page.content()
      soup = BeautifulSoup(html, 'html.parser')

      # Find all post articles
      articles = soup.select(POST_SELECTOR)

      print(f"Successfully scraped {len(articles)} posts.")

      # Extract text from the posts
      for i, article in enumerate(articles, 1):
          text_element = article.find("div", {"data-testid": "tweetText"})
          if text_element:
              print(f"\nPost {i}: {text_element.get_text(strip=True)}")

      browser.close() """

  def get_posts(self, api, fields):

    try:
      # 1. Fetch the webpage
      response = requests.get(api.url)
      soup = BeautifulSoup(response.text, 'html.parser')

      # 2. Extract multiple items in different tags
      extracted_data = []

      # get parent classes
      parent_classes = []
      for field in fields:
        if field.type == 'parent':
          all_classes = field.value
          parent_classes = all_classes.split()

      # Assuming the page has multiple 'article' blocks containing the posts
      for post in soup.find_all(parent_classes):
        elements = {
          'title': "",
          'time': "",
        }
        for field in fields:
          if field.field == 'time':
            # Grab the time of the post (commonly found in <time> tags)
            time_tag = post.find('time')
            elements['time'] = time_tag.get('datetime') if time_tag else 'No Time'
          else:
            # If tag is a span
            all_classes = field.value
            classes = all_classes.split()
            element_span = post.find(field.field, class_=classes)
            elements['title'] = element_span.text.strip() if element_span else 'No Value'

        # Append to our list
        extracted_data.append(elements)

      # 3. Save raw parsed results to a JSON file
      filename = ModelUtils.machine_name(api.name)+".json"

      return filename, extracted_data
    except Exception as e:
      flash(f"Error fetching chain: {e}", "danger")
      return False

  def save_to_json(self, filename, extracted_data):
    file_path = ModelUtils.resource_path(os.path.join("uploads", "feeds", filename))
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(extracted_data, f, ensure_ascii=False, indent=4)

    return file_path

