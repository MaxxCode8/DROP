import requests
import time
import os
import logging
import argparse
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Set up 

load_dotenv()

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('audio_api.log')
    ]
)
logger = logging.getLogger(__name__)

# API configuration
BASE_URL = "https://apibox.erweima.ai/api/v1"
API_KEY = os.getenv("SUNO_API_KEY")
HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

# --- (generate_audio, check_status, download_audio functions remain the same) ---
def generate_audio(payload):
    """
    Generate audio by sending request to the API
    """
    logger.info("Sending request to generate audio")
    logger.debug(f"Request URL: {BASE_URL}/generate")
    logger.debug(f"Request headers: {HEADERS}")
    logger.debug(f"Request payload: {payload}")

    try:
        response = requests.post(
            f"{BASE_URL}/generate",
            headers=HEADERS,
            json=payload
        )

        logger.debug(f"Response status code: {response.status_code}")
        logger.debug(f"Response headers: {response.headers}")
        logger.debug(f"Response content: {response.text}")

        if response.status_code == 200:
            result = response.json()
            task_id = result.get('data', {}).get('taskId')
            logger.info(f"Generation request successful. Task ID: {task_id}")
            return task_id
        else:
            logger.error(f"Error generating audio: {response.status_code}")
            logger.error(f"Error response: {response.text}")
            return None
    except Exception as e:
        logger.exception(f"Exception occurred during generate_audio: {str(e)}")
        return None

def check_status(task_id):
    """
    Check the status of the audio generation task
    """
    logger.info(f"Checking status for task ID: {task_id}")
    logger.debug(f"Request URL: {BASE_URL}/generate/record-info?taskId={task_id}")
    logger.debug(f"Request headers: {HEADERS}")

    try:
        response = requests.get(
            f"{BASE_URL}/generate/record-info?taskId={task_id}",
            headers=HEADERS
        )

        logger.debug(f"Response status code: {response.status_code}")
        logger.debug(f"Response headers: {response.headers}")
        logger.debug(f"Response content: {response.text}")

        if response.status_code == 200:
            result = response.json()
            status_data = result.get('data', {})
            status = status_data.get('status')
            logger.info(f"Status check successful: {status}")
            return status_data
        else:
            logger.error(f"Error checking status: {response.status_code}")
            logger.error(f"Error response: {response.text}")
            return None
    except Exception as e:
        logger.exception(f"Exception occurred during check_status: {str(e)}")
        return None

def download_audio(url, filename="output.mp3"):
    """
    Download the audio file from the given URL
    """
    logger.info(f"Downloading audio from: {url}")

    try:
        response = requests.get(url)

        logger.debug(f"Download response status code: {response.status_code}")
        logger.debug(f"Download response headers: {response.headers}")

        if response.status_code == 200:
            with open(filename, 'wb') as f:
                f.write(response.content)
            logger.info(f"Audio downloaded successfully to {filename}")
            return True
        else:
            logger.error(f"Error downloading audio: {response.status_code}")
            logger.error(f"Error download response: {response.text[:200]}...")  # Truncate large responses
            return False
    except Exception as e:
        logger.exception(f"Exception occurred during download_audio: {str(e)}")
        return False

# --- process_audio function remains the same ---
def process_audio(fullpayload, task_id=None, wait_time=30, max_attempts=20, check_interval=15, pending_timeout=60):
    """
    Process audio generation and download
    """
    logger.info("Inside Process Audio")
    if task_id is None:
        # Step 1: Generate audio
        task_id = generate_audio(fullpayload)

        if not task_id:
            logger.error("Failed to get task ID. Exiting.")
            return

        # Step 2: Initial wait
        logger.info(f"Waiting for {wait_time} seconds...")
        time.sleep(wait_time)
    else:
        logger.info(f"Using provided task ID: {task_id}")

    # Step 3: Check status and download when ready
    attempt = 0
    pending_start_time = None

    while attempt < max_attempts:
        logger.info(f"Checking status attempt {attempt+1}/{max_attempts}")
        status_info = check_status(task_id)

        if not status_info:
            logger.error("Failed to get status info. Exiting.")
            return

        status = status_info.get('status')
        logger.info(f"Current status: {status}")

        if status == "SUCCESS":
            # Fix: Properly navigate the nested structure to get audio URLs
            response_data = status_info.get('response', {})
            suno_data = response_data.get('sunoData', [])

            if suno_data:
                logger.info(f"Found {len(suno_data)} audio generation results")

                # Download all generated audio files
                for i, data in enumerate(suno_data):
                    audio_url = data.get('audioUrl')
                    duration = data.get('duration', 0)

                    if audio_url:
                        # Use the duration to distinguish between versions
                        filename = f"output_{i+1}_{duration:.2f}s.mp3"
                        logger.info(f"Downloading audio {i+1} (duration: {duration}s)")
                        download_audio(audio_url, filename)
                return
            else:
                logger.error("No audio data found in response.")
                logger.debug(f"Full response: {status_info}")
                return
        elif status == "FAILED":
            logger.error("Audio generation failed.")
            logger.debug(f"Full status info: {status_info}")
            return
        elif status == "PENDING":
            # Track how long we've been in pending status
            if pending_start_time is None:
                pending_start_time = datetime.now()
                logger.info(f"Started tracking PENDING status at {pending_start_time}")

            # Check if we've exceeded the pending timeout
            pending_duration = (datetime.now() - pending_start_time).total_seconds()
            logger.info(f"Task has been PENDING for {pending_duration:.1f} seconds")

            if pending_duration >= pending_timeout:
                logger.warning(f"Task remained in PENDING status for over {pending_timeout} seconds. Stopping.")
                return

            logger.info(f"Audio still pending. Waiting {check_interval} seconds...")
            time.sleep(check_interval)
            attempt += 1
        else:
            # Reset pending timer if status changed from PENDING
            pending_start_time = None
            logger.info(f"Audio processing. Status: {status}. Waiting {check_interval} seconds...")
            time.sleep(check_interval)
            attempt += 1

    logger.warning("Maximum attempts reached. Audio may still be processing.")

