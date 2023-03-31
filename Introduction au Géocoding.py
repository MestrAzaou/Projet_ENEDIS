import streamlit as st
from PIL import Image 

st.set_page_config(
    page_title='Multipage App'
)

st.title('Présentation Geocoding (réalisée par des cerveaux dynamiques !)')
st.sidebar.success('Sélectionner la page souhaitée dans le menu ci-dessus.')


st.image('https://upload.wikimedia.org/wikipedia/commons/thumb/e/ea/La_Loire_%C3%A0_Orl%C3%A9ans.jpg/1200px-La_Loire_%C3%A0_Orl%C3%A9ans.jpg',
         width=800)