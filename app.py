from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from playsound import playsound
import schedule
import time
import random
from datetime import datetime, timedelta

# Configuration
URL = "https://in.bookmyshow.com/buytickets/the-greatest-of-all-time-bengaluru/movie-bang-ET00401439-MT/20240905"
# URL = "https://in.bookmyshow.com/buytickets/stree-2-sarkate-ka-aatank-bengaluru/movie-bang-ET00364249-MT/20240831"
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
RETRY_DELAY = 10  # Delay between retries in seconds
DRIVER_RETRY_ATTEMPTS = 5  # Number of retry attempts for the driver

def timestamp():
    """Return the current timestamp formatted as a string."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def log(level, message):
    """Log messages with a timestamp and severity level."""
    print(f"{timestamp()} - {level.upper()}: {message}")

def create_driver():
    attempts = 0
    while attempts < DRIVER_RETRY_ATTEMPTS:
        try:
            # log('info', 'Attempting to create a new ChromeDriver instance.')
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
            # log('info', 'Driver created successfully.')
            return driver
        
        except Exception as e:
            log('debug', f'Driver creation failed with error: {e}')
            attempts += 1
            if attempts < DRIVER_RETRY_ATTEMPTS:
                log('info', f'Retrying driver creation in {RETRY_DELAY} seconds...')
                time.sleep(RETRY_DELAY)  # Wait before retrying
            else:
                log('error', 'Max retry attempts reached for driver creation.')
                raise  # Re-raise the last exception if max attempts are reached

def check_theatre_availability():
    driver = None
    while True:
        try:
            # log('info', 'Checking theatre availability.')
            driver = create_driver()  # Create a new browser instance
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
                log('info', 'Target theatre found. Disabling scheduler and playing sound...')
                schedule.clear()  # Stop the scheduler
                while True:
                    playsound(SOUND_FILE)  # Play the sound in a loop
            else:
                log('info', 'No target theatres found.')

            break  # Exit the loop if no exception occurs

        except Exception as e:
            log('error', f'An error occurred: {e}')
            time.sleep(RETRY_DELAY)  # Wait before retrying

        finally:
            if driver:
                driver.quit()  # Close the browser if it was created
                # log('info', 'Driver closed.')

            # Randomize the next check time within 1-5 minutes (300 seconds)
            next_interval = random.randint(60, 300)
            next_check_time = datetime.now() + timedelta(seconds=next_interval)
            schedule.clear()  # Clear any existing schedule to avoid overlaps
            schedule.every(next_interval).seconds.do(check_theatre_availability)
            log('info', f'Next check scheduled in {next_interval} seconds at {next_check_time.strftime("%Y-%m-%d %H:%M:%S")}.')

if __name__ == "__main__":
    # Initial check
    # log('info', 'Starting initial check for theatre availability.')
    check_theatre_availability()

    # Run the scheduler
    while True:
        schedule.run_pending()
        time.sleep(1)
