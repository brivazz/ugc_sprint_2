conn = new Mongo();
db = conn.getDB("ugc2_movies");

db.createCollection("liked_movies");
db.createCollection("bookmarks_movies");
db.createCollection("reviewed_movies");

db.liked_films.createIndex({ film_id: 1, user_id: 1 }, { unique: true });
db.bookmarks_films.createIndex({ film_id: 1, user_id: 1 }, { unique: true });
db.reviewed_films.createIndex({ film_id: 1, user_id: 1 }, { unique: true });
