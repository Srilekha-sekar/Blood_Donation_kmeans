import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import folium
from streamlit_folium import folium_static
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score, davies_bouldin_score

# Function to get coordinates from location address
def get_coordinates(location):
    geolocator = Nominatim(user_agent="geo_locator")
    try:
        coordinates = geolocator.geocode(location, timeout=10)
        if coordinates:
            return (coordinates.latitude, coordinates.longitude)
        else:
            st.warning("Location not found. Please enter a valid location.")
            return None
    except AttributeError:
        st.warning("Geocoding service timed out. Please try again later.")
        return None

# Function to preprocess data and apply K-means clustering
def apply_kmeans(donor_data):
    # Select relevant features
    selected_features = ['Latitude', 'Longitude', 'Recency (months)', 'Frequency (times)', 'Monetary (c.c. blood)', 'Time (months)']
    X = donor_data[selected_features]

    # Standardize numerical features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Apply K-means clustering
    kmeans = KMeans(n_clusters=3, random_state=42)  # Specify the number of clusters
    donor_data['Cluster'] = kmeans.fit_predict(X_scaled)

    return donor_data

# Function to display clustered donors on map and in a table
def display_clustered_donors(donor_data, location_coordinates, threshold_distance, blood_type):
    st.title("Cluster Analysis")
    
    # Filter donors based on distance and blood type
    donor_data['Distance (km)'] = donor_data.apply(lambda row: geodesic(location_coordinates, (row['Latitude'], row['Longitude'])).kilometers, axis=1)
    filtered_donors = donor_data[(donor_data['Distance (km)'] <= threshold_distance) & (donor_data['Blood Type'] == blood_type)]

    if len(filtered_donors) > 0:
        # Display donors in a table
        st.subheader("Nearby Donors:")
        st.write(filtered_donors[['Names', 'Age', 'Gender', 'Blood Type', 'Contact Number', 'Country', 'State', 'District', 'Location', 'Pincode']])

        # Create a folium map
        cluster_map = folium.Map(location=[location_coordinates[0], location_coordinates[1]], zoom_start=10)

        # Add markers for each donor colored by cluster
        for _, donor in filtered_donors.iterrows():
            cluster_color = 'red' if donor['Cluster'] == 0 else 'green' if donor['Cluster'] == 1 else 'blue'
            popup_content = f"""
            <b>Name:</b> {donor['Names']}<br>
            <b>Cluster:</b> {donor['Cluster']}<br>
            <b>Location:</b> {donor['Location']}<br>
            <b>Blood Type:</b> {donor['Blood Type']}<br>
            """
            folium.Marker(
                location=[donor['Latitude'], donor['Longitude']],
                popup=folium.Popup(popup_content, max_width=300),
                icon=folium.Icon(color=cluster_color)
            ).add_to(cluster_map)

        # Render the map
        st.subheader("Map View:")
        folium_static(cluster_map)
    else:
        st.write("No donors with Blood Type", blood_type, "found within", threshold_distance, "km of the specified location.")

# Function to calculate and display clustering evaluation metrics
def display_clustering_metrics(donor_data):
    st.subheader("Clustering Evaluation Metrics:")

    # Define a range of cluster numbers to evaluate
    cluster_range = range(2, 10)

    inertia_scores = []
    silhouette_scores = []
    davies_bouldin_scores = []

    for n_clusters in cluster_range:
        # Apply K-means clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        donor_data['Cluster'] = kmeans.fit_predict(donor_data[['Latitude', 'Longitude']])

        # Inertia
        inertia_scores.append(kmeans.inertia_)

        # Silhouette Score
        silhouette_scores.append(silhouette_score(donor_data[['Latitude', 'Longitude']], donor_data['Cluster']))

        # Davies–Bouldin Index
        davies_bouldin_scores.append(davies_bouldin_score(donor_data[['Latitude', 'Longitude']], donor_data['Cluster']))

    # Display the metrics
    st.line_chart(pd.DataFrame({'Inertia': inertia_scores, 'Silhouette Score': silhouette_scores, 'Davies–Bouldin Index': davies_bouldin_scores}, index=cluster_range))

# Streamlit app
def main():
    # Set page config

    logo_path = "logo.jpeg"

    # Display title and logo
    col1, col2 = st.columns([8, 1])
    with col1:
        st.markdown(f'<p style="background-color:#ffffff;color:#000000;font-size:62px;border-radius:2%; text-align:center;"><strong>Find Your Donor</strong></p>', unsafe_allow_html=True)
    with col2:
        st.image(logo_path, width=100)

    # Load the donor dataset
    donor_data = pd.read_csv('donor_dataset.csv')

    # Apply K-means clustering
    donor_data = apply_kmeans(donor_data)

    # Collect user input for location
    location_address = st.text_input("Enter Location Address (City or State):")

    # Define variables to store user inputs
    location_coordinates = None
    threshold_distance = None
    blood_type = None

    if location_address:
        # Define the threshold distance (in kilometers)
        threshold_distance = st.number_input('Threshold Distance (km):', value=20.0)

        # Select blood type
        blood_type = st.selectbox('Select Blood Type:', ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'])

        if st.button("Get Coordinates"):
            # Get coordinates for the user input location
            location_coordinates = get_coordinates(location_address)

            if location_coordinates:
                st.success("Location coordinates:")
                st.write(location_coordinates)

                # Display clustered donors on map and in a table
                display_clustered_donors(donor_data, location_coordinates, threshold_distance, blood_type)

                # Display clustering evaluation metrics
                display_clustering_metrics(donor_data)

if __name__ == "__main__":
    main()
