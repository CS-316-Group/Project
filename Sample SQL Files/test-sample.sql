--What are a user’s top artists?

SELECT DISTINCT artist_name, TopArtists.artist_id
FROM Artists JOIN TopArtists ON Artists.artist_id = TopArtists.artist_id
WHERE listener_id = '314xcqarki42gnkosjtfplluumya' AND time_span = 'short_term';


--What are a user’s top tracks?

CREATE VIEW TopTrackNames_1 AS
SELECT Tracks.track_id, Tracks.track_name
FROM TopTracks JOIN Tracks ON TopTracks.track_id = Tracks.track_id
WHERE listener_id = '314xcqarki42gnkosjtfplluumya' AND time_span = 'short_term';

CREATE VIEW TopTrackWithArtists_1 AS
SELECT TopTrackNames.track_name, CreatedBy.artist_id
FROM CreatedBy JOIN TopTrackNames ON TopTrackNames.track_id = CreatedBy.track_id;

CREATE VIEW TopTracksAndArtistsNames_1 AS
SELECT TopTrackWithArtists.track_name, Artists.artist_name
FROM TopTrackNames JOIN Artists ON TopTrackNames.artist_id = Artists.artist_id;

SELECT *
FROM TopTracksAndArtistNames_1;


--What top artists do two users have in common?

CREATE VIEW TopArtists_1 AS
SELECT DISTINCT artist_name, TopArtists.artist_id
FROM Artists JOIN TopArtists ON Artists.artist_id = TopArtists.artist_id
WHERE listener_id = '314xcqarki42gnkosjtfplluumya' AND time_span = 'short_term';


CREATE VIEW TopArtists_2 AS
SELECT DISTINCT artist_name, TopArtists.artist_id
FROM Artists JOIN TopArtists ON Artists.artist_id = TopArtists.artist_id
WHERE listener_id = '314xcqarki42gnkosjtfplluumya' AND time_span = 'short_term';

SELECT *
FROM TopArtists_1 JOIN TopArtists_2 ON TopArtists_1.artist_id = TopArtists_2.artist_id;


--What top tracks do two users have in common?

CREATE VIEW TopTrackNames_1 AS
SELECT Tracks.track_id, Tracks.track_name
FROM TopTracks JOIN Tracks ON TopTracks.track_id = Tracks.track_id
WHERE listener_id = '314xcqarki42gnkosjtfplluumya' AND time_span = 'short_term';

CREATE VIEW TopTrackWithArtists_1 AS
SELECT TopTrackNames.track_name, TopTrackNames.track_id CreatedBy.artist_id
FROM CreatedBy JOIN TopTrackNames ON TopTrackNames.track_id = CreatedBy.track_id;

CREATE VIEW TopTracksAndArtistsNames_1 AS
SELECT TopTrackWithArtists.track_name, TopTrackWithArtists.track_id Artists.artist_name, Artists.artist_id
FROM TopTrackNames JOIN Artists ON TopTrackNames.artist_id = Artists.artist_id;

CREATE VIEW TopTrackNames_2 AS
SELECT Tracks.track_id, Tracks.track_name
FROM TopTracks JOIN Tracks ON TopTracks.track_id = Tracks.track_id
WHERE listener_id = '314xcqarki42gnkosjtfplluumya' AND time_span = 'short_term';

CREATE VIEW TopTrackWithArtists_2 AS
SELECT TopTrackNames.track_name, TopTrackNames.track_id, CreatedBy.artist_id
FROM CreatedBy JOIN TopTrackNames ON TopTrackNames.track_id = CreatedBy.track_id;

CREATE VIEW TopTracksAndArtistsNames_2 AS
SELECT TopTrackWithArtists.track_name, TopTrackWithArtists.track_id Artists.artist_name, Artists.artist_id
FROM TopTrackNames JOIN Artists ON TopTrackNames.artist_id = Artists.artist_id;

SELECT * 
FROM TopTracksAndArtistNames_1 JOIN TopTracksAndArtistNames_2 ON TopTracksAndArtistNames_1.track_id = TopTracksAndArtistNames_2.track_id 
AND TopTracksAndArtistNames_1.artist_id = TopTracksAndArtistsNames_2.artist_id;
