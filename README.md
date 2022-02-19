to run bot locally create local version ```.env``` file, example is in  ```.env.example```;

-----
Alternatively can pass Environment variable TOKEN. 
https://devcenter.heroku.com/articles/config-vars#managing-config-vars

-----
to run bot in Docker,  pass Environment variable TOKEN
i.e.
```$ docker build -t queuebot:0.0.1 ./
   $ docker run --env TOKEN=telegram_bot_token  queuebot:0.0.1
```
