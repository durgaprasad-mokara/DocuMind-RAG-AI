# API Authentication Guide

To authenticate with our API, you must include a Bearer token in the Authorization header. `Authorization: Bearer <YOUR_API_KEY>`. If you receive a 401 Unauthorized error, it means your token is missing, expired, or invalid. You can regenerate tokens in the developer dashboard under API Settings.