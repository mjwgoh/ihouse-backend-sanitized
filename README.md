# Backend API Documentation

## Overview
This backend service, built using Flask, interacts with a MongoDB database and provides endpoints for managing events, users, and other fields. It also includes Google OAuth authentication.

## Prerequisites
- Python 3
- Flask
- MongoDB
- Google OAuth credentials

## Configuration
Set up the following environment variables in a `.env` file:
- `MONGODB_URI`: URI connection string for MongoDB.
- `GOOGLE_CLIENT_ID`: Google client ID for OAuth.

# Endpoints

## General
GET /: Confirms that the API server is running.
Users
POST /users/login: Validates user login using a JWT token.
Events
GET /events: Retrieves events based on query parameters.
POST /events: Adds a new event.
GET /events/<event_id>: Retrieves a specific event.
POST /events/<event_id>: Updates a specific event.
PUT /events/<event_id>: Modifies an existing event.
DELETE /events/<event_id>: Deletes an event.
Fields
GET /fields: Retrieves fields based on query parameters.
POST /fields: Adds a new field.
PUT /fields/<field>/<id>: Updates a specific field.
DELETE /fields/<field>/<id>: Deactivates a field.
Utility Functions
