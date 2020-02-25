--What are a user’s top artists?
  
SELECT DISTINCT artist_name, TopArtists.artist_id
FROM Artists JOIN TopArtists ON Artists.id = TopArtists.artist_id
WHERE listener_id = '314xcqarki42gnkosjtfplluumya' AND time_span = 'short_term';


--What are a user’s top tracks?

SELECT Tracks.track_name, TopTracks.track_id
FROM TopTracks JOIN Tracks ON TopTracks.track_id = Tracks.id
WHERE listener_id = '314xcqarki42gnkosjtfplluumyb' AND time_span = 'short_term';