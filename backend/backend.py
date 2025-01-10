from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import JSONResponse
import requests
from bs4 import BeautifulSoup
import os
import json
import pandas as pd
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

CSV_FOLDER = "./data_test"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def getRMP(professorName):
    return;


async def getProfRating(prof_name:str):
    URL = "https://www.ratemyprofessors.com/search/professors/1111?q="
    
    r = requests.get(f"{URL}{prof_name}")
    if r.status_code != 200: 
        return JSONResponse(status_code=400, content={"message": "Error fetching professor search results"})
    
    page = BeautifulSoup(r.content, 'html.parser')

    # Get the link to the professor info
    div = page.find('div', class_='SearchResultsPage__StyledResultsWrapper-vhbycj-3 bdmepv')   
    if not div or not div.find('a'): 
        return JSONResponse(status_code=404, content={"message": "Professor not found"})
    
    a_value = div.find('a')['href']

    # Get the info from the professor page
    professor_page = requests.get(f"https://www.ratemyprofessors.com{a_value}")
    if professor_page.status_code != 200: 
        return JSONResponse(status_code=400, content={"message": "Error fetching professor details"})
    
    professor_page_parsed = BeautifulSoup(professor_page.content, 'html.parser')

    # Extract data from the professor's page
    name = professor_page_parsed.find('h1', class_='NameTitle__NameWrapper-dowf0z-2 erLzyk')
    avg_rating = professor_page_parsed.find('div', class_='RatingValue__Numerator-qw8sqy-2 liyUjw')
    prof_dept = professor_page_parsed.find('div', class_="NameTitle__Title-dowf0z-1 iLYGwn")
    would_take_again = professor_page_parsed.find('div', class_="FeedbackItem__FeedbackNumber-uof32n-1 kkESWs")
    # rating_image = professor_page_parsed.find('img', class_="RatingDistribution__ChartImage-p5irx9-3 eolSHJ")

    # Prepare the response
    response = {
        "name": name.text.strip().replace("\n", "") if name else "Not Available",
        "avg_rating": avg_rating.text.strip().replace("\n", "") if avg_rating else "Not available",
        "prof_dept": prof_dept.text.strip().replace("\n", "") if prof_dept else "Not available",
        "would_take_again": would_take_again.text.strip().replace("\n", "") if would_take_again else "Not available",
        # "rating_image": rating_image['src'] if rating_image else "Not available",
    }
    return response


async def getMultipleProfRating(prof_names):
    response = []

    for name in prof_names:
        response.append(await getProfRating(name))
    
    return response

# The actual server functions. Everything above gets called by these:

@app.get('/')
async def root():
    files = [f for f in os.listdir(CSV_FOLDER) if f.endswith('.csv')]
    return {f"csv_files: {files}"}


@app.get('/find_class/{CRS_SUBJ_CD}/{CRS_NBR}')
@app.get('/find_class/{CRS_SUBJ_CD}/')
async def getClass(CRS_SUBJ_CD:str,CRS_NBR:str = None):
    classes = []
    professors = []

    for file in os.listdir(CSV_FOLDER):
        if file.endswith('.csv'):
            try:
                df = pd.read_csv(f"{CSV_FOLDER}/{file}")
            except Exception as e:
                return JSONResponse(status_code=400, content={"message": f"Error reading {file}: {e}"})

            if "CRS SUBJ CD" in df.columns and "CRS NBR" in df.columns:
                df["CRS SUBJ CD"] = df["CRS SUBJ CD"].str.strip()
                df["CRS NBR"] = df["CRS NBR"].astype(str).str.strip()

                matches = df[(df["CRS SUBJ CD"] == CRS_SUBJ_CD.strip()) & (df["CRS NBR"] == CRS_NBR.strip())]
                rows_as_dict = matches.to_dict(orient="records")
                
                base_file_name = os.path.splitext(file)[0]
                for row in rows_as_dict:
                    row["file_name"] = base_file_name.upper()
                
                classes.extend(rows_as_dict)
            elif "CRS SUBJ CD" in df.columns:
                matches = df[df["CRS SUBJ CD"] == CRS_SUBJ_CD.strip()]

                rows_as_dict = matches.to_dict(orient="records")
                
                base_file_name = os.path.splitext(file)[0]
                for row in rows_as_dict:
                    row["file_name"] = base_file_name.upper()
                
                classes.extend(rows_as_dict)    

    if not classes:
        return {"message": f"No data found for class {CRS_SUBJ_CD} {CRS_NBR}"}
    
    for _class in classes:
        professors.append(_class["Primary Instructor"].strip())

    professor_ratings = await getMultipleProfRating(professors)
    
    return {"classes": classes, "professor_ratings": professor_ratings}
    



