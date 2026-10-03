from api.auth import create_access_token

def generate_demo_users():
    roles = ["admin", "forecaster", "viewer", "public"]
    for role in roles:
        token = create_access_token(data={"sub": f"{role}_user", "role": role})
        print(f"Role: {role}, Token: {token}")

if __name__ == "__main__":
    generate_demo_users()
