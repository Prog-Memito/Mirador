from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from functools import wraps

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"]='sqlite:///mirador.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=False

db = SQLAlchemy(app)

#  HACE SISTEMA DE AUTENTICACION

def requiere_autenticacion(f):
    @wraps(f)
    def decorator(*args,**kwargs):
        auth = request.authorization
        if not auth or auth.username !='ADMIN' or auth.password !='ADMIN':
            return jsonify({"mensaje":"Autenticacion requerida"}),401
        return f(*args,**kwargs)
    return decorator

# HACE QUE EL USUARIO SE TENGA QUE AUTENTICAR PARA USAR EL SISTEMA

@app.route('/api/auth', methods=['GET'])
def autenticar():
    auth = request.authorization
    if not auth or auth.username !='ADMIN' or auth.password !='ADMIN':
        return jsonify({"mensaje":"Autenticacion exitosa muyayo"}),401
    return jsonify({'mensaje': 'Credenciales correctas'}),401

# CREA LOS MODELOS

class Depto(db.Model):
    iddepto= db.Column(db.Integer, primary_key=True)
    pisos= db.Column(db.Integer, nullable=False)

class Owner(db.Model):
    idowner= db.Column(db.Integer, primary_key=True)
    o_nombre= db.Column(db.String(300), nullable=False)
    o_apellido= db.Column(db.String(300), nullable=False)
    iddepto= db.Column(db.Integer, db.ForeignKey('depto.iddepto'), nullable=False)

    # RELACIONA CON EL DEPARTAMENTO
    depto= db.relationship('Depto', backref='owners', lazy=True)

class Tenant(db.Model):
    idtenant= db.Column(db.Integer, primary_key=True)
    t_nombre= db.Column(db.String(300), nullable=False)
    t_apellido= db.Column(db.String(300), nullable=False)
    iddepto= db.Column(db.Integer, db.ForeignKey('depto.iddepto'), nullable=False)
    

    # RELACIONA CON EL DEPARTAMENTO
    depto= db.relationship('Depto', backref='tenants', lazy=True)

with app.app_context():
    db.create_all()

# SISTEMA CRUD DEPARTAMENTO

## CREA LOS DEPARTAMENTOS

@app.route('/api/depto', methods=['POST'])
@requiere_autenticacion
def crear_depto():
    datos = request.get_json()
    nuevo_dpto = Depto(
        pisos = int(datos['pisos'])
    )

    db.session.add(nuevo_dpto)
    db.session.commit()
    return jsonify({'mensaje': 'Departamento creado', 'id':nuevo_dpto.iddepto})

## LECTURA DE LOS DEPARTAMENTOS

@app.route('/api/depto', methods=['GET'])
@requiere_autenticacion
def obtener_deptos():
    deptos= Depto.query.all()
   
    resultado= [
        {'id':d.iddepto, 'pisos':d.pisos}
        for d in deptos
    ]
    return jsonify(resultado)

# LECTURA DE UN SOLO DEPARTAMENTO

@app.route('/api/depto/<int:id>', methods=['GET'])
@requiere_autenticacion
def obtener_depto(id):
    depto = Depto.query.get(id)
    if not depto:
        return jsonify({'mensaje': 'Departamento no encontrado'}),404
    return jsonify({
        'id': depto.iddepto,
        'pisos': depto.pisos
    })

# SISTEMA CRUD PROPIETARIO

## CREACION DE LOS PROPIETARIOS

@app.route('/api/owner', methods=['POST'])
@requiere_autenticacion
def crear_owner():
    datos = request.get_json()
    nuevo_owner = Owner(
        o_nombre = str(datos['o_nombre']),
        o_apellido = str(datos['o_apellido']),
        iddepto = int(datos['iddepto'])
    )

    db.session.add(nuevo_owner)
    db.session.commit()
    return jsonify({'mensaje': 'Propietario creado', 'id':nuevo_owner.idowner})

## LECTURA DE LOS PROPIETARIOS

@app.route('/api/owner', methods=['GET'])
@requiere_autenticacion
def obtener_owners():
    owners= Owner.query.all()

    resultado= [
        {'id':o.idowner, 'nombre':o.o_nombre, 'apellido':o.o_apellido, 'iddepto':o.iddepto}
        for o in owners
    ]
    return jsonify(resultado)

# LECTURA DE UN SOLO PROPIETARIO

