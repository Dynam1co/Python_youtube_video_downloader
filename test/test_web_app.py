"""Pruebas individuales de validación y manejo de errores de la aplicación web."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import web_app


class WebAppErrorTests(unittest.TestCase):
    def setUp(self):
        self.client = web_app.app.test_client()
        with web_app.JOBS_LOCK:
            web_app.JOBS.clear()

    def test_preview_rejects_invalid_url(self):
        response = self.client.post("/api/preview", json={"url": "https://example.com/video"})

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.get_json())

    def test_preview_reports_extractor_error(self):
        with patch.object(web_app, "extract_video", side_effect=RuntimeError("fallo simulado")):
            response = self.client.post(
                "/api/preview", json={"url": "https://www.youtube.com/watch?v=abc123"}
            )

        self.assertEqual(response.status_code, 422)
        self.assertIn("fallo simulado", response.get_json()["error"])

    def test_download_rejects_empty_or_invalid_urls(self):
        for urls in ("", "https://example.com/video"):
            with self.subTest(urls=urls):
                response = self.client.post("/api/download", json={"urls": urls})
                self.assertEqual(response.status_code, 400)
                self.assertIn("error", response.get_json())

    def test_download_rejects_unknown_mode(self):
        response = self.client.post(
            "/api/download",
            json={"urls": "https://youtu.be/abc123", "mode": "document"},
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.get_json())

    def test_download_rejects_malformed_quality(self):
        response = self.client.post(
            "/api/download",
            json={"urls": "https://youtu.be/abc123", "mode": "video", "itag": "bad value"},
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.get_json())

    def test_unknown_job_returns_not_found(self):
        response = self.client.get("/api/jobs/not-a-real-job")

        self.assertEqual(response.status_code, 404)
        self.assertIn("error", response.get_json())

    def test_download_failure_is_recorded_and_job_finishes(self):
        job_id = "test-job"
        url = "https://www.youtube.com/watch?v=abc123"
        with web_app.JOBS_LOCK:
            web_app.JOBS[job_id] = {
                "status": "queued",
                "completed": 0,
                "total": 1,
                "errors": [],
            }

        class FailingDownloader:
            def __init__(self, options):
                pass

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc_value, traceback):
                return False

            def extract_info(self, url, download):
                raise RuntimeError("fallo simulado de descarga")

        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.object(web_app, "output_dir", return_value=Path(temp_dir)), patch.object(
                web_app, "YoutubeDL", FailingDownloader
            ):
                web_app.run_download(job_id, [url], "video", None)

        with web_app.JOBS_LOCK:
            job = web_app.JOBS[job_id]
            self.assertEqual(job["status"], "done")
            self.assertEqual(job["completed"], 1)
            self.assertEqual(job["files"], [])
            self.assertEqual(len(job["errors"]), 1)
            self.assertIn("fallo simulado de descarga", job["errors"][0])


if __name__ == "__main__":
    unittest.main()
