from flask import Flask, render_template, request, redirect, url_for, flash
import matplotlib
matplotlib.use('Agg')  # Pour générer des images sans affichage interactif
import matplotlib.pyplot as plt
import os
from database import init_db, ajouter_personne, get_tous_en_poste, supprimer_personne, get_stats_par_region

app = Flask(__name__)
app.secret_key = "votre_cle_secrete_123"  # Pour les messages flash

# Initialisation de la base au démarrage
init_db()

@app.route('/')
def index():
    personnel = get_tous_en_poste()
    return render_template('index.html', personnel=personnel)

@app.route('/ajouter', methods=['POST'])
def ajouter():
    matricule = request.form['matricule'].strip()
    nom = request.form['nom'].strip()
    prenom = request.form['prenom'].strip()
    fonction = request.form['fonction']
    region = request.form['region']
    etablissement = request.form['etablissement'].strip()
    
    if not all([matricule, nom, prenom, fonction, region, etablissement]):
        flash("Tous les champs sont obligatoires !")
        return redirect(url_for('index'))
    
    success = ajouter_personne(matricule, nom, prenom, fonction, region, etablissement)
    if success:
        flash(f"Personne ajoutée avec succès (matricule {matricule})")
    else:
        flash("Erreur : ce matricule existe déjà !")
    
    return redirect(url_for('index'))

@app.route('/supprimer/<matricule>')
def supprimer(matricule):
    supprimer_personne(matricule)
    flash(f"Personne avec matricule {matricule} supprimée.")
    return redirect(url_for('index'))

@app.route('/stats')
def stats():
    stats_data, regions = get_stats_par_region()
    
    # Génération du graphique à barres
    totals = [stats_data[reg]["total"] for reg in regions]
    plt.figure(figsize=(10, 6))
    bars = plt.bar(regions, totals, color='red')
    plt.title("Effectifs des personnels en poste par région", fontsize=14)
    plt.xlabel("Région", fontsize=12)
    plt.ylabel("Nombre de personnes", fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    # Sauvegarde de l'image dans static/
    if not os.path.exists('static'):
        os.makedirs('static')
    graph_path = 'static/effectifs_region.png'
    plt.savefig(graph_path)
    plt.close()
    
    return render_template('stats.html', stats=stats_data, regions=regions, graph_path=graph_path)

