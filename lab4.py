import os
import redis
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import ssl
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)
CORS(app)

# Ініціалізація PrometheusMetrics
metrics = PrometheusMetrics(app)

# Локальні витрати для тестування
local_expenses = [
    {"id": 1, "category": "Food", "amount": 50.0, "date": "2024-12-01"},
    {"id": 2, "category": "Transport", "amount": 20.0, "date": "2024-12-02"}
]

# Підключення до Redis
def get_redis_connection():
    redis_url = os.environ.get('REDIS_URL')
    if not redis_url:
        return None

    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    r = redis.from_url(redis_url, ssl=True, ssl_context=context)

    r.config_set("maxmemory", "100mb")
    r.config_set("maxmemory-policy", "allkeys-lru")
    r.config_set("maxclients", "100")
    r.config_set("timeout", "300")

    return r


redis_client = get_redis_connection()

# Ліміти запитів
limiter = Limiter(
    get_remote_address,
    storage_uri=os.environ.get("REDIS_URL", "redis://localhost:6379"),
    app=app
)

EXPENSES_KEY = "expenses"

@app.route('/expenses', methods=['GET'])
@limiter.limit("101 per hour")
def get_expenses():
    expenses = local_expenses

    if redis_client:
        expenses = redis_client.lrange(EXPENSES_KEY, 0, -1)
        expenses = [json.loads(expense.decode('utf-8')) for expense in expenses]

    month = request.args.get('month', "")
    category = request.args.get('category', "")

    filtered_expenses = [
        e for e in expenses
        if (not month or e["date"].startswith(month)) and (not category or e["category"] == category)
    ]

    return jsonify(filtered_expenses), 200

@app.route('/expenses', methods=['POST'])
@limiter.limit("101 per hour")
def add_expense():
    new_expense = request.json

    if redis_client:
        expenses = redis_client.lrange(EXPENSES_KEY, 0, -1)
        new_expense['id'] = len(expenses) + 1
        redis_client.rpush(EXPENSES_KEY, json.dumps(new_expense))
        redis_client.expire(EXPENSES_KEY, 3600)
    else:
        new_expense['id'] = len(local_expenses) + 1
        local_expenses.append(new_expense)

    return jsonify(new_expense), 201

@app.route('/metrics')
def metrics_route():
    return metrics.export()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=5001)
