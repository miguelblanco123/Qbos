import streamlit as st
from streamlit_option_menu import option_menu
from tools.scheduleGenerator import scheduleGenerator

def main():
    st.set_page_config(page_title="Multi-Page App", layout="wide")
    with st.sidebar:
        menu = option_menu(
            menu_title="Speedcubing Tools",
            
            options=["Schedule Generator", 
                ],
            
            icons=["house", 
            "file-earmark"],
            
            menu_icon="cast",
            
            default_index=0,
            
            orientation="vertical",
            
            styles={
            "container": {"padding": "0!important", "background-color": "#333333"},
            "icon": {"color": "#ffffff", "font-size": "25px"},
            "nav-link": {"font-size": "16px", "text-align": "left", "margin": "0px", "--hover-color": "#444444"},
            "nav-link-selected": {"background-color": "#555555"},
            }
        )

    if menu == "Schedule Generator":
        scheduleGenerator()
        
    elif menu == "Page 1":
        st.title("Page 1")
        st.write("denme chance, luego meto mas")



if __name__ == "__main__":
    main()