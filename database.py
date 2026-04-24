import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "personnel.db")


def init_db():
    """Crée la table si elle n'existe pas."""
    conn = os.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS personnel (
            matricule TEXT PRIMARY KEY,
            nom TEXT NOT NULL,
            prenom TEXT NOT NULL,
            fonction TEXT NOT NULL,
            region TEXT NOT NULL,
            etablissement TEXT NOT NULL,
            en_poste INTEGER DEFAULT 1
        )
    ''')
    conn.commit()
    conn.close()

def ajouter_personne(matricule, nom, prenom, fonction, region, etablissement):
    """Ajoute une nouvelle personne (en poste par défaut)."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO personnel (matricule, nom, prenom, fonction, region, etablissement, matiere_enseignez, en_poste)
            VALUES (?, ?, ?, ?, ?, ?, 1)
        ''', (matricule, nom, prenom, fonction, region, etablissement))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # Matricule déjà existant
    finally:
        conn.close()

def get_tous_en_poste():
    """Retourne la liste des personnes encore en poste (en_poste = 1)."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT matricule, nom, prenom, fonction, region, etablissement FROM personnel WHERE en_poste = 1 ORDER BY region, nom")
    data = cursor.fetchall()
    conn.close()
    return data

def supprimer_personne(matricule):
    """Supprime définitivement une fiche (ou passe en_poste à 0). On choisit suppression réelle."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM personnel WHERE matricule = ?", (matricule,))
    conn.commit()
    conn.close()

def get_stats_par_region():
    """
    Retourne un dictionnaire {region: {'total': int, 'professeur': int, 'proviseur': int, ...}}
    et la liste des régions.
    """
    regions = [
        "Adamaoua", "Centre", "Est", "Extrême-Nord", "Littoral",
        "Nord", "Nord-Ouest", "Ouest", "Sud", "Sud-Ouest"
    ]
    fonctions = ["professeur", "proviseur", "principal", "directeur de CES", "vacataires"]
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    stats = {}
    for reg in regions:
        stats[reg] = {"total": 0, "professeur":0, "proviseur":0, "principal":0, "directeur de CES":0, "vacataires":0}
        for f in fonctions:
            cursor.execute('''
                SELECT COUNT(*) FROM personnel
                WHERE region = ? AND fonction = ? AND en_poste = 1
            ''', (reg, f))
            count = cursor.fetchone()[0]
            stats[reg][f] = count
            stats[reg]["total"] += count
    
    conn.close()
    return stats, regions