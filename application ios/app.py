from flask import Flask, request, redirect, render_template, send_from_directory, flash
import os
import requests

# Configuration
app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'secret_key'  # Nécessaire pour utiliser flash messages

# Types de fichiers autorisés
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'mov', 'avi', 'mkv'}

# Webhook Discord
DISCORD_WEBHOOK_URL = 'https://discord.com/api/webhooks/1323023095212015668/XXhvRjV4U4LwDYiEZAQ3rHMx6OntFD7zQ7Hx4b0rPNkYX7j7YjRAUSvuYwaHKG_5NhqA'  # Remplacez par votre URL de webhook

def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def send_to_discord(filepath, filename):
    """Envoie un fichier au webhook Discord."""
    with open(filepath, 'rb') as file:
        response = requests.post(
            DISCORD_WEBHOOK_URL,
            files={'file': (filename, file)},
            data={'content': f"📁 Nouveau fichier téléchargé : {filename}"}
        )
    if response.status_code == 204:
        print(f"Fichier {filename} envoyé à Discord avec succès.")
    else:
        print(f"Échec de l'envoi du fichier {filename} à Discord : {response.status_code}, {response.text}")

# Page d'accueil
@app.route('/')
def home():
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('index.html', files=files)

# Téléchargement de fichiers
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('Aucun fichier sélectionné.')
        return redirect('/')
    file = request.files['file']
    if file.filename == '':
        flash('Nom de fichier vide.')
        return redirect('/')
    if allowed_file(file.filename, ALLOWED_IMAGE_EXTENSIONS) or allowed_file(file.filename, ALLOWED_VIDEO_EXTENSIONS):
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        send_to_discord(filepath, file.filename)  # Envoi au webhook Discord
        flash(f"Fichier {file.filename} téléchargé avec succès.")
    else:
        flash("Type de fichier non autorisé.")
    return redirect('/')

# Supprimer un fichier
@app.route('/delete/<filename>', methods=['POST'])
def delete_file(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        flash(f"Fichier {filename} supprimé avec succès.")
    else:
        flash("Le fichier n'existe pas.")
    return redirect('/')

# Servir les fichiers téléchargés
@app.route('/files/<filename>')
def get_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Lancer le serveur
if __name__ == '__main__':
    app.run(debug=True)
