import os
import logging
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
    session,
)
from markupsafe import Markup
import tempfile
import uuid
from werkzeug.utils import secure_filename
import asyncio
import nest_asyncio
from dotenv import load_dotenv
from financial_analysis import AutomotiveSectorAnalysisWorkflow, create_extract_agent

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Configure upload settings
UPLOAD_FOLDER = tempfile.gettempdir()
ALLOWED_EXTENSIONS = {"pdf"}

# Apply nest_asyncio to allow running asyncio in Flask
nest_asyncio.apply()


# Add custom nl2br filter
@app.template_filter("nl2br")
def nl2br_filter(text):
    if text is None:
        return ""
    return Markup(text.replace("\n", "<br>"))


# Helper function to check allowed file extensions
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
async def upload_and_analyze():
    # Check if both files were submitted
    if "file1" not in request.files or "file2" not in request.files:
        flash("Both files are required", "danger")
        return redirect(url_for("index"))

    file1 = request.files["file1"]
    file2 = request.files["file2"]

    # Check if filenames are empty
    if file1.filename == "" or file2.filename == "":
        flash("Both files must be selected", "danger")
        return redirect(url_for("index"))

    # Check if files are allowed types
    if not allowed_file(file1.filename) or not allowed_file(file2.filename):
        flash("Only PDF files are allowed", "danger")
        return redirect(url_for("index"))

    # Use a temporary directory that auto-cleans up
    with tempfile.TemporaryDirectory() as temp_dir:
        # Save files to the temporary directory
        file1_path = os.path.join(temp_dir, secure_filename(file1.filename))
        file2_path = os.path.join(temp_dir, secure_filename(file2.filename))
        file1.save(file1_path)
        file2.save(file2_path)

        try:
            # Create the extraction agent
            extract_agent = create_extract_agent()

            # Create the workflow with the agent
            workflow = AutomotiveSectorAnalysisWorkflow(
                agent=extract_agent,
                verbose=True,
                timeout=240,
            )

            # Run the workflow with the uploaded files
            result = await workflow.run(
                deck_path_a=file1_path,
                deck_path_b=file2_path,
            )

            # Get the final memo from the result
            final_memo = result["memo"]

            # Store filenames for display
            final_memo.company_a_name = file1.filename
            final_memo.company_b_name = file2.filename

            # Render the results
            return render_template(
                "results.html",
                memo=final_memo,
                company_a_name=file1.filename,
                company_b_name=file2.filename,
                currency="₹",
            )

        except Exception as e:
            logger.exception("Error during analysis")
            flash(f"Analysis failed: {str(e)}", "danger")
            return redirect(url_for("index"))


@app.route("/api/status")
def status():
    # This endpoint could be used to check analysis progress in a future implementation
    return jsonify({"status": "processing"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7001, debug=True)
