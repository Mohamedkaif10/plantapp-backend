from fastapi import FASTAPI 
app=FASTAPI()
@app.get("/")
async def health_check():
      return "the check is successfull"