import os
import json
import wikipedia
import requests
from datetime import datetime
from flask import Flask, render_template, request, redirect, session,url_for , flash, redirect
from googleapiclient.discovery import build
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///users.db" 
app.config['SQLALCHAMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


DATA_FILE = "searchData.json"
CREDITS_FILE = "credits.json"
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")


########### DB MODEL ###########
class User(db.Model):
    # Primary key for the User model, auto-incremented
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True, autoincrement=True)
    # Username column, unique and cannot be null
    username = db.Column(db.String(25), unique=True, nullable=False)
    # Email column, unique and cannot be null
    email = db.Column(db.String(150), nullable=False, unique=True)
    # Password column, cannot be null
    password_hash = db.Column(db.String(150), nullable=False)
    # Date and time when the user is created, defaults to current time
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Method to set the password after hashing it
    def set_password(self, password):
        # Use the Werkzeug method to generate a secure hash of the password
        self.password_hash = generate_password_hash(password)
    
    # Method to check if the given password matches the stored password hash
    def check_password(self, password):
        # Use the Werkzeug method to check the password hash
        return check_password_hash(self.password_hash, password)

# Make sure the database is created when you run the app
with app.app_context():
    db.create_all()
    
########### FUNCTIONS ###########
# credits
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

# Fetch YouTube videos related to a person's name and podcasts
def fetch_youtube_videos(name):
    """
    Fetches YouTube videos related to the person's name and podcasts.
    
    Args:
        name (str): The person's name to search for.
    
    Returns:
        list: A list of dictionaries containing video titles and URLs, or None if an error occurs.
    """
    try:
        # Build the YouTube API client using the API key
        youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
        
        # Create a search request for YouTube videos related to the person's name and podcasts
        request = youtube.search().list(
            q=f"{name} podcast",  # Search query
            part="snippet",  # Specify the data to retrieve (e.g., title, description)
            type="video",  # Restrict results to videos
            maxResults=5  # Limit results to 5 videos
        )
        
        # Execute the API request and get the response
        response = request.execute()
        
        # Extract relevant information (title and URL) from the response
        videos = [
            {"title": item["snippet"]["title"], "url": f"https://www.youtube.com/watch?v={item['id']['videoId']}"}
            for item in response.get("items", [])  # Default to an empty list if no items
        ]
        return videos
    except Exception as e:
        # Handle any exceptions that occur and print the error message
        print(f"Error fetching YouTube videos: {e}")
        return None

# Fetch summary and URL of a Wikipedia page related to the person's name
def fetch_wikipedia(name):
    """
    Fetches a brief summary and URL from Wikipedia based on the person's name.
    
    Args:
        name (str): The person's name to search for.
    
    Returns:
        dict: A dictionary containing the summary and URL, or None if an error occurs.
    """
    try:
        # Get a brief summary of the Wikipedia page (2 sentences)
        info = wikipedia.summary(name, sentences=2)
        
        # Get the full URL of the Wikipedia page
        url = wikipedia.page(name).url
        return {"summary": info, "url": url}
    except Exception:
        # Handle cases where the page does not exist or another error occurs
        return None

# Fetch news articles using NewsAPI
def fetch_news(name):
    """
    Fetches news articles related to the person's name using NewsAPI.
    
    Args:
        name (str): The person's name to search for in the news.
    
    Returns:
        list: A list of dictionaries containing article titles and URLs, or None if an error occurs.
    """
    # Construct the API endpoint URL with the query and API key
    url = f"https://newsapi.org/v2/everything?q={name}&apiKey={NEWS_API_KEY}"
    try:
        # Send an HTTP GET request to the NewsAPI endpoint
        response = requests.get(url)
        
        # Debugging: Print the response status code and a portion of the response text
        print(f"Status Code: {response.status_code}")
        print(f"Response Text: {response.text[:500]}")
        
        # Raise an exception if an HTTP error occurs
        response.raise_for_status()
        
        # Parse the response JSON data
        data = response.json()
        
        # Extract relevant information (title and URL) from the articles
        articles = data.get("articles", [])  # Default to an empty list if no articles
        return [
            {"title": article["title"], "url": article["url"]}
            for article in articles[:5]  # Limit to the top 5 articles
        ]
    except requests.exceptions.HTTPError as http_err:
        # Handle HTTP-specific errors
        print(f"HTTP error occurred: {http_err}")
    except requests.exceptions.RequestException as req_err:
        # Handle general request errors
        print(f"Request error occurred: {req_err}")
    except json.JSONDecodeError:
        # Handle errors related to JSON decoding
        print("Failed to decode JSON response.")
    return None


