from flask import Flask, request, jsonify, render_template
import subprocess
import sys
import os
import tempfile
import json

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_sinhala', methods=['POST'])
def process_sinhala():
    """Process Sinhala input using the original si_to_sql.py script"""
    try:
        data = request.json
        sinhala = data.get('sinhala', '')
        division = data.get('division', 'Division_Not_Found')
        
        if not sinhala:
            return jsonify({'error': 'Sinhala text is required'}), 400
            
        # Create a temporary file to pass the Sinhala text
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', suffix='.txt', delete=False) as tmp_file:
            json.dump({'sinhala': sinhala, 'division': division}, tmp_file, ensure_ascii=False)
            tmp_filename = tmp_file.name
        
        try:
            # Path to Python 3.12 and the script
            python_path = r"C:\Users\Javindi Nethnika\AppData\Local\Programs\Python\Python312\python.exe"
            script_path = os.path.join(os.path.dirname(__file__), 'si_to_sql_wrapper.py')
            
            print(f"Processing: {sinhala} with division: {division}")  # Debug
            
            # Set environment for UTF-8 handling
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            
            # Run the wrapper script with temp file
            result = subprocess.run(
                [python_path, script_path, tmp_filename],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore',
                env=env
            )
            
            print(f"Return code: {result.returncode}")  # Debug
            print(f"STDOUT: {result.stdout}")  # Debug
            print(f"STDERR: {result.stderr}")  # Debug
            
            if result.returncode != 0:
                return jsonify({'error': f'Script execution failed: {result.stderr}'}), 500
                
            # Parse the output
            output_lines = result.stdout.strip().split('\n') if result.stdout else []
            
            # Extract information from output
            translation_line = ""
            entities_line = ""
            keywords_line = ""
            sql_line = ""
            
            for line in output_lines:
                if " --> " in line:
                    translation_line = line
                elif line.startswith("Entities:"):
                    entities_line = line
                elif line.startswith("Keywords:"):
                    keywords_line = line
                elif line.startswith("Generated SQL Query:"):
                    sql_line = line
                    
            return jsonify({
                'success': True,
                'translation': translation_line,
                'entities': entities_line,
                'keywords': keywords_line,
                'sql': sql_line,
                'full_output': result.stdout
            })
            
        finally:
            # Clean up temp file
            try:
                os.unlink(tmp_filename)
            except:
                pass
        
    except Exception as e:
        print(f"Exception: {str(e)}")  # Debug
        return jsonify({'error': f'Error processing request: {str(e)}'}), 500

if __name__ == '__main__':
    print("Starting Flask app...")
    app.run(debug=True, port=5001)
