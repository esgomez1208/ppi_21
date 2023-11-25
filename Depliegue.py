# Se importan las librerías necesarias
# Versión Pandas: 2.1.1
import pandas as pd  

# Versión Numpy: 1.26.0
import numpy as np

# Versión Matplotlib: 3.8.1
import matplotlib.pyplot as plt

# Versión: 1.27.2
import streamlit as st  

# Versión: 4.8.0
from tinydb import TinyDB, Query

from deta import Deta
import base64
from io import BytesIO
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def registrar_usuario(username, password, first_name, last_name, email, confirm_password):
    '''Esta funcion usa la libreria tinydb para registrar un usuario en un archivo llamado
    db_usurios
    '''
    # User = Query()
    # Verifica si el usuario ya existe en la base de datos
    users = db_usuarios.fetch({"username": username})
    
    # Si hay algún resultado, significa que el usuario ya existe
    if users.count > 0:
        return False, "El usuario ya existe. Por favor, elija otro nombre de usuario."

    # Verifica si las contraseñas coinciden
    if password != confirm_password:
        return False, "Las contraseñas no coinciden. Por favor, vuelva a intentar."

    # Agrega el nuevo usuario a la base de datos
    db_usuarios.put({'username': username, 'password': password, 'first_name': first_name,
                'last_name': last_name, 'email': email})

    return True, "Registro exitoso. Ahora puede iniciar sesión."

def login(username, password):
    '''Esta funcion recibe como argumento el username y el password y verifica que
    sean inguales para permitir el ingreso al sistema
    '''
    #User = Query()
    # Busca el usuario en la base de datos
    user = db_usuarios.fetch({"username": username, "password": password})
    
    if user.count > 0:
        return True, "Inicio de sesión exitoso."
    else:
        return False, "Credenciales incorrectas. Por favor, verifique su nombre de usuario y contraseña."

def usuario_actual():
    '''Esta funcion obtiene el nombre del usuario actual despues
    del inicio de sesion
    '''
    return st.session_state.username

def cargar_dataset():
    '''Función para importar la base de datos
    de las 250 recetas'''
    df = pd.read_csv('db_es.csv')
    return df

def cargar_dataset_nutricion():
    """
    Función para importar la base de datos
    de los valores nutricionales de los
    ingredientes
    """
    nutr_df = pd.read_csv('db_nutricion.csv', encoding="ISO-8859-1")
    return nutr_df
        
def promedio(receta_nombre, nueva_calificacion):
    """
    Calcula el promedio de calificaciones para una receta y agrega una nueva calificación.

    Esta función busca las calificaciones existentes para una receta y calcula el promedio de
    esas calificaciones. Si no hay calificaciones previas para la receta, agrega la nueva 
    calificación directamente. Luego, muestra un mensaje con la calificación ingresada y el 
    promedio actual.

    Parameters:
    receta_nombre (str): El nombre de la receta para la cual se va a calcular el promedio.
    nueva_calificacion (float): La nueva calificación a agregar (de 1 a 5).

    Returns:
    float: El promedio actual de calificaciones para la receta.

    Raises:
    Exception: Si ocurre un error durante la ejecución.
    """
    try:
        receta = Query()
        busqueda = cf.search(receta.Título == receta_nombre)

        if not busqueda:
            # Si no se encuentra la receta, agrega la calificación directamente
            agregar_calificacion(receta_nombre, nueva_calificacion)
            imp = f'Tu calificación es {nueva_calificacion} y el promedio es {nueva_calificacion}'
            st.success(imp)
        else:
            # Extraer las calificaciones válidas de la búsqueda
            calificaciones = [item['Calificación'] for item in busqueda if isinstance(item['Calificación'], (int, float))]

            # Verificar si hay calificaciones válidas antes de calcular el promedio
            if calificaciones:
                calificaciones.append(nueva_calificacion)  # Agregar la nueva calificación
                promedio_calificaciones = round(sum(calificaciones) / len(calificaciones),2)
                imp = f'Tu calificación es {nueva_calificacion} y el promedio de calificación de esta receta es {promedio_calificaciones}'
                st.success(imp)
            else:
                st.warning("No hay calificaciones válidas para calcular el promedio.")
    except Exception as e:
        st.warning(f"Error en la función promedio: {e}")

def agregar_calificacion(receta_nombre, nueva_calificacion):
    """
    Agrega una nueva calificación para una receta en la base de datos.

    Esta función inserta una nueva calificación para una receta específica en la base de datos.
    El nombre de la receta y su calificación se proporcionan como argumentos.

    Parameters:
    receta_nombre (str): El nombre de la receta para la cual se va a agregar una calificación.
    nueva_calificacion (float): La nueva calificación a agregar (de 1 a 5).

    Raises:
    Exception: Si ocurre un error durante la inserción de la calificación.
    """
    try:
        # Asegúrate de que el campo 'Título' sea el correcto en tu base de datos
        cf.insert({"Título": receta_nombre, "Calificación": nueva_calificacion})
    except Exception as e:
        st.warning(f"Error en la función agregar_calificacion: {e}")

