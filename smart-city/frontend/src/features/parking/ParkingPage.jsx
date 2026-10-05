import { useEffect, useState } from "react";
import { API_URLS, apiFetch } from "../../api.js";

export default function ParkingPage() {
  const [parkings, setParkings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function load() {
    setLoading(true);
    setError("");
    try {
      setParkings(await apiFetch(API_URLS.transport, "/parking"));
    } catch (e) {
      setError(e.message || "Не удалось загрузить парковки");
    } finally {
      setLoading(false);
    }
  }

  async function reserve(id) {
    setError("");
    try {
      await apiFetch(API_URLS.transport, `/parking/${id}/reserve`, {
        method: "POST",
      });
      await load();
    } catch (e) {
      setError(e.message || "Не удалось забронировать парковку");
    }
  }

  useEffect(() => {
    load();
  }, []);

  if (loading) return <p>Загрузка парковок...</p>;
  if (error) return <p className="error" role="alert">{error}</p>;
  if (!parkings.length) return <p>Парковок пока нет.</p>;

  return (
    <section className="card">
      <h1>Парковки</h1>
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Адрес</th>
            <th>Всего мест</th>
            <th>Свободно</th>
            <th>Действие</th>
          </tr>
        </thead>
        <tbody>
          {parkings.map((p) => (
            <tr key={p.id}>
              <td>{p.id}</td>
              <td>{p.address}</td>
              <td>{p.total_spaces}</td>
              <td>{p.available_spaces}</td>
              <td>
                <button
                  className="button"
                  onClick={() => reserve(p.id)}
                  disabled={p.available_spaces <= 0}
                >
                  Забронировать
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}