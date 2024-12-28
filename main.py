from flask import Flask, request, jsonify
from flask_cors import CORS
from serpapi import GoogleSearch
from urllib.parse import parse_qsl, urlsplit
import json

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing

SERPAPI_API_KEY = "85c261d44fa7d3f382a97b305a953bb0f58b9ab395f57b396a887cdf415235e7"

def fetch_news_with_serpapi(keyword):
    """ 
    Fetch news articles using SerpAPI.
    """
    params = {
        "api_key": SERPAPI_API_KEY,
        "engine": "google",
        "q": keyword,
        "gl": "us",
        "hl": "en",
        "num": "100",
        "tbm": "nws"
    }

    search = GoogleSearch(params)
    page_num = 0
    all_results = {
        "name": f"News about {keyword}",
        "news_results": []
    }

    while True:
        results = search.get_dict()

        if "error" in results:
            print(results["error"])
            break

        page_num += 1
        print(f"Current page: {page_num}")

        # Iterate over organic results and extract the data
        for result in results.get("news_results", []):
            news_entry = {
                "position": result.get("position"),
                "link": result.get("link"),
                "title": result.get("title"),
                "source": result.get("source"),
                "date": result.get("date"),
                "thumbnail": result.get("thumbnail")
            }
            all_results["news_results"].append(news_entry)

        if "next" in results.get("serpapi_pagination", {}):
            search.params_dict.update(dict(parse_qsl(urlsplit(results.get("serpapi_pagination").get("next")).query)))
        else:
            break

    return all_results

@app.route('/api/news', methods=['POST'])
def get_news():
    """
    API endpoint to fetch news based on a keyword.
    """
    data = request.json
    keyword = data.get('keyword', '')

    if not keyword:
        return jsonify({"error": "Keyword is required."}), 400

    try:
        # Fetch news with SerpAPI
        news_data = fetch_news_with_serpapi(keyword)
        return jsonify(news_data)
    except Exception as e:
        print(f"Error in /api/news: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/')
def index():
    """
    Root endpoint to confirm the API is running.
    """
    return jsonify({
        "message": "Welcome to the Python Backend API!",
        "routes": [
            "/api/news (POST) - Fetch news by keyword using SerpAPI"
        ]
    })

if __name__ == '__main__':
    app.run(debug=True)
