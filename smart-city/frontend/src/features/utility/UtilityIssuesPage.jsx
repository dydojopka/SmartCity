import { useEffect, useState } from "react";
import { API_URLS, apiFetch } from "../../api.js";

export default function UtilityIssuesPage() {
  const [issues, setIssues] = useState([]);
  const [form, setForm] = useState({
    title: "",
    description: "",
    category: "",
    address: "",
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function load() {
    setLoading(true);
    setError("");
    try {
      setIssues(await apiFetch(API_URLS.utility, "/issues"));
    } catch (e) {
      setError(e.message || "Не удалось загрузить заявки ЖКХ");
    } finally {
      setLoading(false);
    }
  }

  async function submit(event) {
    event.preventDefault();
    setError("");
    try {
      await apiFetch(API_URLS.utility, "/issues", {
        method: "POST",
        body: JSON.stringify(form),
      });
      setForm({ title: "", description: "", category: "", address: "" });
      await load();
    } catch (e) {
      setError(e.message || "Не удалось создать заявку");
    }
  }

  useEffect(() => {
    load();
  }, []);

  return (
    <section className="card">
      <h1>Заявки ЖКХ</h1>

      <form onSubmit={submit}>
        <label>
          Тема
          <input
            value={form.title}
            onChange={(e) => setForm({ ...form, title: e.target.value })}
            required
          />
        </label>
        <label>
          Описание
          <textarea
            value={form.description}
            onChange={(e) => setForm({ ...form, description: e.target.value })}
            required
          />
        </label>
        <label>
          Категория
          <input
            value={form.category}
            onChange={(e) => setForm({ ...form, category: e.target.value })}
            required
          />
        </label>
        <label>
          Адрес
          <input
            value={form.address}
            onChange={(e) => setForm({ ...form, address: e.target.value })}
            required
          />
        </label>
        <button className="button" type="submit">
          Отправить
        </button>
      </form>

      {loading && <p>Загрузка заявок...</p>}
      {error && <p className="error" role="alert">{error}</p>}
      {!loading && !issues.length && <p>Заявок пока нет.</p>}

      {!loading && issues.length > 0 && (
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Тема</th>
              <th>Категория</th>
              <th>Адрес</th>
              <th>Статус</th>
            </tr>
          </thead>
          <tbody>
            {issues.map((issue) => (
              <tr key={issue.id}>
                <td>{issue.id}</td>
                <td>{issue.title}</td>
                <td>{issue.category}</td>
                <td>{issue.address}</td>
                <td>{issue.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  );
}