
import { useFilters } from '../context/FilterContext';
import { useData } from '../hooks/useData';
import {
  getBrands,
  getCategories,
  getProducts,
  getEmotions,
} from '../services/api';

const MONTHS = [
  'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec',
];

function Select({ label, value, onChange, children }) {
  return (
    <label>
      {label}
      <select value={value} onChange={onChange}>
        <option value="">All</option>
        {children}
      </select>
    </label>
  );
}

export default function FilterBar() {
  const { filters, setFilters, reset } = useFilters();

  const brands = useData(() => getBrands(), []);
  const categories = useData(() => getCategories(), []);
  const products = useData(() => getProducts(), []);
  const emotions = useData(() => getEmotions({ data: 'all' }), []);

  const allProducts = products.data || [];
  const allBrands = brands.data || [];
  const allCategories = categories.data || [];

  // Check which category and brand each product belongs to.
  // Supports either direct name fields or nested objects.
 const getBrandName = (p) =>
  typeof p.brand === 'string'
    ? p.brand
    : p.brand?.brand_name ?? p.brand_name ?? '';

const getCategoryName = (p) =>
  typeof p.category === 'string'
    ? p.category
    : p.category?.category_name ?? p.category_name ?? '';

  // Products matching the currently selected brand and category.
  const filteredProducts = allProducts.filter((p) => {
    const matchesBrand =
      !filters.brand || getBrandName(p) === filters.brand;

    const matchesCategory =
      !filters.category || getCategoryName(p) === filters.category;

    return matchesBrand && matchesCategory;
  });

  // Show brands that have products in the selected category.
  const filteredBrands = allBrands.filter((b) =>
    allProducts.some((p) => {
      const matchesBrand = getBrandName(p) === b.brand_name;
      const matchesCategory =
        !filters.category || getCategoryName(p) === filters.category;

      return matchesBrand && matchesCategory;
    })
  );

  // Show categories that have products from the selected brand.
  const filteredCategories = allCategories.filter((c) =>
    allProducts.some((p) => {
      const matchesCategory = getCategoryName(p) === c.category_name;
      const matchesBrand =
        !filters.brand || getBrandName(p) === filters.brand;

      return matchesCategory && matchesBrand;
    })
  );

  // Reset the product when brand/category changes.
  const set = (key) => (e) => {
    const value = e.target.value;

    if (key === 'category') {
      setFilters({
        ...filters,
        category: value,
        product: '',
      });
    } else if (key === 'brand') {
      setFilters({
        ...filters,
        brand: value,
        product: '',
      });
    } else {
      setFilters({ ...filters, [key]: value });
    }
  };

  return (
    <div className="filters panel">
      <Select
        label="Category"
        value={filters.category}
        onChange={set('category')}
      >
        {filteredCategories.map((c) => (
          <option key={c.category_id} value={c.category_name}>
            {c.category_name}
          </option>
        ))}
      </Select>

      <Select
        label="Brand"
        value={filters.brand}
        onChange={set('brand')}
      >
        {filteredBrands.map((b) => (
          <option key={b.brand_id} value={b.brand_name}>
            {b.brand_name}
          </option>
        ))}
      </Select>

      <Select
        label="Product"
        value={filters.product}
        onChange={set('product')}
      >
        {filteredProducts.map((p) => (
          <option key={p.product_id} value={p.product_name}>
            {p.product_name}
          </option>
        ))}
      </Select>

      <Select
        label="Month"
        value={filters.month}
        onChange={set('month')}
      >
        {MONTHS.map((m, i) => (
          <option key={m} value={i + 1}>
            {m}
          </option>
        ))}
      </Select>

      <label>
        Year
        <input
          type="number"
          placeholder="2026"
          value={filters.year}
          onChange={set('year')}
        />
      </label>

      <Select
        label="Sentiment"
        value={filters.sentiment}
        onChange={set('sentiment')}
      >
        {['positive', 'negative', 'neutral'].map((s) => (
          <option key={s} value={s}>
            {s}
          </option>
        ))}
      </Select>

      <Select
        label="Emotion"
        value={filters.emotion}
        onChange={set('emotion')}
      >
        {(emotions.data || []).map((e) => (
          <option key={e.label} value={e.label}>
            {e.label}
          </option>
        ))}
      </Select>

      <label>
        From
        <input
          type="date"
          value={filters.date_from}
          onChange={set('date_from')}
        />
      </label>

      <label>
        To
        <input
          type="date"
          value={filters.date_to}
          onChange={set('date_to')}
        />
      </label>

      <label>
        Data
        <select value={filters.data} onChange={set('data')}>
          <option value="real">Real only</option>
          <option value="sample">Sample only</option>
          <option value="all">Real + sample</option>
        </select>
      </label>

      <button onClick={reset}>Reset</button>
    </div>
  );
}
