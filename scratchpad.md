## user registration
''' bash
curl -X POST "http://localhost:8000/register" \
-H "Content-Type: application/json" \
-d '{
  "email": "user@example.com",
  "password": "password123"
}'
'''

## 