def agregar_receta_fav(usuario, receta):
    """
    Agrega una receta a la lista de recetas favoritas de un usuario.

    Args:
    - usuario: Nombre de usuario para identificar al usuario.
    - receta: Nombre o identificador de la receta a agregar a las favoritas.

    Returns:
    - La receta '{receta}' fue agregada a las favoritas de {usuario}
    - Nueva lista de recetas favoritas creada para {usuario} con la receta '{receta}'

    Raises:
    - Exception: Posibles errores durante el proceso de agregado de recetas favoritas.
    """
    try:
        Recetas = Query()
        user_entry = fav_recetas.get(Recetas.Usuario == usuario)

        if user_entry:
            # El usuario ya tiene recetas favoritas
            fav_recetas.update({'Recetas': user_entry['Recetas'] + [receta]}, Recetas.Usuario == usuario)
            st.success(f"La receta '{receta}' fue agregada a las favoritas de {usuario}")
        else:
            # El usuario no tiene recetas favoritas aún
            fav_recetas.insert({'Usuario': usuario, 'Recetas': [receta]})
            st.success(f"Nueva lista de recetas favoritas creada para {usuario} con la receta {receta}")

    except Exception as e:
        st.warning(f"Error en la función agregar_receta_fav: {e}")

def eliminar_receta_fav(usuario, receta):
    """
    Elimina una receta de la lista de recetas favoritas de un usuario
    en la base de datos fav_recetas.json.

    Args:
    - usuario: Nombre de usuario para identificar al usuario.
    - receta: Nombre o identificador de la receta a eliminar de las favoritas.

    Returns:
    - Receta '{receta}' eliminada de las favoritas de {usuario}
    - La receta '{receta}' no existe en las favoritas de {usuario}

    Raises:
    - Exception: Posibles errores durante el proceso de eliminación de recetas favoritas.
    """
    try:
        Recetas = Query()
        user_entry = fav_recetas.get(Recetas.Usuario == usuario)

        if user_entry and receta in user_entry['Recetas']:
            user_recipes = user_entry['Recetas']
            user_recipes.remove(receta)
            fav_recetas.update({'Recetas': user_recipes}, Recetas.Usuario == usuario)
            st.success(f"Receta '{receta}' eliminada de las favoritas de {usuario}")
        else:
            st.warning(f"La receta '{receta}' no existe en las favoritas de {usuario}")

    except Exception as e:
        st.warning(f"Error en la función eliminar_receta_fav: {e}")

def cambiar_contraseña(usuario, contraseña_actual, contraseña_nueva):
    """
    Esta función cambia la contraseña de un usuario en la base de datos usuarios.

    Args:
    - usuario: Nombre de usuario para identificar al usuario.
    - contraseña_actual: Contraseña actual del usuario.
    - contraseña_nueva: Nueva contraseña que se asignará al usuario.

    Returns:
    - Cambio de contraseña exitoso
    - Error al cambiar de contraseña: contraseña actual incorrecta

    Raises:
    - Exception: Posibles errores durante el proceso de cambio de contraseña.
    """
    try:
        User = Query()
        user_entry = usuarios.get(User.username == usuario)

        if user_entry and user_entry['password'] == contraseña_actual:
            usuarios.update({'password': contraseña_nueva}, User.username == usuario)
            st.success("Cambio de contraseña exitoso")
        else:
            st.warning("Error al cambiar de contraseña: contraseña actual incorrecta")

    except Exception as e:
        st.warning("Error al cambiar de contraseña: {}".format(e))

def enviar_correo(destinatario, asunto, cuerpo):
    ''' Esta funcion envia correo segun el destinatario, el asunto y el cuerpo
    Usando servidores TTS para el envio de ellos , usando contraseña de aplicacion y el correo
    '''

    #Puerto y Servidor
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587

    # Usuario y contraseña de correo
    smtp_username = 'culinarycraftt@gmail.com'  
    smtp_password = 'tbvf wdwa cxnq ysut'  
    # Crear el mensaje MIME
    msg = MIMEMultipart()
    msg['From'] = smtp_username
    msg['To'] = destinatario
    msg['Subject'] = asunto

    # Adjuntar el cuerpo del correo al mensaje con codificación UTF-8
    body = cuerpo.encode('utf-8')
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    context = ssl.create_default_context()
    try:
        # Iniciar conexión con el servidor SMTP de Gmail utilizando TLS
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls(context=context)
            server.login(smtp_username, smtp_password)
            
            # Enviar el correo con el mensaje MIME como string
            server.sendmail(smtp_username, destinatario, msg.as_string())

        st.success("Correo enviado con éxito")

    except Exception as e:
        st.error(f"Error al enviar el correo: {e}")

##########################################

# Almacenamos la key de la base de datos en una constante
DETA_KEY = "e0zpnxfprhj_k9mu6XgGYApSvzNJHuFyvuQ74sYRZgvR"

# Creamos nuestro objeto deta para hacer la conexion a la DB
deta = Deta(DETA_KEY)

# Inicializa la base de datos para usuarios

db_usuarios = deta.Base("usuarios")

##########################################



# Se crea una instancia de la base de datos TinyDB llamada 'cf.json'
cf = TinyDB('cf.json')
# usuarios = TinyDB('usuarios.json')
fav_recetas = TinyDB('fav_recetas.json')

