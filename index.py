import requests
import re

# URL to request
url = "https://blsspain-russia.com/moscow/english/appointment.php"

# Cookies
cookies = {
    "PHPSESSID": "pj9mjt8gvdm4cjpl71tmic5h64"
    # Add other PHPSESSID cookies if needed
}

# Send the GET request with cookies
response = requests.get(url, cookies=cookies)

# Check if the response contains the expected JavaScript content
expected_js_content = r'var blocked_dates = \[.*var available_dates = \[\];.*'
if re.search(expected_js_content, response.text, re.DOTALL):
    print("Expected JavaScript content found in response.")

    # Extract the PHPSESSID value from the response headers
    new_phpsessid = response.cookies.get("PHPSESSID")
    if new_phpsessid:
        print(f"New PHPSESSID value: {new_phpsessid}")

    # Check if available_dates is not empty
    if "var available_dates = [];" not in response.text:
        print("available_dates is not empty.")
    else:
        print("available_dates is empty.")
else:
    print("JavaScript content does not match expectations.")


# Extract blocked_dates, available_dates, fullCapicity_dates, and offDates_dates
js_content = response.text
blocked_dates = re.findall(r'var blocked_dates = (\[.*?\]);', js_content)[0]
available_dates = re.findall(
    r'var available_dates = (\[.*?\]);', js_content)[0]
fullCapicity_dates = re.findall(
    r'var fullCapicity_dates = (\[.*?\]);', js_content)[0]
offDates_dates = re.findall(r'var offDates_dates = (\[.*?\]);', js_content)[0]

# Convert the extracted strings to actual Python lists
blocked_dates = eval(blocked_dates)
available_dates = eval(available_dates)
fullCapicity_dates = eval(fullCapicity_dates)
offDates_dates = eval(offDates_dates)

# Print the extracted values
print("available_dates:", available_dates)
print("fullCapicity_dates:", fullCapicity_dates)
print("offDates_dates:", offDates_dates)
