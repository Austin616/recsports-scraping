import requests

def run_scrape():
    try:
        response = requests.post("https://recsports-scraping.onrender.com/scrape")
        if response.status_code == 200:
            print("Scraping successful!")
        else:
            print(f"Scraping failed with status code: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"An error occurred while scraping: {e}")

if __name__ == "__main__":
    run_scrape()
