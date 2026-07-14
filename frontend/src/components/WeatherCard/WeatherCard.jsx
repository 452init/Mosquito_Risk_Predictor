import "./WeatherCard.css";

function WeatherCard({ weather, forecast, cityName }) {
  if (!weather) return null;

  const dayNames = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

  function formatDate(dateStr) {
    if (!dateStr) return "—";
    try {
      const d = new Date(dateStr);
      if (isNaN(d.getTime())) return dateStr;
      return dayNames[d.getDay()];
    } catch {
      return dateStr;
    }
  }

  return (
    <div className="weather-card" id="weather-card">
      <div className="weather-card-header">
        <span className="weather-card-icon" aria-hidden="true">🌤️</span>
        <h3 className="weather-card-title">
          Current Weather in {cityName}
        </h3>
      </div>

      <div className="weather-card-grid">
        <div className="weather-stat">
          <span className="weather-stat-icon" aria-hidden="true">🌡️</span>
          <span className="weather-stat-value">
            {weather.temperature != null
              ? `${Math.round(weather.temperature)}°C`
              : "—"}
          </span>
          <span className="weather-stat-label">Temperature</span>
        </div>

        <div className="weather-stat">
          <span className="weather-stat-icon" aria-hidden="true">💧</span>
          <span className="weather-stat-value">
            {weather.humidity != null
              ? `${Math.round(weather.humidity)}%`
              : "—"}
          </span>
          <span className="weather-stat-label">Humidity</span>
        </div>

        <div className="weather-stat">
          <span className="weather-stat-icon" aria-hidden="true">💨</span>
          <span className="weather-stat-value">
            {weather.wind_speed != null
              ? `${Math.round(weather.wind_speed)}`
              : "—"}
          </span>
          <span className="weather-stat-label">Wind km/h</span>
        </div>

        <div className="weather-stat">
          <span className="weather-stat-icon" aria-hidden="true">☁️</span>
          <span className="weather-stat-value weather-condition-text">
            {weather.condition || "—"}
          </span>
          <span className="weather-stat-label">Condition</span>
        </div>
      </div>

      {forecast && forecast.length > 0 && (
        <div className="weather-forecast">
          <p className="weather-forecast-title">7-Day Forecast</p>
          <div className="weather-forecast-scroll">
            {forecast.map((day, i) => (
              <div className="forecast-day" key={i}>
                <span className="forecast-day-name">
                  {formatDate(day.date)}
                </span>
                {day.temp_high != null && (
                  <span className="forecast-day-temp">
                    {Math.round(day.temp_high)}°
                    {day.temp_low != null && (
                      <span style={{ opacity: 0.5, fontWeight: 400 }}>
                        /{Math.round(day.temp_low)}°
                      </span>
                    )}
                  </span>
                )}
                {day.precipitation != null && day.precipitation > 0 && (
                  <span className="forecast-day-rain">
                    🌧 {day.precipitation}mm
                  </span>
                )}
                {day.condition && (
                  <span className="forecast-day-condition">
                    {day.condition}
                  </span>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default WeatherCard;