def parse_arguments():
    """Parses command-line arguments for standalone execution."""
    logger.info("Parsing arguments for standalone execution")

    parser = argparse.ArgumentParser(description='Suno API Audio Generation (Standalone)')
    # Add arguments needed if run directly
    parser.add_argument('--lyrics', type=str, required=True, help='Lyrics text for audio generation') # Example: Need lyrics if run standalone
    parser.add_argument('--task-id', type=str, help='Task ID to check status (skips generation step)')
    parser.add_argument('--wait-time', type=int, default=30, help='Initial wait time in seconds')
    parser.add_argument('--max-attempts', type=int, default=20, help='Maximum number of status checks')
    parser.add_argument('--check-interval', type=int, default=15, help='Time between status checks in seconds')
    parser.add_argument('--pending-timeout', type=int, default=60, help='Maximum time to wait in PENDING status (seconds)')

    args = parser.parse_args() # Parse the arguments
    logger.debug(f"Parsed arguments: {args}") # Log *after* parsing
    logger.info("Argument parsing complete")
    return args # Return the parsed arguments

def InitiateBattleSimulator(lyricstohere):
    """
    Entry point when called programmatically from battle.py.
    Does NOT parse command-line arguments. Uses default timings.
    """
    try:
        logger.info("Battle Simulator execution started (programmatic call)")

        # DO NOT parse arguments here. Use defaults or pass them in if needed.
        # args = parse_arguments() # <--- REMOVE THIS LINE

        payload={
            "prompt": lyricstohere,
            "style": "Rap battle, pop, funk",
            "title": "Rap battle between software projects",
            "customMode": True,
            "instrumental": False,
            "model": "V4",
            "negativeTags": "Relaxing Piano",
            "callBackUrl": "https://webhook-test.com/67ccc2284f5edc4616d7094c21d6366e" # Consider making this configurable if needed
        }

        # Call process_audio directly, using default values for timing/retries
        # If you needed to override defaults, you'd pass them here, e.g., wait_time=45
        process_audio(
            fullpayload=payload
            # task_id=None, # Default is None
            # wait_time=30, # Default is 30
            # max_attempts=20, # Default is 20
            # check_interval=15, # Default is 15
            # pending_timeout=60 # Default is 60
        )
        logger.info("Battle Simulator execution completed (programmatic call)")
    except KeyboardInterrupt:
        logger.info("Script interrupted by user")
    except Exception as e:
        logger.exception(f"Unhandled exception in InitiateBattleSimulator: {str(e)}")

# --- Add main execution block for standalone use ---
if __name__ == "__main__":
    """
    This block executes only when battle_simulator.py is run DIRECTLY
    from the command line (e.g., python battle_simulator.py --lyrics "some lyrics")
    """
    try:
        logger.info("Battle Simulator script started directly")
        args = parse_arguments() # Parse arguments specifically for standalone run

        # Construct payload using arguments provided for standalone run
        payload={
            "prompt": args.lyrics, # Get lyrics from command line arg
            "style": "Rap battle, pop, funk",
            "title": "Rap battle between software projects",
            "customMode": True,
            "instrumental": False,
            "model": "V4",
            "negativeTags": "Relaxing Piano",
            "callBackUrl": "https://webhook-test.com/67ccc2284f5edc4616d7094c21d6366e"
        }

        # Call process_audio using arguments parsed from command line
        process_audio(
            fullpayload=payload,
            task_id=args.task_id,
            wait_time=args.wait_time,
            max_attempts=args.max_attempts,
            check_interval=args.check_interval,
            pending_timeout=args.pending_timeout
        )
        logger.info("Battle Simulator script execution completed (standalone)")
    except KeyboardInterrupt:
        logger.info("Script interrupted by user (standalone)")
    except Exception as e:
        # Catch argparse errors specifically if needed
        if "the following arguments are required" in str(e):
             logger.error(f"Argument error: {e}")
             # parser.print_help() # Optionally print help on error
        else:
            logger.exception(f"Unhandled exception in main (standalone): {str(e)}")
