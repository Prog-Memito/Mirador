from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
from functools import wraps
from datetime import datetime

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

    # RELACIONA CON LA TABLA DEPARTAMENTO
    depto= db.relationship('Depto', backref='owners', lazy=True)

class Tenant(db.Model):
    idtenant= db.Column(db.Integer, primary_key=True)
    t_nombre= db.Column(db.String(300), nullable=False)
    t_apellido= db.Column(db.String(300), nullable=False)
    iddepto= db.Column(db.Integer, db.ForeignKey('depto.iddepto'), nullable=False)
    

    # RELACIONA CON LA TABLA DEPARTAMENTO
    depto= db.relationship('Depto', backref='tenants', lazy=True)

class Staff(db.Model):
    idstaff= db.Column(db.Integer, primary_key=True)
    s_nombre= db.Column(db.String(300), nullable=False)
    s_apellido= db.Column(db.String(300), nullable=False)
    funcion= db.Column(db.String(300), nullable=False)

class Gastos_Comunes(db.Model):
    idgc= db.Column(db.Integer, primary_key=True)
    iddepto= db.Column(db.Integer, db.ForeignKey('depto.iddepto'), nullable=False)
    anio= db.Column(db.Integer)
    mes= db.Column(db.Integer)
    fechap= db.Column(db.String(10), nullable=False)
    valor= db.Column(db.Integer, nullable=False)
    pagado= db.Column(db.String(2), nullable=False)

    # RELACIONA CON LA TABLA DEPARTAMENTO
    depto= db.relationship('Depto', backref='gcomunes', lazy=True)

    # VALIDA QUE EN LA COLUMNA PAGADO SOLAMENTE ADMITA SI O NO
    @validates('pagado')
    def validate_pagado(self, key, value):
        if not isinstance(value, str):
            raise ValueError("El campo 'pagado' debe ser un string.")
        value = value.strip().upper()
        if value not in ['SI', 'NO']:
            raise ValueError("El campo 'pagado' solo puede tener los valores 'SI' o 'NO'.")
        return value

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

# SISTEMA CRUD PERSONAL

## CREACION DE LOS PERSONAL

@app.route('/api/staff', methods=['POST'])
@requiere_autenticacion
def crear_staff():
    datos = request.get_json()
    nuevo_staff = Staff(
        s_nombre = str(datos['nombre']),
        s_apellido = str(datos['apellido']),
        funcion = int(datos['funcion'])
    )

    db.session.add(nuevo_staff)
    db.session.commit()
    return jsonify({'mensaje': 'Personal creado', 'id':nuevo_staff.idstaff})

## LECTURA DE LOS PERSONAL

@app.route('/api/staff', methods=['GET'])
@requiere_autenticacion
def obtener_staffs():
    staffs= Staff.query.all()

    resultado= [
        {'id':s.itstaff, 'nombre':s.s_nombre, 'apellido':s.s_apellido, 'funcion':s.funcion}
        for s in staffs
    ]
    return jsonify(resultado)

# LECTURA DE UN SOLO PERSONAL

@app.route('/api/staff/<int:id>', methods=['GET'])
@requiere_autenticacion
def obtener_staff(id):
    staff = Staff.query.get(id)
    if not staff:
        return jsonify({'mensaje': 'Personal no encontrado'}),404
    return jsonify({
        'id': staff.idstaff,
        'nombre': staff.s_nombre,
        'apellido': staff.s_apellido,
        'funcion' : staff.funcion
    })

## ACTUALIZA LOS PERSONAL

@app.route('/api/staff/<int:id>', methods=['PUT'])
@requiere_autenticacion
def actualizar_staff(id):
    datos = request.get_json()
    staff = Staff.query.get(id)
    if not staff:
        return jsonify({'mensaje': 'Personal no encontrado'}),404
    
    staff.s_nombre = datos.get('nombre', staff.s_nombre)
    staff.s_apellido = datos.get('apellido', staff.s_apellido)
    staff.funcion = datos.get('funcion', staff.funcion)

    db.session.commit()
    return jsonify({'mensaje': 'Personal modificado', 'id': staff.idstaff})

## ELIMINA EL PERSONAL

@app.route('/api/staff/<int:id>', methods=['DELETE'])
@requiere_autenticacion
def eliminar_staff(id):
    staff = Staff.query.get(id)
    if not staff:
        return jsonify({'mensaje': 'Personal no encontrado'}),404
    db.session.delete(staff)
    db.session.commit()
    return jsonify({'mensaje': 'ERAI'}),401

