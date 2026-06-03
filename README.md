# ujji-fastapi-inference

# Scalable FastAPI ML Inference Service

A simple Machine Learning Inference Service built using FastAPI that provides CRUD APIs to manage inference records and perform sentiment analysis. The service is containerized using Docker and deployed on a Kubernetes cluster with Horizontal Pod Autoscaler (HPA) to demonstrate scalable and self-adjusting backend infrastructure.

DockerHub Repo: https://hub.docker.com/r/ujji2006/ujji (Run via: `docker run -p 8000:8000 ujji2006/ujji:v1`)

Working and load test results :

1. FastAPI Interface :

<img width="1338" height="724" alt="image" src="https://github.com/user-attachments/assets/a75ca8e5-1abc-4d5d-8b46-c7cab595ac78" />


2. Libraries and Parameters Used :

```python
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from contextlib import asynccontextmanager
from typing import List, Dict
import asyncio
import aiohttp
```
3. This shows current cpu utilization during load , u see how percentage spiked first , then hpa did the math nd changed the no of replica :

<img width="1327" height="750" alt="image" src="https://github.com/user-attachments/assets/bb6391b9-63b2-4b10-a2cc-e465cebd36de" />


4. Pods status while load was increased and decreased , hpa autoscaled pods to 3 and then back to minimum 1 :
   
   NAME                                  READY   STATUS              RESTARTS   AGE
fastapi-deployment-66f5dcf57b-jmbwl   1/1     Running             0          4h9m
fastapi-deployment-66f5dcf57b-t6nvb   0/1     Pending             0          0s
fastapi-deployment-66f5dcf57b-t6nvb   0/1     ContainerCreating   0          0s
fastapi-deployment-66f5dcf57b-t6nvb   1/1     Running             0          2s
fastapi-deployment-66f5dcf57b-698tj   0/1     Pending             0          0s
fastapi-deployment-66f5dcf57b-698tj   0/1     ContainerCreating   0          0s
fastapi-deployment-66f5dcf57b-698tj   1/1     Running             0          2s

5. CRUD API

A resilient, containerized FastAPI-based CRUD application designed to manage machine learning inference records, simulate heavy production traffic using a custom Python asynchronous script, and dynamically scale using a Kubernetes Horizontal Pod Autoscaler (HPA) within a Kind cluster. Features
FastAPI Backend: Fully typed API endpoints for creating, reading, updating, deleting, and generating ML predictions.
Data Persistence: Local database simulation using an in-memory dictionary storage pattern.
Pydantic Validation: Strict metadata validations for schema compliance.
Performance Testing: Dedicated asynchronous script using aiohttp to simulate realistic multi-user patterns pushing concurrent endpoints.
Cloud-Native Autoscaling: Instrumented with a Kubernetes deployment configuration ready to scale infrastructure dynamically up and down based on resource spikes.

API Endpoints Summary:

| Method | Endpoint | Description |
| `POST` | `/predict` | Receives text, processes it through the ML model, and returns sentiment analysis. |
| `GET` | `/items` | Retrieves all historical inference records. |
| `GET` | `/items/{id}` | Retrieves a specific inference record by ID. |
| `PUT` | `/items/{id}` | Updates an existing inference record. |
| `DELETE` | `/items/{id}` | Deletes a specific inference record. |


Prerequisites
Ensure you have the following installed locally:

    Python 3.10+

    Docker

    Kind & kubectl

    Git

Installation & Local Setup

1. Clone the repository and navigate into the project directory:

git clone [https://github.com/YOUR_USERNAME/ujji-fastapi-inference.git](https://github.com/YOUR_USERNAME/ujji-fastapi-inference.git)
cd ujji-fastapi-inference

2. Set up a Python Virtual Environment:

python3 -m venv venv
source venv/bin/activate

(Windows users run: venv\Scripts\activate)

3. Install Dependencies:

pip install -r requirements.txt

4. Run the Server Manually (Optional Dev Check):

fastapi run main1.py

5. Run Production Build via Docker (Recommended):

docker run -p 8000:8000 ujji2006/ujji:v1
