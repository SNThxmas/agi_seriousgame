#!/usr/bin/python3
# -*- coding: utf-8 -*-

#*#####################################
#*#           PY THINGS               #
#*#####################################

#* Importing the libraries
from flask import Flask, url_for, request, render_template, redirect, abort
from python_custom import dbrequests
from datetime import datetime

#* Create app and reset JSON
app = Flask(__name__)
app.config['SECRET_KEY'] = '081124f41f7be1efebdc288330e3e179d62d8494b2885301'

# AUTOMODE automatically orders to LOG when CLI order
# If False, LEAN has to order to LOG manually
AUTOMODE = True


#*#####################################
#*#           PURE HTML               #
#*#####################################

#* Root page
@app.route('/')
def index():
    return render_template('accueil.html')

#* 404 page
@app.errorhandler(404)
def page_not_found(error):
    return render_template('error.html', errno=404, errmsg="La page demandée n'existe pas...", special = True), 404

#* 500 page
@app.errorhandler(500)
def internal_server_error(error):
    return render_template('error.html', errno=500, errmsg="Erreur interne...", special = False), 500

#*Client page
@app.route('/espace-client')
def client():
    commandes = dbrequests.read_DB("SELECT * FROM commandes_client_lean")
    return render_template('espace-client.html', commandes = commandes)

#* Agilog page
@app.route('/agilog')
def agilog():
    stocklist = dbrequests.read_DB("SELECT * FROM agilog_inventaire")
    commandes_agilean = dbrequests.read_DB("SELECT * FROM commandes_client_lean")

    return render_template('agilog.html', stocklist = stocklist, commandes_kit = commandes_agilean)

#* Agilean page
@app.route('/agilean')
def agilean():
    commandes_client_lean = dbrequests.read_DB("SELECT * FROM commandes_client_lean")
    commandes_lean_log = dbrequests.read_DB("SELECT * FROM commandes_lean_log")

    #? Format: N°, Date, Modele, Options, Etat
    return render_template('agilean.html', commandes_cl = commandes_client_lean, commandes_ll = commandes_lean_log)

@app.route('/test')
def validate():
    return render_template('validated.html')
#*#####################################
#*#             FORMS                 #
#*#####################################

#?######################### Client form
@app.route('/cli_commande', methods=['POST'])
def cli_commande():
    form = request.form
    modele = form['modele']
    option = ""

    try:
        form['antenne']
        option += "Antenne "
    except KeyError:
        pass

    try:
        form['attache']
        option += "Attache "
    except KeyError:
        pass

    try:
        form['attelage']
        option += "Attelage"
    except KeyError:
        pass

    date = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
    etat = "En attente"

    try:
        dbrequests.write_DB("INSERT INTO commandes_client_lean (date_cmde, modele, option, etat) VALUES (?,?,?,?)" , (date, modele, option, etat))
    except:
        print("Erreur d'insertion dans la BDD")
        abort(500)
    
    if AUTOMODE:
        pieces = "2 B2*2, 2 MY, 4 JT, 4 PN, 1 PL2*2, 1 P2*4, 1 P1*2, 1 GR, 1 RA, 2 FV, 1 P1*4, 2 FR, 2 GB, 1 P2*4, 1 P1*4, 2 P1*3, 1 PB, 1 AT, 1 VL, 1 SG"
        if modele == "CCO":
            pieces += ", 1 P2*8, 2 P1*6, 1 AC"
        elif modele == "CCF":
            pieces += ", 1 P2*8, 4 FN, 1 P4*4, 1 P1*4, 2 P1*6"
        elif modele == "CLO":
            pieces += ", 2 P1*3, 1 P4*4, 1 P2*12, 4 FN, 1 P4*4, 1 P1*4, 2 P1*4, 2 P1*1, 2 P1*6, 2 P1*4, 1 EQ"
        elif modele == "CLF":
            pieces += ", 2 P1*3, 1 P4*4, 1 P2*12, 4 FN, 1 P4*4, 1 P1*4, 2 P1*4, 2 P1*1, 2 P1*6, 2 P1*4, 1 EQ, 1 TT, 1 B2*4, 1 B1*4"
        else:
            print("Erreur de modele")
            abort(500)
        
        if "Antenne" in option:
            pieces += ", 1 Antenne"
        if "Attache" in option:
            pieces += ", 1 Attache"
        if "Attelage" in option:
            pieces += ", 1 Crochet_attelage"

        try:
            dbrequests.write_DB("INSERT INTO commandes_lean_log VALUES (?, ?, ?, 'En cours')", (None, date, pieces))
        except:
            print("Erreur d'insertion dans la BDD")
            abort(500)

    return render_template('validated.html')