########### ROUTES ###########
# Route for the homepage
@app.route("/")
def homepage():
    # Render the main page template (index.html)
    return render_template("index.html")

# Route for handling user login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':  # Check if the request is a POST method (form submission)
        # Collect the username and password from the submitted form
        username = request.form['username']
        password = request.form['password']
        
        # Query the database to find a user with the provided username
        user = User.query.filter_by(username=username).first()
        
        # Check if the user exists and if the provided password matches the stored password
        if user and user.check_password(password):  # Assumes `check_password` verifies the password
            # If authentication is successful, store the username in the session
            session['username'] = username
            
            # Redirect to the dashboard page after successful login
            return render_template('dashboard.html')
        
        else:
            # If the login fails (invalid username or password), flash an error message
            flash('Invalid email or password.', 'danger')
    
    # Render the login form for GET requests or after a failed login
    return render_template('login.html')

# Route for handling user registration
@app.route('/register', methods=['GET', 'POST'])
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':  # Check if the request method is POST (form submission)
        # Collect the username, email, and password from the form
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        # Query the database to check if the username or email already exists
        user = User.query.filter((User.username == username) | (User.email == email)).first()
        
        if user:  # If a user with the same username or email is found
            # Flash an error message to the user
            flash('Username or email already exists. Please choose a different one.', 'error')
            # Re-render the registration form so the user can try again
            return render_template('register.html')
        else:
            # Create a new user instance
            new_user = User(username=username, email=email)
            
            # Call the set_password method to hash the password
            new_user.set_password(password)
            
            # Add the new user to the database session
            db.session.add(new_user)
            
            # Commit the transaction to save the user to the database
            db.session.commit()
            
            # Store the username in the session for authentication purposes
            session['username'] = username
            
            # Flash a success message to the user
            flash('Registration successful! Please log in.', 'success')
            
            # Redirect the user to the login page
            return redirect(url_for('login'))

    # Render the registration form for GET requests
    return render_template('register.html')

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    # if "username" in session:
    #     return redirect(url_for('dashboard'))
    if 'user_id' not in session:
        flash('Please log in first.', 'danger')
        return redirect('/')
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

    return render_template("dashboard.html", name=name, person_data=person_data)

# Route for the invoice page
@app.route('/invoice')
def invoice():
    # Render the invoice page template (invoice.html)
    return render_template('invoice.html')

# Route for the wallet page
@app.route('/wallet')
def wallet():
    # Load the user's remaining credits (assumes load_credits() is a defined function)
    credits_left = load_credits()
    
    # Render the wallet page template (wallet.html) and pass the credits_left variable
    return render_template('wallet.html', credits_left=credits_left)  

# Route for adding credits to the user's wallet (POST method)
@app.route('/wallet/add_credit', methods=["POST"])
def add_credit_route():
    """
    Handles adding credits to the user's wallet from the wallet page.
    """
    # Retrieve the "amount" input from the submitted form
    amount = request.form.get("amount")
    
    # Check if an amount is provided
    if amount:
        try:
            # Try to convert the amount to an integer
            amount = int(amount)
            
            # Add the specified amount of credits (assumes add_credit() is a defined function)
            add_credit(amount)
            
            # Success message if the amount is valid
            message = f"{amount} credits added successfully."
        except ValueError:
            # Error message if the input is not a valid number
            message = "Invalid amount. Please enter a valid number."
    else:
        # Error message if no amount is provided
        message = "No amount provided."
    
    # Reload the user's credits after the addition
    credits_left = load_credits()
    
    # Render the wallet page with updated credits and a feedback message
    return render_template('wallet.html', credits_left=credits_left, message=message)

# Route for the profile page
@app.route('/profile')
def profile():
    # Render the profile page template (profile.html)
    return render_template('profile.html')

# Ensures this block only runs when the script is executed directly
if __name__ == "__main__":
    # Starts the Flask development server with debugging enabled
    # Debug mode provides detailed error messages and reloads the server on code changes
    app.run(debug=True)
