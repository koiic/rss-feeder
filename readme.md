


#               Build Status
[![Build Status](https://travis-ci.com/koiic/Shopmate-Turing.svg?token=Q32jG2NqTmqEXpyGpEP1&branch=master)](https://travis-ci.com/koiic/Shopmate-Turing)

#                   RSSFEED
---
###### `An RSS scraper application which saves RSS feeds to a database and lets a user view and manage feeds they’ve added to the system`

 #                  Getting Started
 ***


##           To get started follow this simple step

##### N:B be sure you have docker installed, If not  follow this link to [Install DOCKER](https://www.docker.com/get-started)

1. ##### Clone or download project
2. ##### Change directory into the root project directory
3. ##### Create a .env file by copying the .env.sample
4. ##### configure your .env to your personal requirement
5. ##### Run `docker-compose up --build` on your bash/terminal to install build and run the container 
7. ##### Application start

##       Development

```
docker-compose up
```
##        Test
```
pytest
```

##        Production
```
docker-compose up
```
##         Route
>**base url** = `api/v1`


>**feed url** =`/feeds`

| Http-Method   | Url           |
| ------------- |:-----------------:|
| GET           |     /             |
| POST           |   **/**     |
| GET           | **/:id**  |
| POST           | **/:id/follow**|
| POST           | **/:id/unfollow**|
| GET           | **/:id/followers**|
| GET           | **/:id/items**|
| GET           | **/:items**|
| GET           | **/items/:item_id**|
| GET           | **/:id/ping**|
| GET           | **/me**|


>**auth url** =`/auth`

| Http-Method   | Url           |
| ------------- |:-----------------:|
| POST          | **/users**        |
| GET          |   **/users**      |
| PATCH         |   **/users/:id**    |
| GET         |   **/users/:id**    |
| POST         |   **/login**    |



##   API DOCUMENTATION

The Api endpoints are document using the OPEN API standards: [Swagger documentation](http://localhost:8000/api/v1/doc/)

## system design
![System flow](/RssFeeder.png)



##          Technology Used (Built With)
___
* ##### [Python](https://www.python.org/)  - Python is a programming language that lets you work quickly and integrate systems more effectively
* ##### [Django Rest Framework](https://www.django-rest-framework.org/) - Django REST framework is a powerful and flexible toolkit for building Web APIs.
* ##### [Django](https://www.djangoproject.com/) -  Django makes it easier to build better web apps more quickly and with less code.
* ##### [BeautifulSoup](https://beautiful-soup-4.readthedocs.io/en/latest/) -  Python library for pulling data out of HTML and XML files.
* ##### [Celery](https://docs.celeryproject.org/en/stable/getting-started/index.html) -  A task queue with focus on real-time processing, while also supporting task scheduling.
* ##### [Redis](https://redis.io/) -  Redis is an in-memory data structure store, used as a distributed, cache and message broker
* ##### [Pytest](https://docs.pytest.org/en/6.2.x/) -  pytest is a mature full-featured Python testing tool that helps you write better programs.



##              Style Guide
 ##### This is the link to the style guide use to build this API [PEP8](https://www.python.org/dev/peps/pep-0008/)


##  Author
##### `Ismail Ibrahim K`

##  License
##### This project is licensed under the MIT License

## Acknowledgement
* ##### [Django Rest](https://www.django-rest-framework.org/)
* ##### [github](https://guides.github.com/features/mastering-markdown/)
* ##### [stack-overflow](https://stackoverflow.com/)



