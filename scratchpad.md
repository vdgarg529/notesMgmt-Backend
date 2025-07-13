## user registration
```bash
curl -X POST "http://localhost:8000/register" \
-H "Content-Type: application/json" \
-d '{
  "email": "user@example.com",
  "password": "password123"
}'
```

<<<<<<< HEAD
## 


## 

```bash
uvicorn main:app --reload
```
=======
## login
``` bash
curl -X POST "http://localhost:8000/login" \
-H "Content-Type: application/json" \
-d '{
  "email": "user@example.com",
  "password": "password123"
}'
```

## Create note
``` bash
curl -X POST "http://localhost:8000/notes" \
-H "Authorization: Bearer <token>" \
-H "Content-Type: application/json" \
-d '{
  "title": "My First Note",
  "content": "Artificial intelligence is changing the world rapidly."
}'
>>>>>>> 878df8cfa4ff65391d21dba202aa605303275d1f
