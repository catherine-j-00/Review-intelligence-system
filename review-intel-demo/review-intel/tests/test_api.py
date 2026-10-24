import io

CSV = (b'review_id,product_name,brand,category,review_text,review_date\n'
       b'r1,Lipstick A,Brand A,Lipstick,Lovely shade,2026-01-10\n'
       b'r2,Lipstick A,Brand A,Lipstick,bad quality,2026-01-12\n'
       b'r3,Lipstick B,Brand B,Lipstick,Lovely colour,2026-02-01\n')


def upload(client, auth, data=CSV, sample='false'):
    return client.post('/api/reviews/bulk', headers=auth, content_type='multipart/form-data',
                       data={'file': (io.BytesIO(data), 'reviews.csv'), 'is_sample': sample})


def test_requires_login(client):
    assert client.get('/api/analytics/overview').status_code == 401


def test_bulk_and_overview(client, auth):
    assert upload(client, auth).get_json()['inserted'] == 3
    o = client.get('/api/analytics/overview', headers=auth).get_json()
    assert (o['total_reviews'], o['positive'], o['negative']) == (3, 2, 1)
    assert o['positive_pct'] == 66.7


def test_duplicates_are_skipped(client, auth):
    upload(client, auth)
    assert upload(client, auth).get_json()['skipped_duplicates'] == 3


def test_sample_data_hidden_by_default(client, auth):
    upload(client, auth, sample='true')
    assert client.get('/api/analytics/overview', headers=auth).get_json()['total_reviews'] == 0
    sample = client.get('/api/analytics/overview?data=sample', headers=auth).get_json()
    assert sample['total_reviews'] == 3


def test_bad_date_is_reported(client, auth):
    bad = b'review_id,review_text,review_date\nx1,Nice,not-a-date\n'
    out = upload(client, auth, data=bad).get_json()
    assert out['inserted'] == 0 and out['errors'][0]['row'] == 2


def test_monthly_and_filter(client, auth):
    upload(client, auth)
    months = client.get('/api/analytics/monthly', headers=auth).get_json()
    assert [m['month'] for m in months] == ['2026-01', '2026-02']
    brand = client.get('/api/analytics/overview?brand=brand%20b', headers=auth).get_json()
    assert brand['total_reviews'] == 1
