# Importar librerías
import streamlit as st

# Datos de ejemplo de recetas con sus respectivos ingredientes
recetas = {
    'Pasta con salsa de tomate': ['pasta', 'tomate', 'queso'],
    'Ensalada César': ['lechuga', 'pollo', 'crutones', 'aderezo'],
    'Pizza Margarita': ['masa de pizza', 'tomate', 'mozzarella', 'albahaca'],
    'Pata con salsa alfredo': ['pasta', 'mantequilla', 'crema de leche', 'nuez moscada']
    
}

# Establecer estilo y formato personalizado
st.markdown('<h1 style="text-align: left; color: blue;">CulinaryCraft</h1>', unsafe_allow_html=True)

# Estilo para el título de las recetas
st.markdown('<h2 style="color: blue;">Recetas:</h2>', unsafe_allow_html=True)

# Interfaz de usuario
ingrediente = st.text_input('Ingresa un ingrediente:')
if ingrediente:
    st.write(f'Recetas que incluyen "{ingrediente.capitalize()}":')
    for receta, ingredientes in recetas.items():
        if ingrediente.lower() in [ing.lower() for ing in ingredientes]:
            st.markdown(f'**{receta}**', unsafe_allow_html=True)
            st.write('Ingredientes:', ", ".join(ingredientes))

