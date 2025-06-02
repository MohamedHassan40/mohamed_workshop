from flask import Flask, render_template, request, redirect, url_for, session
import json


# Make `data` available in all templates
import re
app = Flask(
    __name__,
    template_folder="website/templates",     # 👈 Add this
    static_folder="website/static"           # 👈 Optional, if you use static files
)
app.secret_key = "aodsiasdioaosd"

with open('website/data/questions.json', encoding='utf-8') as f:
    data = json.load(f)


def clean_surrogates(obj):
    if isinstance(obj, dict):
        return {k: clean_surrogates(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_surrogates(i) for i in obj]
    elif isinstance(obj, str):
        return re.sub(r'[\ud800-\udfff]', '', obj)  # Remove surrogate characters
    return obj

@app.context_processor
def inject_data():
    return dict(data=clean_surrogates(data))


# JSON data structure (as before)

@app.route('/')
def index():
    session.clear()
    return render_template('index.html', intro=data['intro'])

@app.route('/phase/<int:phase_index>', methods=['GET', 'POST'])
def phase(phase_index):
    phases = data['phases']
    if phase_index < 0 or phase_index >= len(phases):
        return redirect(url_for('index'))

    phase = phases[phase_index]

    if request.method == 'POST':
        correct_count = 0
        total_questions = len(phase['questions'])

        # Loop through each question index
        for i, q in enumerate(phase['questions']):
            key_name = f"phase{phase_index}_q{i}"
            selected = request.form.get(key_name)
            if selected == q['correct']:
                correct_count += 1

        # Store phase score in session
        if 'scores' not in session:
            session['scores'] = {}
        session['scores'][phase['id']] = correct_count

        return render_template(
            'feedback.html',
            phase_index=phase_index,
            phase=phase,
            correct_count=correct_count,
            total_questions=total_questions,
            total_phases=len(phases)
        )

    return render_template(
        'phase.html',
        phase_index=phase_index,
        phase=phase,
        total_phases=len(phases)
    )

@app.route('/final')
def final():
    if 'scores' not in session:
        return redirect(url_for('index'))

    total_score = sum(session['scores'].values())
    total_questions = sum(len(p['questions']) for p in data['phases'])
    return render_template('final.html', total_score=total_score, total_questions=total_questions)
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)

