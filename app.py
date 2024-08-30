from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from playsound import playsound
import schedule
import time

# Configuration
URL = "https://in.bookmyshow.com/buytickets/the-greatest-of-all-time-bengaluru/movie-bang-ET00401439-MT/20240905"
TARGET_THEATRES = [
    # BookMyShow
    "PVR: Nexus (Formerly Forum), Koramangala",
    "PVR: Vega City, Bannerghatta Road",
    "Gopalan Cinemas: Bannerghatta Road",
    "INOX: Garuda Swagath Mall, Jayanagar",
    "INOX: Mantri Square, Malleshwaram",
    "INOX: Central, JP Nagar, Mantri Junction",
    # TicketNew
    # "PVR Inox Nexus (Formerly Forum), Koramangala",
    # "PVR Inox Vega City, Bannerghatta Road",
    # "INOX Shree Garuda Swagath Mall, Jayanagar",
    # "INOX Mantri Square, Malleshwaram",
    # "INOX Central Mantri Junction, JP Nagar",
]
SOUND_FILE = "alert.wav"  # Path to your alert sound file


# Configure Selenium to use a visible Chrome browser
def create_driver():
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration
    chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
    chrome_options.add_argument(
        "--disable-dev-shm-usage"
    )  # Overcome limited resource problems
    chrome_options.add_argument("--window-size=1920,1080")  # Set window size
    chrome_options.add_argument(
        "--user-agent=Mozilla/5.0 (X11; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0"
    )  # User-Agent header

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=chrome_options
    )
    return driver


def check_theatre_availability():
    driver = create_driver()  # Create a new browser instance
    try:
        # Fetch the content from the URL
        driver.get(URL)
        time.sleep(2)  # Give some time for the page to load completely

        # Get the page source and parse it
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # Find all theatre names on the page
        theatres = soup.find_all("a", {"href": True})
        found = False

        # Check if any of the target theatres are in the list
        for theatre in theatres:
            for target_theatre in TARGET_THEATRES:
                if target_theatre in theatre.get_text():
                    found = True
                    break
            if found:
                break

        # Play sound if any target theatre is found and stop the scheduler
        if found:
            print(f"Target theatre found. Disabling scheduler and playing sound...")
            schedule.clear()  # Stop the scheduler
            while True:
                playsound(SOUND_FILE)  # Play the sound in a loop
        else:
            print("No target theatres found.")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        driver.quit()  # Close the browser


if __name__ == "__main__":
    # Initial check
    check_theatre_availability()

    # Schedule the function to run every 5 minutes
    schedule.every(2).minutes.do(check_theatre_availability)

    # Run the scheduler
    print("Scheduler started. Checking theatre availability every 2 minutes...")
    while True:
        schedule.run_pending()
        time.sleep(1)
