from flask import Blueprint, render_template_string

bp = Blueprint("hobbies", __name__)

@bp.get("/")
def index():
    return render_template_string("""
    {% extends 'base.html' %}
    {% block content %}
    <h2>Hobbies</h2>
    <p>v0 placeholder. Projects & sessions.</p>
    {% endblock %}
    """)