@app.route('/cli_state', methods=['POST'])
def cli_state():
    form = request.form
    num_cmd = form['num_cmd']
    state = form['statut']

    #try:
    dbrequests.write_DB("UPDATE commandes_client_lean SET etat = ? WHERE numero_cmde = ?", (state, num_cmd))
    #except:
    #    print("Erreur d'insertion dans la BDD")
    #    abort(500)

    return render_template('validated.html')

#?######################## Agilean form
@app.route('/lean_cslean', methods=['POST'])
def agilean_changestate():
    result = request.form
    num_cmd = result['num_cmd']
    state = result['statut']

    try:
        dbrequests.write_DB("UPDATE commandes_client_lean SET etat = ? WHERE numero_cmde = ?", (state, num_cmd))
    except:
        print("Erreur d'insertion dans la BDD")
        abort(500)

    return render_template('validated.html')

@app.route('/lean_clog', methods=['POST'])
def cde_agilog():
    form = request.form
    modele = form['modele']
    option = ""

    try:
        form['antenne']
        option += "Antenne "
    except KeyError:
        pass

    try:
        form['attache']
        option += "Attache "
    except KeyError:
        pass

    try:
        form['attelage']
        option += "Attelage"
    except KeyError:
        pass


    date = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")

    # Get the column "qte_CCO" and "code_article" together
    # qte_CCO = dbrequests.read_DB("SELECT qte_CCO, code_article FROM piecesparposte", ())
    # qte_CCF = dbrequests.read_DB("SELECT qte_CCF, code_article FROM piecesparposte", ())
    # qte_CLO = dbrequests.read_DB("SELECT qte_CLO, code_article FROM piecesparposte", ())
    # qte_CLF = dbrequests.read_DB("SELECT qte_CLF, code_article FROM piecesparposte", ())
    # 
    # Add options x1
    # Create str with "qte1 [ ] code1 [,] qte2 [ ] code2 [,] ..."
    #? Split "," to get the list of pieces
    #? Then strip and split " " to get the number of pieces
    pieces = "2 B2*2, 2 MY, 4 JT, 4 PN, 1 PL2*2, 1 P2*4, 1 P1*2, 1 GR, 1 RA, 2 FV, 1 P1*4, 2 FR, 2 GB, 1 P2*4, 1 P1*4, 2 P1*3, 1 PB, 1 AT, 1 VL, 1 SG"
    if modele == "CCO":
        pieces += ", 1 P2*8, 2 P1*6, 1 AC"
    elif modele == "CCF":
        pieces += ", 1 P2*8, 4 FN, 1 P4*4, 1 P1*4, 2 P1*6"
    elif modele == "CLO":
        pieces += ", 2 P1*3, 1 P4*4, 1 P2*12, 4 FN, 1 P4*4, 1 P1*4, 2 P1*4, 2 P1*1, 2 P1*6, 2 P1*4, 1 EQ"
    elif modele == "CLF":
        pieces += ", 2 P1*3, 1 P4*4, 1 P2*12, 4 FN, 1 P4*4, 1 P1*4, 2 P1*4, 2 P1*1, 2 P1*6, 2 P1*4, 1 EQ, 1 TT, 1 B2*4, 1 B1*4"
    else:
        print("Erreur de modele")
        abort(500)
    
    if "antenne" in option:
        pieces += ", 1 Antenne"
    elif "attache" in option:
        pieces += ", 1 Attache"
    elif "attelage" in option:
        pieces += ", 1 Crochet_attelage"
    else:
        pass

    try:
        dbrequests.write_DB("INSERT INTO commandes_lean_log VALUES (?, ?, ?, 'En cours')", (None, date, pieces))
    except:
        print("Erreur d'insertion dans la BDD")
        abort(500)

    return render_template('validated.html')

@app.route('/lean_csleanlog', methods=['POST'])
def lean_csleanlog():
    result = request.form
    num_cmd = result['num_cmd']
    statut = result['statut']

    try:
        dbrequests.write_DB("UPDATE commandes_lean_log SET etat = ? WHERE id_cmde = ?", (statut, num_cmd))
    except:
        print("Erreur d'insertion dans la BDD")
        abort(500)
    
    return render_template('validated.html')

#?######################### Agilog form
@app.route('/log_csstock', methods=['POST'])
def agilog_changestate_stock():
    result = request.form
    id_part = result['id_part']
    qte = result['quantity']
    
    old_qte = dbrequests.readone_DB("SELECT stock_log FROM agilog_inventaire WHERE id_piece LIKE " + "'%" + id_part + "%'", ())
    #try:
    dbrequests.write_DB("UPDATE agilog_inventaire SET stock_log = "+str(int(qte) + int(old_qte))+"  WHERE id_piece LIKE " + "'%" + id_part + "%'", ())
    #except:
    #    print("SQLITE ROW -> INT")
    #    abort(500)
    
    return render_template('validated.html')

if __name__ == '__main__':
    app.run(debug=True, port=5959)