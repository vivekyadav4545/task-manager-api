def test_signup_user(client):
    response = client.post("/signup", json={"email": "vivek@gamil.com", "password": "testpass123"})
    assert response.status_code == 201

    data = response.json()
    assert data["email"] == "vivek@gamil.com"
    assert "hashed_password" not in data 

def test_duplicate_user(client):
    client.post("/signup" , json={"email": "vivek@gamil.com", "password": "testpass123"})
    response = client.post("/signup" ,json={"email": "vivek@gamil.com", "password": "testpass123"} )

    assert response.status_code == 400


def test_login_user(client):
    client.post("/signup", json={"email": "vivek@gamil.com", "password": "testpass123"})
    response = client.post(
        "/login",
        data={"username": "vivek@gamil.com", "password": "testpass123"} 
    )

    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_wrong_password(client):
    client.post("/signup" ,  json={"email": "vivek@gamil.com", "password": "testpass123"})

    response = client.post("/login" , data = {"username" : "vivek@gamil.com" , "password":"tstdrrd"})
    assert response.status_code == 401