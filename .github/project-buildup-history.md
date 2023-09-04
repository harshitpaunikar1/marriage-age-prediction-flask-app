# Project Buildup History: Marriage Age Prediction Flask App

- Repository: `marriage-age-prediction-flask-app`
- Category: `flask_ml_app`
- Subtype: `prediction`
- Source: `project_buildup_2021_2025_daily_plan_extra.csv`
## 2023-09-04 - Day 3: Flask route setup

- Task summary: Picked up the Marriage Age Prediction Flask app after the summer's model work. Today was about getting the Flask routing layer in a clean state. The original routing code had two endpoints doing similar work in slightly different ways — consolidated them into one with a query parameter to control the output format. Also fixed the error handling in the prediction route which was returning a 500 with a stack trace on invalid inputs instead of a proper 400 with a descriptive message.
- Deliverable: Routes consolidated. Error handling now returns 400 with message instead of 500 stack trace.
