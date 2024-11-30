# Aivello - Podcast Guest Research Tool

**Aivello** is a web-based tool designed to help podcasters research their guests effortlessly. It aggregates information from multiple sources such as Wikipedia, NewsAPI, and YouTube, providing insights into the guest's background, recent activities, and related videos. 

---

## Features

- **Wikipedia Integration**: Fetches summaries and URLs for the entered guest name.
- **NewsAPI Integration**: Retrieves recent news articles about the guest.
- **YouTube Integration**: Lists YouTube video links related to the guest in the context of podcasts.
- **Data Storage**: Saves aggregated information locally in a JSON file for reuse and offline processing.

---

## Technologies Used

- **Frontend**: HTML, CSS
- **Backend**: Flask (Python)
- **APIs**:
  - [Wikipedia API](https://pypi.org/project/wikipedia/)
  - [NewsAPI](https://newsapi.org/)
  - [YouTube Data API v3](https://developers.google.com/youtube/v3)
- **Storage**: JSON

---

## Setup Instructions

### Prerequisites

1. Python 3.9 or higher installed on your system.
2. API keys for:
   - [NewsAPI](https://newsapi.org/register)
   - [YouTube Data API](https://console.cloud.google.com/)

---

### Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/your-username/aivello.git
   cd aivello
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up API keys:
   - Rename the `.env.example` file to `.env`.
   - Add your API keys for NewsAPI and YouTube in the `.env` file:
     ```
     NEWS_API_KEY=your_news_api_key
     YOUTUBE_API_KEY=your_youtube_api_key
     ```

5. Initialize the `data.json` file:
   ```bash
   echo "{}" > data.json
   ```

---

### Running the Application

1. Start the Flask app:
   ```bash
   python app.py
   ```

2. Open your browser and navigate to:
   ```
   http://127.0.0.1:5000/
   ```

3. Enter a name in the input box to fetch information about the guest.

---

### Project Structure

```
aivello/
│
├── static/
│   └── style.css       # CSS for the application
│
├── templates/
│   └── index.html      # HTML structure for the app
│
├── app.py              # Flask app with API integrations
├── data.json           # Local storage for aggregated data
├── requirements.txt    # Python dependencies
├── .env                # Environment variables for API keys
└── README.md           # Project documentation
```

---

## Usage

1. **Enter a Guest Name**: Input the name of the guest you want to research.
2. **Fetch Information**: The app will query Wikipedia, NewsAPI, and YouTube to gather information.
3. **View Results**: See the guest's Wikipedia summary, recent news articles, and relevant YouTube videos.
4. **Data Storage**: All fetched data is saved locally for reuse.

---

## Known Issues

- Ensure the APIs are correctly configured and active. Errors like `JSONDecodeError` can occur if the API response is invalid.
- Free API limits may restrict the number of queries you can make per day.

---

## Future Enhancements

- Add integration with more data sources (e.g., LinkedIn, Twitter).
- Improve error handling and logging for API requests.
- Implement user authentication for personalized data storage.
- Create a more advanced UI with filtering and sorting capabilities.

---

## Contributing

Contributions are welcome! Feel free to:
1. Fork the repository.
2. Create a feature branch:
   ```bash
   git checkout -b feature-name
   ```
3. Commit your changes:
   ```bash
   git commit -m "Description of feature"
   ```
4. Push to your fork and submit a pull request.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Contact

For any questions or feedback, feel free to reach out:
- **Email**: [vaidiksulemusic@gmail.com](vaidiksulemusic@gmail.com)
- **GitHub**: [vaidiksule](https://github.com/vaidiksule)

--- 

Let me know if you'd like to customize it further!
