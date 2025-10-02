from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from business_object.match_new_text_V0 import match_new_card
from business_object.class_of_cards import CardModel


app = FastAPI(title="Find Magic cards")


@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    """Redirect to the API documentation"""
    return RedirectResponse(url="/docs")


@app.post("/find_corresponding_text/", tags=["match"])
async def find_corresponding_text(c: CardModel):
    result_card = match_new_card(c.text)
    return result_card


@app.get("/hello/{name}")
async def hello_name(name: str):
    """Afficher Hello"""
    return f"message : Hello {name}"


# Run the FastAPI application
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=9876)
