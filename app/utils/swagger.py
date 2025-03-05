import json
import os
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from flask import current_app

def generate_swagger_spec(app):
    """
    Генерирует Swagger спецификацию для API
    """
    spec = APISpec(
        title="Restaurant Reviews API",
        version="1.0.0",
        openapi_version="3.0.2",
        plugins=[MarshmallowPlugin()],
    )
    
    # Определение компонентов схемы
    spec.components.schema("User", {
        "type": "object",
        "properties": {
            "id": {"type": "integer"},
            "username": {"type": "string"},
            "email": {"type": "string", "format": "email"},
            "role": {"type": "string", "enum": ["admin", "respondent"]},
            "created_at": {"type": "string", "format": "date-time"},
            "updated_at": {"type": "string", "format": "date-time"}
        }
    })
    
    spec.components.schema("Restaurant", {
        "type": "object",
        "properties": {
            "id": {"type": "integer"},
            "name": {"type": "string"},
            "address": {"type": "string"},
            "description": {"type": "string"},
            "created_at": {"type": "string", "format": "date-time"},
            "updated_at": {"type": "string", "format": "date-time"}
        }
    })
    
    spec.components.schema("Review", {
        "type": "object",
        "properties": {
            "id": {"type": "integer"},
            "restaurant_id": {"type": "integer"},
            "user_id": {"type": "integer"},
            "food_rating": {"type": "integer", "minimum": 1, "maximum": 5},
            "drinks_rating": {"type": "integer", "minimum": 1, "maximum": 5},
            "overall_rating": {"type": "integer", "minimum": 1, "maximum": 5},
            "comment": {"type": "string"},
            "created_at": {"type": "string", "format": "date-time"},
            "updated_at": {"type": "string", "format": "date-time"}
        }
    })
    
    # Определение безопасности
    spec.components.security_scheme("BearerAuth", {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT"
    })
    
    # Определение путей API
    
    # Аутентификация
    spec.path(
        path="/api/v1/auth/register",
        operations={
            "post": {
                "tags": ["Authentication"],
                "summary": "Регистрация нового пользователя",
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "username": {"type": "string"},
                                    "email": {"type": "string", "format": "email"},
                                    "password": {"type": "string", "format": "password"}
                                },
                                "required": ["username", "email", "password"]
                            }
                        }
                    }
                },
                "responses": {
                    "201": {
                        "description": "Пользователь успешно зарегистрирован",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/User"}
                            }
                        }
                    },
                    "400": {
                        "description": "Ошибка валидации данных"
                    }
                }
            }
        }
    )
    
    spec.path(
        path="/api/v1/auth/login",
        operations={
            "post": {
                "tags": ["Authentication"],
                "summary": "Вход в систему",
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "username": {"type": "string"},
                                    "password": {"type": "string", "format": "password"}
                                },
                                "required": ["username", "password"]
                            }
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "Успешный вход",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "access_token": {"type": "string"},
                                        "user": {"$ref": "#/components/schemas/User"}
                                    }
                                }
                            }
                        }
                    },
                    "401": {
                        "description": "Неверные учетные данные"
                    }
                }
            }
        }
    )
    
    # Пользователи
    spec.path(
        path="/api/v1/users",
        operations={
            "get": {
                "tags": ["Users"],
                "summary": "Получение списка пользователей (только для администраторов)",
                "security": [{"BearerAuth": []}],
                "responses": {
                    "200": {
                        "description": "Список пользователей",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "array",
                                    "items": {"$ref": "#/components/schemas/User"}
                                }
                            }
                        }
                    },
                    "403": {
                        "description": "Доступ запрещен"
                    }
                }
            },
            "post": {
                "tags": ["Users"],
                "summary": "Создание нового пользователя (только для администраторов)",
                "security": [{"BearerAuth": []}],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "username": {"type": "string"},
                                    "email": {"type": "string", "format": "email"},
                                    "password": {"type": "string", "format": "password"},
                                    "role": {"type": "string", "enum": ["admin", "respondent"]}
                                },
                                "required": ["username", "email", "password", "role"]
                            }
                        }
                    }
                },
                "responses": {
                    "201": {
                        "description": "Пользователь успешно создан",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/User"}
                            }
                        }
                    },
                    "400": {
                        "description": "Ошибка валидации данных"
                    },
                    "403": {
                        "description": "Доступ запрещен"
                    }
                }
            }
        }
    )
    
    spec.path(
        path="/api/v1/users/{user_id}",
        operations={
            "get": {
                "tags": ["Users"],
                "summary": "Получение данных пользователя",
                "security": [{"BearerAuth": []}],
                "parameters": [
                    {
                        "name": "user_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "integer"}
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Данные пользователя",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/User"}
                            }
                        }
                    },
                    "403": {
                        "description": "Доступ запрещен"
                    },
                    "404": {
                        "description": "Пользователь не найден"
                    }
                }
            },
            "put": {
                "tags": ["Users"],
                "summary": "Обновление данных пользователя (только для администраторов)",
                "security": [{"BearerAuth": []}],
                "parameters": [
                    {
                        "name": "user_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "integer"}
                    }
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "username": {"type": "string"},
                                    "email": {"type": "string", "format": "email"},
                                    "role": {"type": "string", "enum": ["admin", "respondent"]}
                                }
                            }
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "Пользователь успешно обновлен",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/User"}
                            }
                        }
                    },
                    "400": {
                        "description": "Ошибка валидации данных"
                    },
                    "403": {
                        "description": "Доступ запрещен"
                    },
                    "404": {
                        "description": "Пользователь не найден"
                    }
                }
            },
            "delete": {
                "tags": ["Users"],
                "summary": "Удаление пользователя (только для администраторов)",
                "security": [{"BearerAuth": []}],
                "parameters": [
                    {
                        "name": "user_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "integer"}
                    }
                ],
                "responses": {
                    "204": {
                        "description": "Пользователь успешно удален"
                    },
                    "403": {
                        "description": "Доступ запрещен"
                    },
                    "404": {
                        "description": "Пользователь не найден"
                    }
                }
            }
        }
    )
    
    # Рестораны
    spec.path(
        path="/api/v1/restaurants",
        operations={
            "get": {
                "tags": ["Restaurants"],
                "summary": "Получение списка ресторанов",
                "responses": {
                    "200": {
                        "description": "Список ресторанов",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "array",
                                    "items": {"$ref": "#/components/schemas/Restaurant"}
                                }
                            }
                        }
                    }
                }
            },
            "post": {
                "tags": ["Restaurants"],
                "summary": "Создание нового ресторана (только для администраторов)",
                "security": [{"BearerAuth": []}],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "address": {"type": "string"},
                                    "description": {"type": "string"}
                                },
                                "required": ["name"]
                            }
                        }
                    }
                },
                "responses": {
                    "201": {
                        "description": "Ресторан успешно создан",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Restaurant"}
                            }
                        }
                    },
                    "400": {
                        "description": "Ошибка валидации данных"
                    },
                    "403": {
                        "description": "Доступ запрещен"
                    }
                }
            }
        }
    )
    
    spec.path(
        path="/api/v1/restaurants/{restaurant_id}",
        operations={
            "get": {
                "tags": ["Restaurants"],
                "summary": "Получение данных ресторана",
                "parameters": [
                    {
                        "name": "restaurant_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "integer"}
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Данные ресторана",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Restaurant"}
                            }
                        }
                    },
                    "404": {
                        "description": "Ресторан не найден"
                    }
                }
            },
            "put": {
                "tags": ["Restaurants"],
                "summary": "Обновление данных ресторана (только для администраторов)",
                "security": [{"BearerAuth": []}],
                "parameters": [
                    {
                        "name": "restaurant_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "integer"}
                    }
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "address": {"type": "string"},
                                    "description": {"type": "string"}
                                }
                            }
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "Ресторан успешно обновлен",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Restaurant"}
                            }
                        }
                    },
                    "400": {
                        "description": "Ошибка валидации данных"
                    },
                    "403": {
                        "description": "Доступ запрещен"
                    },
                    "404": {
                        "description": "Ресторан не найден"
                    }
                }
            },
            "delete": {
                "tags": ["Restaurants"],
                "summary": "Удаление ресторана (только для администраторов)",
                "security": [{"BearerAuth": []}],
                "parameters": [
                    {
                        "name": "restaurant_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "integer"}
                    }
                ],
                "responses": {
                    "204": {
                        "description": "Ресторан успешно удален"
                    },
                    "403": {
                        "description": "Доступ запрещен"
                    },
                    "404": {
                        "description": "Ресторан не найден"
                    }
                }
            }
        }
    )
    
    # Отчеты
    spec.path(
        path="/api/v1/restaurants/report",
        operations={
            "get": {
                "tags": ["Reports"],
                "summary": "Выгрузка сводного отчета по всем ресторанам (только для администраторов)",
                "security": [{"BearerAuth": []}],
                "responses": {
                    "200": {
                        "description": "Сводный отчет в формате CSV",
                        "content": {
                            "text/csv": {
                                "schema": {
                                    "type": "string",
                                    "format": "binary"
                                }
                            }
                        }
                    },
                    "403": {
                        "description": "Доступ запрещен"
                    }
                }
            }
        }
    )
    
    # Отзывы
    spec.path(
        path="/api/v1/reviews",
        operations={
            "get": {
                "tags": ["Reviews"],
                "summary": "Получение списка отзывов",
                "security": [{"BearerAuth": []}],
                "parameters": [
                    {
                        "name": "restaurant_id",
                        "in": "query",
                        "schema": {"type": "integer"},
                        "description": "Фильтр по ID ресторана"
                    },
                    {
                        "name": "user_id",
                        "in": "query",
                        "schema": {"type": "integer"},
                        "description": "Фильтр по ID пользователя"
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Список отзывов",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "array",
                                    "items": {"$ref": "#/components/schemas/Review"}
                                }
                            }
                        }
                    },
                    "403": {
                        "description": "Доступ запрещен"
                    }
                }
            },
            "post": {
                "tags": ["Reviews"],
                "summary": "Создание нового отзыва",
                "security": [{"BearerAuth": []}],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "restaurant_id": {"type": "integer"},
                                    "food_rating": {"type": "integer", "minimum": 1, "maximum": 5},
                                    "drinks_rating": {"type": "integer", "minimum": 1, "maximum": 5},
                                    "overall_rating": {"type": "integer", "minimum": 1, "maximum": 5},
                                    "comment": {"type": "string"}
                                },
                                "required": ["restaurant_id", "food_rating", "drinks_rating", "overall_rating"]
                            }
                        }
                    }
                },
                "responses": {
                    "201": {
                        "description": "Отзыв успешно создан",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Review"}
                            }
                        }
                    },
                    "400": {
                        "description": "Ошибка валидации данных или отзыв уже существует"
                    },
                    "401": {
                        "description": "Требуется аутентификация"
                    },
                    "404": {
                        "description": "Ресторан не найден"
                    }
                }
            }
        }
    )
    
    spec.path(
        path="/api/v1/reviews/{review_id}",
        operations={
            "get": {
                "tags": ["Reviews"],
                "summary": "Получение данных отзыва",
                "security": [{"BearerAuth": []}],
                "parameters": [
                    {
                        "name": "review_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "integer"}
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Данные отзыва",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Review"}
                            }
                        }
                    },
                    "403": {
                        "description": "Доступ запрещен"
                    },
                    "404": {
                        "description": "Отзыв не найден"
                    }
                }
            }
        }
    )
    
    # Сохранение спецификации в JSON файл
    static_dir = os.path.join(app.root_path, 'static')
    os.makedirs(static_dir, exist_ok=True)
    
    with open(os.path.join(static_dir, 'swagger.json'), 'w') as f:
        json.dump(spec.to_dict(), f)
