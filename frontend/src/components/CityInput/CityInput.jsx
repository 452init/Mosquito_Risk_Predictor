import { useState } from "react";
import "./CityInput.css";

function CityInput({ onSubmit, isLoading }) {
  const [city, setCity] = useState("");

  function handleSubmit(e) {
    e.preventDefault();
    const trimmed = city.trim();
    if (trimmed && !isLoading) {
      onSubmit(trimmed);
    }
  }

  function handleKeyDown(e) {
    if (e.key === "Enter") {
      handleSubmit(e);
    }
  }

  return (
    <div className="city-input-container" id="city-input-section">
      <label className="city-input-label" htmlFor="city-input">
        Enter your city name
      </label>
      <form className="city-input-wrapper" onSubmit={handleSubmit}>
        <span className="city-input-icon" aria-hidden="true">📍</span>
        <input
          id="city-input"
          className="city-input-field"
          type="text"
          placeholder="e.g. Nairobi, Lagos, Dar es Salaam…"
          value={city}
          onChange={(e) => setCity(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={isLoading}
          autoComplete="off"
          autoFocus
        />
        <button
          type="submit"
          className="city-input-button"
          disabled={!city.trim() || isLoading}
          id="analyze-button"
        >
          {isLoading ? "Analyzing…" : "Analyze Risk"}
          <span className="city-input-button-icon" aria-hidden="true">
            {isLoading ? "⏳" : "→"}
          </span>
        </button>
      </form>
    </div>
  );
}

export default CityInput;
