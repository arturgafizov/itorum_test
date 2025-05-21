### How to use:

#### Clone the repo:

    git clone https://github.com/arturgafizov/itorum_test.git 
    

#### Before running create your superuser email/password and project name in docker/prod/env/.data.env file
    
    docker-compose exec itorum_test python manage.py makemigrations
    docker-compose exec itorum_test python manage.py migrate
    docker-compose exec itorum_test python manage.py createsuperuser

#### Run the local develop server:

    docker-compose up -d --build
    docker-compose logs -f
    
##### Server will bind 8000 port. You can get access to server by browser [http://localhost:8000](http://localhost:8000)
  
