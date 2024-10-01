import requests
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from io import BytesIO
import json
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from scraper import fetch_sale_items, fetch_wishlist_items
import schedule
import time
import threading
from dotenv import load_dotenv

app = Flask(__name__)
CORS(app)

load_dotenv()
email_password = os.getenv("email_password")

MATCH_COUNT_FILE = 'previous_matches.json'

def read_previous_match_count():
    if os.path.exists(MATCH_COUNT_FILE):
        with open(MATCH_COUNT_FILE, 'r') as file:
            data = json.load(file)
            return data.get('match_count', 0)
    return 0

def save_new_match_count(new_count):
    with open(MATCH_COUNT_FILE, 'w') as file:
        json.dump({'match_count': new_count}, file)

def send_email_notification(new_items, recipient_email):
    sender_email = "thamim.hus@gmail.com"
    sender_password = email_password
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    subject = "New Uniqlo Wishlist Items on Sale!"
    
    body = "Sale: "

    # Iterate through new items, limit name to 15 characters and include price
    for item in new_items:
        item_name = item['name']  # Truncate the name to 15 characters
        item_price = item.get('price', 'N/A')  # Get the price or default to 'N/A'
        body += f"{item_name} ${item_price}, "  # Add name and price to the body

    # Remove the trailing comma and space
    body = body.rstrip(", ")

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)  
        text = msg.as_string()

        server.sendmail(sender_email, recipient_email, text)
        print(f"Email sent successfully to {recipient_email}")

        server.quit()

    except Exception as e:
        print(f"Failed to send email: {e}")

def check_sales():
    try:
        sale_items = fetch_sale_items()
        wishlist_items = fetch_wishlist_items()

        matching_items = []
        for sale_item in sale_items:
            for wishlist_item in wishlist_items:
                if sale_item['name'] == wishlist_item['name']:
                    matching_items.append(sale_item)

        previous_match_count = read_previous_match_count()

        current_match_count = len(matching_items)

        if current_match_count > previous_match_count:
            new_items = matching_items[previous_match_count:]  
            recipient_email = "2487593124@vtext.com"  
            send_email_notification(new_items, recipient_email)

        save_new_match_count(current_match_count)

    except Exception as e:
        print(f"Error checking sales: {e}")

# Schedule the job to run every hour
schedule.every(1).hours.do(check_sales)

def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)

@app.route('/api/sales', methods=['GET'])
def get_sales():
    try:
        sale_items = fetch_sale_items()
        wishlist_items = fetch_wishlist_items()

        matching_items = []
        for sale_item in sale_items:
            for wishlist_item in wishlist_items:
                if sale_item['name'] == wishlist_item['name']:
                    matching_items.append(sale_item)

        previous_match_count = read_previous_match_count()

        current_match_count = len(matching_items)

        save_new_match_count(current_match_count)

        return jsonify({
            'sale_items': sale_items,
            'wishlist_items': wishlist_items,
            'matches': matching_items,  
            'previous_match_count': previous_match_count,
            'current_match_count': current_match_count
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/proxy-image', methods=['GET'])
def proxy_image():
    image_url = request.args.get('url')
    
    if not image_url:
        return jsonify({'error': 'No image URL provided'}), 400
    
    try:
        response = requests.get(image_url)
        image = BytesIO(response.content)
        return send_file(image, mimetype='image/jpeg')
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    # Start the Flask app in one thread
    threading.Thread(target=run_schedule).start()
    app.run(debug=True)
