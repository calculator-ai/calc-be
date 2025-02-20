from fastapi import APIRouter
import base64
from io import BytesIO
from apps.calculators.utils import analyze_image
from schema import ImageData
from PIL import Image

router = APIRouter()

@router.post('/')
async def run(data: ImageData):
    try:
        # ✅ Decode image safely
        image_data = base64.b64decode(data.image.split(',')[1])
        image_bytes = BytesIO(image_data)
        image = Image.open(image_bytes)

        # ✅ Ensure `responses` is always assigned
        responses = analyze_image(image, dict_of_vars=data.dict_of_vars) or []
        
        data_list = []
        for response in responses:
            data_list.append(response)

        # ✅ Check if responses exist before printing
        if responses:
            print('response in route:', responses)
        else:
            print('No valid responses received.')

        return {
            "message": "Image Processed",
            "type": "success",
            "data": data_list
        }

    except Exception as e:
        print(f"Error in route: {e}")  # ✅ Log error
        return {
            "message": "Error processing image",
            "type": "error",
            "error": str(e)
        }
