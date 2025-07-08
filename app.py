# app.py
# Author: [Your Name/Handle Here]
# WAF-SMASHER v2.0 - A Server-Side Template Injection (SSTI) CTF Challenge

import os
import re
import logging
from pathlib import Path
from flask import (Flask, request, render_template, render_template_string,
                   redirect, url_for, session, jsonify, abort)

# --- App Configuration & Initialization ---
app = Flask(__name__)

# IMPORTANT: For production/GitHub, set this key as an environment variable.
# For local testing, a hardcoded key is fine.
# Example: export SECRET_KEY='some_truly_random_string'
app.secret_key = os.environ.get('SECRET_KEY', 'd0nt_l34k_th1s_s3cr3t_k3y_for_t3st1ng_!@#')
app.config['FLAG'] = os.environ.get('FLAG', 'NULL{d1n0s4ur_w4f_g0t_pwnd_by_futur3_h4ckz}')

# --- Logging Configuration ---
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] - %(message)s')

# --- Global Challenge State ---
FLAG = app.config['FLAG']

def initialize_decoy_flag():
    """Creates a decoy flag file to act as a red herring for players."""
    flag_path = Path(__file__).parent / ".decoy_flag.txt"
    if not flag_path.exists():
        logging.info(f"Decoy flag file not found. Creating at {flag_path}")
        with open(flag_path, "w") as f:
            f.write("D3C0Y{this_is_a_trap!}")
initialize_decoy_flag()


# --- Web Application Firewall (WAF) Definitions ---

def waf_stage3(payload: str) -> bool:
    """Blocks common object traversal and OS command execution terms."""
    blacklist = ['__class__', '__subclasses__', 'config', 'os', 'self', 'request', 'mro', 'popen', 'system']
    return not any(bad in payload.lower() for bad in blacklist)

def waf_stage4(payload: str) -> bool:
    """Blocks nearly all useful Jinja2 globals and builtins by name."""
    blacklist = ['__class__', '__mro__', '__subclasses__', '__init__', '__globals__',
                 '__builtins__', '__import__', 'os', 'popen', 'system', 'open']
    return not any(bad in payload.lower() for bad in blacklist)


# --- Stage Validation Logic ---

def validate_stage1(payload: str):
    """Stage 1: Basic Template Execution"""
    is_correct = payload.strip() == "{{7*7}}"
    if is_correct:
        message = "Access Granted. Calculation correct. Target system is vulnerable to basic expressions."
    else:
        message = "Access Denied. Incorrect calculation."
    return is_correct, message

def validate_stage2(payload: str):
    """Stage 2: In-Memory Object Discovery vs. File System Trap"""
    # The hint pushes players to read the decoy flag, which will fail validation.
    # The correct path is discovering how to read the app's in-memory config.
    rendered = render_template_string(payload)
    is_correct = FLAG in rendered
    message = "Success! The real flag wasn't in a file, it was in memory. Good work."
    return is_correct, message

def validate_stage3(payload: str):
    """Stage 3: Bypassing Name-Based Blacklists"""
    rendered = render_template_string(payload)
    is_correct = FLAG in rendered
    message = 'WAF Bypassed. Flag captured.<br><br>// Recovered developer log fragment:<br>// "Note to self: `request.args` can be used to bypass string-based WAFs. Need to patch this..."'
    return is_correct, message

def validate_stage4(payload: str):
    """Stage 4: Ultimate WAF Bypass"""
    # This regex ensures the player is submitting a Jinja2 expression,
    # preventing them from just pasting the flag as the payload.
    if not re.search(r'\{\{.*\}\}', payload):
         return False, "Payload ineffective. A valid Jinja2 expression is required."
    
    rendered = render_template_string(payload)
    is_correct = FLAG in rendered
    message = f"System Compromised. You are the WAF-Smasher!<br><br><b>Output:</b><pre>{rendered}</pre>"
    return is_correct, message

