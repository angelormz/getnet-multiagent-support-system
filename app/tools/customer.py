
import json
from pathlib import Path


# Ubicación de la carpeta data/
DATA_DIR = Path(__file__).resolve().parents[2] / "data"


def load_data(filename: str) -> dict:
    """Carga datos desde un archivo JSON."""
    file_path = DATA_DIR / filename

    with file_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def get_customer(user_id: str) -> dict:
    """Consulta la información de un cliente."""
    customers = load_data("customers.json")

    customer = customers.get(user_id)

    if customer is None:
        return {"error": "Customer not found"}

    return {
        "user_id": user_id,
        **customer,
    }


def get_transactions(user_id: str) -> dict:
    """Consulta las transacciones de un cliente."""
    customers = load_data("customers.json")

    if user_id not in customers:
        return {"error": "Customer not found"}

    transactions = load_data("transactions.json")

    return {
        "user_id": user_id,
        "transactions": transactions.get(user_id, []),
    }
