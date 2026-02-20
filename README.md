# FDA_API_Exercise
# Diabetes Food Recall Tracking API

**Final Project – Combining Exercise 1 and Exercise 2**

---

## Overview

This project integrates:

* **Exercise 1** – Querying the openFDA Food Enforcement API
* **Exercise 2** – Building a REST API using FastAPI with user accounts and notes

The system allows a diabetic patient to search for FDA food recall information and automatically store the retrieved data as personal notes.

---

## User Story

As a patient living with diabetes,
I want to search for a specific food item and retrieve recent FDA food recall information related to that food,
so that I can avoid unsafe products and make safer dietary decisions.

Additionally, I want the recall information to be automatically saved in my personal account as a note,
so that I can review my food safety history later.

---

## Features

### User Management

* Create user with a unique username
* Retrieve user by ID
* Return `409 Conflict` if username already exists
* Return `404 Not Found` if user does not exist

### Notes Management

* Add manual text notes
* Retrieve all notes for a user

### FDA Integration

* Query openFDA Food Enforcement API
* Use query parameters (`search`, `limit`, `skip`)
* Extract relevant JSON fields:

  * product_description
  * recalling_firm
  * reason_for_recall
  * classification
  * recall_initiation_date
* Handle empty results
* Save retrieved FDA data as a structured note under the user

---

## API Endpoints

### Create User

`POST /users`

Request:

```json
{
  "username": "alice"
}
```

Responses:

* `201 Created`
* `409 Conflict`

---

### Get User

`GET /users/{user_id}`

Responses:

* `200 OK`
* `404 Not Found`

---

### Add Text Note

`POST /users/{user_id}/notes`

Request:

```json
{
  "text": "Check carbs before dinner."
}
```

Response:

* `201 Created`

---

### Get Notes

`GET /users/{user_id}/notes`

Response:

```json
{
  "user_id": "...",
  "notes": [...]
}
```

---

### Query FDA and Save as Note

`POST /users/{user_id}/fda-food-recalls`

Request:

```json
{
  "food_query": "yogurt",
  "limit": 5,
  "skip": 0
}
```

Behavior:

* Calls openFDA Food Enforcement API
* Extracts relevant recall fields
* Saves results as a structured note

Response:

```json
{
  "query": "yogurt",
  "results": [...],
  "saved_note_id": "..."
}
```

---

## Technologies Used

* Python
* FastAPI
* Uvicorn
* Requests
* openFDA Food Enforcement API

---

## How to Run

### Install dependencies

```
pip install fastapi uvicorn requests
```

### Start the server

```
uvicorn main:app --reload
```

### Open API documentation

```
http://127.0.0.1:8000/docs
```

---

