import requests

def fetch_data_from_my_api():
    url = "http://192.168.100.50:8000/products/"
    headers = {"Content-Type": "application/json"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    existing_data = {item['name']: item for item in response.json()}  # Creating a dictionary of existing items by name
    return existing_data



def fetch_data_from_external_api():
    url = "https://mysupplier.mozzn.com/products/?page_size=999"
    headers = {"Authorization": "SUPP eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzM5MzA1MTYzLCJpYXQiOjE3MDc3NjkxNjMsImp0aSI6IjM5YzdmYzVlMmQ2YTQ1MGRiZTYwZjIxNmIwZTViMjljIiwidXNlcl9pZCI6MTJ9.-P2ZPwdyUkImvm34_RWi-fB3Pjk_rFGzKAc7Ywg8uSo",
               "Content-Type": "application/json"
               }
    # Send GET request to external API
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raises an exception for HTTP error responses
    return response.json()['results']

def prepare_data_for_post(my_data, external_data):
    new_data = []
    for item in external_data:
        if item['name'] not in my_data:  # Check if the product name from external data does not exist in our data
            new_data.append({
                'name': item['name'],
                'is_active': item['is_active'],
                'category': item['category']
            })
    return new_data

def post_data_to_my_api(prepared_data):
    url = "http://192.168.100.50:8000/products/"
    headers = {"Content-Type": "application/json"}
    for product in prepared_data:
        response = requests.post(url, json=product, headers=headers)
        response.raise_for_status()  # Raises an exception for HTTP error responses
        print("Product created:", response.json())


def main():
    # Step 1: Fetch data from your API
    my_data = fetch_data_from_my_api()
    
    # Step 2: Fetch data from an external API
    external_data = fetch_data_from_external_api()
    
    # Step 3: Prepare data that doesn't exist in your system
    new_data = prepare_data_for_post(my_data, external_data)
    
    # Step 4: Post new data to your API
    if new_data:
        post_data_to_my_api(new_data)
    else:
        print("No new data to post.")

if __name__ == "__main__":
    main()