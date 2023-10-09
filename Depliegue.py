import streamlit as st
import pandas as pd

# Función que utiliza la base de datos de 100 mil líneas de recetas
def cargar_dataset():
    df = pd.read_csv('CienMilRecetas.csv')
    return df

df = cargar_dataset()


# Datos de ejemplo de recetas con sus respectivos ingredientes
recetas = {
    'Pasta con salsa de tomate': ['pasta', 'tomate', 'queso'],
    'Ensalada César': ['lechuga', 'pollo', 'crutones', 'aderezo'],
    'Pizza Margarita': ['masa de pizza', 'tomate', 'mozzarella', 'albahaca'],
    'Pata con salsa alfredo': ['pasta', 'mantequilla', 'crema de leche', 'nuez moscada']
}

# Establecer estilo y formato personalizado
st.markdown('<h1 style="text-align: left; color: skyblue;">CulinaryCraft</h1>', unsafe_allow_html=True)

# Crear una barra lateral para la tabla de contenidos
st.sidebar.title('Tabla de Contenido')
selected_option = st.sidebar.selectbox(
    'Selecciona una opción:',
    ['Inicio', 'Búsqueda de Recetas por Ingrediente', 'Búsqueda de Recetas por Filtrado']
)

# Interfaz de usuario
if selected_option == 'Inicio':
    st.write('Bienvenido a una aplicación que te ayudará a descubrir nuevas recetas de cocina basadas en tus ingredientes disponibles y tus preferencias culinarias. Además podrás filtrar las recetas por categorías y criterios de busqueda para excluir ingredientes no deseados.')

elif selected_option == 'Búsqueda de Recetas por Ingrediente':
    st.markdown('<h2 id="busqueda" style="text-align: left; color: white; font-style: italic;">Búsqueda de Recetas por Ingrediente</h2>', unsafe_allow_html=True)
    
    ingrediente = st.text_input('Ingresa un ingrediente:')
    if ingrediente:
        df_ingredientes = df[df['NER'].str.contains(ingrediente, case=False, na=False)]
        
        # Mostrar los nombres de las recetas
        if not df_ingredientes.empty:
            st.subheader('Recetas que contienen "{}":'.format(ingrediente))
            for idx, row in df_ingredientes.iterrows():
                st.write(row['Título'])
        
        """st.write(f'Recetas que incluyen "{ingrediente.capitalize()}":')
        for receta, ingredientes in recetas.items():
            if ingrediente.lower() in [ing.lower() for ing in ingredientes]:
                st.markdown(f'**{receta}**', unsafe_allow_html=True)
                st.write('Ingredientes:', ", ".join(ingredientes))"""
        
elif selected_option == 'Búsqueda de Recetas por Filtrado':
    st.markdown('<h2 id="filtrado" style="text-align: left; color: white; font-style: italic;">Búsqueda de Recetas por Filtrado</h2>', unsafe_allow_html=True)
    st.write('Ingresa los ingredientes que deseas excluir:')
    ingredientes_excluir = st.text_input('Ingredientes a excluir (separados por comas):')
    
    # Convertir la entrada en una lista de ingredientes a excluir
    ingredientes_excluir = [ingrediente.strip() for ingrediente in ingredientes_excluir.split(',')]
    
    if ingredientes_excluir:
        st.write(f'Recetas que no contienen los siguientes ingredientes: {", ".join(ingredientes_excluir)}')
        for receta, ingredientes in recetas.items():
            if not any(ing.lower() in ingredientes_excluir for ing in ingredientes):
                st.markdown(f'**{receta}**', unsafe_allow_html=True)
                st.write('Ingredientes:', ", ".join(ingredientes))


