# Backend API Documentation

## Overview

This backend service is built using Flask and communicates with a MongoDB database. It provides various endpoints for managing events, users, and other related fields. The service also includes authentication functionality using Google OAuth.

## Prerequisites

- Python 3
- Flask
- MongoDB
- Google OAuth credentials

## Configuration

Before starting the service, configure the following environment variables in a `.env` file:

- `MONGODB_URI`: The URI connection string for your MongoDB database.
- `GOOGLE_CLIENT_ID`: Your Google client ID for OAuth authentication.

## Running the Service

To start the service, run:

```bash
python [your_script_name].py
