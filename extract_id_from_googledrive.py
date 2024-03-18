import re

def extract_googledrive_folder_id(url):
    #used regular expression to extract the folder ID from the URL
    google_drive_folder_id = re.search(r"/folders/([^\s/]+)", url).group(1)
    return google_drive_folder_id