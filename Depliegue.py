import streamlit as st

# Datos de ejemplo de recetas
recetas = {
    'Pasta con salsa de tomate': ['pasta', 'tomate', 'queso'],
    'Ensalada César': ['lechuga', 'pollo', 'crutones', 'aderezo'],
    'Pizza Margarita': ['masa de pizza', 'tomate', 'mozzarella', 'albahaca'],
    # Agrega más recetas aquí
}

# Interfaz de usuario
st.title('Aplicativo de Recomendación de Cocina')

ingrediente = st.text_input('Ingresa un ingrediente:')
if ingrediente:
    st.write('Recetas que incluyen', ingrediente.capitalize() + ':')
    for receta, ingredientes in recetas.items():
        if ingrediente.lower() in [ing.lower() for ing in ingredientes]:
            st.write(f'- {receta}')

# Puedes agregar más componentes de la interfaz de usuario según tus necesidades
