import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import os


# Function to get coordinates from location address
def get_coordinates(location):
    geolocator = Nominatim(user_agent="geo_locator")
    try:
        location = geolocator.geocode(location)
        if location:
            return location.latitude, location.longitude
        else:
            st.warning("Location not found. Please enter a valid location.")
            return None, None
    except GeocoderTimedOut:
        st.warning("Geocoding service timed out. Please try again later.")
        return None, None

# Function to load donor dataset
def load_dataset(dataset_filename):
    if not os.path.isfile(dataset_filename):
        return pd.DataFrame(columns=["Names", "Age", "Gender", "Blood Type", "Medical Conditions", "Allergies", "Blood Pressure", "Height (cm)", "Weight (kg)", "Contact Number", "Country", "State", "District", "Location", "Pincode", "Latitude", "Longitude", "Recency (months)", "Frequency (times)", "Monetary (c.c. blood)", "Time (months)"])
    else:
        return pd.read_csv(dataset_filename)

# Function to update donor dataset
def update_dataset(donor_data, new_donor_info, dataset_filename):
    # Append new donor information to the dataset
    new_donor = pd.DataFrame([new_donor_info])
    donor_data = pd.concat([donor_data, new_donor], ignore_index=True)
    
    # Save the updated dataset to the CSV file
    donor_data.to_csv(dataset_filename, index=False)
    
    return donor_data

# Function to get donor information
def get_donor_info():
    st.title("Donor Information")
    names = st.text_input("Names:")
    age = st.number_input("Age:", min_value=0, max_value=150)
    gender = st.selectbox("Gender:", ["Male", "Female", "Other"])
    blood_type = st.selectbox("Blood Type:", ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'])
    medical_conditions = st.text_input("Medical Conditions:")
    allergies = st.text_input("Allergies:")
    blood_pressure = st.text_input("Blood Pressure:")
    height_cm = st.number_input("Height (cm):", min_value=0)
    weight_kg = st.number_input("Weight (kg):", min_value=0)
    contact_number = st.text_input("Contact Number:")
    country = st.text_input("Country:")
    state = st.text_input("State:")
    district = st.text_input("District:")
    location = st.text_input("Location:")
    pincode = st.text_input("Pincode:")
    
    # Ask if the donor has donated blood before
    previous_donation = st.radio("Have you donated blood before?", ("Yes", "No"))
    
    # Default values for previous donation fields
    recency_months = 0
    frequency_times = 0
    monetary_cc_blood = 0
    time_months = 0
    
    if previous_donation == "Yes":
        # Additional fields for previous donation information
        recency_months = st.number_input("Recency (months):", min_value=0)
        frequency_times = st.number_input("Frequency (times):", min_value=0)
        monetary_cc_blood = st.number_input("Monetary (c.c. blood):", min_value=0)
        time_months = st.number_input("Time (months) since first donation:", min_value=0)

    if st.button("Submit"):
        # Get coordinates for the entered location
        latitude, longitude = get_coordinates(location)
        if latitude is not None and longitude is not None:
            donor_info = {
                "Names": names,
                "Age": age,
                "Gender": gender,
                "Blood Type": blood_type,
                "Medical Conditions": medical_conditions,
                "Allergies": allergies,
                "Blood Pressure": blood_pressure,
                "Height (cm)": height_cm,
                "Weight (kg)": weight_kg,
                "Contact Number": contact_number,
                "Country": country,
                "State": state,
                "District": district,
                "Location": location,
                "Pincode": pincode,
                "Latitude": latitude,
                "Longitude": longitude,
                "Recency (months)": recency_months,
                "Frequency (times)": frequency_times,
                "Monetary (c.c. blood)": monetary_cc_blood,
                "Time (months)": time_months
            }
            
            return donor_info
        else:
            st.error("Failed to retrieve coordinates for the entered location. Please try again.")
    return None

# Function to display donor information tab
def donor_info_tab(donor_data, dataset_filename):
    st.title("Donor Information")
    donor_info = get_donor_info()
    if donor_info:
        st.success("Donor information submitted successfully!")
        st.write("Donor Information:")
        st.write(donor_info)
        # Update the dataset with new donor information
        update_dataset(donor_data, donor_info, dataset_filename)

# Main function
def main():
    # Load the dataset
    dataset_filename = "donor_dataset.csv"
    donor_data = load_dataset(dataset_filename)

    # Display donor information tab
    donor_info_tab(donor_data, dataset_filename)

if __name__ == "__main__":
    main()