# --- Stage Definitions Dictionary ---
# Central place to manage all stage data.
STAGES = {
    1: {"title": "Initial Breach", "hint": "The system trusts basic computations. How much is 7 times 7 in template form?", "validator": validate_stage1, "waf": None},
    2: {"title": "The Decoy", "hint": "Our intel says a flag file `.decoy_flag.txt` exists. Can you read it? Or is the real flag stored somewhere safer... like in the application's memory?", "validator": validate_stage2, "waf": None},
    3: {"title": "Restricted Environment", "hint": "The WAF now blocks direct access to `config`, `self`, and `request`. Find an alternate object to pivot from to reach the app's configuration.", "validator": validate_stage3, "waf": waf_stage3},
    4: {"title": "Forbidden Arts", "hint": "The WAF is god-tier, blocking `__globals__`, `__builtins__`, etc. It only inspects the payload in the form body. Use the dev log from Stage 3 to smuggle forbidden strings past the guards.", "validator": validate_stage4, "waf": waf_stage4}
}


# --- HTTP Routes and Views ---

@app.after_request
def add_security_headers(response):
    """Add basic security headers to every response."""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    return response

@app.errorhandler(404)
def page_not_found(e):
    """Custom 404 handler."""
    return render_template('404.html'), 404

@app.route('/')
def index():
    """Serves the main homepage showing stage progress."""
    progress = session.get("progress", 0)
    return render_template("index.html", progress=progress, total_stages=len(STAGES))

@app.route('/stage/<int:stage_num>', methods=['GET', 'POST'])
def stage_view(stage_num):
    """Serves individual stage pages and handles the final flag submission on Stage 4."""
    if stage_num not in STAGES:
        abort(404)
    
    progress = session.get("progress", 0)
    if stage_num > progress + 1:
        return redirect(url_for('index'))

    final_message = None
    # Handle the final flag submission form, which only exists on Stage 4.
    if stage_num == 4 and request.method == 'POST' and 'flag' in request.form:
        submitted_flag = request.form.get('flag', '').strip()
        if submitted_flag == FLAG:
            if progress < len(STAGES):
                session['progress'] = len(STAGES)
            final_message = {
                "text": "[SYSTEM_OVERRIDE_ACCEPTED] Dominance achieved. <a href='/reset'>[REBOOT_SYSTEM]</a>",
                "class": "success"
            }
        else:
            final_message = {"text": "[ACCESS_DENIED] Incorrect flag signature.", "class": "error"}
    
    return render_template("stage.html", 
                           stage_info=STAGES[stage_num], 
                           stage_num=stage_num,
                           final_message=final_message,
                           total_stages=len(STAGES))

@app.route('/submit/<int:stage_num>', methods=["POST"])
def submit_payload(stage_num):
    """API endpoint to handle SSTI payload submissions for each stage."""
    if stage_num not in STAGES:
        return jsonify({"success": False, "message": "Error: Invalid stage."}), 404
    
    current_stage = STAGES[stage_num]
    progress = session.get("progress", 0)
    if stage_num > progress + 1:
        return jsonify({"success": False, "message": "Error: Stage not unlocked."}), 403
    
    payload = request.form.get("payload", "")
    if not payload:
        return jsonify({"success": False, "message": "Error: No payload provided."}), 400
    
    if not current_stage["waf"](payload) if current_stage["waf"] else False:
        return jsonify({"success": False, "message": ">> [WAF] THREAT DETECTED. PAYLOAD NEUTRALIZED."})
    
    try:
        is_correct, message = current_stage["validator"](payload)
        if is_correct:
            if stage_num > progress: session["progress"] = stage_num
            return jsonify({"success": True, "message": f">> [SUCCESS] {message}", "unlocked": stage_num})
        else:
            return jsonify({"success": False, "message": f">> [FAILURE] {message}"})
    except Exception as e:
        logging.error(f"Stage {stage_num} error with payload '{payload}': {e}")
        return jsonify({"success": False, "message": f">> [EXCEPTION] An unexpected error occurred: {e}"})

@app.route('/reset')
def reset_progress():
    """Clears the user's session and restarts the challenge."""
    session.clear()
    return redirect(url_for('index'))

# --- Main Application Runner ---
if __name__ == '__main__':
    # The 'debug=True' mode is great for development but should be
    # turned off for a real production deployment.
    app.run(host='0.0.0.0', port=5000, debug=True)
