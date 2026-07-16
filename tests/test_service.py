"""Tests du service d'admission. Le conteneur Docker doit deja tourner
sur http://localhost:3000 (voir README.md pour le demarrer)."""

import time

import pytest
import requests

BASE_URL = "http://localhost:3000"
GOOD_CREDENTIALS = {"username": "admin", "password": "admin123"}
SAMPLE_STUDENT = {
    "data": {
        "gre_score": 330,
        "toefl_score": 115,
        "university_rating": 4,
        "sop": 4.5,
        "lor": 4.5,
        "cgpa": 9.2,
        "research": 1,
    }
}


@pytest.fixture(scope="session", autouse=True)
def wait_for_service():
    for _ in range(30):
        try:
            response = requests.post(BASE_URL + "/login", json=GOOD_CREDENTIALS, timeout=2)
            if response.status_code == 200:
                return
        except requests.exceptions.ConnectionError:
            pass
        time.sleep(1)
    raise RuntimeError("Le service n'a pas repondu sur " + BASE_URL)


def get_valid_token(expires_in=3600):
    payload = {**GOOD_CREDENTIALS, "expires_in": expires_in}
    response = requests.post(BASE_URL + "/login", json=payload)
    return response.json()["access_token"]


def test_login_success():
    response = requests.post(BASE_URL + "/login", json=GOOD_CREDENTIALS)
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_wrong_credentials():
    response = requests.post(
        BASE_URL + "/login", json={"username": "admin", "password": "wrong_password"}
    )
    assert response.status_code == 401


def test_predict_without_token():
    response = requests.post(BASE_URL + "/predict", json=SAMPLE_STUDENT)
    assert response.status_code == 401


def test_predict_with_invalid_token():
    headers = {"Authorization": "Bearer this.is.not.a.valid.token"}
    response = requests.post(BASE_URL + "/predict", json=SAMPLE_STUDENT, headers=headers)
    assert response.status_code == 401


def test_predict_with_expired_token():
    token = get_valid_token(expires_in=1)
    time.sleep(2)
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(BASE_URL + "/predict", json=SAMPLE_STUDENT, headers=headers)
    assert response.status_code == 401


def test_predict_with_valid_token():
    token = get_valid_token()
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(BASE_URL + "/predict", json=SAMPLE_STUDENT, headers=headers)
    assert response.status_code == 200
    prediction = response.json()["chance_of_admit"]
    assert 0 <= prediction <= 1


def test_predict_invalid_input():
    token = get_valid_token()
    headers = {"Authorization": f"Bearer {token}"}
    bad_student = {"data": {**SAMPLE_STUDENT["data"], "gre_score": 9999}}
    response = requests.post(BASE_URL + "/predict", json=bad_student, headers=headers)
    assert response.status_code >= 400
