import { useState } from "react";
import CityInput from "./components/CityInput/CityInput";
import Loader from "./components/Loader/Loader";
import WeatherCard from "./components/WeatherCard/WeatherCard";
import RiskDisplay from "./components/RiskDisplay/RiskDisplay";
import { getRiskReport } from "./services/api";
import "./App.css";

function App() {
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  async function handleCitySubmit(cityName) {
    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await getRiskReport(cityName);
      setResult(data);
    } catch (err) {
      const message =
        err.response?.data?.error ||
        err.message ||
        "Something went wrong. Please try again.";
      setError(message);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="app-header-icon" aria-hidden="true">
          🦟
        </div>
        <h1 className="app-title">Mosquito Risk Predictor</h1>
        <p className="app-subtitle">
          Enter a city to assess mosquito activity risk based on current weather
          and forecast conditions.
        </p>
      </header>

      <main className="app-main">
        <CityInput onSubmit={handleCitySubmit} isLoading={isLoading} />

        {error && (
          <div className="app-error" role="alert">
            <span aria-hidden="true">⚠️</span>
            {error}
          </div>
        )}

        {isLoading && <Loader />}

        {result && !isLoading && (
          <div className="app-results">
            <WeatherCard
              weather={result.current_weather}
              forecast={result.forecast_summary}
              cityName={result.city_name}
            />
            <RiskDisplay risk={result.risk} />
          </div>
        )}
      </main>

      <footer className="app-footer">
        <p>
          Risk scores consider temperature (20–30°C), humidity (≥60%), and
          recent or upcoming rain within 48 hours.
        </p>
      </footer>
    </div>
  );
}

export default App;
