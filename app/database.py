
DATABASE_URL = "postgres://meeting:meeting100@192.168.2.67:5432/meeting"


TORTOISE_ORM = {
    "connections": {"default": DATABASE_URL},
    "apps": {
        "models": {
            "models": ["app.models", "aerich.models"],
            "default_connection": "default",
        },
    },
}