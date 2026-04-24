# cis4930-sp26-django-project-group-21

<p>The Team: Aiden Duncan (AJD24C), Sofie Szlezak (SSS23J), Sam Miller(SSM23A), Sraddha Karthik (SK23BJ) <br>
<strong>The Project:</strong> We incorporated two datasets into a Django application, pulling from a weather API focusing on Florida locations and a 1000+ unit dataset of Pokemon characters and their subsequent statistics. Our application determines what Pokemon would thrive near major cities in the state of Florida, cross referencing weather data over time with Pokemon characteristics. <br>
<strong>Setup instructions:</strong> git clone, pip install -r requirements.txt, python manage.py, migrate, python manage.py seed_data, python manage.py runserver <br>
<strong>Original Pokemon Dataset:</strong> https://www.kaggle.com/datasets/mariotormo/complete-pokemon-dataset-updated-090420 <br>
<strong>Open-Meteo:</strong> https://open-meteo.com/ <br>
Open-Meteo requires no API key, as it is open source and public. However, it does rate limit requests to 10,000 calls per day limiting the amount of requests we can make for cities. Moreover, the data gathered is not real-time data but rather hourly data ranging from a time lag of 1-4 hours of most recent data. <br>
<strong>Application Features:</strong> There exists a home screen which gives the user a basic definition of what the project aims to accomplish and the button allows you to browse Pokemon if you so choose. A the top bar there is a track bar that contains all the sites of a website. Once navigated to the browse page then allows you to add, edit, and delete Pokemon. There also exists a weather boost page, and a fetch data page, both pertaining to weather data. Our last page is the analytics dashboard, which provides visual representations of various Pokemon statistics coupled with graphic containing weather information in current Florida cities. These datasets are connected to create the "boosted type" analytic, which displays which Pokemon type is boosted based on current weather in Florida.</p> <br>
<img width="756" height="779" alt="readme4" src="https://github.com/user-attachments/assets/3cde00b5-40b7-434a-bb25-1df9545aba0f" />
<img width="1240" height="704" alt="readme3" src="https://github.com/user-attachments/assets/23a1e8be-db32-458d-819b-d54b5cf0263a" />
<img width="448" height="779" alt="readme2" src="https://github.com/user-attachments/assets/60ec85de-01b6-485f-b512-a64f557c624b" />
<img width="1240" height="721" alt="readme6" src="https://github.com/user-attachments/assets/cb2d442f-3d2d-4d50-9ab0-b883854db1a2" />
<img width="1219" height="779" alt="readme5" src="https://github.com/user-attachments/assets/a03ed9a0-4a54-41e6-acae-92665af70e41" />

