import urllib3
import json
import os

zip_dir_path = os.path.join(os.path.dirname(__file__), "zips/")

swagger_url = "https://generator.swagger.io/api/gen/servers"

body_json_path = "./swagger/swagger_active_asset.json"

def POST_SERVER(path, language_framework, url): 
    with open(path, "r") as in_file:
        data = json.load(in_file)

    req_headers = {
        'Content-Type': 'application/json'
    }

    body = {
            "options": {},
            "spec": data
            }

    encoded_data = json.dumps(body).encode('utf-8')

    http = urllib3.PoolManager()
    resp = http.request(
        method="POST",
        headers=req_headers,
        url=url+"/"+language_framework,
        body=encoded_data
    )

    # Parse the JSON response to get the actual download link
    response_data = json.loads(resp.data.decode('utf-8'))
    download_url = response_data.get('link')
    if not download_url:
        print("Error: No download link found in the response.")
        return

    #print(response_data)

    GET_CODE(download_url, zip_dir_path+"default.zip")


def GET_CODE(url, save_path):
    http = urllib3.PoolManager()
    # Set the headers as needed (including accept for octet-stream)
    headers = {
        'accept': 'application/octet-stream'
    }

    # Send a GET request to the URL with the required headers
    response = http.request('GET', url, headers=headers, preload_content=False)

    # Check if the request was successful
    if response.status != 200:
        print(f"Error: Unable to download file. Status code: {response.status}")
        return

    # Extract the filename from the Content-Disposition header, if available
    content_disposition = response.headers.get('Content-Disposition')
    if content_disposition and 'filename=' in content_disposition:
        filename = content_disposition.split('filename=')[1].strip('"')
        save_path = zip_dir_path+filename

    # Save the response data (ZIP file) to a file
    with open(save_path, 'wb') as f:
        while True:
            data = response.read(1024)  # Read 1KB at a time
            if not data:
                break
            f.write(data)

    # Close the response object
    response.release_conn()


if __name__ == "__main__":
    POST_SERVER(body_json_path, "python-flask", swagger_url)