from fastapi import FastAPI, Path, HTTPException, Query
import json
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Literal, Optional
from fastapi.responses import Response

app = FastAPI()


class Patient(BaseModel):

    id : Annotated[str, Field(..., description=' ID of the patient', examples=['P001'])]
    name: Annotated[str, Field(..., description=' Name of the Patient')]
    city: Annotated[str, Field(..., description='City name patient belong')]
    age: Annotated[int, Field(..., gt=0, lt = 120, description='Age of the patient')]
    gender : Annotated[Literal['male','Female','Other'], Field(..., description='Gender of the Patient')] 
    height: Annotated[float, Field(..., gt=0, description='Height of the patient in meters')] # gt = greater than 
    weight: Annotated[float, Field(...,gt= 0, description='Weight of the patient')] # gt = greater than 

    @computed_field
    @property
    def bmi(self) -> float :
        bmi = round(self.weight / (self.height**2),2)
        return bmi


    @computed_field
    @property
    def Verdict(self)-> str:
        if self.bmi < 18.5:
            return 'Underweight'
        elif self.bmi < 25:
            return 'Normal'
        elif self.bmi < 30:
            return 'Overweight'
        else:
            return 'Obese'


class PateintUpdate(BaseModel):
    name: Annotated[Optional[str], Field(default = None)]
    city: Annotated[Optional[str], Field(deafult = None)]
    age: Annotated[Optional[int], Field(deafult = None)]
    gender: Annotated[Optional[Literal['male','Female']], Field(deafult = None)]
    height: Annotated[Optional[float], Field(deafult = None,gt = 0)]
    weight: Annotated[Optional[float], Field(deafult = None, gt = 0)]



@app.put('/edit/{patient_id}')

def update_pateint(patient_id: str, pateint_update: PateintUpdate):

    data = load_data()
    if patient_id not in data:
        HTTPException(status_code=404, detail = 'Patient not exist')

    exsiting_patient_info = data[patient_id] #extracting info from json file 

    update_patient_info = pateint_update.model_dump(exclude_unset=True)
    
    for key, value in update_patient_info.items():
        exsiting_patient_info[key] = value

    existing_patient_info['id'] = patient_id
    patient_pydantic_obj = Patient(**existing_patient_info)
    existing_patient_info = patient_pydantic_obj.model_dump(exclude = 'id')
        
    data[patient_id] = exsiting_patient_info

    save_data(data)

    return JSONResponse(status_code= 200, content={'message':'patient updated'})



@app.delete('/delete/{pateint_id}')
def delete_pateint(patient_id: str):
    data = load_data()

    if patient_id not in data:
        raise HTTPException(status_code=404,detail = 'Patient not found')
    
    del data[patient_id]

    save_data(data)

    return JSONResponse(status_code= 200, content='Patient Deleted')




def load_data():
    with open('patients.json','r') as f:
        data = json.load(f)

    return data

def save_data(data):
    with open('patients.json','w') as f:
        json.dump(data,f)


@app.get("/")

def hello():
    return {'Hello'}

@app.get('/about')

def about():
    return {'message' : " This is a Patient management project"}

#using a dataset 
@app.get('/view')

def view():
    data = load_data()
    return data


#path parameters and PATH
@app.get('/patient/{patient_id}')   

def view_patient(patient_id : str = Path(..., description = "ID of the Patient in DB ", example='P001')):
    data = load_data()

    if patient_id in data:
        return data[patient_id]
    #return {'error' : 'Not found'}
    raise HTTPException(status_code= 404, detail='Not Found')
        

@app.get('/sort')

def sort_patient(sort_by : str = Query(..., description= ' Sort the data on user condition'), order: str = Query('asc', description= ' sort in asc or desc order')):
    valid_fields = ['height','weight', 'bmi']

    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail=f'Invalid field selected{valid_fields}')

    if order not in ['asc','desc']:
        raise HTTPException(status_code=400, detail='Invalid field selected')

    data = load_data()   

    sorted_order = True if order == 'desc' else False

    sorted_data = sorted(data.values(), key = lambda x:x.get(sort_by, 0), reverse= sorted_order)

    return sorted_data


@app.post('/create')

def create_patient(patient: Patient):

    #load existing data
    data = load_data()

    #checking if aptient is already exists in database 
    if patient.id in data:
        raise HTTPException(status_code= 400, detail=' Patient already exists')
        #return "patient already exist"

    #adding this new patient in the database
    data[patient.id] = patient.model_dump(exclude=['id'])


    #dict to json
    save_data(data)

    return JSONResponse(status_code= 201, content={'message':'Patient is created successfully'})
