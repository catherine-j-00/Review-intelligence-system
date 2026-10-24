def serialize_review(r):
    a, p = r.analysis, r.product
    return {
        'review_id': r.review_id, 'external_id': r.external_id,
        'review_text': r.review_text,
        'review_date': r.review_date.isoformat() if r.review_date else None,
        'product': p.product_name if p else None,
        'brand': p.brand.brand_name if p and p.brand else None,
        'category': p.category.category_name if p and p.category else None,
        'sentiment': a.sentiment, 'emotion': a.emotion,
        'confidence': a.confidence_score, 'needs_review': a.needs_review,
        'is_sample': r.is_sample,
    }
