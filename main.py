from fastapi import FastAPI, Form, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

from database import engine, SessionLocal
from models import Base, Survey, Response

# ---------------------------
# INIT APP
# ---------------------------
Base.metadata.create_all(bind=engine)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

VALID_ANSWERS = {"Yes", "No", "Not sure"}

# ---------------------------
# HOME
# ---------------------------
@app.get("/")
def home():
    return RedirectResponse(url="/admin")


# ---------------------------
# ADMIN DASHBOARD (FIXED)
# ---------------------------
@app.get("/admin")
def admin_page(request: Request):
    db = SessionLocal()
    surveys = db.query(Survey).all()
    db.close()

    clean_surveys = [
        {
            "id": s.id,
            "question": s.question,
            "slug": s.slug
        }
        for s in surveys
    ]

    return templates.TemplateResponse(
        request,
        "admin.html",
        {"surveys": clean_surveys}
    )


# ---------------------------
# DELETE SURVEY
# ---------------------------
@app.post("/admin/delete/{survey_id}")
def delete_survey(survey_id: int):
    db = SessionLocal()

    survey = db.query(Survey).filter(Survey.id == survey_id).first()

    if survey:
        db.delete(survey)
        db.commit()

    db.close()
    return RedirectResponse(url="/admin", status_code=303)


# ---------------------------
# PUBLIC SURVEY PAGE
# ---------------------------
@app.get("/s/{slug}")
def get_survey(request: Request, slug: str):
    db = SessionLocal()

    survey = db.query(Survey).filter(Survey.slug == slug).first()

    db.close()

    if not survey:
        return {"error": "Survey not found"}

    survey_data = {
        "id": survey.id,
        "question": survey.question,
        "slug": survey.slug
    }

    return templates.TemplateResponse(
        request,
        "survey.html",
        {"survey": survey_data}
    )


# ---------------------------
# SUBMIT ANSWER
# ---------------------------
@app.post("/submit")
def submit_answer(
    survey_id: int = Form(...),
    answer: str = Form(...)
):
    db = SessionLocal()

    survey = db.query(Survey).filter(Survey.id == survey_id).first()

    if not survey:
        db.close()
        return {"error": "Survey not found"}

    if answer not in VALID_ANSWERS:
        db.close()
        return {"error": "Invalid answer"}

    db.add(Response(
        survey_id=survey_id,
        answer=answer
    ))

    db.commit()
    db.close()

    return RedirectResponse(url="/thank-you", status_code=303)


# ---------------------------
# THANK YOU PAGE
# ---------------------------
@app.get("/thank-you", response_class=HTMLResponse)
def thank_you():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Thank You</title>
        <style>
            body {
                font-family: Arial;
                background: #f5f5f5;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
            }
            .card {
                background: white;
                padding: 40px;
                border-radius: 12px;
                text-align: center;
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            }
            h1 { color: #28a745; }
            a {
                display: inline-block;
                margin-top: 15px;
                padding: 10px 15px;
                background: #007bff;
                color: white;
                text-decoration: none;
                border-radius: 6px;
            }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>Thank you 🙏</h1>
            <p>Your response has been recorded.</p>
            <a href="/admin">Back to dashboard</a>
        </div>
    </body>
    </html>
    """


# ---------------------------
# ANALYTICS UI (FIXED)
# ---------------------------
@app.get("/admin/analytics-ui")
def analytics_ui(request: Request):
    db = SessionLocal()

    surveys = db.query(Survey).all()
    results = []

    for s in surveys:
        responses = db.query(Response).filter(Response.survey_id == s.id).all()

        results.append({
            "survey": {
                "id": s.id,
                "question": s.question,
                "slug": s.slug
            },
            "yes": sum(1 for r in responses if r.answer == "Yes"),
            "no": sum(1 for r in responses if r.answer == "No"),
            "unsure": sum(1 for r in responses if r.answer == "Not sure"),
            "total": len(responses)
        })

    db.close()

    return templates.TemplateResponse(
        request,
        "analytics.html",
        {"results": results}
    )


# ---------------------------
# ANALYTICS API
# ---------------------------
@app.get("/admin/analytics")
def admin_analytics():
    db = SessionLocal()

    surveys = db.query(Survey).all()

    data = []

    for s in surveys:
        responses = db.query(Response).filter(Response.survey_id == s.id).all()

        data.append({
            "id": s.id,
            "question": s.question,
            "slug": s.slug,
            "yes": sum(1 for r in responses if r.answer == "Yes"),
            "no": sum(1 for r in responses if r.answer == "No"),
            "unsure": sum(1 for r in responses if r.answer == "Not sure"),
            "total": len(responses)
        })

    db.close()
    return data