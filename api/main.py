from fastapi import FastAPI 
app=FASTAPI()
@app.get("/")
async def health_check():
      return "the check is successfull"