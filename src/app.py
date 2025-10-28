from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from service.card_service import CardService
# from business_object.class_of_cards import CardModel


app = FastAPI(title="Find Magic cards")


@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    """Redirect to the API documentation"""
    return RedirectResponse(url="/docs")


@app.post("/find_corresponding_text/", tags=["match"])
async def find_corresponding_text(text: str):
    result_card = CardService().semantic_search(text, 1)
    return result_card


@app.get("/hello/{name}")
async def hello_name(name: str):
    """Afficher Hello"""
    return f"message : Hello {name}"


# Run the FastAPI application
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=9876)
