#curl -X 'DELETE' 'http://bareos.svc.ot.ru:8000/control/volumes/Wal-31420' -H 'accept: application/json' -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTY4MzIxMjk2Mn0.fXIM-gHmyDIA_-vDEl8fP0iCdyLHf49ldAE9g979ZPw" 
curl -X 'DELETE' 'http://bareos.svc.ot.ru:8000/control/volumes/Wal-31420' -H 'accept: application/json' -H "Authorization: Bearer $1" 
