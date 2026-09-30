from contextlib import contextmanager
from flask import Flask, request, jsonify
from sqlalchemy.exc import IntegrityError
from framework.database import SessionLocal
from framework.models import User, Drone, LandingPad, ChargingStation, UserRole, DroneStatus

app = Flask(__name__)

@contextmanager
def get_db():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

@app.errorhandler(KeyError)
def handle_key_error(e):
    return jsonify({"error": f"missing required field: {e.args[0]}"}), 400

@app.errorhandler(ValueError)
def handle_value_error(e):
    return jsonify({"error": f"invalid field value: {e}"}), 400

@app.errorhandler(IntegrityError)
def handle_integrity_error(e):
    return jsonify({"error": "database constraint violation (e.g. duplicate value)"}), 409

@app.get("/health")
def health():
    return jsonify({"status":"ok"})

#users
@app.post("/users")
def create_user():
    data = request.get_json(force=True)
    with get_db() as db:
        user = User(
            username=data["username"],
            email=data["email"],
            password_hash=data["password_hash"],
            role=UserRole(data.get("role","resident")),
        )
        db.add(user)
        db.flush()
        return jsonify(user.to_dict()),201

@app.get("/users")
def list_users():
    with get_db() as db:
        users = db.query(User).all()
        return jsonify([u.to_dict() for u in users])

@app.get("/users/<int:user_id>")
def get_user(user_id):
    with get_db() as db:
        user = db.get(User, user_id)
        if not user:
            return jsonify({"error":"not found"}), 404
        return jsonify(user.to_dict())
    
#landing pads
@app.post("/landing_pads")
def create_pad():
    data = request.get_json(force=True)
    with get_db() as db:
        pad = LandingPad(
            name=data["name"],
            latitude=data["latitude"],
            longitude=data["longitude"],
            capacity=data.get("capacity",1),
        )
        db.add(pad)
        db.flush()
        return jsonify(pad.to_dict()),201

@app.get("/landing_pads")
def list_pads():
    with get_db() as db:
        pads = db.query(LandingPad).all()
        return jsonify([p.to_dict() for p in pads])

@app.get("/landing_pads/<int:pad_id>")
def get_pad(pad_id):
    with get_db() as db:
        pad = db.get(LandingPad, pad_id)
        if not pad:
            return jsonify({"error":"not found"}), 404
        return jsonify(pad.to_dict())

#charging stations
@app.post("/charging_stations")
def create_charger():
    data = request.get_json(force=True)
    with get_db() as db:
        charger = ChargingStation(
            pad_id = data.get("pad_id"),
            latitude=data["latitude"],
            longitude=data["longitude"],
            charger_type=data.get("charger_type", "contact_pad"),
        )
        db.add(charger)
        db.flush()
        return jsonify(charger.to_dict()),201

@app.get("/charging_stations")
def list_chargers():
    with get_db() as db:
        chargers = db.query(ChargingStation).all()
        return jsonify([c.to_dict() for c in chargers])

    
#drones
@app.post("/drones")
def create_drone():
    data = request.get_json(force=True)
    with get_db() as db:
        drone = Drone(
            name =data["name"],
            model=data.get("model"),
            status=DroneStatus(data.get("status", "idle")),
            battery_pct=data.get("battery_pct", 100.0),
            current_latitude = data.get("current_latitude"),
            current_longitude=data.get("current_longitude"),
            owned_by_city=data.get("owned_by_city", True),
        )
        db.add(drone)
        db.flush()
        return jsonify(drone.to_dict()), 201

@app.get("/drones")
def list_drones():
    with get_db() as db:
        drones = db.query(Drone).all()
        return jsonify([d.to_dict() for d in drones])


@app.get("/drones/<int:drone_id>")
def get_drone(drone_id):
    with get_db() as db:
        drone = db.get(Drone, drone_id)
        if not drone:
            return jsonify({"error": "not found"}), 404
        return jsonify(drone.to_dict())

@app.patch("/drones/<int:drone_id>/telemetry")
def update_drone_telemetry(drone_id):
    data = request.get_json(force=True)
    with get_db() as db:
        drone = db.get(Drone, drone_id)
        if not drone:
            return jsonify({"error": "not found"}), 404
        if "battery_pct" in data:
            drone.battery_pct = data["battery_pct"]
        if "latitude" in data:
            drone.current_latitude = data["latitude"]
        if "longitude" in data:
            drone.current_longitude = data["longitude"]
        if "status" in data:
            drone.status = DroneStatus(data["status"])
        return jsonify(drone.to_dict())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True) #0.0.0.0 just means all interfaces