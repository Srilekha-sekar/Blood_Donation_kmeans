import streamlit as st
from Final_donor_find import main as find_donor_main
from donation_signup import main as donation_signup_main

# Main page
def main():
    st.title("Blood Donation Application")
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Go to", ["Home", "Find Donor", "Register Donor"])

    if page == "Home":
        st.write("Welcome to the Blood Donation Application!")
        st.write("Learn more about blood donation here.")

    elif page == "Find Donor":
        find_donor_main()

    elif page == "Register Donor":
        donation_signup_main()

if __name__ == "__main__":
    main()

