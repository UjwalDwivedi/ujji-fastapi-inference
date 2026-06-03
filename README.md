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
