import { useState } from 'react';
import FilterBar from '../components/FilterBar';
import Panel from '../components/Panel';
import { useFilters } from '../context/FilterContext';
import { useData } from '../hooks/useData';
import { getReviews, analyzeReview, createReview, uploadCsv } from '../services/api';

const EMPTY = { review_text: '', product_name: '', brand: '', category: '' };

export default function Reviews() {
  const { params } = useFilters();
  const [page, setPage] = useState(1);
  const [refresh, setRefresh] = useState(0);
  const [form, setForm] = useState(EMPTY);
  const [result, setResult] = useState(null);
  const [message, setMessage] = useState('');
  const [file, setFile] = useState(null);
  const [isSample, setIsSample] = useState(false);
  const [summary, setSummary] = useState(null);
  const key = JSON.stringify(params);
  const list = useData(() => getReviews({ ...params, page }), [key, page, refresh]);
  const field = (name) => ({ value: form[name], onChange: (e) => setForm({ ...form, [name]: e.target.value }) });
  const errorOf = (e) => (e.response && e.response.data && e.response.data.error) || 'Request failed';

  const preview = async () => {
    try { setResult(await analyzeReview(form.review_text)); } catch (e) { setMessage(errorOf(e)); }
  };
  const save = async () => {
    try {
      await createReview(form);
      setMessage('Saved'); setForm(EMPTY); setResult(null); setRefresh((n) => n + 1);
    } catch (e) { setMessage(errorOf(e)); }
  };
  const upload = async () => {
    try { setSummary(await uploadCsv(file, isSample)); setRefresh((n) => n + 1); }
    catch (e) { setMessage(errorOf(e)); }
  };

  const data = list.data;
  return (
    <>
      <h1>Reviews</h1>
      <div className='grid'>
        <Panel title='Analyze one review'>
          <textarea rows={3} placeholder='Review text' {...field('review_text')} />
          <input placeholder='Product (optional)' {...field('product_name')} />
          <input placeholder='Brand (optional)' {...field('brand')} />
          <input placeholder='Category (optional)' {...field('category')} />
          <button onClick={preview}>Analyze only</button>{' '}
          <button onClick={save}>Analyze and save</button>
          {result && <p>{result.sentiment} / {result.emotion} / confidence {result.confidence == null ? '-' : result.confidence.toFixed(2)}</p>}
          {message && <p className='note'>{message}</p>}
        </Panel>
        <Panel title='Upload CSV'>
          <p className='note'>Columns: review_id, product_name, brand, category, review_text, review_date (YYYY-MM-DD)</p>
          <input type='file' accept='.csv' onChange={(e) => setFile(e.target.files[0])} />
          <label><input type='checkbox' checked={isSample} onChange={(e) => setIsSample(e.target.checked)} />
            {' '}These rows are sample data</label>
          <button disabled={!file} onClick={upload}>Upload</button>
          {summary && (
     <div>
       <p>
         <b>Upload finished.</b> {summary.inserted} added, {summary.skipped_duplicates} duplicates
         skipped, {summary.errors.length} rows with errors.
       </p>
       {summary.errors.length > 0 && (
         <ul className='note'>
           {summary.errors.slice(0, 5).map((e) => <li key={e.row}>Row {e.row}: {e.error}</li>)}
           {summary.errors.length > 5 && <li>...and {summary.errors.length - 5} more</li>}
         </ul>
       )}
     </div>
   )}
        </Panel>
      </div>
      <FilterBar />
      <Panel title={'Reviews' + (data ? ' (' + data.total + ')' : '')}>
        {list.error && <p className='note'>{list.error}</p>}
        <div className='table-wrap'>
          <table>
            <thead><tr><th>Date</th><th>Product</th><th>Review</th><th>Sentiment</th><th>Emotion</th><th>Conf.</th></tr></thead>
            <tbody>
              {(data ? data.items : []).map((r) => (
                <tr key={r.review_id}>
                  <td>{r.review_date}</td><td>{r.product || '-'}{r.is_sample ? ' (sample)' : ''}</td>
                  <td>{r.review_text.slice(0, 120)}</td><td>{r.sentiment}</td><td>{r.emotion}</td>
                  <td>{r.confidence == null ? '-' : r.confidence.toFixed(2)}{r.needs_review ? ' (low)' : ''}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <button disabled={page <= 1} onClick={() => setPage(page - 1)}>Previous</button>{' '}
        <button disabled={!data || page * data.per_page >= data.total} onClick={() => setPage(page + 1)}>Next</button>
      </Panel>
    </>
  );
}