# Cargar el conjunto de datos
df = cargar_dataset()

# Cargar datset de datos nutricionales
nutr_df = cargar_dataset_nutricion()

# Crear nueva columna con los valores separados por & para que sea una lista
df['NER_separados'] = df['NER'].str.split('&')
nutr_df['name'] = nutr_df['name'].str.split('&')

# Realizar unión basada en la coincidencia de ingredientes
valor_nutricional = df.explode('NER_separados').merge(
    nutr_df.explode('name'),
    left_on = 'NER_separados',
    right_on = 'name',
    how = 'left')

# Establecer estilo y formato personalizado del titulo de la App
st.markdown('<h1 style="text-align: left; color: skyblue;">CulinaryCraft</h1>',\
             unsafe_allow_html=True)

# Inicializar la variable de sesión para el nombre de usuario
if 'username' not in st.session_state:
    st.session_state.username = None

# verifica si el usuario inició sesión
if usuario_actual() is not None:

    # se registra el username del usuario que inició sesión
    username = st.session_state.username
    
    # Sidebar para usuario logeado
    st.sidebar.title('Tabla de Contenido')
    selected_option = st.sidebar.selectbox("Menú", ['Inicio','Búsqueda por Nombre de Receta',
                                        'Búsqueda de Recetas por Ingrediente',
                                        'Búsqueda de Recetas por Filtrado'])
    
    # reserva de espacio para mostrar botón en la parte inferior
    for i in np.arange(15):
        st.sidebar.text("")

    # Botón para cerrar sesión
    if st.sidebar.button("Cerrar sesión"):
            st.session_state.username = None
            st.success("Sesión cerrada con éxito. Presione el botón nuevamente.")
            selected_option = 'Iniciar sesión'

    # se registra el username del usuario que inició sesión
    # username = st.session_state.username
    #User = Query()

    # Sección de inicio del usuario
    if selected_option == 'Inicio':
        st.markdown(f'<h3 id="busqueda" style="text-align: left; color: white;"\
                    " font-style: italic;">Bienvenido {username}</h3>',\
                        unsafe_allow_html=True)
        
        # Apartado para cambiar de contraseña
        with st.expander(f'{username} aquí puede cambiar su contraseña:'):

            ps = st.text_input("Contraseña actual:", type="password")
            ps_new = st.text_input("Nueva Contraseña:", type="password")
            ps_new_conf = st.text_input("Confirmar Nueva Contraseña:", type="password")
            if ps_new == ps_new_conf:
                if st.button("Cambiar contraseña"):
                    login_successful, message = login(username, ps)
                    if login_successful:
                        us_s = db_usuarios.fetch({"username":username})
                        itm = us_s.items[0]
                        llave = itm.get("key")
                        db_usuarios.update({"password":ps_new},key=llave)
                        st.success("Contraseña cambiada con exito")

                    else:
                        st.warning("Credenciales incorrectas")
            else:
                st.warning("Las Contraseñas no coinciden")

        # Impresión de las recetas guardadas por el usuario
        st.write("Estas son las recetas que has guardado:")

        try:
            Recetas = Query()
            user_entry = fav_recetas.get(Recetas.Usuario == username)

            if len(user_entry['Recetas']) > 0:
                print(f"Recetas favoritas de {username}:")
                for receta in user_entry['Recetas']:
                    
                    if receta:
                        # Filtrar el DataFrame por ingredientes
                        df_titulo = df[df['Título'].str.contains(receta, case=False, na=False)]

                        # Mostrar los nombres de las recetas
                        if not df_titulo.empty:
                
                            # Filtrar recetas si es necesario (según ingredientes excluidos y opción de azúcar)
                            recetas_filtradas = []
                            for idx, row in df_titulo.iterrows():
                                #mostrar_receta = True
                                recetas_filtradas.append(row)

                            if recetas_filtradas:
                                titulo = row['Título']
    
                                # Variable que guarda el valor nutricional
                                ingredientes_receta = row['NER'].split('&')
    
                                # Mostrar la receta si no se excluye
                                st.markdown(f'<h4 id="filtrado" style="text-align: left; color: skyblue;"\
                                " font-style: italic;">{titulo}</h4>',\
                                    unsafe_allow_html=True)
                                
                                # Lista para almacenar el valor nutricional de cada ingrediente
                                nutricional = []
    
                                for ingrediente in ingredientes_receta:
                                    info_nutricional = valor_nutricional[valor_nutricional['name'] == ingrediente]
                                    calorias = info_nutricional['calories'].values[0] if not info_nutricional.empty else "No encontrado"
    
                                    nutricional.append({'Ingrediente' : ingrediente, 'Calorías' : calorias})
    
                                # convirtiendo lista en un dataframe para mostrarlo como tabla
                                tabla_valor_nutricional = pd.DataFrame(nutricional)
    
    
                                # Agregar una sección de detalles emergente
                                with st.expander(f'Detalles de la receta: {row["Título"]}', expanded=False):
    
                                    # Importar la columna de las imágenes de la receta
                                    image_URL = row['Imagen']
                                    st.image(image_URL)
    
                                    # Impresion de ingredientes
                                    ingredientes = row['Ingredientes'].split('&')
    
                                    st.markdown(f'<h5 id="filtrado" style="text-align: left; color: skyblue;"\
                                " font-style: italic;">Ingredientes:</h5>',\
                                    unsafe_allow_html=True)
    
                                    for i in range(len(ingredientes)):
                                        st.write(i+1 , ingredientes[i] )
    
                                    # Impresion de preparación
                                    preparacion = row['Preparacion'].split('&')
    
                                    st.markdown(f'<h5 id="filtrado" style="text-align: left; color: skyblue;"\
                                " font-style: italic;">Preparación paso a paso:</h5>',\
                                    unsafe_allow_html=True)
    
                                    for i in range(len(preparacion)):
                                        st.write(i+1 , preparacion[i] )
    
                                    # Aquí colocamos la tabla del valor nutricional de los ingredientes
                                    st.write(tabla_valor_nutricional)
    
                                    # Solicita al usuario la calificación
                                    calificacion = st.number_input(f"¿Cuánto le pones a esta receta {row['Título']} del 1 al 5?:", 
                                                                    min_value=0, max_value=5, step=1)
    
                                    # Verifica si el usuario proporcionó una calificación.
                                    if calificacion:
                                        # Obtiene el título de la receta en formato de string
                                        titulo = str(row['Título'])
                                        
                                        # Llama a una función para agregar la calificación a la receta
                                        agregar_calificacion(titulo, calificacion)
                                        
                                        # Llama a una función para calcular el nuevo promedio de calificaciones de la receta
                                        promedio(titulo, calificacion)
    
                                    if st.button(f'Borrar receta {titulo}'):
                                        eliminar_receta_fav(username, titulo)
            else:
                st.write(f"No se encontraron recetas favoritas para {username}")

        except Exception as e:
            st.write(f"No se encontraron recetas favoritas para {username}")

   
    # Sección de busqueda por nombre de receta
    elif selected_option == 'Búsqueda por Nombre de Receta':
        st.markdown('<h3 id="busqueda" style="text-align: left; color: white;"\
                    " font-style: italic;">Búsqueda por Nombre de Receta</h3>',\
                        unsafe_allow_html=True)
        
        nombre = st.text_input('Ingresa el nombre:')
        if nombre:
            # Filtrar el DataFrame por el titulo
            df_titulo = df[df['Título'].str.contains(nombre, case=False, na=False)]
            
            # Páginas de recetas
            st.write("Navegue entre los resultados usando el (+) y el (-)")
            # Cantidad de recetas por página
            recetas_por_pagina = 10  
            pagina = st.number_input('Página', min_value=1, value=1)

            # Mostrar los nombres de las recetas
            if not df_titulo.empty:
                st.subheader('Recetas que coinciden con "{}":'.format(nombre))
    
                # Filtrar recetas si es necesario (según ingredientes excluidos y opción de azúcar)
                recetas_filtradas = []
                for idx, row in df_titulo.iterrows():
                    #mostrar_receta = True
                    recetas_filtradas.append(row)

                # Calcular los índices de inicio y fin para la página actual
                inicio = (pagina - 1) * recetas_por_pagina
                fin = min(inicio + recetas_por_pagina, len(recetas_filtradas))

                if recetas_filtradas:
                    st.write(f"Mostrando recetas {inicio + 1} - {fin} de {len(recetas_filtradas)}")
                    for idx in range(inicio, fin):
                        row = recetas_filtradas[idx]

                        titulo = row['Título']

                        # Variable que guarda el valor nutricional
                        ingredientes_receta = row['NER'].split('&')


                        # Mostrar la receta si no se excluye
                        st.markdown(f'<h4 id="filtrado" style="text-align: left; color: skyblue;"\
                        " font-style: italic;">{titulo}</h4>',\
                            unsafe_allow_html=True)
                        
                        # Lista para almacenar el valor nutricional de cada ingrediente
                        nutricional = []

                        for ingrediente in ingredientes_receta:
                            info_nutricional = valor_nutricional[valor_nutricional['name'] == ingrediente]
                            calorias = info_nutricional['calories'].values[0] if not info_nutricional.empty else "No encontrado"

                            nutricional.append({'Ingrediente' : ingrediente, 'Calorías' : calorias})

                        # convirtiendo lista en un dataframe para mostrarlo como tabla
                        tabla_valor_nutricional = pd.DataFrame(nutricional)


                        # Agregar una sección de detalles emergente
                        with st.expander(f'Detalles de la receta: {row["Título"]}', expanded=False):

                            # Importar la columna de las imágenes de la receta
                            image_URL = row['Imagen']
                            st.image(image_URL)

                            # Impresion de ingredientes
                            ingredientes = row['Ingredientes'].split('&')

                            st.markdown(f'<h5 id="filtrado" style="text-align: left; color: skyblue;"\
                        " font-style: italic;">Ingredientes:</h5>',\
                            unsafe_allow_html=True)

                            for i in range(len(ingredientes)):
                                st.write(i+1 , ingredientes[i] )

                            # Impresion de preparación
                            preparacion = row['Preparacion'].split('&')

                            st.markdown(f'<h5 id="filtrado" style="text-align: left; color: skyblue;"\
                        " font-style: italic;">Preparación paso a paso:</h5>',\
                            unsafe_allow_html=True)

                            for i in range(len(preparacion)):
                                st.write(i+1 , preparacion[i] )

                            # Aquí colocamos la tabla del valor nutricional de los ingredientes
                            st.write(tabla_valor_nutricional)

                            # Solicita al usuario la calificación
                            calificacion = st.number_input(f"¿Cuánto le pones a esta receta {row['Título']} del 1 al 5?:",
                                                             min_value=0, max_value=5, step=1)

                            # Verifica si el usuario proporcionó una calificación.
                            if calificacion:
                                # Obtiene el título de la receta en formato de string
                                titulo = str(row['Título'])
                                
                                # Llama a una función para agregar la calificación a la receta
                                agregar_calificacion(titulo, calificacion)
                                
                                # Llama a una función para calcular el nuevo promedio de calificaciones de la receta
                                promedio(titulo, calificacion)

                            if st.button(f'Guardar receta {titulo}'):
                                agregar_receta_fav(username,titulo)
            else:
                st.warning("No se encontraron coincidencias con tu busqueda.")

        cf.close()

    # Sección de Búsqueda de Recetas por Ingrediente
    elif selected_option == 'Búsqueda de Recetas por Ingrediente':
        st.markdown('<h3 id="busqueda" style="text-align: left; color: white;"\
                    " font-style: italic;">Búsqueda de Recetas por Ingrediente</h3>',\
                        unsafe_allow_html=True)
        
        ingrediente = st.text_input('Ingresa un ingrediente:')
        if ingrediente:
            # Filtrar el DataFrame por ingredientes
            df_ingredientes = df[df['Ingredientes'].str.contains(ingrediente, case=False, na=False)]
            
            # Páginas de recetas
            st.write("Navegue entre los resultados usando el (+) y el (-)")
            recetas_por_pagina = 10 
            pagina = st.number_input('Página', min_value=1, value=1)

            # Mostrar los nombres de las recetas
            if not df_ingredientes.empty:
                st.subheader('Recetas que contienen "{}":'.format(ingrediente))
    
                # Filtrar recetas si es necesario (según ingredientes excluidos y opción de azúcar)
                recetas_filtradas = []
                for idx, row in df_ingredientes.iterrows():
                    #mostrar_receta = True
                    recetas_filtradas.append(row)

                # Calcular los índices de inicio y fin para la página actual
                inicio = (pagina - 1) * recetas_por_pagina
                fin = min(inicio + recetas_por_pagina, len(recetas_filtradas))

                if recetas_filtradas:
                    st.write(f"Mostrando recetas {inicio + 1} - {fin} de {len(recetas_filtradas)}")
                    for idx in range(inicio, fin):

                        # 'row' es la variable que guarda la receta actual
                        row = recetas_filtradas[idx]

                        titulo = row['Título']

                        # Variable para guardar el valor nutricional
                        ingredientes_receta = row['NER'].split('&')

                        # Mostrar la receta si no se excluye
                        st.markdown(f'<h4 id="filtrado" style="text-align: left; color: skyblue;"\
                        " font-style: italic;">{titulo}</h4>',\
                            unsafe_allow_html=True)


                        # Lista para almacenar el valor nutricional de cada ingrediente
                        nutricional = []

                        for ingrediente in ingredientes_receta:
                            info_nutricional = valor_nutricional[valor_nutricional['name'] == ingrediente]
                            calorias = info_nutricional['calories'].values[0] if not info_nutricional.empty else "No encontrado"

                            nutricional.append({'Ingrediente' : ingrediente, 'Calorías' : calorias})

                        # convirtiendo lista en un dataframe para mostrarlo como tabla
                        tabla_valor_nutricional = pd.DataFrame(nutricional)

                        # Agregar una sección de detalles emergente
                        with st.expander(f'Detalles de la receta: {row["Título"]}', expanded=False):

                            # Importar la columna de las imágenes de la receta
                            image_URL = row['Imagen']
                            st.image(image_URL)

                            # Impresion de ingredientes
                            ingredientes = row['Ingredientes'].split('&')

                            st.markdown(f'<h5 id="filtrado" style="text-align: left; color: skyblue;"\
                        " font-style: italic;">Ingredientes:</h5>',\
                            unsafe_allow_html=True)

                            for i in range(len(ingredientes)):
                                st.write(i+1 , ingredientes[i] )

                            # Impresion de preparación
                            preparacion = row['Preparacion'].split('&')

                            st.markdown(f'<h5 id="filtrado" style="text-align: left; color: skyblue;"\
                        " font-style: italic;">Preparación paso a paso:</h5>',\
                            unsafe_allow_html=True)

                            for i in range(len(preparacion)):
                                st.write(i+1 , preparacion[i] )

                            # Aquí colocamos la tabla del valor nutricional de los ingredientes
                            st.write(tabla_valor_nutricional)

                            # Solicita al usuario la calificación
                            calificacion = st.number_input(f"¿Cuánto le pones a esta receta {row['Título']} del 1 al 5?:",
                                                             min_value=0, max_value=5, step=1)

                            # Verifica si el usuario proporcionó una calificación.
                            if calificacion:
                                # Obtiene el título de la receta en formato de string
                                titulo = str(row['Título'])
                                
                                # Llama a una función para agregar la calificación a la receta
                                agregar_calificacion(titulo, calificacion)
                                
                                # Llama a una función para calcular el nuevo promedio de calificaciones de la receta
                                promedio(titulo, calificacion) 


                            if st.button(f'Guardar receta {titulo}'):
                                agregar_receta_fav(username,titulo)
        
            else:
                st.warning("No se encontraron coincidencias con tu busqueda.")
        
        cf.close()

    # Sección de busqueda de receta por filtros
    elif selected_option == 'Búsqueda de Recetas por Filtrado':
        st.markdown('<h3 id="filtrado" style="text-align: left; color: white;"\
                    " font-style: italic;">Búsqueda de Recetas por Filtrado</h3>',\
                        unsafe_allow_html=True)
    
        # Cuadro de entrada para ingredientes a excluir
        ingredientes_a_excluir = st.text_input('Ingresa ingredientes a excluir (separados por comas):')

        # Definir el ingrediente "azúcar" para buscar en las recetas
        ingrediente_azucar = "azúcar"

        # Opción para excluir recetas con azúcar
        excluir_azucar = st.checkbox('Excluir recetas con azúcar')

        # Definir la lista de ingredientes no vegetarianos
        ingredientes_no_vegetarianos = ["pollo", "carne", "pavo", "pechuga", "res"]


        # Páginas de recetas
        st.write("Navegue entre los resultados usando el (+) y el (-)")
        recetas_por_pagina = 10
        pagina = st.number_input('Página', min_value=1, value=1)

        if not df.empty:
            # Filtrar recetas si es necesario (según ingredientes excluidos y opción de azúcar)
            recetas_filtradas = []
            for idx, row in df.iterrows():
                mostrar_receta = True

                # Verificar si se debe excluir la receta debido a ingredientes excluidos
                if ingredientes_a_excluir:
                    ingredientes_excluidos = [ingrediente.strip() for ingrediente in ingredientes_a_excluir.split(',')]
                    for ingrediente in ingredientes_excluidos:
                        if ingrediente in row['Ingredientes']:
                            mostrar_receta = False

                # Verificar si se debe excluir la receta debido al azúcar
                if excluir_azucar and ingrediente_azucar in row['Ingredientes']:
                    mostrar_receta = False


                # Agregar la receta a la lista si no se excluye
                if mostrar_receta:
                    recetas_filtradas.append(row)

            # Calcular los índices de inicio y fin para la página actual
            inicio = (pagina - 1) * recetas_por_pagina
            fin = min(inicio + recetas_por_pagina, len(recetas_filtradas))

            if recetas_filtradas:
                st.write(f"Mostrando recetas {inicio + 1} - {fin} de {len(recetas_filtradas)}")
                for idx in range(inicio, fin):
                    row = recetas_filtradas[idx]

                    titulo = row['Título']

                    # NUEVA VARIABLE PARA VALOR NUTRICIONAL
                    ingredientes_receta = row['NER'].split('&')

                    # Mostrar la receta si no se excluye
                    st.markdown(f'<h4 id="filtrado" style="text-align: left; color: skyblue;"\
                    " font-style: italic;">{titulo}</h4>',\
                        unsafe_allow_html=True)
                    
                    # Lista para almacenar el valor nutricional de cada ingrediente
                    nutricional = []

                    for ingrediente in ingredientes_receta:
                        info_nutricional = valor_nutricional[valor_nutricional['name'] == ingrediente]
                        calorias = info_nutricional['calories'].values[0] if not info_nutricional.empty else "No encontrado"

                        nutricional.append({'Ingrediente' : ingrediente, 'Calorías' : calorias})

                    # convirtiendo lista en un dataframe para mostrarlo como tabla
                    tabla_valor_nutricional = pd.DataFrame(nutricional)


                    # Agregar una sección de detalles emergente
                    with st.expander(f'Detalles de la receta: {row["Título"]}', expanded=False):

                        # Importar la columna de las imágenes de la receta
                        image_URL = row['Imagen']
                        st.image(image_URL)

                        # Impresion de ingredientes
                        ingredientes = row['Ingredientes'].split('&')

                        st.markdown(f'<h5 id="filtrado" style="text-align: left; color: skyblue;"\
                    " font-style: italic;">Ingredientes:</h5>',\
                        unsafe_allow_html=True)

                        for i in range(len(ingredientes)):
                            st.write(i+1 , ingredientes[i] )

                        # Impresion de preparación
                        preparacion = row['Preparacion'].split('&')

                        st.markdown(f'<h5 id="filtrado" style="text-align: left; color: skyblue;"\
                    " font-style: italic;">Preparación paso a paso:</h5>',\
                        unsafe_allow_html=True)

                        for i in range(len(preparacion)):
                            st.write(i+1 , preparacion[i] )

                        # Aquí colocamos la tabla del valor nutricional de los ingredientes
                        st.write(tabla_valor_nutricional)

                        # Solicita al usuario la calificación
                        calificacion = st.number_input(f"¿Cuánto le pones a esta receta {row['Título']} del 1 al 5?:",
                                                         min_value=0, max_value=5, step=1)

                        # Verifica si el usuario proporcionó una calificación.
                        if calificacion:
                            # Obtiene el título de la receta en formato de string
                            titulo = str(row['Título'])
                            
                            # Llama a una función para agregar la calificación a la receta
                            agregar_calificacion(titulo, calificacion)
                            
                            # Llama a una función para calcular el nuevo promedio de calificaciones de la receta
                            promedio(titulo, calificacion) 

                        if st.button(f'Guardar receta {titulo}'):
                            agregar_receta_fav(username,titulo)

        else:
            st.write("No se encontraron resultados.")

        cf.close()

        

