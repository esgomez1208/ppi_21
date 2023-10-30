# Se importan las librerías necesarias
# Versión Pandas: 2.1.1
import pandas as pd  

# Versión: 1.27.2
import streamlit as st  

# Versión: 4.8.0
from tinydb import TinyDB, Query


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

# Cargar el conjunto de datos
df = cargar_dataset()

# Cargar datset de datos nutricionales
nutr_df = cargar_dataset_nutricion()

# Establecer estilo y formato personalizado
st.markdown('<h1 style="text-align: left; color: skyblue;">CulinaryCraft</h1>',\
             unsafe_allow_html=True)

# Crear una barra lateral para la tabla de contenidos
st.sidebar.title('Tabla de Contenido')
selected_option = st.sidebar.selectbox(
    'Selecciona una opción:',
    ['Inicio', 'Búsqueda por Nombre de Receta','Búsqueda de Recetas por Ingrediente', 'Búsqueda de Recetas por Filtrado']
)

# Crear nueva columna con los valores separados por & para que sea una lista
df['NER_separados'] = df['NER'].str.split('&')
nutr_df['name'] = nutr_df['name'].str.split('&')

# Realizar unión basada en la coincidencia de ingredientes
valor_nutricional = df.explode('NER_separados').merge(
    nutr_df.explode('name'),
    left_on = 'NER_separados',
    right_on = 'name',
    how = 'left')

# Interfaz de usuario
if selected_option == 'Inicio':
    st.write('Bienvenido a una aplicación que te ayudará\
              a descubrir nuevas recetas de cocina basadas\
              en tus ingredientes disponibles y tus preferencias culinarias.\
              Además podrás filtrar las recetas por categorías y criterios de\
              busqueda para excluir ingredientes no deseados.')

    # Ventana tratamiento de datos
    st.markdown('<h3 style="text-align: left; color: white;"\
        ">Política de Tratamiento de Datos Personales</h3>', unsafe_allow_html=True)
    
    # Ruta al archivo de texto
    archivo_txt = "Politica_tratamiento_de_datos.txt"
    with open(archivo_txt, "r") as file:
        contenido = file.read()
    st.write(contenido)

    # Crear dos columnas para los checkboxes
    col1, col2 = st.columns(2)

    # Opciones para aceptar o denegar
    aceptar = col1.checkbox("Acepto los términos y condiciones")
    denegar = col2.checkbox("Deniego los términos y condiciones")

    # Mensaje de confirmación o denegación
    # Mensaje de confirmación o denegación
    if aceptar:
        st.success("¡Has aceptado los términos y condiciones!")
    else:
        st.warning("Debes aceptar los términos y condiciones para continuar.")

    # Resto de la aplicación
    if aceptar:
        # Aquí puedes continuar con el resto de tu aplicación si el usuario acepta
        pass

# Sección de Búsqueda de Búsqueda por Nombre de Receta
elif selected_option == 'Búsqueda por Nombre de Receta':
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

        else:
            st.write("No se encontraron resultados.")

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
       
        else:
            st.write("No se encontraron resultados.")

# Sección de Búsqueda de Búsqueda de Recetas por Filtrado
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
                    if ingrediente in row['ingredientes']:
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

    else:
        st.write("No se encontraron resultados.")