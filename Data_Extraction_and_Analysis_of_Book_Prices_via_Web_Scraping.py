# Required libraries are imported for the script: time, pandas for data handling, Selenium for browser automation,
# and BeautifulSoup for HTML parsing.
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# Configure Firefox browser options and start the browser instance with specified settings
options = webdriver.FirefoxOptions()
options.add_argument("--start-maximized")  # Start browser in maximized mode
driver = webdriver.Firefox(executable_path='/home/train/web_scraping/Selenium/geckodriver', options=options)  # Specify geckodriver path
time.sleep(2)  # Wait for the browser to initialize

# Function to retrieve URLs of all books in a specific category
def get_category_detail_urls(driver, category_url):
    detail_urls = []  # List to store URLs of individual book details
    page_num = 1  # Page number for pagination handling

    # Loop through pages in the category until no products are found
    while True:
        # Load first page or subsequent pages based on page number
        if page_num == 1:
            driver.get(category_url)  # Load category URL for the first page
        else:
            # For subsequent pages, replace "index.html" with the specific page number
            driver.get(f"{category_url.replace('index.html', '')}page-{page_num}.html")

        # Wait for the page to load by checking for an element with the class "page_inner"
        try:
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "page_inner")))
        except Exception as e:
            # If an error occurs during loading, break the loop and print the error message
            print(f"Error occurred while loading the page, Page load complete: {e}")
            break

        # Find product elements on the page; if not found, exit the loop
        product_list = driver.find_elements(By.XPATH, "//h3/a")  # Locate book titles to get detail URLs
        if not product_list:
            break  # No products found, end pagination loop

        # For each product, extract the URL to its detail page and add it to the list
        for product in product_list:
            detail_url = product.get_attribute("href")  # Get href attribute for book detail link
            detail_urls.append(detail_url)  # Append to list of detail URLs

        page_num += 1  # Move to the next page

    return detail_urls  # Return the list of all collected detail URLs for the category

# Function to get detailed information about a single book
def get_book_details(driver):
    # Locate the main content div where book details are located
    content_div = driver.find_element(By.CLASS_NAME, "content")  # This div holds book information
    inner_html = content_div.get_attribute("innerHTML")  # Get inner HTML for parsing
    soup = BeautifulSoup(inner_html, "html.parser")  # Parse with BeautifulSoup

    # Extract book title, which is located within an <h1> tag
    book_title = soup.find("h1").text

    # Extract book price, located in a <p> tag with class "price_color"
    book_price = soup.find("p", class_="price_color").text

    # Extract star rating, stored as a CSS class in <p> tag with class "star-rating"
    book_rating = soup.find("p", class_="star-rating")['class'][1]

    # Return extracted details in a dictionary
    return {
        "Book Title": book_title,
        "Book Price": book_price,
        "Book Rating": book_rating
    }

# Function to scrape all books from specific categories and collect their details
def scrape_selected_categories(driver, categories):
    all_books_details = []  # List to store details of all books across categories

    # Iterate over each category URL
    for category_url in categories:
        # Extract category name from URL, format it, and print it
        category_name = category_url.split("/")[-2].split("_")[0].capitalize()  # Extract category name from URL
        print(f"\nCategory: {category_name}")

        # Get all detail URLs within the category by calling get_category_detail_urls
        detail_urls = get_category_detail_urls(driver, category_url)
        category_books = []  # Temporary list to store book titles within the category

        # Iterate through each book URL to get details
        for url in detail_urls:
            driver.get(url)  # Load book detail page
            time.sleep(2)  # Wait for page to fully load
            book_detail = get_book_details(driver)  # Extract book details with get_book_details
            book_detail['Category'] = category_name  # Add category information to book details
            all_books_details.append(book_detail)  # Append book details to main list
            category_books.append(book_detail["Book Title"])  # Add book title to category list for counting
            print(f"- {book_detail['Book Title']}")  # Print book title for tracking

        print(f"\nTotal {category_name} Books: {len(category_books)}")  # Print total books in the category

    return all_books_details  # Return all book details

# URLs of categories to scrape (limited to Travel and Nonfiction categories)
categories = [
    "https://books.toscrape.com/catalogue/category/books/travel_2/index.html",
    "https://books.toscrape.com/catalogue/category/books/nonfiction_13/index.html"
]

# Call scrape_selected_categories to collect all book details in specified categories
books_details = scrape_selected_categories(driver, categories)

# Close the browser after scraping
driver.quit()

# Create a pandas DataFrame to organize book details in tabular format
df = pd.DataFrame(books_details)

print(df.head(10))  # Display the first 10 rows of the DataFrame for inspection
print(df.shape)  # Print the shape of the DataFrame to show the number of rows and columns

# Define the file path to save the DataFrame as an Excel file
excel_file_path = "/home/train/Desktop/books_details.xlsx"
df.to_excel(excel_file_path, index=False)  # Save the DataFrame to an Excel file without row indices
print(f"\nBook details saved to '{excel_file_path}'.")  # Print confirmation message with file path
