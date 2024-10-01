from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json
from dotenv import load_dotenv
import os

load_dotenv()

email_password = os.getenv("other_password")

def fetch_sale_items():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        page = browser.new_page()
        page.goto('https://www.uniqlo.com/us/en/feature/sale/men')
        page.wait_for_selector('.fr-ec-product-tile-resize-wrapper')

        html = page.content()
        browser.close()

    soup = BeautifulSoup(html, 'html.parser')
    product_containers = soup.find_all('div', class_='fr-ec-product-tile-resize-wrapper')

    sale_items = []
    seen_names = set()

    for product in product_containers:
        link_tag = product.find('a', class_='fr-ec-tile')
        name_tag = product.find('h3', class_='fr-ec-title')
        price_tag = product.find('div', class_='fr-ec-price')
        image_div = product.find('div', class_='fr-ec-image')

        name = name_tag.get_text(strip=True) if name_tag else "No name"
        if name not in seen_names:
            link = f"https://www.uniqlo.com{link_tag['href']}" if link_tag else None
            price = price_tag.find('p').get_text(strip=True) if price_tag else "No price"
            image_url = None
            if image_div and 'style' in image_div.attrs:
                style = image_div['style']
                start = style.find("url(")
                end = style.find(")", start)
                image_url = style[start+4:end].strip('\"')  

            sale_items.append({
                'name': name,
                'price': price,
                'link': link,
                'image': image_url
            })
            seen_names.add(name)

    return sale_items

# Function to save cookies to a file
def save_cookies(page):
    cookies = page.context.cookies()  # Get the cookies from the page context
    with open('cookies.json', 'w') as f:
        json.dump(cookies, f)  # Save cookies to a file

# Function to load cookies from a file
def load_cookies(page):
    try:
        with open('cookies.json', 'r') as f:
            cookies = json.load(f)  # Load cookies from the file
        page.context.add_cookies(cookies)  # Add cookies to the current page context
    except FileNotFoundError:
        print("No cookies file found. Proceeding without cookies.")

# Main function to fetch wishlist items
def fetch_wishlist_items():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # Headless browser
        page = browser.new_page()

        try:
            load_cookies(page)

            page.goto('https://www.uniqlo.com/us/en/wishlist')
            page.wait_for_timeout(3000)

            # Check if login is required by checking if a login form exists
            if page.locator('#email-input').is_visible():
                print("Login required. Logging in...")

                # Login process
                page.fill('#email-input', 'thamim.hus@gmail.com')  # Replace with your email
                page.fill('#password-input', email_password)  # Replace with your password
                page.click('button[type="submit"]')

                # Wait for login to complete
                page.wait_for_timeout(5000)

                # Save cookies after login
                save_cookies(page)

                print("Login successful, cookies saved.")

            # Navigate to the wishlist page if not already there
            page.goto('https://www.uniqlo.com/us/en/wishlist')
            page.wait_for_selector('li.fr-ec-collection-list__item', timeout=5000)  # Wait for items to load

            # Get the wishlist HTML content
            html = page.content()

            browser.close()

        except Exception as e:
            print(f"An error occurred: {e}")
            browser.close()
            return []

    # Parse the wishlist HTML with BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')

    # Extract wishlist items
    wishlist_items = []
    wishlist_containers = soup.find_all('li', class_='fr-ec-collection-list__item')

    if not wishlist_containers:
        print("No wishlist items found")
    else:
        print(f"Found {len(wishlist_containers)} wishlist items")

    for product in wishlist_containers:
        name_tag = product.find('h3', class_='fr-ec-title')
        name = name_tag.get_text(strip=True) if name_tag else "No name"

        link_tag = product.find('a', class_='fr-ec-tile')
        link = f"https://www.uniqlo.com{link_tag['href']}" if link_tag else None

        image_div = product.find('div', class_='fr-ec-image')
        image_url = None
        if image_div and 'style' in image_div.attrs:
            style = image_div['style']
            start = style.find("url(")
            end = style.find(")", start)
            image_url = style[start+4:end].strip('\"')

        wishlist_items.append({
            'name': name,
            'link': link,
            'image': image_url
        })

    return wishlist_items

