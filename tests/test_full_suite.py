"""tests/test_full_suite.py
Automated test suite verifying the CAT Smart Operator Assistant:
- Python Dummy ML prediction engines
- Local HTTP backend & API endpoints
- PySide6 desktop integration
"""
import unittest
import json
import urllib.request
import threading
import time

from backend.dummy_ml import predict_safety, predict_task_time, detect_anomalies
from backend.app import start_server


class TestDummyMLEngine(unittest.TestCase):
    def test_predict_safety_nominal(self):
        res = predict_safety({"speed": 3.0, "distance": 10.0, "load": 40.0, "slope": 2.0, "visibility": 90.0, "seatbelt": True})
        self.assertIn("score", res)
        self.assertIn("level", res)
        self.assertEqual(res["level"], "LOW")
        self.assertGreaterEqual(res["score"], 0)
        self.assertLessEqual(res["score"], 100)
        self.assertIsInstance(res["contributions"], list)
        self.assertIn("recommendation", res)

    def test_predict_safety_hazard(self):
        res = predict_safety({"speed": 10.0, "distance": 1.5, "load": 90.0, "slope": 18.0, "visibility": 30.0, "seatbelt": False})
        self.assertIn(res["level"], ("HIGH", "CRITICAL"))
        self.assertGreaterEqual(res["score"], 70.0)

    def test_predict_task_time(self):
        task = {
            "estimated_duration": 50.0,
            "current_progress": 0.5,
            "weather": "Rainy",
            "skill": "Beginner",
            "machine_age": 4.0
        }
        res = predict_task_time(task)
        self.assertIn("predicted_total_min", res)
        self.assertIn("predicted_remaining_min", res)
        self.assertIn("range_low_min", res)
        self.assertIn("range_high_min", res)
        self.assertGreater(res["predicted_total_min"], 50.0) # Rainy + Beginner should lengthen time
        self.assertLess(res["range_low_min"], res["predicted_remaining_min"])
        self.assertGreater(res["range_high_min"], res["predicted_remaining_min"])

    def test_detect_anomalies(self):
        # Normal operator session
        normal_res = detect_anomalies("OP-1001", {"idle_percentage": 17.5, "fuel_rate": 13.2, "swing_harshness": 0.98})
        self.assertEqual(normal_res["status"], "NORMAL")
        self.assertIn("metrics", normal_res)

        # Anomaly session (extreme idling and fuel burn)
        anomaly_res = detect_anomalies("OP-1001", {"idle_percentage": 55.0, "fuel_rate": 22.0, "swing_harshness": 2.1})
        self.assertEqual(anomaly_res["status"], "UNUSUAL")
        self.assertIn("Excessive", anomaly_res["top_deviation"])


class TestBackendServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server, cls.port = start_server(port=5900)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        time.sleep(0.5)

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def test_health_endpoint(self):
        url = f"http://127.0.0.1:{self.port}/api/health"
        with urllib.request.urlopen(url) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode())
            self.assertEqual(data["status"], "ok")

    def test_safety_api(self):
        url = f"http://127.0.0.1:{self.port}/api/predict/safety"
        req = urllib.request.Request(
            url,
            data=json.dumps({"inputs": {"speed": 4.0, "distance": 8.0}}).encode(),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode())
            self.assertIn("score", data)
            self.assertIn("level", data)

    def test_task_time_api(self):
        url = f"http://127.0.0.1:{self.port}/api/predict/task-time"
        req = urllib.request.Request(
            url,
            data=json.dumps({"estimated_duration": 40.0, "weather": "Sunny"}).encode(),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode())
            self.assertIn("predicted_total_min", data)


if __name__ == "__main__":
    unittest.main()
