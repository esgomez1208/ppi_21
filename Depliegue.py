import streamlit as st

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
    st.write('Bienvenido a la página principal de la aplicación.')
elif selected_option == 'Búsqueda de Recetas por Ingrediente':
    st.markdown('<h2 id="busqueda" style="text-align: left; color: white; font-style: italic;">Búsqueda de Recetas por Ingrediente</h2>', unsafe_allow_html=True)
    
    ingrediente = st.text_input('Ingresa un ingrediente:')
    if ingrediente:
        st.write(f'Recetas que incluyen "{ingrediente.capitalize()}":')
        for receta, ingredientes in recetas.items():
            if ingrediente.lower() in [ing.lower() for ing in ingredientes]:
                st.markdown(f'**{receta}**', unsafe_allow_html=True)
                st.write('Ingredientes:', ", ".join(ingredientes))
elif selected_option == 'Búsqueda de Recetas por Filtrado':
    st.markdown('<h2 id="filtrado" style="text-align: left; color: white; font-style: italic;">Búsqueda de Recetas por Filtrado</h2>', unsafe_allow_html=True)
    # Agrega aquí la implementación de tu otra función
