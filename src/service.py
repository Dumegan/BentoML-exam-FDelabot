"""API BentoML: login (JWT) + predict (chance d'admission), predict protege par JWT."""

import functools
from datetime import datetime, timedelta, timezone

import bentoml
import jwt
import pandas as pd
from pydantic import BaseModel, Field

SECRET_KEY = "admission-exam-secret-key"
JWT_ALGORITHM = "HS256"

USERS = {"admin": "admin123"}


class AdmissionInput(BaseModel):
    gre_score: float = Field(ge=0, le=340)
    toefl_score: float = Field(ge=0, le=120)
    university_rating: float = Field(ge=1, le=5)
    sop: float = Field(ge=1, le=5)
    lor: float = Field(ge=1, le=5)
    cgpa: float = Field(ge=0, le=10)
    research: float = Field(ge=0, le=1)


def require_auth(func):
    #Middleware d'authentification: verifie le JWT avant d'appeler la methode

    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        ctx = kwargs["ctx"]
        auth_header = ctx.request.headers.get("Authorization", "")

        if not auth_header.startswith("Bearer "):
            ctx.response.status_code = 401
            return {"error": "Token manquant"}

        token = auth_header.removeprefix("Bearer ")
        try:
            jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        except jwt.PyJWTError:
            ctx.response.status_code = 401
            return {"error": "Token invalide ou expire"}

        return func(self, *args, **kwargs)

    return wrapper


@bentoml.service(name="admission_prediction_service")
class AdmissionService:
    model_ref = bentoml.models.get("admission_lr:latest")

    def __init__(self):
        self.model = bentoml.sklearn.load_model(self.model_ref)

    @bentoml.api
    def login(
        self,
        ctx: bentoml.Context,
        username: str,
        password: str,
        expires_in: int = 3600,
    ) -> dict:
        if USERS.get(username) != password:
            ctx.response.status_code = 401
            return {"error": "Identifiants invalides"}

        expire_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
        payload = {"sub": username, "exp": expire_at}
        token = jwt.encode(payload, SECRET_KEY, algorithm=JWT_ALGORITHM)
        return {"access_token": token, "token_type": "bearer"}

    @bentoml.api
    @require_auth
    def predict(self, ctx: bentoml.Context, data: AdmissionInput) -> dict:
        input_df = pd.DataFrame(
            [
                {
                    "GRE Score": data.gre_score,
                    "TOEFL Score": data.toefl_score,
                    "University Rating": data.university_rating,
                    "SOP": data.sop,
                    "LOR": data.lor,
                    "CGPA": data.cgpa,
                    "Research": data.research,
                }
            ]
        )
        prediction = self.model.predict(input_df)[0]
        return {"chance_of_admit": float(prediction)}
