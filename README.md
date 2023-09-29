# Image Hosting Service README

## Introduction

This project is an image hosting service developed with Django Rest Framework (DRF). 
It offers a flexible platform for users to upload, images and download their thumbnails. 
This README provides instructions on setting up and using the project. There are 3 tiers stored in the application 
(basic, premium, enterprise) which admin assigns to the user. Admin can add more tiers via admin-panel. 

## Setup

### Requirements

- Python 3.9
- Django 4.2.5
- djangorestframework 3.14.0
- pillow 10.0.1
- psycopg2-binary 2.9.7
- django-db-file-storage 0.5.5
- Docker and Docker Compose (optional)

All requirements are located in Pipfile. If you want to install manually all requirements, use:
`install pipenv`
### Installation

1. Clone the project repository:

   ```bash
   git clone https://github.com/acieply97/images-thumbnail-api.git
   ```
   
2. Navigate to the project directory and build the Docker image:
   ```bash
   docker-compose up
   ```

## Usage
# User authentication
User is created by admin in admin-panel. user must retrieve the token from the server, example:
```
curl -X POST -H "Content-Type: application/json" -d '{"username": "user1", "password": "userpassword"}' http://localhost:10565/api-token-auth/
```

# Uploading an image to server
```
curl -X POST -H "Authorization: Token <token>" -F "image=@<image_path>" -F "expire_link_value=<value>" http://localhost:10565/upload/
```
- <token> - User authentication token, only user and admin can retrieve their data
- <image> - image path from disc to upload
- <value> - value specifying when the link will not work, you can not specify the value, then the link will be permanent. value between 300 and 30000 measuring the time in seconds


# List images
user can see links to uploaded photos and their thumbnails
```
curl -H "Authorization: Token <token>" "http://localhost:10565/user-images/"
```

# Download image
User can download image or thumbnail using wget
```
wget --header="Authorization: Token <token>" -O output.jpg <url_image>
```

# Admin panel
Admin has the ability to:
1. new user
2. account tier
3. assign user to account tier
4. manage account tier, user profiles, thumbnails.
5. admin is authenticated in all users profiles. 

# Testing
The project includes test cases to ensure functionality and reliability. To run tests, use the following command in project directory:
`python manage.py test`

# Time taken
The time taken to complete this project was approximately 4-5 days

This README provides an overview of the Image Hosting Service project, its setup, usage, and important considerations. If you encounter any issues or have questions, please contact acieply97@gmail.com.
