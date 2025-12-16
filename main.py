from flask import Flask, request, jsonify, render_template, session, send_from_directory
from agent import run_agent, clear_conversation
import logging
from datetime import timedelta
import secrets
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder="web", static_folder="web", static_url_path='')
app.secret_key = secrets.token_hex(32)
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

@app.route("/")
def home():
    """Serve the main chat interface."""
    return render_template("index.html")

@app.route("/style.css")
def serve_css():
    """Serve the CSS file."""
    return send_from_directory('web', 'style.css')

@app.route("/chat", methods=["POST"])
def chat():
    """Handle chat messages with conversation memory."""
    try:
        data = request.get_json()
        
        if not data or "message" not in data:
            return jsonify({"error": "No message provided"}), 400
        
        user_message = data.get("message", "").strip()
        
        if not user_message:
            return jsonify({"error": "Message cannot be empty"}), 400
        
        if len(user_message) > 2000:
            return jsonify({"error": "Message too long (max 2000 characters)"}), 400
        
        # Get or create session ID for conversation tracking
        if 'session_id' not in session:
            session['session_id'] = secrets.token_hex(16)
            session.permanent = True
        
        session_id = session['session_id']
        
        # Process message with conversation memory
        response = run_agent(user_message, session_id)
        
        return jsonify({
            "response": response,
            "session_id": session_id
        })
    
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}", exc_info=True)
        return jsonify({"error": "An error occurred processing your request"}), 500

@app.route("/clear", methods=["POST"])
def clear():
    """Clear conversation history for the current session."""
    try:
        if 'session_id' in session:
            session_id = session['session_id']
            clear_conversation(session_id)
            logger.info(f"Cleared conversation for session: {session_id}")
        
        return jsonify({"status": "success", "message": "Conversation cleared"})
    
    except Exception as e:
        logger.error(f"Error clearing conversation: {str(e)}")
        return jsonify({"error": "Failed to clear conversation"}), 500

@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy"}), 200

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def server_error(e):
    logger.error(f"Internal server error: {str(e)}")
    return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)