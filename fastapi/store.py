from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def hello():
    return  {'message' : 'hello world'}   #end point 1

@app.get("/about")
def about():
    return {'message' : 'ghar me jaake ke padh'}    #end point 2