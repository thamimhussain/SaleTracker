import React, { useEffect, useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [saleItems, setSaleItems] = useState([]);
  const [wishlistMatches, setWishlistMatches] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSaleItems();
  }, []);

  const fetchSaleItems = async () => {
    try {
      setLoading(true);
      const response = await axios.get('http://127.0.0.1:5000/api/sales');
      setSaleItems(response.data.sale_items);
      setWishlistMatches(response.data.matches);
    } catch (error) {
      console.error('Error fetching sale items:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="App">
        <h1>Uniqlo Sale Watcher</h1>
        <div className="spinner-container">
          <div className="spinner"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="App">
      <h1>Uniqlo Sale Watcher</h1>

      <h2>Items in Your Wishlist That Are On Sale</h2>
      <div className="sale-items">
        {wishlistMatches.length > 0 ? (
          wishlistMatches.map((item, index) => (
            <div key={index} className="sale-item">
              {item.image && <img src={`http://127.0.0.1:5000/api/proxy-image?url=${encodeURIComponent(item.image)}`} alt={item.name} />}
              <h2>{item.name}</h2>
              <p>{item.price}</p>
              <a href={item.link} target="_blank" rel="noopener noreferrer">View Item</a>
            </div>
          ))
        ) : (
          <p>No items in your wishlist are on sale.</p>
        )}
      </div>

      <h2>All Sale Items</h2>
      <div className="sale-items">
        {saleItems.map((item, index) => (
          <div key={index} className="sale-item">
            {item.image && <img src={`http://127.0.0.1:5000/api/proxy-image?url=${encodeURIComponent(item.image)}`} alt={item.name} />}
            <h2>{item.name}</h2>
            <p>{item.price}</p>
            <a href={item.link} target="_blank" rel="noopener noreferrer">View Item</a>
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;
