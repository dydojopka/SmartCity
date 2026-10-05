import { useEffect, useState } from "react";
import { API_URLS, apiFetch } from "../../api.js";

export default function TransportPage() {
  const [vehicles, setVehicles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function load() {
    setLoading(true);
    setError("");
    try {
      setVehicles(await apiFetch(API_URLS.transport, "/vehicles"));
    } catch (e) {
      setError(e.message || "Не удалось загрузить транспорт");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  if (loading) return <p>Загрузка транспорта...</p>;
  if (error) return <p className="error" role="alert">{error}</p>;
  if (!vehicles.length) return <p>Транспорт пока не добавлен.</p>;

  return (
    <section className="card">
      <h1>Транспорт</h1>
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Номер</th>
            <th>Модель</th>
            <th>Статус</th>
          </tr>
        </thead>
        <tbody>
          {vehicles.map((v) => (
            <tr key={v.id}>
              <td>{v.id}</td>
              <td>{v.number}</td>
              <td>{v.model}</td>
              <td>{v.status}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}