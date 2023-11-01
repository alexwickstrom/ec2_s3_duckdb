Directory Structure:

``` bash
.
├── Makefile  # contains commands for building/destroying containers & services
├── Pipfile
├── Pipfile.lock
├── README.md
├── app  # the main python app for creating data models on MySQL
│   ├── Dockerfile
│   ├── Pipfile
│   ├── Pipfile.lock
│   ├── __init__.py
│   ├── config.py  # stores ENVVARS and contains getters for DB connections etc.
│   ├── crud.py  # script. Calls the functions for creating & populating DB tables
│   ├── entrypoint.sh  # runs on launch
│   ├── factories.py
│   ├── models.py  # defines data models.
│   ├── olap.py  # Script used by DuckDB but maintained here for common dependencies
│   └── replicate_to_s3.py  # Script to replicate data from MySQL to "s3" bucket.
├── docker-compose.yml  # specifies all the Docker containers
├── duck  # for DuckDB
│   ├── Dockerfile
│   └── mv_example.sql
├── k8s  # for kubernetes stuff  
│   └── lightdash
│       └── values.yaml
│── terraform  # TODO
│   └── main.tf
│── .env  # envvars
```

```mermaid
erDiagram
    Doctor ||--o{ Office : ""
    Doctor ||--o{ CashPayment : ""
    Doctor ||--o{ LineItemTransaction : ""

    Office ||--o{ Appointment : ""
    
    Patient ||--o{ Appointment : ""
    Patient ||--o{ CashPayment : ""
    Patient ||--o{ LineItemTransaction : ""
    
    Appointment ||--o{ LineItem : ""
    
    LineItem ||--o{ CashPayment : ""
    LineItem ||--o{ LineItemTransaction : ""


```

