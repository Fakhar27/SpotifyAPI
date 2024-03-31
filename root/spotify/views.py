from django.shortcuts import render, redirect
import requests
from .models import SpotifyUserInfo,FormDataModel
import csv
import os
from django.contrib.auth.decorators import login_required

#SPOTIFY API CREDENTIALS
CLIENT_ID = ''
CLIENT_SECRET = ''
REDIRECT_URI = ''

#USER FIRST REDIRECTED TO ENTER INFORMATION AND SAVED IN FormDataModel AND THEN THROUGH API CREDENTIALS LOGGED IN SPOTIFY ACCOUNT
def spotify_login(request):
    if request.method == 'POST':
        first_name = request.POST.get('firstName')
        last_name = request.POST.get('lastName')
        contact_number = request.POST.get('contactNumber')
        email = request.POST.get('email')

        if first_name and last_name and contact_number and email:
            form_data = FormDataModel.objects.create(
                first_name=first_name,
                last_name=last_name,
                contact_number=contact_number,
                email=email
            )
            
            form_data.save()
            scope = 'user-library-read user-read-email playlist-read-private user-follow-read'
            url = f'https://accounts.spotify.com/authorize?response_type=code&client_id={CLIENT_ID}&scope={scope}&redirect_uri={REDIRECT_URI}'
            return redirect(url)
        else:
            return render(request, 'error.html')

    return render(request, 'index.html')


#THIS FUNCTION WILL BE THE NEXT CONTROLFLOW IF USER IS LOGGED IN SPOTIFYAPI SUCCESSFULLY AND HERE SESSIONTOKENS AND OTHER IMPORTANT STUFF WILL BE GENERATED
def spotify_callback(request):
    code = request.GET.get('code')
    if not code:
        return redirect('index.html')

    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    response = requests.post('https://accounts.spotify.com/api/token', data=data, headers=headers)
    response_json = response.json()

    if 'access_token' not in response_json:
        return redirect('error')

    access_token = response_json['access_token']
    request.session['access_token'] = access_token
    
    return redirect('user_info')

