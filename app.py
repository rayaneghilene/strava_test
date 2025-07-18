import streamlit as st
from stravalib.client import Client
from datetime import timezone
import time

# CONFIGURATION
STRAVA_CLIENT_ID = "YOUR_CLIENT_ID"
STRAVA_CLIENT_SECRET = "YOUR_CLIENT_SECRET"
REDIRECT_URI = "http://localhost:8501"  

# OAuth & Authentication
def authenticate_strava(code=None):
    client = Client()

    if code:
        try:
            token_response = client.exchange_code_for_token(
                client_id=int(STRAVA_CLIENT_ID),
                client_secret=STRAVA_CLIENT_SECRET,
                code=code
            )
            client.access_token = token_response['access_token']
            return client
        except Exception as e:
            st.error(f"Authentication failed: {e}")
            return None

    authorize_url = client.authorization_url(
        client_id=int(STRAVA_CLIENT_ID),
        redirect_uri=REDIRECT_URI,
        scope=["read", "read_all", "activity:read_all"]
    )

    st.markdown(f"[Cliquez ici pour autoriser Strava]({authorize_url})")
    return None

# Fetch recent activities
def fetch_activities(client, max_activities=5):
    activities = []
    try:
        for i, activity in enumerate(client.get_activities()):
            if i >= max_activities:
                break
            activities.append(activity)
    except Exception as e:
        st.error(f"Error fetching activities: {e}")
    return activities

# Fetch photos for an activity
def get_activity_photos(client, activity_id):
    try:
        photos = client.get_activity_photos(activity_id)
        return [photo.urls.get('600') or photo.urls.get('default') for photo in photos if photo.urls]
    except Exception as e:
        return []

# Streamlit App UI
def main():
    st.title("🔗 Analyse de vos activités Strava")
    st.write("Autorisez l'accès pour visualiser et analyser vos dernières séances.")

    code = st.experimental_get_query_params().get("code", [None])[0]
    client = authenticate_strava(code)

    if client:
        athlete = client.get_athlete()
        st.success(f"Connecté en tant que {athlete.firstname} {athlete.lastname}")
        st.write("Voici vos dernières activités 👇")

        activities = fetch_activities(client, max_activities=5)
        for activity in activities:
            st.subheader(f"🏃 {activity.name}")
            st.write(f"**Date :** {activity.start_date_local.strftime('%Y-%m-%d %H:%M')}")
            st.write(f"**Distance :** {activity.distance.kilometers:.2f} km")
            st.write(f"**Temps :** {activity.elapsed_time}")
            st.write(f"**Type :** {activity.type}")
            st.write(f"**Description :** {activity.description or '—'}")

            photos = get_activity_photos(client, activity.id)
            if photos:
                for url in photos:
                    st.image(url, use_column_width=True)
            else:
                st.write("Aucune photo disponible.")

if __name__ == "__main__":
    main()
