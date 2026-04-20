from app.services.user_store import load_users, save_users

users = load_users()


def get_or_create_user(user_id: str):
    if user_id not in users:
        users[user_id] = {
            "id": user_id,
            "email": f"{user_id}@mock.com",
            "plan": "free",
            "requests_used": 0,
        }
        save_users(users)  # 👈 persist immediately

    return users[user_id]
