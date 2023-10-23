# Se importan las libreías necesarias
import pandas as pd  # Versión: 2.1.1
import streamlit as st  # Versión: 1.27.2

def cargar_dataset():
    '''Función para importar la base de datos
    de las 250 recetas'''
    df = pd.read_csv('db_reducida_spanish.csv')
    return df

# Cargar el conjunto de datos
df = cargar_dataset()

# Establecer estilo y formato personalizado
st.markdown('<h1 style="text-align: left; color: skyblue;">CulinaryCraft</h1>',\
             unsafe_allow_html=True)


# Crear una barra lateral para la tabla de contenidos
st.sidebar.title('Tabla de Contenido')
selected_option = st.sidebar.selectbox(
    'Selecciona una opción:',
    ['Inicio', 'Búsqueda por Nombre de Receta','Búsqueda de Recetas por Ingrediente', 'Búsqueda de Recetas por Filtrado']
)

# Interfaz de usuario
if selected_option == 'Inicio':
    st.write('Bienvenido a una aplicación que te ayudará"\
             " a descubrir nuevas recetas de cocina basadas"\
             " en tus ingredientes disponibles y tus preferencias culinarias."\
             " Además podrás filtrar las recetas por categorías y criterios de"\
             " busqueda para excluir ingredientes no deseados.')

elif selected_option == 'Búsqueda de Recetas por Ingrediente':
    st.markdown('<h3 id="busqueda" style="text-align: left; color: white;"\
                " font-style: italic;">Búsqueda de Recetas por Ingrediente</h3>',\
                      unsafe_allow_html=True)
    
    ingrediente = st.text_input('Ingresa un ingrediente:')
    if ingrediente:
        # Filtrar el DataFrame por ingredientes
        df_ingredientes = df[df['NER'].str.contains(ingrediente, case=False, na=False)]
        
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
    ingredientes_no_vegetarianos = ["pollo", "carne", "pavo"]

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
                    if ingrediente in row['NER']:
                        mostrar_receta = False

            # Verificar si se debe excluir la receta debido al azúcar
            if excluir_azucar and ingrediente_azucar in row['NER']:
                mostrar_receta = False

            # Verificar si se debe excluir la receta debido a ingredientes no vegetarianos
            if excluir_no_vegetarianas and ((ingredientes_no_vegetarianos[0] or ingredientes_no_vegetarianos[1] or ingredientes_no_vegetarianos[2]) in row['NER']):
                mostrar_receta = False

            # Agregar la receta a la lista si no se excluye
            if mostrar_receta:
                recetas_filtradas.append(row)

        # Calcular los índices de inicio y fin para la página actual
        inicio = (pagina - 1) * recetas_por_pagina
        fin = min(inicio + recetas_por_pagina, len(recetas_filtradas))
    
