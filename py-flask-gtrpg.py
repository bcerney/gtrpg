from app import create_app, db
from app.models import User, Category, Task, UserCategory

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Category': Category, 'Task': Task, 'UserCategory': UserCategory}