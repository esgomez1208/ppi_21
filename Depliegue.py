# Se importan las librerías necesarias
# Versión Pandas: 2.1.1
import pandas as pd  

# Versión: 1.27.2
import streamlit as st  

# Versión: 4.8.0
from tinydb import TinyDB, Query

###########################################

# Función para registrar un nuevo usuario
def registrar_usuario(username, password, first_name, last_name, email, confirm_password):
    '''Esta funcion usa la libreria tinydb para registrar un usuario en un archivo llamado
    db_users
    '''
    User = Query()
    # Verifica si el usuario ya existe en la base de datos
    if usuarios.search(User.username == username):
        return False, "El usuario ya existe. Por favor, elija otro nombre de usuario."

    # Verifica si las contraseñas coinciden
    if password != confirm_password:
        return False, "Las contraseñas no coinciden. Por favor, vuelva a intentar."

    # Agrega el nuevo usuario a la base de datos
    usuarios.insert({'username': username, 'password': password, 'first_name': first_name, 'last_name': last_name, 'email': email})

    return True, "Registro exitoso. Ahora puede iniciar sesión."


# Función para verificar credenciales
def login(username, password):
    '''Esta funcion recibe como argumento el username y el password y verifica que
    sean inguales para permitir el ingreso al sistema
    '''
    User = Query()
    # Busca el usuario en la base de datos
    user = usuarios.get((User.username == username) & (User.password == password))
    if user:
        return True, "Inicio de sesión exitoso."
    else:
        return False, "Credenciales incorrectas. Por favor, verifique su nombre de usuario y contraseña."


def get_current_user():
    '''Esta funcion obtiene el nombre del usuario actual despues
    del inicio de sesion
    '''
    return st.session_state.username
###########################################

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
                promedio_calificaciones = sum(calificaciones) / len(calificaciones)
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
        receta = Query()
        # Asegúrate de que el campo 'Título' sea el correcto en tu base de datos
        cf.insert({"Título": receta_nombre, "Calificación": nueva_calificacion})
    except Exception as e:
        st.warning(f"Error en la función agregar_calificacion: {e}")


# Se crea una instancia de la base de datos TinyDB llamada 'cf.json'
cf = TinyDB('cf.json')
usuarios = TinyDB('usuarios.json')

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



 ######################################################################
# Inicializar la variable de sesión para el nombre de usuario
if 'username' not in st.session_state:
    st.session_state.username = None



if get_current_user() is not None:
    # Sidebar menu options for logged-in users
    st.sidebar.title('Tabla de Contenido')
    selected_option = st.sidebar.selectbox("Menú", ['Búsqueda por Nombre de Receta',
                                        'Búsqueda de Recetas por Ingrediente',
                                        'Búsqueda de Recetas por Filtrado', 'Cerrar sesión'])

    username = st.session_state.username
    User = Query()
   

    if selected_option == 'Búsqueda por Nombre de Receta':
        st.markdown('<h3 id="busqueda" style="text-align: left; color: white;"\
                    " font-style: italic;">Búsqueda por Nombre de Receta</h3>',\
                        unsafe_allow_html=True)
        
        nombre = st.text_input('Ingresa el nombre:')
        if nombre:
            # Filtrar el DataFrame por ingredientes
            df_titulo = df[df['Título'].str.contains(nombre, case=False, na=False)]
            
            # Páginas de recetas
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
                        calificacion = st.number_input(f"¿Cuánto le pones a esta receta {row['Título']} del 1 al 5?:")

                        # Verifica si el usuario proporcionó una calificación.
                        if calificacion:
                            # Obtiene el título de la receta en formato de string
                            titulo = str(row['Título'])
                            
                            # Llama a una función para agregar la calificación a la receta
                            agregar_calificacion(titulo, calificacion)
                            
                            # Llama a una función para calcular el nuevo promedio de calificaciones de la receta
                            promedio(titulo, calificacion)
            else:
                st.write("No se encontraron resultados.")

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
            recetas_por_pagina = 10  # Cantidad de recetas por página
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
                            calificacion = st.number_input(f"¿Cuánto le pones a esta receta {row['Título']} del 1 al 5?:")

                            # Verifica si el usuario proporcionó una calificación.
                            if calificacion:
                                # Obtiene el título de la receta en formato de string
                                titulo = str(row['Título'])
                                
                                # Llama a una función para agregar la calificación a la receta
                                agregar_calificacion(titulo, calificacion)
                                
                                # Llama a una función para calcular el nuevo promedio de calificaciones de la receta
                                promedio(titulo, calificacion) 
        
            else:
                st.write("No se encontraron resultados.")
        
        cf.close()

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

        #FILTRO VEGETARIANO
        # Opción para excluir recetas no vegetarianas
        excluir_no_vegetarianas = st.checkbox('Excluir recetas no vegetarianas')

        # Páginas de recetas
        recetas_por_pagina = 10  # Cantidad de recetas por página
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

                # Verificar si se debe excluir la receta debido a ingredientes no vegetarianos
                if excluir_no_vegetarianas and ((ingredientes_no_vegetarianos[0] or ingredientes_no_vegetarianos[1] or ingredientes_no_vegetarianos[2]) in row['Ingredientes']):
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
                        calificacion = st.number_input(f"¿Cuánto le pones a esta receta {row['Título']} del 1 al 5?:")

                        # Verifica si el usuario proporcionó una calificación.
                        if calificacion:
                            # Obtiene el título de la receta en formato de string
                            titulo = str(row['Título'])
                            
                            # Llama a una función para agregar la calificación a la receta
                            agregar_calificacion(titulo, calificacion)
                            
                            # Llama a una función para calcular el nuevo promedio de calificaciones de la receta
                            promedio(titulo, calificacion) 

        else:
            st.write("No se encontraron resultados.")

        cf.close()

    elif selected_option == "Cerrar sesión":
        if st.button('Salir'):
            st.session_state.username = None
            st.success("Sesión cerrada con éxito. Por favor, inicie sesión nuevamente.")
        

else:
    # Menú desplegable en la barra lateral para usuarios no logeados
    st.sidebar.title('Tabla de Contenido')
    selected_option = st.sidebar.selectbox("Menú", ['Inicio',
                                        'Registrarse','Iniciar sesión',
                                        'Búsqueda por Nombre de Receta'])

    # Sección de inicio
    if selected_option == 'Inicio':
        st.write('Bienvenido a una aplicación que te ayudará\
              a descubrir nuevas recetas de cocina basadas\
              en tus ingredientes disponibles y tus preferencias culinarias.\
              Además podrás filtrar las recetas por categorías y criterios de\
              busqueda para excluir ingredientes no deseados.')

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
            if 'politica_vista' not in st.session_state:
                st.session_state.politica_vista = False

            # Botón para abrir la ventana emergente en la segunda columna
            if col2.button("Ver Política de Tratamiento de Datos"):
                with open("Politica_tratamiento_de_datos.txt", "r") as archivo:
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

        if st.button("Iniciar Sesión"):
            login_successful, message = login(username, password)
            if login_successful:
                st.success(message)
                # Almacenar el nombre de usuario en la sesión
                st.session_state.username = username  

            elif not login_successful:
                st.error(message)

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


######################################################################
