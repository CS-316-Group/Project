## RUNNING APP LOCALLY. THROUGH LOCAL HOST.
1. Navigate to the src folder and run:
`python -m d04_app.app`

## TODO LIST.
1. Still need a page that directly links to spotify authentication on our website.
2. Still need to redirect artist page but bigger problem is to redirect from our base dataset to one that is customized for the user.
3. Also need to figure out how to run the website through vcm if that is what we eventually want to do.





SELECT display_name, artist_name
FROM topartists, listeners,artists
WHERE topartists.listener_id = listeners.id  and topartists.artist_id=artists.id;

results=db.session.query(models.Topartists, models.Listeners,model.Artists).filter(models.Listeners.display_name == listener_name).join(models.Topartists.listener_id == models.Listeners.id).all()

results=db.session.query(models.Topartists, listeners,artists).filter(listeners.display_name == listener_name).join(topartists.listener_id == listeners.id).all();