@app.route('/api/owner/<int:id>', methods=['GET'])
@requiere_autenticacion
def obtener_owner(id):
    owner = Owner.query.get(id)
    if not owner:
        return jsonify({'mensaje': 'Propietario no encontrado'}),404
    return jsonify({
        'id': owner.idowner,
        'nombre': owner.o_nombre,
        'apellido': owner.o_apellido,
        'iddepto' : owner.iddepto
    })

## ACTUALIZA LOS PROPIETARIOS

@app.route('/api/owner/<int:id>', methods=['PUT'])
@requiere_autenticacion
def actualizar_owner(id):
    datos = request.get_json()
    owner = Owner.query.get(id)
    if not owner:
        return jsonify({'mensaje': 'Propietario no encontrado'}),404
    
    owner.o_nombre = datos.get('nombre', owner.o_nombre)
    owner.o_apellido = datos.get('apellido', owner.o_apellido)
    owner.iddepto = datos.get('iddepto', owner.iddepto)

    db.session.commit()
    return jsonify({'mensaje': 'Propietario modificado', 'id': owner.idowner})

## ELIMINA EL PROPIETARIO

@app.route('/api/owner/<int:id>', methods=['DELETE'])
@requiere_autenticacion
def eliminar_owner(id):
    owner = Owner.query.get(id)
    if not owner:
        return jsonify({'mensaje': 'Propietario no encontrado'}),404
    db.session.delete(owner)
    db.session.commit()
    return jsonify({'mensaje': 'ERAI'}),401


# SISTEMA CRUD ARRIENDATARIO

## CREACION DE LOS ARRIENDATARIOS

@app.route('/api/tenant', methods=['POST'])
@requiere_autenticacion
def crear_tenant():
    datos = request.get_json()
    nuevo_tenant = Tenant(
        t_nombre = str(datos['t_nombre']),
        t_apellido = str(datos['t_apellido']),
        iddepto = int(datos['iddepto'])
    )

    db.session.add(nuevo_tenant)
    db.session.commit()
    return jsonify({'mensaje': 'Arrendatario creado', 'id':nuevo_tenant.idtenant})

## LECTURA DE LOS ARRIENDATARIOS

@app.route('/api/tenant', methods=['GET'])
@requiere_autenticacion
def obtener_tenants():
    tenants= Tenant.query.all()

    resultado= [
        {'id':t.idtenant, 'nombre':t.t_nombre, 'apellido':t.t_apellido, 'iddepto':t.iddepto}
        for t in tenants
    ]
    return jsonify(resultado)

# LECTURA DE UN SOLO ARRIENDATARIO

@app.route('/api/tenant/<int:id>', methods=['GET'])
@requiere_autenticacion
def obtener_tenant(id):
    tenant = Tenant.query.get(id)
    if not tenant:
        return jsonify({'mensaje': 'Arriendatario no encontrado'}),404
    return jsonify({
        'id': tenant.idtenant,
        'nombre': tenant.t_nombre,
        'apellido': tenant.t_apellido,
        'iddepto' : tenant.iddepto
    })

## ACTUALIZA LOS ARRIENDATARIOS

@app.route('/api/tenant/<int:id>', methods=['PUT'])
@requiere_autenticacion
def actualizar_tenant(id):
    datos = request.get_json()
    tenant = Tenant.query.get(id)
    if not tenant:
        return jsonify({'mensaje': 'Arriendatario no encontrado'}),404
    
    tenant.t_nombre = datos.get('nombre', tenant.t_nombre)
    tenant.t_apellido = datos.get('apellido', tenant.t_apellido)
    tenant.iddepto = datos.get('iddepto', tenant.iddepto)

    db.session.commit()
    return jsonify({'mensaje': 'Arriendatario modificado', 'id': tenant.idtenant})

## ELIMINA EL ARRIENDATARIO

@app.route('/api/tenant/<int:id>', methods=['DELETE'])
@requiere_autenticacion
def eliminar_tenant(id):
    tenant = Tenant.query.get(id)
    if not tenant:
        return jsonify({'mensaje': 'Arriendatario no encontrado'}),404
    db.session.delete(tenant)
    db.session.commit()
    return jsonify({'mensaje': 'ERAI'}),401

## PERMITE EJECUTAR LA API

if __name__=='__main__':
    app.run(debug=True)