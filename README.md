
# Intelligent Document Finder with Llama Index

The Intelligent Document Finder project aims to create a seamless, user-friendly platform 
that allows for the uploading and automatic indexing of various document formats, 
including PDFs, PPTs, Word documents, and other forms of unstructured data. By 
leveraging Llama Index for data indexing and retrieval, the system will enable precise query 
handling through a front-end application, enhancing the user's ability to find specific 
information efficiently.





## Documentation

For setup instruction and system overview look for Documentation file in Repository.

### Video demonstration: 
https://1drv.ms/v/s!Apnj3NYYFZr6gXrDvjSValSH0EiW?e=fd97wb


### Authentication working with the system:


Signup form takes two input username and password and in username user should provide his/her emailId and it do hashing on password and then username and hashed password will be stored in database. 

Login form takes two input same as signup and at backend provided username and password will be matched for authentication if it will successful then JWT encoded token will be generated.

When user will provide google drive folder ID at that time encoded JWT token and Folder ID both will be send to server then at the backend emaiID will be extracted from folderID and token will be decoded and from token username(which in our case is emailid) will be fetched and it will be compared with emailID fetched from google drive folder ID and if it matches successfully then data will be fetched from user provided folder and now user can query.


### Instruction To Run Updated App:


Once your done with above setup and installation process then run main.py file to start backend server so signup and login and other functionality work properly, and this file automatically start streamlit app with help of subprocess. now you can see interface and in that you can select option from selectbox for SignUp, login, and search and you can use the app. Signup first if you are new user and then login and then select search from selectbox and now you can connect your google drive or onedrive with the system by clicking on appropriate button. once it display success message then query whatever you want based on files you have provided.

