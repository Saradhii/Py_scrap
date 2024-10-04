import os
from PyPDF2 import PdfReader
from collections import Counter

keyword_sets = {
    "BOOKING_CONFIRMATION_ORIGINAL_FROM_CMA_CGM": [
        "CMA CGM Agencies (India) Pvt Ltd", "Merchant Haulage",
        "Booking Confirmation", "VGM Cut-Off Date/Time", "Ramp Cut-Off Date/Time"
    ],
    "BOOKING_CONFIRMATION_ORIGINAL_FROM_HAPAG": [
        "HAPAG-LLOYD INDIA PVT. LTD.", "Booking Confirmation", "Customs Details",
        "Container Type", "Estimated time of arrival", "- original"
    ],
    "BOOKING_CONFIRMATION_UPDATE_FROM_HAPAG": [
        "HAPAG-LLOYD INDIA PVT. LTD.", "Booking Confirmation", "Customs Details",
        "Container Type", "Estimated time of arrival", "update"
    ],
    "BOOKING_CONFIRMATION_ORIGINAL_FROM_MAERSK": [
        "MAERSK", "BOOKING CONFIRMATION",
        "Thank you for placing your booking with Maersk A/S, as Carrier",
        "Intended Transport Plan", "Load Itinerary"
    ],
    "BOOKING_CONFIRMATION_ORIGINAL_FROM_MSC": [
        "MSC AGENCY (INDIA) PVT. LTD", "BOOKING RELEASE ORDER",
        "Booking Release No",
        "Empty Container Pickup Location:",
        "Cargo Details furnished by the shipper"
    ],
    "BOOKING_CONFIRMATION_ORIGINAL_FROM_COSCO": [
        "COSCO SHIPPING LINES (INDIA) PRIVATE LIMITED", "Booking Confirmation",
        "CARGO INFORMATION", "REQUIRED DOCUMENT INFORMATION", "ROUTE INFORMATION"
    ],
    "BOOKING_CONFIRMATION_ORIGINAL_FROM_OOCL": [
        "OOCL (India) Private Limited", "BOOKING NUMBER", "ROUTE INFORMATION",
        "INTENDED VGM CUT-OFF", "CARGO INFORMATION"
    ],
    "BOOKING_CONFIRMATION_ORIGINAL_FROM_ONE": [
        "OCEAN NETWORK EXPRESS","VGM Cut-off","Booking Receipt Notice","Booking Ref. No",
        "Booking Date"
    ]
}

url = """https://maps.googleapis.com/maps/api/place/autocomplete/json?input=${search}&components=country%3A${country.toLowerCase()}&key=${process.env.GOOGLE_PLACES_API_KEY}&types=${isCity ? 'locality' : 'postal_code'}""";

def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    return text

def check_keywords(text, keywords):
    text = text.lower()
    found_keywords = [keyword for keyword in keywords if keyword.lower() in text]
    missing_keywords = [keyword for keyword in keywords if keyword.lower() not in text]
    return found_keywords, missing_keywords

def main():
    dump_folder = "BOOKING_CONFIRMATION_ORIGINAL"  
    match_counts = Counter()
    total_files = 0
    unmatched_files = 0

    for filename in os.listdir(dump_folder):
        if filename.endswith(".pdf"):
            total_files += 1
            file_path = os.path.join(dump_folder, filename)
            text = extract_text_from_pdf(file_path)

            matches = []
            # print(f"\nChecking {filename}:")

            for shipper, keywords in keyword_sets.items():
                found, missing = check_keywords(text, keywords)
                if not missing:
                    matches.append(shipper)
                    match_counts[shipper] += 1
                    # print(f"  Matches {shipper}")
                # else:
                    # print(f"  Does not match {shipper}")
                    # print(f"    Missing keywords: {', '.join(missing)}")

            if matches:
                print(f"  Document matches: {', '.join(matches)}")
            else:
                print(filename)
                print("  Document does not match any shipping line")
                unmatched_files += 1

    print("\nSummary:")
    print(f"Total files processed: {total_files}")
    for shipper in keyword_sets.keys():
        match_percentage = (match_counts[shipper] / total_files) * 100
        print(f"{shipper}: {match_counts[shipper]} matches ({match_percentage:.2f}%)")

    unmatched_percentage = (unmatched_files / total_files) * 100
    print(f"\nUnmatched files: {unmatched_files} ({unmatched_percentage:.2f}%)")

if __name__ == "__main__":
    main()