# @app.get('/find_prof/{profName}')
# async def getProfessor(profName:str):
#     professor = []

#     for file in os.listdir(CSV_FOLDER):
#         if file.endswith('.csv'):
#             try:
#                 df = pd.read_csv(f"{CSV_FOLDER}/{file}")
#             except Exception as e:
#                 return JSONResponse(status_code=400, content={"message": f"Error reading {file}: {e}"})
            
#             if "Primary Instructor" in df.columns:
                
#                 matches = df[df["Primary Instructor"] == profName]
#                 rows_as_dict = matches.to_dict(orient="records")

#                 professor.extend(rows_as_dict)

#     if not professor:
#         return {"message": f"No data found for professor {profName}"}

#     return professor



# @app.get('/find_class/{CRS_SUBJ_CD}')
# async def getClass(CRS_SUBJ_CD:str,):
#     classes = []

#     for file in os.listdir(CSV_FOLDER):
#         if file.endswith('.csv'):
#             try:
#                 df = pd.read_csv(f"{CSV_FOLDER}/{file}")
#             except Exception as e:
#                 return JSONResponse(status_code=400, content={"message": f"Error reading {file}: {e}"})

#             if "CRS SUBJ CD" in df.columns:
#                 matches = df[df["CRS SUBJ CD"] == CRS_SUBJ_CD.strip()]

#                 rows_as_dict = matches.to_dict(orient="records")
                
#                 base_file_name = os.path.splitext(file)[0]
#                 for row in rows_as_dict:
#                     row["file_name"] = base_file_name.upper()
                
#                 classes.extend(rows_as_dict)
    
#     if not classes:
#         return {"message": f"No data found for class {CRS_SUBJ_CD}"}

#     return classes


# @app.get('/get_prof_rating/{prof_name}')
# async def getProfRating(prof_name:str):
#     URL = "https://www.ratemyprofessors.com/search/professors/1111?q="
    
#     r = requests.get(f"{URL}{prof_name}")
#     if r.status_code != 200: 
#         return JSONResponse(status_code=400, content={"message": "Error fetching professor search results"})
    
#     page = BeautifulSoup(r.content, 'html.parser')

#     # Get the link to the professor info
#     div = page.find('div', class_='SearchResultsPage__StyledResultsWrapper-vhbycj-3 bdmepv')   
#     if not div or not div.find('a'): 
#         return JSONResponse(status_code=404, content={"message": "Professor not found"})
    
#     a_value = div.find('a')['href']

#     # Get the info from the professor page
#     professor_page = requests.get(f"https://www.ratemyprofessors.com{a_value}")
#     if professor_page.status_code != 200: 
#         return JSONResponse(status_code=400, content={"message": "Error fetching professor details"})
    
#     professor_page_parsed = BeautifulSoup(professor_page.content, 'html.parser')

#     # Extract data from the professor's page
#     name = professor_page_parsed.find('h1', class_='NameTitle__NameWrapper-dowf0z-2 erLzyk')
#     avg_rating = professor_page_parsed.find('div', class_='RatingValue__Numerator-qw8sqy-2 liyUjw')
#     prof_dept = professor_page_parsed.find('div', class_="NameTitle__Title-dowf0z-1 iLYGwn")
#     would_take_again = professor_page_parsed.find('div', class_="FeedbackItem__FeedbackNumber-uof32n-1 kkESWs")
#     # rating_image = professor_page_parsed.find('img', class_="RatingDistribution__ChartImage-p5irx9-3 eolSHJ")

#     # Prepare the response
#     response = {
#         "name": name.text.strip().replace("\n", "") if name else "Not Available",
#         "avg_rating": avg_rating.text.strip().replace("\n", "") if avg_rating else "Not available",
#         "prof_dept": prof_dept.text.strip().replace("\n", "") if prof_dept else "Not available",
#         "would_take_again": would_take_again.text.strip().replace("\n", "") if would_take_again else "Not available",
#         # "rating_image": rating_image['src'] if rating_image else "Not available",
#     }

#     return response


# @app.get('/get_multiple_prof_rating/{prof_names}')
# async def getMultipleProfRating(prof_names):
#     response = []

#     for name in prof_names:
#         response.append(getProfRating(name))
    
#     return response
