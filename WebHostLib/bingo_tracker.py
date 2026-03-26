"""
Bingo Tracker Web Interface

Provides web pages for viewing and tracking bingo boards.
"""

from uuid import UUID

from flask import render_template, abort, request, redirect, url_for, flash
from werkzeug.utils import secure_filename

from . import app
from .models import Room
from .tracker import TrackerData


@app.route("/bingo/<suuid:tracker>")
def bingo_tracker_view(tracker: UUID):
    """
    Display interactive bingo board for a tracker session.

    Auto-updates as players check locations.
    """
    room: Room | None = Room.get(tracker=tracker)
    if not room:
        abort(404)

    tracker_data = TrackerData(room)
    seed_name = tracker_data.get_seed_name()

    # Check if bingo board is available
    # The actual data will be loaded via API call from the frontend

    return render_template(
        "bingo_tracker.html",
        tracker=tracker,
        room=room,
        seed_name=seed_name,
    )


@app.route("/bingo/<suuid:tracker>/upload", methods=["GET", "POST"])
def bingo_upload_view(tracker: UUID):
    """
    Upload page for bingo board JSON.
    """
    room: Room | None = Room.get(tracker=tracker)
    if not room:
        abort(404)

    if request.method == "POST":
        # The actual upload is handled by the API endpoint
        # This redirects to it
        return redirect(url_for("api.bingo_upload", tracker=tracker))

    tracker_data = TrackerData(room)
    seed_name = tracker_data.get_seed_name()

    return render_template(
        "bingo_upload.html",
        tracker=tracker,
        room=room,
        seed_name=seed_name,
    )
