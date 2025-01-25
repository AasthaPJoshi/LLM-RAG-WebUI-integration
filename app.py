from flask import Flask, render_template, jsonify, request

app = Flask(__name__)
regular_history = []
rag_history = []
mode = "regular"

@app.route('/')
def index():
    return render_template('index.html', mode=mode)

@app.route('/history', methods=['GET', 'POST'])
def get_history():
    global regular_history, rag_history
    if request.method == 'POST':
        if mode == 'regular':
            regular_history = request.json
        elif mode == 'RAG':
            rag_history = request.json
    if mode == 'regular':
        return jsonify(regular_history)
    elif mode == 'RAG':
        return jsonify(rag_history)

@app.route('/full_history')
def full_history():
    return jsonify({'regular': regular_history, 'RAG': rag_history})

@app.route('/mode', methods=['POST', 'GET'])
def set_mode():
    global mode
    if request.method == 'POST':
        mode = request.json.get('mode', 'regular')
    return jsonify({'mode': mode})

if __name__ == "__main__":
    app.run(debug=True)
