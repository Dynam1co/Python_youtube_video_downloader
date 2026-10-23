"""Small Flask interface for the existing YouTube downloader."""
from __future__ import annotations

import os
import re
import threading
import uuid
from pathlib import Path

from flask import Flask, abort, jsonify, render_template, request, send_file
import imageio_ffmpeg
from yt_dlp import YoutubeDL

import conf_management as cfg

app = Flask(__name__)
JOBS: dict[str, dict] = {}
JOBS_LOCK = threading.Lock()


def output_dir() -> Path:
    configured = Path(cfg.get_ruta_descargas())
    # The original config used a Linux-only path. Keep it when usable, otherwise
    # place downloads in the project so the app works on Windows too.
    if configured.is_absolute() and configured.drive and configured.exists():
        return configured
    return Path(__file__).resolve().parent / "downloads"


def valid_url(value: str) -> bool:
    return bool(re.match(r"^https?://(www\.)?(youtube\.com|youtu\.be)/", value.strip(), re.I))


def extract_video(url: str) -> dict:
    # Ignore playlist parameters so a single pasted URL always means one video.
    with YoutubeDL({"quiet": True, "no_warnings": True, "noplaylist": True}) as ydl:
        return ydl.extract_info(url, download=False)


@app.get("/")
def home():
    return render_template("index.html")


@app.get("/documentacion")
def documentation():
    return render_template("documentation.html")


@app.get("/manual")
def user_manual():
    return render_template("manual.html")


@app.post("/api/preview")
def preview():
    url = (request.json or {}).get("url", "").strip()
    if not valid_url(url):
        return jsonify(error="Pega un enlace válido de YouTube."), 400
    try:
        video = extract_video(url)
        streams = [f for f in video.get("formats", []) if f.get("ext") == "mp4" and f.get("vcodec", "none") != "none"]
        # Prefer H.264 and already-muxed formats when YouTube offers duplicates.
        by_height = {}
        for fmt in streams:
            height = fmt.get("height") or 0
            score = (fmt.get("vcodec", "").startswith("avc1"), fmt.get("acodec", "none") != "none", fmt.get("tbr") or 0)
            if height not in by_height or score > by_height[height][0]:
                by_height[height] = (score, fmt)
        streams = [entry[1] for entry in by_height.values()]
        streams.sort(key=lambda f: f.get("height") or 0, reverse=True)
        return jsonify({
            "title": video.get("title", "Video de YouTube"),
            "author": video.get("uploader", ""),
            "thumbnail": video.get("thumbnail", ""),
            "duration": video.get("duration") or 0,
            "formats": [{"itag": (s["format_id"] if s.get("acodec", "none") != "none" else f'{s["format_id"]}+bestaudio[ext=m4a]'), "resolution": f'{s.get("height") or "Estándar"}p', "size": s.get("filesize")} for s in streams],
        })
    except Exception as exc:
        return jsonify(error=f"No se pudo consultar el video: {exc}"), 422


def run_download(job_id: str, urls: list[str], mode: str, itag: str | None):
    with JOBS_LOCK:
        JOBS[job_id].update(status="running", message="Preparando descarga", completed=0, total=len(urls))
    root = output_dir()
    folder = root / ("audio" if mode == "audio" else "video")
    folder.mkdir(parents=True, exist_ok=True)
    with JOBS_LOCK:
        JOBS[job_id]["files"] = []
    for number, url in enumerate(urls, 1):
        try:
            def progress(status):
                if status.get("status") != "downloading":
                    return
                percent = status.get("_percent_str", "").strip()
                with JOBS_LOCK:
                    JOBS[job_id]["message"] = f'Descargando {number}/{len(urls)} · {status.get("info_dict", {}).get("title", "video")} {percent}'
            options = {
                "quiet": True, "no_warnings": True, "noplaylist": True,
                "ffmpeg_location": imageio_ffmpeg.get_ffmpeg_exe(), "merge_output_format": "mp4",
                "outtmpl": str(folder / "%(title)s.%(ext)s"), "progress_hooks": [progress],
                "format": ("bestaudio[ext=m4a]/bestaudio" if mode == "audio" else (itag or "best[ext=mp4][vcodec!=none][acodec!=none]/bestvideo[ext=mp4][vcodec^=avc1]+bestaudio[ext=m4a]/bestvideo[ext=mp4]+bestaudio")),
            }
            with YoutubeDL(options) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = Path(info.get("filepath") or info.get("_filename") or ydl.prepare_filename(info))
                if not filename.is_file():
                    merged = filename.with_suffix(".mp4")
                    if merged.is_file():
                        filename = merged
                    else:
                        downloads = info.get("requested_downloads") or []
                        found = next((Path(item["filepath"]) for item in downloads if item.get("filepath") and Path(item["filepath"]).is_file()), None)
                        if found is None:
                            raise FileNotFoundError("No se encontró el archivo descargado.")
                        filename = found
            with JOBS_LOCK:
                JOBS[job_id]["files"].append({"name": filename.name, "path": str(filename)})
                JOBS[job_id]["completed"] = number
                JOBS[job_id]["message"] = f"Guardado: {Path(filename).name}"
        except Exception as exc:
            with JOBS_LOCK:
                JOBS[job_id].setdefault("errors", []).append(f"{url}: {exc}")
                JOBS[job_id]["completed"] = number
    with JOBS_LOCK:
        JOBS[job_id]["status"] = "done"
        JOBS[job_id]["message"] = "Descarga finalizada"
        JOBS[job_id]["folder"] = str(folder)


@app.post("/api/download")
def download():
    data = request.json or {}
    urls = [line.strip() for line in data.get("urls", "").splitlines() if line.strip()]
    mode = data.get("mode", "video")
    if not urls or any(not valid_url(url) for url in urls):
        return jsonify(error="Añade uno o más enlaces válidos de YouTube."), 400
    if mode not in ("video", "audio"):
        return jsonify(error="Elige video o audio."), 400
    itag = data.get("itag") or None
    if itag and (not isinstance(itag, str) or len(itag) > 80 or not re.fullmatch(r"[A-Za-z0-9+\[\]=._-]+", itag)):
        return jsonify(error="Calidad de video no v?lida."), 400
    job_id = uuid.uuid4().hex
    with JOBS_LOCK:
        JOBS[job_id] = {"status": "queued", "message": "En cola", "completed": 0, "total": len(urls), "errors": []}
    threading.Thread(target=run_download, args=(job_id, urls, mode, itag), daemon=True).start()
    return jsonify(job_id=job_id)


@app.get("/api/jobs/<job_id>")
def job_status(job_id):
    with JOBS_LOCK:
        job = JOBS.get(job_id)
        if not job:
            return jsonify(error="La descarga no existe."), 404
        return jsonify(job)


@app.get("/api/jobs/<job_id>/files/<int:file_index>")
def view_download(job_id, file_index):
    with JOBS_LOCK:
        job = JOBS.get(job_id)
        if not job or job.get("status") != "done":
            abort(404)
        files = job.get("files", [])
        if file_index < 0 or file_index >= len(files):
            abort(404)
        path = Path(files[file_index]["path"])
    if not path.is_file():
        abort(404)
    return send_file(path, as_attachment=False, download_name=path.name, conditional=True)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", 5000)), debug=False)
