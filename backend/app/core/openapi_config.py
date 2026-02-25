from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi


def custom_openapi(app: FastAPI):
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Grocery Management API",
        version="1.0.0",
        description="...",
        routes=app.routes,
    )

    # Replace the confusing OAuth2 password flow with clean http bearer
    openapi_schema["components"]["securitySchemes"] = {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Enter your JWT token.\n\nPrefix with 'Bearer '"
        }
    }

    # Apply to all protected paths (or do it selectively)
    for path_item in openapi_schema["paths"].values():
        for operation in path_item.values():
            if "security" in operation:
                operation["security"] = [{"bearerAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema
