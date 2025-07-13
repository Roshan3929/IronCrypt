from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from main import run_full_analysis
from patch_fixer import execute_patch
from documentation_generator import generate_executive_summary, generate_technical_report
from patch_recommender import get_patch_recommendation, generate_ansible_playbook
import os
import werkzeug.utils
import traceback
import uuid
import threading
import subprocess
import json
from datetime import datetime
import yaml
from typing import Optional

app = Flask(__name__)
# Temporarily bypass CORS for development by allowing all origins
CORS(app, resources={r"/api/*": {"origins": "*"}})


# Define the path for uploaded files
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# In-memory store for patch job statuses
patch_jobs = {}
PATCH_LOGS_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'patch_logs')
if not os.path.exists(PATCH_LOGS_FOLDER):
    os.makedirs(PATCH_LOGS_FOLDER)

def run_ansible_playbook(patch_id: str, tag: Optional[str] = None):
    """
    Runs the ansible-playbook command in a background thread.
    Updates the job status and logs the output upon completion.
    """
    try:
        # Define the command
        command = ["ansible-playbook", "-i", "hosts", "patch.yml"]
        if tag:
            command.extend(["--tags", tag])
        
        # Start the subprocess
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Store process object to check status later
        patch_jobs[patch_id]['process'] = process
        
        # Wait for the process to complete
        stdout, stderr = process.communicate()
        
        # Update status based on return code
        status = "success" if process.returncode == 0 else "failure"
        patch_jobs[patch_id].update({
            "status": status,
            "stdout": stdout,
            "stderr": stderr,
        })

    except Exception as e:
        patch_jobs[patch_id].update({
            "status": "failure",
            "stderr": str(e),
        })
    
    # Log to file
    log_path = os.path.join(PATCH_LOGS_FOLDER, f"{patch_id}.json")
    with open(log_path, 'w') as f:
        json.dump({
            "patch_id": patch_id,
            "tag": tag,
            "status": patch_jobs[patch_id]["status"],
            "stdout": patch_jobs[patch_id].get("stdout", ""),
            "stderr": patch_jobs[patch_id].get("stderr", ""),
            "timestamp": datetime.now().isoformat()
        }, f, indent=4)


@app.route('/api/trigger-patch', methods=['POST'])
def trigger_patch():
    """
    Triggers an ansible playbook to apply a patch.
    Runs as a non-blocking background task.
    """
    req_data = request.get_json() or {}
    tag = req_data.get('tag')

    patch_id = str(uuid.uuid4())
    patch_jobs[patch_id] = {"status": "running"}

    # Run the playbook in a background thread
    thread = threading.Thread(target=run_ansible_playbook, args=(patch_id, tag))
    thread.daemon = True
    thread.start()

    return jsonify({"message": "Patching process started.", "patch_id": patch_id}), 202

@app.route('/api/patch-status/<string:patch_id>', methods=['GET'])
def patch_status(patch_id: str):
    """
    Returns the status of a specific patch job.
    """
    job = patch_jobs.get(patch_id)
    if not job:
        return jsonify({"error": "Patch ID not found."}), 404

    # If the process is still running, poll its status
    if job["status"] == "running":
         process = job.get('process')
         if process and process.poll() is None:
              return jsonify({"status": "running"})
         else:
            # The job finished since the last check, update the record
            # The run_ansible_playbook function will handle the final state update and logging
            # We can re-check the job status which should now be updated
            final_job_state = patch_jobs.get(patch_id, {})
            return jsonify(final_job_state)


    # Return the final state of the job
    return jsonify({
        "status": job.get("status"),
        "stdout": job.get("stdout"),
        "stderr": job.get("stderr"),
    })


@app.route('/api/patches', methods=['GET'])
def get_patches():
    """
    Parses the patch.yml file and returns a list of available patches (tasks).
    """
    try:
        with open('patch.yml', 'r') as f:
            playbook = yaml.safe_load(f)
        
        patches = []
        # Check if the playbook is not empty or malformed
        if playbook and isinstance(playbook, list):
            for play in playbook:
                # Ensure 'tasks' key exists and is a list
                if 'tasks' in play and isinstance(play['tasks'], list):
                    for task in play['tasks']:
                        # Ensure task is a dictionary with 'name' and 'tags'
                        if isinstance(task, dict) and 'name' in task and 'tags' in task:
                            patches.append({
                                "name": task['name'],
                                "tag": task['tags'][0] if task['tags'] else None
                            })
        return jsonify(patches)
    except FileNotFoundError:
        return jsonify({"error": "patch.yml not found"}), 404
    except Exception as e:
        return jsonify({"error": f"Error parsing playbook: {str(e)}"}), 500


@app.route('/api/generate-playbook', methods=['POST'])
def generate_playbook():
    """
    Generates a patch.yml file from vulnerability data.
    """
    vulnerability_data = request.get_json()
    if not vulnerability_data:
        return jsonify({"error": "Invalid vulnerability data"}), 400

    tasks = []
    for host_ip, host_data in vulnerability_data.items():
        for service in host_data.get('services', []):
            for vuln in service.get('vulnerabilities', []):
                package = vuln.get('package')
                fixed_version = vuln.get('fixed_version')

                if package and fixed_version:
                    task_name = f"Update {package} on {host_ip}"
                    tag = f"patch_{package.replace('.', '_')}_{host_ip.replace('.', '_')}"
                    
                    # --- PERMANENT FIX ---
                    # Changed the generated task to use the reliable `shell` module
                    # instead of the `apt` module, which was causing Python errors.
                    # Removed the unsupported 'args' parameter from the shell task.
                    tasks.append({
                        'name': task_name,
                        'shell': f"apt-get install -y --only-upgrade {package}",
                        'tags': [tag]
                    })

    playbook = [{
        'hosts': 'servers', 
        'become': True,
        'tasks': tasks
    }]

    try:
        # Re-enabled playbook saving.
        with open('patch.yml', 'w') as f:
            yaml.dump(playbook, f, default_flow_style=False)
        return jsonify({"message": "Playbook generated successfully."}), 200
    except Exception as e:
        return jsonify({"error": f"Error writing playbook: {str(e)}"}), 500


@app.route('/api/generate-ai-playbook', methods=['POST'])
def generate_ai_playbook_endpoint():
    """
    Generates an Ansible playbook and inventory using the AI, saves the inventory,
    and returns the playbook for user review.
    """
    vulnerability_data = request.get_json()
    if not vulnerability_data:
        return jsonify({"error": "Invalid vulnerability data"}), 400

    raw_content = generate_ansible_playbook(vulnerability_data)
    if raw_content.startswith("Error:"):
        return jsonify({"error": raw_content}), 500
    
    try:
        # Split the content into inventory and playbook
        if '# --- INVENTORY ---' not in raw_content or '# --- PLAYBOOK ---' not in raw_content:
            return jsonify({"error": "AI response did not follow the expected format with INVENTORY and PLAYBOOK markers."}), 500

        parts = raw_content.split('# --- PLAYBOOK ---')
        inventory_part = parts[0].replace('# --- INVENTORY ---', '').strip()
        playbook_part = parts[1].strip()

        # Save the inventory to the 'hosts' file
        with open('hosts', 'w') as f:
            f.write(inventory_part)
            
        return jsonify({"playbook": playbook_part})
    except Exception as e:
        return jsonify({"error": f"Failed to parse AI response or save inventory: {str(e)}"}), 500


@app.route('/api/save-playbook', methods=['POST'])
def save_playbook():
    """
    Saves the user-approved playbook content to patch.yml.
    """
    if not request.is_json:
        return jsonify({"error": "Invalid request: Content-Type must be application/json."}), 415

    req_data = request.get_json()
    
    if req_data is None:
        return jsonify({"error": "Invalid request: Malformed JSON."}), 400

    playbook_content = req_data.get('playbook')
    if not playbook_content:
        return jsonify({"error": "No playbook content provided in the 'playbook' key."}), 400
    
    try:
        # Validate that it's proper YAML before writing
        yaml.safe_load(playbook_content)
        with open('patch.yml', 'w') as f:
            f.write(playbook_content)
        return jsonify({"message": "Playbook saved successfully."}), 200
    except yaml.YAMLError:
        traceback.print_exc()
        return jsonify({"error": "Invalid YAML format in the provided playbook."}), 400
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"An unexpected error occurred while saving the playbook: {str(e)}"}), 500


@app.route('/api/logs', methods=['GET'])
def get_logs():
    """
    Returns a list of all available patch logs.
    """
    try:
        logs = [f for f in os.listdir(PATCH_LOGS_FOLDER) if f.endswith('.json')]
        return jsonify(logs)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/logs/<string:patch_id>', methods=['GET'])
