# To run docker 
```
docker-compose up --build

```
# How to init db

```

docker ps

docker exec -it <container-name> psql -U postgres -d transport

INSERT INTO carriers (name, api_key) VALUES (<carrier>, <api_key>);

# To see it:

SELECT * FROM carriers;

```