import os
import json
import wikipedia
import requests
from flask import Flask, render_template, request
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
DATA_FILE = "searchData.json"
CREDITS_FILE = "credits.json"
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
YOUTUBE_API_KEY = os.getenv("your_youtube_api_key")


def load_credits():
    try:
        with open(CREDITS_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {"user": {"credit": 0}}  # Default value if file is missing
    except json.JSONDecodeError:
        return {"user": {"credit": 0}}  # Default value if JSON is corrupte

def save_credits(data):
    try:
        with open(CREDITS_FILE, "w") as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        print(f"Error saving credits: {e}")

def reduce_credit():
    data = load_credits()
    if data["user"]["credit"] > 0:
        data["user"]["credit"] -= 1
        save_credits(data)
        
def add_credit(amount):
    """
    Adds the specified amount of credits to the user's account.

    Args:
        amount (int): The number of credits to add.
    """
    if amount <= 0:
        print("Invalid amount. Please provide a positive number.")
        return
    
    data = load_credits()
    data["user"]["credit"] += amount
    save_credits(data)
    print(f"{amount} credits successfully added.")



# loading already saved data
def load_data():
    """Load data from the local JSON file."""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as file:
                return json.load(file)
        except json.JSONDecodeError:
            print("Warning: JSON file is empty or invalid. Resetting data.")
            return {}  # Return an empty dictionary
    return {}

def save_data(data):
    try:
        with open(DATA_FILE, "w") as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        print(f"Error saving data: {e}")


# fetching data from different sources
def fetch_youtube_videos(name):
    """Fetch YouTube videos related to the person's name and podcasts."""
    try:
        youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
        request = youtube.search().list(
            q=f"{name} podcast",
            part="snippet",
            type="video",
            maxResults=5  # Limit results to 5
        )
        response = request.execute()
        
        videos = [
            {"title": item["snippet"]["title"], "url": f"https://www.youtube.com/watch?v={item['id']['videoId']}"}
            for item in response.get("items", [])
        ]
        return videos
    except Exception as e:
        print(f"Error fetching YouTube videos: {e}")
        return None

def fetch_wikipedia(name):
    """Fetch Wikipedia data."""
    try:
        info = wikipedia.summary(name, sentences=2)
        url = wikipedia.page(name).url
        return {"summary": info, "url": url}
    except Exception:
        return None

def fetch_news(name):
    """Fetch news data using NewsAPI."""
    url = f"https://newsapi.org/v2/everything?q={name}&apiKey={NEWS_API_KEY}"
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")  # Debugging
        print(f"Response Text: {response.text[:500]}")  # Print a portion of the response
        response.raise_for_status()  # Raise exception for HTTP errors
        data = response.json()
        articles = data.get("articles", [])
        return [
            {"title": article["title"], "url": article["url"]}
            for article in articles[:5]  # Limit to 5 articles
        ]
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"Request error occurred: {req_err}")
    except json.JSONDecodeError:
        print("Failed to decode JSON response.")
    return None


# routing
@app.route("/", methods=["GET", "POST"])
def index():
    name = ""
    person_data = {}
    local_data = load_data()
    credits_left = load_credits()["user"]["credit"]

    if request.method == "POST":
        name = request.form.get("name")
        if name:
            if name in local_data:
                person_data = local_data[name]
            else:
                if credits_left > 0:
                    reduce_credit()
                    # Fetch data from multiple sources
                    person_data = {
                        "wikipedia": fetch_wikipedia(name),
                        "news": fetch_news(name),
                        "youtube": fetch_youtube_videos(name),
                    }
                    # Save only if data is valid
                    if any(person_data.values()):
                        local_data[name] = person_data
                        save_data(local_data)
                else:
                    person_data = {"error": "Insufficient credits"}

    return render_template("index.html", name=name, person_data=person_data)

@app.route('/invoice')
def invoice():
    return render_template('invoice.html')   

@app.route('/wallet')
def wallet():
    credits_left = load_credits()
    return render_template('wallet.html', credits_left=credits_left)   

@app.route('/wallet/add_credit', methods=["POST"])
def add_credit_route():
    """
    Adds credits to the user's wallet from the wallet page.
    """
    amount = request.form.get("amount")
    if amount:
        try:
            amount = int(amount)
            add_credit(amount)
            message = f"{amount} credits added successfully."
        except ValueError:
            message = "Invalid amount. Please enter a valid number."
    else:
        message = "No amount provided."

    credits_left = load_credits()
    return render_template('wallet.html', credits_left=credits_left, message=message)

@app.route('/profile')
def profile():
    return render_template('profile.html') 
if __name__ == "__main__":
    app.run(debug=True)  