#####################################################################################

## GENERA EL GASTO COMUN

def generar_gasto_comun(anio, mes):
    # Validar que el mes sea entre 1 y 12
    if mes < 1 or mes > 12:
        return jsonify({"mensaje": "El mes debe ser un número entre 1 y 12."}), 400

    # Verificar si ya existe un gasto común para el año y mes
    gasto_existente = Gastos_Comunes.query.filter_by(anio=anio, mes=mes).first()
    if gasto_existente:
        return jsonify({"mensaje": "Ya existe un gasto común para este año y mes."}), 400

    # Obtener todos los departamentos
    departamentos = Depto.query.all()

    if not departamentos:
        return jsonify({"mensaje": "No hay departamentos disponibles."}), 400
    
    fecha_actual= datetime.now().strftime('%d/%m/%Y')

    # Crear un gasto común para cada departamento
    for depto in departamentos:
        nuevo_gasto = Gastos_Comunes(
            iddepto= depto.iddepto,
            anio= anio,
            mes= mes,
            fechap= fecha_actual,
            valor= 50000,
            pagado= "NO"
        )
        db.session.add(nuevo_gasto)

    db.session.commit()

    return jsonify({"mensaje": "Gastos comunes generados correctamente."}), 201

# Ruta para generar el gasto común
@app.route('/api/generar', methods=['POST'])
def generar():
    data = request.get_json()

    anio = data.get('anio')
    mes = data.get('mes')

    # Validar que el año y mes sean proporcionados
    if not anio or not mes:
        return jsonify({"mensaje": "El año y mes son requeridos."}), 400

    return generar_gasto_comun(anio, mes)

####################################################################################################

## FUNCION PARA PAGAR LOS GASTOS COMUNES

@app.route('/api/pagar', methods=['POST'])
@requiere_autenticacion
def pagar():
    datos= request.get_json()

    iddepto= datos.get('iddepto')
    anio= datos.get('anio')
    mes= datos.get('mes')
    valor= datos.get('valor')

    # VERIFICA QUE TODOS LOS DATOS NO ESTEN EN BLANCO 
    if not all([iddepto, anio, mes, valor]):
        return jsonify({"mensaje": "Todos los campos (IdDepto, Anio, Mes, Valor) son requeridos."}), 400
    
    # BUSCA EL GASTO COMUN 
    gasto= Gastos_Comunes.query.filter_by(iddepto= iddepto, anio= anio, mes= mes).first()

    if not gasto:
        return jsonify({"mensaje": "No se encontró el gasto común especificado."}), 404
    
    if gasto.pagado == 'SI':
        return jsonify({"mensaje": "El gasto común ya fue pagado."}), 400
    
    # VALIDA QUE EL VALOR PROPORCIONADO COINCIDA
    if gasto.valor != valor:
        return jsonify({"mensaje": "El valor proporcionado no coincide con el monto del gasto común."}), 400
    
    # MARCA EL PAGADO COMO SI
    gasto.pagado = 'SI'
    db.session.commit()

    return jsonify({"mensaje": "El gasto común ha sido pagado correctamente."}), 200

#######################################################################################################################################

## FUNCION PARA GENERAR EL INFORME DE LOS MOROSOS

@app.route('/api/informe', methods=['GET'])
@requiere_autenticacion
def informe():
    morosos= (
        db.session.query(
            Depto.iddepto,
            Depto.pisos,
            Tenant.t_nombre.label("nombre_residente"),
            Gastos_Comunes.pagado.label("pagado")
        )
        .join(Gastos_Comunes, Depto.iddepto == Gastos_Comunes.iddepto)
        .join(Tenant, Depto.iddepto == Tenant.iddepto)
        .filter(Gastos_Comunes.pagado == 'NO')
        .all()
    )

    resultado= [
        {
            "iddepto": m.iddepto,
            "piso": m.pisos,
            "Nombre Residente": m.nombre_residente,
            "pagado": m.pagado,
            "moroso": "SI" if m.pagado == "NO" else "NO"
        }
        for m in morosos
    ]
    return jsonify(resultado), 200

## PERMITE EJECUTAR LA API

if __name__=='__main__':
    app.run(debug=True)