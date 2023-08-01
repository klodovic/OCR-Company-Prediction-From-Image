from flask import Flask, request
import cv2
import utils.func as func
import predictions as pred
from model.company import *

app = Flask(__name__)

@app.route('/', methods=["POST","GET"])
def predict():   
    try:
        if request.method=='POST':
            image=request.files['image']
            image_name=image.filename
            ext = image_name.split('.')[1].lower()
            if ext in('jpg', 'jpeg', 'png', 'webp', 'gif' ):
                image.save("./img/predict.jpg")
                img = cv2.imread('./img/predict.jpg')
                entities = pred.getPredictions(img)
                
                company = func.createCompany(entities=entities)

                return func.json_encoder(company=company)
            else:
                return {"error":"select you image file"}
    except Exception as e:
        return {"error":str(e)}

if __name__ == "__main__":
    app.run(debug=True)
    
    
    