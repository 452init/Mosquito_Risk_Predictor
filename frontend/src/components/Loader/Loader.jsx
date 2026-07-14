import "./Loader.css";

function Loader({ message = "Analyzing mosquito risk…" }) {
  return (
    <div className="loader-overlay" id="loader">
      <div className="loader-spinner">
        <div className="loader-ring"></div>
        <div className="loader-ring"></div>
        <div className="loader-ring"></div>
        <span className="loader-mosquito">🦟</span>
      </div>
      <p className="loader-text">{message}</p>
      <p className="loader-subtext">
        Fetching weather data &amp; computing risk factors
      </p>
    </div>
  );
}

export default Loader;
