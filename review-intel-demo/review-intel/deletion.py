
from backend.app import create_app
from backend.database.db import db
from backend.database.models import Review

app = create_app()
with app.app_context():
    reviews = Review.query.all()
    count = len(reviews)

    print(f"Saved reviews found: {count}")

    if count == 0:
        print("There are no saved reviews to delete.")
    else:
        confirmation = input(
            f"Delete all {count} saved reviews and their "
            "associated analysis records? Type DELETE REVIEWS: "
        )

        if confirmation != "DELETE REVIEWS":
            print("Cancelled. No reviews were deleted.")
        else:
            for review in reviews:
                db.session.delete(review)

            db.session.commit()
            print(f"Successfully deleted {count} reviews.")
            print("Products, brands, categories and users were kept.")