else:
    # Menú desplegable en la barra lateral para usuarios no logeados
    st.sidebar.title('Tabla de Contenido')
    selected_option = st.sidebar.selectbox("Menú", ['Acerca de CulinaryCraft',
                                        'Registrarse','Iniciar sesión',
                                        'Búsqueda por Nombre de Receta'])

    # Sección de Bienvenida
    if selected_option == 'Acerca de CulinaryCraft':
        st.write("Descubre un mundo de sabores adaptado a ti. Nuestra aplicación te \
                ayuda a encontrar recetas deliciosas según tus ingredientes y preferencias\
                 culinarias. ¿Eres vegano, te apasiona la comida italiana o buscas algo\
                sin gluten? Con nuestra aplicación, filtrar las recetas es fácil: podrás\
                 seleccionar categorías y excluir los ingredientes que no desees. Además,\
                 al registrarte, desbloquearás la posibilidad de guardar tus recetas favoritas,\
                 calificarlas y acceder a información detallada sobre sus nutrientes.\
                 ¡Únete a nosotros y experimenta la cocina de una manera totalmente nueva!")

        st.markdown('<h2 style="text-align: left; color: skyblue;">Acerca de nosotros</h2>',\
             unsafe_allow_html=True)

        st.write("Somos un equipo apasionado por la comida y la facilidad en la cocina.\
                Nuestra misión es simplificar tu experiencia culinaria y hacerla más emocionante.\
                Nos esforzamos por ofrecerte una amplia gama de recetas, desde platos tradicionales\
                hasta las últimas tendencias gastronómicas, todo adaptado a tus gustos y necesidades.")

        st.markdown('<h2 style="text-align: left; color: skyblue;">¡Regístrate para más beneficios!</h2>',\
             unsafe_allow_html=True)

        st.write("¿Quieres sacarle el máximo provecho a la aplicación? Regístrate para acceder a\
                 dos funcionalidades exclusivas: podrás guardar tus recetas favoritas y, además,\
                 tendrás la oportunidad de calificarlas, lo que nos ayudará a mejorar continuamente.\
                ¡Pero eso no es todo! También podrás visualizar información nutricional detallada de \
                cada receta. Únete a nosotros y convierte tu experiencia culinaria en algo aún más increíble.")

        st.markdown('<h2 style="text-align: left; color: skyblue;">Contacto</h2>',\
             unsafe_allow_html=True)

        st.write("¡Nos encantaría escucharte! Si tienes preguntas, comentarios o sugerencias,\
                 no dudes en ponerte en contacto con nosotros.")
        st.write("-Correo Electrónico: culinarycraftt@gmail.com")
        st.write("-Teléfono: +57 301 518 5942")

    # Sección de Registro
    elif selected_option == "Registrarse":
            st.write("Registro de Usuario")

            # Campos de registro
            first_name = st.text_input("Nombre del Usuario:")
            last_name = st.text_input("Apellidos del Usuario:")
            email = st.text_input("Correo electronico del Usuario:")
            new_username = st.text_input("Nickname:")
            new_password = st.text_input("Nueva Contraseña:", type = "password")
            confirm_password = st.text_input("Confirmar contraseña:", type = "password")

            # Crear dos columnas para los botones
            col1, col2 = st.columns(2)
            # Casilla de verificación para aceptar la política de datos personales
            # Inicializa la variable aceptar_politica
            
            # Variable de estado para rastrear si el usuario ha visto la política
            st.session_state.politica_vista = True

            
            # Botón para abrir la ventana emergente en la segunda columna
            if col2.button("Ver Política de Tratamiento de Datos"):
                with open("Politica_tratamiento_de_datos.txt", "r", encoding="utf-8") as archivo:
                    politica = archivo.read()
                    with st.expander("Política de Tratamiento de Datos",expanded=True):
                        st.write(politica)
                        st.session_state.politica_vista = True

            # Casilla de verificación para aceptar la política
            aceptar_politica = st.checkbox("Acepta la política de datos personales")

            # Botón de registro de usuario en la primera columna
            if col1.button("Registrarse") and aceptar_politica and st.session_state.politica_vista:
                registration_successful, message = registrar_usuario(new_username, new_password, first_name, last_name, email, confirm_password)
                if registration_successful:
                    st.success(message)

                    asunto='registro exitoso en CulinaryCraft'

                    cuerpo=f"Hola {first_name},\n ¡Gracias por registrarte en nuestra app de cocina!\n Ahora formas parte de la comunidad de CulinaryCraft.\n ¡Empieza a explorar deliciosas recetas y disfruta cocinando!\n¡Bienvenido y que disfrutes tu experiencia culinaria!\n Recuerda que tu contraseña es: {confirm_password}\n Atentamente, El equipo de culinary craft."
                    
                    enviar_correo(email,asunto,cuerpo)
                    
                else:
                    st.error(message)

            if not aceptar_politica:
                st.warning("Por favor, acepta la política de datos personales antes de registrarte.")

            if not st.session_state.politica_vista:
                st.warning("Por favor, ve la política de datos personales antes de registrarte.")

    # Sección de Inicio de sesión
    elif selected_option == 'Iniciar sesión':
        st.write("Bienvenido al inicio de la aplicación.")

        # Campos de inicio de sesión
        username = st.text_input("Usuario:")
        password = st.text_input("Contraseña:", type="password")

        # crear dos columnas para los botones
        col1, col2 = st.columns(2)

        if col1.button("Iniciar Sesión"):
            login_successful, message = login(username, password)
            if login_successful:
                st.success(message)
                # Almacenar el nombre de usuario en la sesión
                st.session_state.username = username
                selected_option = 'Inicio'  

            elif not login_successful:
                st.error(message)

        # Botón para recuperar contraseña
        elif col2.button("Recuperar contraseña"):
            try:
                if username is not None:
                    User = Query()
                    user_info = usuarios.get(User.username == username)

                    email_recuperar = user_info['email']
                    contraseña_recuperar = user_info['password']
                    nombre = user_info['first_name']
                    destinatario = email_recuperar  
                    asunto = 'Recuperacion de Contraseña'
                    cuerpo = (f'Hola {nombre} ,  Te enviamos este correo para recordarte la contraseña\n\n Usuario : {username} \n\n Contraseña : {contraseña_recuperar}  ')

                    enviar_correo(destinatario, asunto, cuerpo)
                    st.success('En el correo puedes verificar tu contraseña.')

            except:
                if True:
                    st.warning('Verifique el nombre de usuario')


    # Sección de Búsqueda de Búsqueda por Nombre de Receta
    elif selected_option == 'Búsqueda por Nombre de Receta':
        st.markdown('<h3 id="busqueda" style="text-align: left; color: white;"\
                    " font-style: italic;">Búsqueda por Nombre de Receta</h3>',\
                        unsafe_allow_html=True)
        
        nombre = st.text_input('Ingresa el nombre:')
        if nombre:
            # Filtrar el DataFrame por título
            df_titulo = df[df['Título'].str.contains(nombre, case=False, na=False)]
            
            # Páginas de recetas
            st.write("Navegue entre los resultados usando el (+) y el (-)")
            recetas_por_pagina = 10  # Cantidad de recetas por página
            pagina = st.number_input('Página', min_value=1, value=1)

            # Mostrar los nombres de las recetas
            if not df_titulo.empty:
                st.subheader('Recetas que coinciden con "{}":'.format(nombre))
    
                # Filtrar recetas si es necesario (según ingredientes excluidos y opción de azúcar)
                recetas_filtradas = []
                for idx, row in df_titulo.iterrows():
                    #mostrar_receta = True
                    recetas_filtradas.append(row)

                # Calcular los índices de inicio y fin para la página actual
                inicio = (pagina - 1) * recetas_por_pagina
                fin = min(inicio + recetas_por_pagina, len(recetas_filtradas))

                if recetas_filtradas:
                    st.write(f"Mostrando recetas {inicio + 1} - {fin} de {len(recetas_filtradas)}")
                    for idx in range(inicio, fin):
                        row = recetas_filtradas[idx]

                        titulo = row['Título']

                        # Variable que guarda el valor nutricional
                        ingredientes_receta = row['NER'].split('&')


                        # Mostrar la receta si no se excluye
                        st.markdown(f'<h4 id="filtrado" style="text-align: left; color: skyblue;"\
                        " font-style: italic;">{titulo}</h4>',\
                            unsafe_allow_html=True)


                        # Agregar una sección de detalles emergente
                        with st.expander(f'Detalles de la receta: {row["Título"]}', expanded=False):

                            # Importar la columna de las imágenes de la receta
                            image_URL = row['Imagen']
                            st.image(image_URL)

                            # Impresion de ingredientes
                            ingredientes = row['Ingredientes'].split('&')

                            st.markdown(f'<h5 id="filtrado" style="text-align: left; color: skyblue;"\
                        " font-style: italic;">Ingredientes:</h5>',\
                            unsafe_allow_html=True)

                            for i in range(len(ingredientes)):
                                st.write(i+1 , ingredientes[i] )

                            # Impresion de preparación
                            preparacion = row['Preparacion'].split('&')

                            st.markdown(f'<h5 id="filtrado" style="text-align: left; color: skyblue;"\
                        " font-style: italic;">Preparación paso a paso:</h5>',\
                            unsafe_allow_html=True)

                            for i in range(len(preparacion)):
                                st.write(i+1 , preparacion[i] )
                       
            else:
                st.write("No se encontraron resultados.")

        cf.close()


