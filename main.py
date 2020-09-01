from google_API import *

def main():
    exit_code = True

    while exit_code:
        location = input("Enter address or zip code: ")
        place_of_interest = input(f"What do you want to find at {location}? ")
        location_radius = input(f"How far around {location} do you want to search?(meters) ")

        client = GoogleMapsClient(api_key=GOOGLE_API_KEY, address=location)
        client.download_info(place_of_interest, location_radius)

        answer = input("Do you want to do another search? Y for yes, N for no ")
        if(answer == "y" or answer == "Y" or answer == "yes" or answer == "YES"):
            continue
        else:
            exit_code = False

main()