#NEXT CONTROLFLOW IS IN THIS FUNCTION WHERE REQUIRED INFORMATION OF THAT PARTICULAR USER IS RETRIEVED AND FORWARDED TO FRONTEND, DEPENDS ON ACCESSTOKEN OTHERWISE WILL NOT RUN 
#THIS FETCHING IS DONE DIRECTLY FROM SPOTIFYAPI NO THIRD PARTY LIBRARY IS USED LIKE SPOTIPY
#INFO IS STORED IN SPOTIFYUSERMODEL AND CSV FILE
def user_info(request):
    if not request.session.get('access_token'):
        return redirect('index') 

    access_token = request.session['access_token']

    print(f"Using access token: {access_token}")

    url = 'https://api.spotify.com/v1/me'
    followed_artists_url = 'https://api.spotify.com/v1/me/following?type=artist&limit=20'
    playlists_url = 'https://api.spotify.com/v1/me/playlists'
    tracks_url = 'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'
    headers = {'Authorization': f'Bearer {access_token}'}

    try:
        response_profile = requests.get(url, headers=headers)
        response_profile_json = response_profile.json()
        
        playlists_response = requests.get(playlists_url, headers=headers)
        playlists_data = playlists_response.json()
        print("Playlists Data:", playlists_data)

        response_artists = requests.get(followed_artists_url, headers=headers)
        response_artists_json = response_artists.json()
        
        print("Profile Response:", response_profile_json)
        print("Artists Response:", response_artists_json)

        if response_profile.status_code != 200 or response_artists.status_code != 200:
            return render(request, 'error.html', {'error_message': 'Error fetching user information'})

        user_info = response_profile_json
        display_name = user_info.get('display_name')
        email = user_info.get('email') 
        explicit_content = user_info.get('explicit_content', {})
        external_urls = user_info.get('external_urls', {})
        followers_info = user_info.get('followers', {})
        playlists = playlists_data.get('items', [])
        followed_artists = response_artists_json.get('artists', {}).get('items', [])
        for playlist in playlists_data.get('items', []):
            playlist_id = playlist.get('id')
            tracks_response = requests.get(tracks_url.format(playlist_id=playlist_id), headers=headers)
            tracks_data = tracks_response.json().get('items', [])

            playlist['tracks'] = tracks_data

        context = {
            'display_name': display_name,
            'email': email,
            'explicit_content': explicit_content,
            'external_urls': external_urls,
            'followers_info': followers_info,
            'playlists': playlists,
            'followed_artists': followed_artists,  
            'tracks_data': tracks_data,
        }
        
        user_info = SpotifyUserInfo.objects.get_or_create(
            display_name=response_profile_json.get('display_name'),
            email=response_profile_json.get('email'),
            filter_enabled=response_profile_json.get('explicit_content', {}).get('filter_enabled', False),
            filter_locked=response_profile_json.get('explicit_content', {}).get('filter_locked', False),
            spotify_url=response_profile_json.get('external_urls', {}).get('spotify', ''),
            followers_count=response_profile_json.get('followers', {}).get('total', 0),
            playlists_data=playlists_data.get('items', []),
            followed_artists_data=response_artists_json.get('artists', {}).get('items', []),
            tracks_data=playlists_data
        )
        user_info = user_info[0]  
        user_info.save()
        
        csv_folder = 'media/csv_files'  
        os.makedirs(csv_folder, exist_ok=True)
        csv_path = os.path.join(csv_folder, 'spotify_user_info.csv')

        with open(csv_path, 'w', newline='',encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(['Display Name', 'Email', 'Filter Enabled', 'Filter Locked', 'Spotify URL', 'Followers Count', 'Playlist Names', 'Artist Names'])
            csv_writer.writerow([
                display_name,
                email,
                explicit_content.get('filter_enabled', False),
                explicit_content.get('filter_locked', False),
                external_urls.get('spotify', ''),
                followers_info.get('total', 0),
                ', '.join([playlist['name'] for playlist in playlists]),
                ', '.join([artist['name'] for artist in followed_artists]),
            ])
            
        return render(request, 'user_info.html', context)

    #EXCEPTION HANDLING IN TERMS OF REQUEST TIMEOUT
    except requests.exceptions.RequestException as e:
        return render(request, 'error.html', {'error_message': f"Error fetching user information: {e}"}) 
    
@login_required(login_url='')
def error(request):
    return render(request, 'error.html')


#CODE PROTOTYPE OF SPOTIPY LIBRARY


# from django.http import HttpResponse
# from django.shortcuts import render
# from .models import SpotifyData,FormDataModel
# import csv
# from django.shortcuts import redirect
# import spotipy
# from spotipy.oauth2 import SpotifyOAuth
# import uuid

# # def export_to_csv(request):
# #     data = SpotifyData.objects.all()

# #     response = HttpResponse(content_type='text/csv')
# #     response['Content-Disposition'] = 'attachment; filename="spotifydata.csv"'

# #     fieldnames = ['_id', 'user_id', 'country', 'playlist_names', 'followed_artists', 'top_tracks_country', 'top_tracks', 'saved_tracks', 'saved_albums', 'recommendations']
# #     writer = csv.DictWriter(response, fieldnames=fieldnames)

# #     writer.writeheader()
# #     for item in data:
# #         writer.writerow({
# #             '_id': item._id,
# #             'user_id': item.user_id,
# #             'country': item.country,
# #             'playlist_names': item.playlist_names,
# #             'followed_artists': item.followed_artists,
# #             'top_tracks_country': item.top_tracks_country,
# #             'top_tracks': item.top_tracks,
# #             'saved_tracks': item.saved_tracks,
# #             'saved_albums': item.saved_albums,
# #             'recommendations': item.recommendations,
# #         })

# #     return response

# client_id = 'd9be9241e5904153bd8b1f1099a3360f'
# client_secret = 'e34589ff33834dfdad90a2d0461bc414'
# redirect_uri = 'http://127.0.0.1:8000/spotify/'
# sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
#                                                client_secret=client_secret,
#                                                redirect_uri=redirect_uri,
#                                                scope='user-library-read playlist-read-private user-follow-read'))

# def generate_recommendations(request):
#     # access_token = request.session.get('spotify_access_token')
#     # if not access_token:
#     #     return redirect('index')  

#     # sp = spotipy.Spotify(auth=access_token)
    
#     # Spotify API integration code here
#     # client_id = '987af1628d2a4031ac05b3bf65320ef1'
#     # client_secret = 'c72580e86f4849c8a80e1458ee3ead0b'
#     # redirect_uri = 'http://spotify.twodotzero.digital/callback'

#     # username = 'twodotzero'
#     # password = 'twodotzero@123'
#     # escaped_username = quote_plus(username)
#     # escaped_password = quote_plus(password)
#     # Initialize spotipy with OAuth2 authentication
#     # sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
#     #                                                client_secret=client_secret,
#     #                                                redirect_uri=redirect_uri,
#     #                                                scope='user-library-read playlist-read-private user-follow-read'))

#     if request.method == 'POST':
#         submission_id = str(uuid.uuid4())
#         form_data = {
#             '_id': submission_id,  # Set _id field to the UUID
#             'firstName': request.POST.get('firstName', ''),
#             'lastName': request.POST.get('lastName', ''),
#             'contactNumber': request.POST.get('contactNumber', ''),
#             'email': request.POST.get('email', ''),
#         }
#         form_result = FormDataModel.objects.create(**form_data)

#         access_token = request.session.get('spotify_access_token')
#         if not access_token:
#             return redirect('spotify_login')  # Redirect to your Spotify login view if access token is missing

#         sp = spotipy.Spotify(auth=access_token)

#         # Retrieve user's profile information
#         user_profile = sp.current_user()
#         display_name = user_profile.get("display_name", "")
#         user_id = user_profile.get("id", "")
#         country = user_profile.get("country", "")

#         # Retrieve user's playlists
#         playlists = sp.current_user_playlists()
#         playlist_names = [playlist["name"] for playlist in playlists["items"]]
        
#         # Retrieve user's followed artists
#         followed_artists = sp.current_user_followed_artists()
#         artist_names = [artist["name"] for artist in followed_artists["artists"]["items"]]
#         followed_artists_str = ", ".join(artist_names)

#         # Retrieve featured playlists for the user's country
#         featured_playlists = sp.featured_playlists(country=country)
#         playlist_ids = [playlist['id'] for playlist in featured_playlists['playlists']['items']]

#         # Retrieve user's top tracks
#         top_tracks = sp.current_user_top_tracks(limit=20, time_range='medium_term')
#         top_tracks_names = [track["name"] for track in top_tracks["items"]]
#         top_tracks_str = ", ".join(top_tracks_names)

#         # Retrieve user's saved tracks
#         saved_tracks = sp.current_user_saved_tracks(limit=20)
#         saved_tracks_names = [item["track"]["name"] for item in saved_tracks["items"]]
#         saved_tracks_str = ", ".join(saved_tracks_names)
        
#         # Retrieve user's saved albums
#         saved_albums = sp.current_user_saved_albums(limit=20)
#         saved_album_names = [album["album"]["name"] for album in saved_albums["items"]]
#         saved_albums_str = ", ".join(saved_album_names)

#         # Retrieve tracks from the featured playlists
#         top_tracks_country_names = []
#         for playlist_id in playlist_ids:
#             tracks = sp.playlist_tracks(playlist_id)
#             track_names = [track['track']['name'] for track in tracks['items']]
#             top_tracks_country_names.extend(track_names)

#         top_tracks_country_str = ", ".join(top_tracks_country_names)

#         # Generate personalized recommendations
#         recommendations = generate_recommendations(user_id)

#         # Assuming you have a Django model for Spotify data
#         spotify_data = {
#             '_id': submission_id,  # Set _id field to the same UUID
#             'user_id': user_id,
#             'country': country,
#             'playlist_names': playlist_names,
#             'followed_artists': followed_artists_str,
#             'top_tracks_country': top_tracks_country_str,
#             'top_tracks': top_tracks_str,
#             'saved_tracks': saved_tracks_str,
#             'saved_albums': saved_albums_str,
#             'recommendations': recommendations
#         }
#         # Save Spotify data to Django model
#         spotify_result = SpotifyData.objects.create(**spotify_data)  # Uncomment and replace SpotifyDataModel with your actual model

#         # Redirect after processing
#         if form_result and spotify_result:
#             return redirect('thankyou')  # Uncomment and replace 'thank_you_page' with your actual URL name
#         else:
#             return render(request, 'error.html')  # Uncomment and replace 'error_page.html' with your actual template

#     return render(request, 'index.html')





# # {"access_token": "BQCxv2WF46SZ4_scvBFXi6ycnJfevAywNR-DDQYpvpvmK3YUrhQvWb2mmKvMIaveqWsfLxsNBgBdWSYjyXFRF0QjMFYCrwV-N2Nwjs4_On8oNbkC4gzmjBIr_wgbz0x0Hjpd6__ots_wDtaPdBGhUUDCOuVsEg6rdAxAhlcJlFFk7EV12AQBj-jbRfthTN0QC4AEUZ04QsfqeCmd07PprFzeYJRsI3M8X26hh-6wd74UUzYp5_PxrbS_ddBlaFxxswd0NGk_FGhPnwcmCx1lMZ7KkA", "token_type": "Bearer", "expires_in": 3600, "scope": "playlist-read-private user-library-read user-follow-read", "expires_at": 1711661503, "refresh_token": "AQAVysioKOTxR2R-EVu9DkFYzWfj2FbNY50ZF2a2x1h9UX4O_CyyMjGd3mGM_bihc0Za6Rio087rWHKXXo041POpFDDqitgb6by5xqo6jP8PtfiouqCrcmW6IasRE8Ux3xw"}
