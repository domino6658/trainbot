import requests
from utils.keyCalc import *


def search_api_request(search_term):
    
    # API endpoint URL
    url = getUrl(f"/v3/search/{search_term}")
    print(f"Search url: {url}")
    
    # Make the GET request
    response = requests.get(url,proxies={'https': '35.185.196.38:3128'})
    
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse and work with the response data (assuming it's JSON)
        data = response.json()
        formatted = format(data)
        print(formatted)
    else:
        # Print an error message if the request was not successful
        print(f"Error: {response.status_code} - {response.text}")

# Example usage
# search_term = 'Lilydale'
# search_api_request(search_term)

def route_api_request(route_id, route_type):
    route_type_dict = {
        "Tram":1,
        "Bus":2,
        "Night Bus":4,
        "0":0
    }
    route_type = route_type_dict[route_type]
    # API endpoint URL
    url = getUrl(f'/v3/routes/?route_name={route_id}&route_types={route_type}')
    print(f"Route search url: {url}")
    
    # Make the GET request
    response = requests.get(url,proxies={'https': '35.185.196.38:3128'})
    
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse and work with the response data (assuming it's JSON)
        data = response.json()
        formatted = format(data)
        print(formatted)
        return(formatted)
    else:
        # Print an error message if the request was not successful
        print(f"Error: {response.status_code} - {response.text}")
        
def routes_list(type):
    # API endpoint URL
    url = getUrl(f'/v3/routes/?route_types={type}')
    print(f"Route search url: {url}")
    
    # Make the GET request
    response = requests.get(url,proxies={'https': '35.185.196.38:3128'})
    
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse and work with the response data (assuming it's JSON)
        data = response.json()
        formatted = format(data)
        print(formatted)
        return(formatted)
    else:
        # Print an error message if the request was not successful
        print(f"Error: {response.status_code} - {response.text}")

def runs_api_request(route_id):
    # API endpoint URL
    url = getUrl(f'/v3/runs/route/{route_id}?expand=All')
    print(f"search url: {url}")
    
    response = requests.get(url,proxies={'https': '35.185.196.38:3128'})
    
    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        return(data)
    else:
        print(f"Error: {response.status_code} - {response.text}")
        
def departures_api_request(stop_id, route_type):
    # API endpoint URL
    url = getUrl(f'/v3/departures/route_type/{route_type}/stop/{stop_id}')
    print(f"search url: {url}")
    
    # Make the GET request
    response = requests.get(url,proxies={'https': '35.185.196.38:3128'})
    
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse and work with the response data (assuming it's JSON)
        data = response.json()
        return(data)
    else:
        # Print an error message if the request was not successful
        print(f"Error: {response.status_code} - {response.text}")
        
        
def route_type_api_request():
    # API endpoint URL
    url = getUrl(f'/v3/route_types')
    print(f"search url: {url}")
    
    # Make the GET request
    response = requests.get(url,proxies={'https': '35.185.196.38:3128'})
    
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse and work with the response data (assuming it's JSON)
        data = response.json()
        return(data)
    else:
        # Print an error message if the request was not successful
        print(f"Error: {response.status_code} - {response.text}")
        
def disruption_api_request(routeId):
    # API endpoint URL
    url = getUrl(f'/v3/disruptions/route/{routeId}')
    print(f"search url: {url}")
    
    # Make the GET request
    response = requests.get(url,proxies={'https': '35.185.196.38:3128'})
    
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse and work with the response data (assuming it's JSON)
        data = response.json()
        print(data)
        return(data)
    else:
        # Print an error message if the request was not successful
        print(f"Error: {response.status_code} - {response.text}")