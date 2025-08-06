import time
import random

class CourtScraper:
    """
    A class dedicated to handling the logic of scraping court case data.
    """
    def __init__(self):
        """Initializes the scraper."""
        print("CourtScraper initialized.")

    def scrape_case(self, case_details: dict) -> dict:
        """
        Simulates the process of scraping a single case from a live source.

        Args:
            case_details: A dictionary with case type, number, and year.

        Returns:
            A dictionary with the result of the scrape.
        """
        print(f"SCRAPING LIVE: Simulating scrape for {case_details['type']} {case_details['number']}/{case_details['year']}")
        time.sleep(1.5) # Simulate the delay of a real network request

        # Randomly succeed or fail to simulate real-world conditions
        if random.random() > 0.2:  # 80% success rate
            # On success, return the found data
            return {
                "success": True,
                "data": {
                    "source": "Live Scrape",
                    "status": "Pending",
                    "parties": f"{case_details['type']} {case_details['number']}/{case_details['year']}: John Doe vs The State",
                    "nextHearingDate": "25-09-2025",
                    "filingDate": f"15-03-{case_details['year']}",
                    "history": [{"date": "20-08-2025", "business": 'Arguments heard. Adjourned.', "orderLink": '#'}]
                }
            }
        else:
            # On failure, return an error message
            return {"success": False, "message": "Live scrape failed: Case not found on the source website."}