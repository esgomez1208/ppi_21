# Importar librerías
import streamlit as st

# Datos de ejemplo de recetas con sus respectivos ingredientes
recetas = {
    'Pasta con salsa de tomate': ['pasta', 'tomate', 'queso'],
    'Ensalada César': ['lechuga', 'pollo', 'crutones', 'aderezo'],
    'Pizza Margarita': ['masa de pizza', 'tomate', 'mozzarella', 'albahaca'],
    'Pata con salsa alfredo': ['pasta', 'mantequilla', 'crema de leche', 'nuez moscada']
    
}

# Interfaz de usuario
st.title('CulinaryCraft')
st.markdown('<h1 style="text-align: left;">CulinaryCraft</h1>', unsafe_allow_html=True)

ingrediente = st.text_input('Ingresa un ingrediente:')
if ingrediente:
    st.write('Recetas que incluyen', ingrediente.capitalize() + ':')
    for receta, ingredientes in recetas.items():
        if ingrediente.lower() in [ing.lower() for ing in ingredientes]:
            st.write(f'- {receta}')

# Puedes agregar más componentes de la interfaz de usuario según tus necesidades
