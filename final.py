# Web Scraping Amazon Reviews
# In this notebook, we'll scrape Amazon product reviews with various filters using Python.
# The purpose is to collect reviews for analysis or research.

# Importing Libraries
# We start by importing the necessary libraries for our web scraping task.

import requests
import pandas as pd
import time
import re
import emoji
from bs4 import BeautifulSoup

# Header for request
HEADER = ( {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'})

# Setting up the URL
# We define the URL for the Amazon product reviews we want to scrape. The URL may include filters based on star ratings or other criteria.

#url = "https://www.amazon.co.uk/product-reviews/B00YT1IZTO/"
url ="https://www.amazon.co.uk/product-reviews/B00M3IFUMK"

# Filter Definitions
# We define a list of filters that we'll apply to the reviews. These filters allow us to collect reviews based on different criteria.

filters = [
    "sortBy=recent",
    "filterByStar=critical",
    "filterByStar=critical&sortBy=recent",
    "filterByStar=positive",
    "filterByStar=positive&sortBy=recent",
    "filterByStar=one_star",  # 1-star filter
    "filterByStar=one_star&sortBy=recent",  # 1-star and "Most Recent" filter
    "filterByStar=two_star",  # 2-star filter
    "filterByStar=two_star&sortBy=recent",  # 2-star and "Most Recent" filter
    "filterByStar=three_star",  # 3-star filter
    "filterByStar=three_star&sortBy=recent",  # 3-star and "Most Recent" filter
    "filterByStar=four_star",  # 4-star filter
    "filterByStar=four_star&sortBy=recent",  # 4-star and "Most Recent" filter
    "filterByStar=five_star",  # 5-star filter
    "filterByStar=five_star&sortBy=recent",  # 5-star and "Most Recent" filter
]

# Data Collection
# We initialize an empty list called reviewlist to store the collected reviews.

reviewlist = []

# Function to Retrieve and Parse the HTML Content
# We define a function called get_soup to retrieve the HTML content of a URL and parse it using BeautifulSoup.

def get_soup(url):
    response = requests.get(url, headers=HEADER)
    if response.status_code == 200:
        return BeautifulSoup(response.text, "html.parser")
    else:
        raise Exception(f"Failed to retrieve the page. Status code: {response.status_code}")

# Function to Check for Duplicate Reviews
# We define a function called review_with_id_exists to check if a review with a specific ID already exists in our list of reviews.

def review_with_id_exists(review_list, review_id):

    if len(review_list) == 0: return False

    df = pd.DataFrame(review_list)

    if review_id in df['id'].tolist():
        return True
    return False



def clean_text(text):

    # Remove emojis
    cleaned_text = emoji.demojize(text)

    # Remove special characters and replace with a space
    cleaned_text = re.sub(r'[^\w\s]', ' ', cleaned_text)
    
    # Remove extra spaces
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
    

    return cleaned_text

# Function to Retrieve Reviews
# We define a function called get_reviews to extract and process reviews from the HTML content.

def get_reviews(soup):
    # Find all review elements on the page
    reviews = soup.find_all('div', {'data-hook': 'review'})
    
    new_reviews = []  # Initialize a list to store new reviews

    for item in reviews:
        # Check for foreign reviews (cmps-review-star-rating indicates non-English reviews)
        try:
            print("*********************************************************")
            # Check for foreign reviews (cmps-review-star-rating indicates non-English reviews)
            none_en_review = item.find('i', {'data-hook': 'cmps-review-star-rating'})
            review_id = item.get('id')
             # Clean the review text
            cleaned_text = clean_text(item.find('span', {'data-hook': 'review-body'}).text.strip())

            
            # Skip foreign reviews
            if none_en_review is not None:
                print("Skipping foreign review:")
                print(item.find('span', {'data-hook': 'review-body'}).text.strip())
                continue
            
            if review_with_id_exists(reviewlist, review_id): # Skip reviews with the same ID to avoid duplicates
                print(f"*** Review with Id {review_id} exists, skipping...")
                continue
            else:
                # Extract review details and add to the list
                review = {
                    'id': review_id,
                    'rating': float(item.find('i', {'data-hook': 'review-star-rating'}).text.replace('out of 5 stars', '').strip()),
                    'text': cleaned_text,
                }
            
                new_reviews.append(review)
                reviewlist.append(review)

        except KeyError:
            print("Error: 'id' attribute not found for a review. Skipping...")
            continue
        except Exception as e:
            print(e)
            continue

    return new_reviews

# Main Loop
# We iterate through the filters to collect reviews based on each filter.

for filter in filters:
    page_number = 1
    reviews_count = 0

    # Limit to 100 reviews per filter
    while reviews_count < 100:
        page_url = f"{url}/ref=cm_cr_getr_d_paging_btm_next_{page_number}?ie=UTF8&reviewerType=all_reviews&pageNumber={page_number}&{filter}"
        print(f"URL: {page_url}")
        soup = get_soup(page_url)

        # Retrieve and Add Reviews
        reviews_on_page = get_reviews(soup)
        reviews_count += len(reviews_on_page)

        print(f"new reviews: {len(reviews_on_page)}, current filter total: {reviews_count}")

        next_button = soup.find('li', {'class': 'a-disabled a-last'})
        button = soup.find('li', {'class': 'a-last'})

        if next_button or button is None:
            break
        page_number += 1

    # If there are more filters, switch to the next one
    if filter != filters[-1]:
        page_number = 1
        reviews_count = 0
        continue

# Creating the DataFrame
# We create a Pandas DataFrame from the collected reviews.

df = pd.DataFrame(reviewlist)

# Saving to Excel
# We generate a dynamic file name based on the current Linux timestamp and save the DataFrame to an Excel file.

timestamp = int(time.time())
file_name = f'Amazon-Reviews-{timestamp}.xlsx'
df.to_excel(file_name, index=False)