def get_log_file(patch_id: str):
    """
    Serves a specific patch log file for download.
    """
    try:
        log_file = f"{patch_id}.json"
        log_path = os.path.join(PATCH_LOGS_FOLDER, log_file)
        if os.path.exists(log_path):
            return send_from_directory(PATCH_LOGS_FOLDER, log_file, as_attachment=True)
        else:
            return jsonify({"error": "Log file not found."}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/recommend-patch', methods=['POST'])
def recommend_patch():
    """
    API endpoint to get a patch recommendation for a single vulnerability.
    """
    try:
        req_data = request.get_json()
        if not req_data:
            return jsonify({"error": "Invalid input, JSON required"}), 400

        vulnerability_data = req_data.get('vulnerability')
        if not vulnerability_data:
            return jsonify({"error": "Missing vulnerability data"}), 400

        recommendation = get_patch_recommendation(vulnerability_data)
        if recommendation.startswith("Error:"):
            return jsonify({"error": recommendation}), 500

        return jsonify({"recommendation": recommendation})
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500


@app.route('/api/recommend-patch-with-context', methods=['POST'])
def recommend_patch_with_context():
    """
    API endpoint to get a patch recommendation, using the generated playbook as context.
    """
    try:
        req_data = request.get_json()
        if not req_data:
            return jsonify({"error": "Invalid input, JSON required"}), 400

        vulnerability_data = req_data.get('vulnerability')
        if not vulnerability_data:
            return jsonify({"error": "Missing vulnerability data"}), 400
        
        playbook_content = None
        try:
            with open('patch.yml', 'r') as f:
                playbook_content = f.read()
        except FileNotFoundError:
            # It's okay if the playbook doesn't exist yet, we can still get a recommendation.
            pass

        recommendation = get_patch_recommendation(vulnerability_data, playbook_content)
        if recommendation.startswith("Error:"):
            return jsonify({"error": recommendation}), 500

        return jsonify({"recommendation": recommendation})
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500


@app.route('/api/upload-and-analyze', methods=['POST'])
def upload_and_analyze():
    """
    API endpoint to upload an Nmap XML file and trigger the analysis.
    """
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    
    file = request.files['file']
    if not file or not file.filename:
        return jsonify({"error": "No file selected for uploading"}), 400

    if file.filename.endswith('.xml'):
        # Securely save the file
        filename = werkzeug.utils.secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        # Run the analysis on the uploaded file
        try:
            # The 'data' variable now holds the result of run_full_analysis
            data = run_full_analysis(filepath)

            # --- PERMANENT FIX ---
            # The following line is commented out to prevent our stable, working
            # patch.yml from being overwritten by the simple template generator
            # every time a file is uploaded.
            # await generate_playbook(data) 
            
            # Check if the analysis returned any data
            if not data or not any(host.get('services') for host in data.values()):
                return jsonify({"error": "Analysis returned no vulnerabilities."}), 400

            return jsonify(data)
        except Exception as e:
            # Log the exception e for debugging
            return jsonify({"error": f"An unexpected error occurred during analysis: {str(e)}"}), 500
    else:
        return jsonify({"error": "Invalid file type, please upload an XML file"}), 400

@app.route('/api/generate-documentation', methods=['POST'])
def generate_documentation():
    """
    API endpoint to generate documentation for a single vulnerability.
    """
    try:
        req_data = request.get_json()
        if not req_data:
            return jsonify({"error": "Invalid input, JSON required"}), 400

        vulnerability_data = req_data.get('vulnerability')
        report_type = req_data.get('reportType')

        if not vulnerability_data or not report_type:
            return jsonify({"error": "Missing vulnerability data or report type"}), 400

        if report_type == 'executive_summary':
            generated_text = generate_executive_summary(vulnerability_data)
        elif report_type == 'technical_report':
            generated_text = generate_technical_report(vulnerability_data)
        else:
            return jsonify({"error": "Invalid report type specified"}), 400

        if generated_text.startswith("Error:"):
             return jsonify({"error": generated_text}), 500

        return jsonify({"content": generated_text})
    except Exception as e:
        print("--- TRACEBACK START ---")
        traceback.print_exc()
        print("--- TRACEBACK END ---")
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500


@app.route('/api/apply-patch', methods=['POST'])
def apply_patch():
    """
    API endpoint to apply a patch to a host.
    """
    req_data = request.get_json()
    if not req_data:
        return jsonify({"error": "Invalid input, JSON required"}), 400

    ip = req_data.get('ip')
    username = req_data.get('username')
    private_key_path = req_data.get('private_key_path')
    patch_command = req_data.get('patch_command')

    if not all([ip, username, private_key_path, patch_command]):
        return jsonify({"error": "Missing required parameters"}), 400

    result = execute_patch(
        ip=ip,
        username=username,
        private_key_path=private_key_path,
        patch_command=patch_command
    )
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, port=5001) 