import { useEffect, useState } from "react";
import { API_URLS, apiFetch } from "../../api.js";

export default function SensorsPage() {
  const [sensors, setSensors] = useState([]);
  const [selectedId, setSelectedId] = useState(null);
  const [readings, setReadings] = useState([]);
  const [loadingSensors, setLoadingSensors] = useState(true);
  const [loadingReadings, setLoadingReadings] = useState(false);
  const [error, setError] = useState("");

  async function loadSensors() {
    setLoadingSensors(true);
    setError("");
    try {
      setSensors(await apiFetch(API_URLS.environment, "/sensors"));
    } catch (e) {
      setError(e.message || "Не удалось загрузить датчики");
    } finally {
      setLoadingSensors(false);
    }
  }

  async function loadReadings(id) {
    setLoadingReadings(true);
    setError("");
    try {
      setReadings(await apiFetch(API_URLS.environment, `/sensors/${id}/data`));
    } catch (e) {
      setError(e.message || "Не удалось загрузить показания");
    } finally {
      setLoadingReadings(false);
    }
  }

  useEffect(() => {
    loadSensors();
  }, []);

  useEffect(() => {
    if (selectedId) {
      loadReadings(selectedId);
    } else {
      setReadings([]);
    }
  }, [selectedId]);

  if (loadingSensors) return <p>Загрузка датчиков...</p>;
  if (error) return <p className="error" role="alert">{error}</p>;
  if (!sensors.length) return <p>Датчиков пока нет.</p>;

  return (
    <section className="card">
      <h1>Датчики</h1>
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Название</th>
            <th>Тип</th>
            <th>Статус</th>
            <th>Действие</th>
          </tr>
        </thead>
        <tbody>
          {sensors.map((s) => (
            <tr key={s.id}>
              <td>{s.id}</td>
              <td>{s.name}</td>
              <td>{s.type}</td>
              <td>{s.status}</td>
              <td>
                <button className="button" onClick={() => setSelectedId(s.id)}>
                  Показания
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {selectedId && (
        <>
          <h2>Показания датчика #{selectedId}</h2>
          {loadingReadings && <p>Загрузка показаний...</p>}
          {!loadingReadings && !readings.length && <p>Показаний пока нет.</p>}
          {!loadingReadings && readings.length > 0 && (
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Значение</th>
                  <th>Ед. изм.</th>
                  <th>Измерено</th>
                </tr>
              </thead>
              <tbody>
                {readings.map((r) => (
                  <tr key={r.id}>
                    <td>{r.id}</td>
                    <td>{r.value}</td>
                    <td>{r.unit}</td>
                    <td>{new Date(r.measured_at).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </>
      )}
    </section>
  );
}