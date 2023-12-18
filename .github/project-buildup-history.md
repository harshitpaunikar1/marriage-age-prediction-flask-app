# Project Buildup History: Marriage Age Prediction Flask App

- Repository: `marriage-age-prediction-flask-app`
- Category: `flask_ml_app`
- Subtype: `prediction`
- Source: `project_buildup_2021_2025_daily_plan_extra.csv`
## 2023-09-04 - Day 3: Flask route setup

- Task summary: Picked up the Marriage Age Prediction Flask app after the summer's model work. Today was about getting the Flask routing layer in a clean state. The original routing code had two endpoints doing similar work in slightly different ways — consolidated them into one with a query parameter to control the output format. Also fixed the error handling in the prediction route which was returning a 500 with a stack trace on invalid inputs instead of a proper 400 with a descriptive message.
- Deliverable: Routes consolidated. Error handling now returns 400 with message instead of 500 stack trace.
## 2023-09-04 - Day 3: Flask route setup

- Task summary: Fixed a potential path traversal issue in the model loading code — it was accepting the model filename from the request which was unnecessary and insecure. Hardcoded the model path.
- Deliverable: Path traversal vulnerability in model loading fixed.
## 2023-09-11 - Day 4: Input validation

- Task summary: Added comprehensive input validation to the prediction endpoint. The model expects seven numeric inputs and was previously silently coercing or failing on bad inputs. Now returns a clear error message listing which fields are missing or out of expected range, and the API documentation in the README was updated to show the valid input schema.
- Deliverable: Input validation added. Error messages describe which fields are invalid.
## 2023-11-13 - Day 6: Deployment prep

- Task summary: Prepared the Marriage Age Prediction Flask app for deployment. Added a Dockerfile, wrote a docker-compose for local testing, and verified that the app starts cleanly in a container. Also ran a quick load test locally with a simple script to make sure it didn't fall over under simultaneous requests. The threading model needed to be set explicitly to avoid gunicorn worker timeout issues.
- Deliverable: Docker setup complete. Load test passed. Gunicorn worker config corrected.
## 2023-12-18 - Day 7: Portfolio wrap

- Task summary: Final pass on the Marriage Age Prediction Flask App. Went through the README and made sure the setup instructions were accurate from scratch — had to update the environment setup steps which had drifted from what actually works. Also added screenshots of the app UI to the README so it reads better as a portfolio piece.
- Deliverable: README setup instructions verified and updated. UI screenshots added.
