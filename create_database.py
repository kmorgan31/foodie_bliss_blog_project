from app import db
db.create_all()

#Initialize default tags
from app.models import Tag

categories = ["Chinese", "Indian", "Japanese", "Italian", "Caribbean"]
for category in categories:
    tag = Tag(category)
    db.session.add(tag)
db.session.commit()