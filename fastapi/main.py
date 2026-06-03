from fastapi import FastAPI, Path, HTTPException, Query
import json

app = FastAPI()

def loaddata():
    with open('patients.json', 'r') as f:
        data = json.load(f)
    
    return data

    

@app.get("/")
def hello():
    return  {'message' : 'hello world'}   #end point 1

@app.get("/about")
def about():
    return {'message' : 'ghar me jaake ke padh'}    #end point 2 


@app.get("/view")
def view():
    data = loaddata()

    return data

@app.get('/patient/{patient_id}')
def viewpatient(patient_id: str = Path(..., description='Id of the patient in db', example= 'P001')):
    data = loaddata()

    if patient_id in data :
        return data[patient_id]
    raise HTTPException(status_code=404, detail='Patient not found')


@app.get('/sort')
def sort_patients(sort_by: str = Query(..., description='sort on the basis of height, weight and bmi'), order: str = Query('asc', description='sort in asc and dec order')):

    valid_fields = ['height', 'weight', 'bmi']
    
    if sort_by not in valid_fields:
        raise HTTPException(status_code= 400, detail='invalid field selected from {valid_fields}')
    
    if order not in ['asc', 'dec']:
        raise HTTPException(status_code=400, detail='invalid order select bw asc or ded')
    
    data = loaddata()

    sort_order = True if order == 'dec' else False

    sorted_data = sorted(data.values(), key = lambda x: x.get(sort_by,0), reverse=sort_order)

    return sorted_data
    
