import urllib.parse

def extract_onedrive_folder_id(url):
    #parse the query string from the URL
    query_string = urllib.parse.urlparse(url).query
    #parse the query parameters into a dictionary
    query_params = urllib.parse.parse_qs(query_string)
    folder_id = None
    #iterate over the query parameters to find the "id" parameter
    for key, value in query_params.items():
        if key == 'id':
            #extract the folder ID
            folder_id = value[0]
            #encode the folder ID to handle special characters
            one_drive_folder_id=urllib.parse.quote_plus(folder_id)
            break
    if folder_id is None:
        return None
    return one_drive_folder_id