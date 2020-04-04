--What artists does each user listen to?

SELECT display_name, artist_name
FROM topartists, listeners,artists
WHERE topartists.listener_id = listeners.listener_id and topartists.artist_id=artists.artist_id;


--Which artists have a popularity above 50?

SELECT artist_name
FROM artists
WHERE artist_pop>=50;


--What is the artist id, popularity, and number of followers of a particular listener's top artists in the short time span?

select a1.artist_id, a1.artist_pop, a1.num_followers 
from artists as a1 
where a1.artist_id in 
    (select a2.artist_id 
     from topartists as a2
     where listener_id='314xcqarki42gnkosjtfplluumya' and time_span='short_term'
    );


--What are the genre and characteristics of a particular user's top tracks in the short term?

select * 
from albumhasgenre 
natural join 
    (select * 
    from tracks as t1
    natural join albumcontainstrack
    where t1.track_id in (
                 select t2.track_id 
                  from toptracks as t2 
                  where listener_id='314xcqarki42gnkosjtfplluumya' and time_span='short_term')
                  ) as track_album_info
where albumhasgenre.album_id = track_album_info.track_id;