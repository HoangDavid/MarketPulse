from fastapi import APIRouter, HTTPException
from services.yahoo import fetch_vix_data

router = APIRouter()

@router.get("/vix")
async def get_vix():
    """
    Endpoint to fetch VIX data.
    """
    try:
        # Fetch intraday VIX data
        vix_data = fetch_vix_data()
        print(vix_data)
        
        # Check if data is empty or None
        if not vix_data:
            raise HTTPException(status_code=404, detail="No intraday VIX data found.")
        
        return {"vix_intraday_data": vix_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")