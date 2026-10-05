import { useEffect, useState } from "react";
import { API_URLS, apiFetch } from "../../api.js";

export default function UsersPage() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function load() {
    setLoading(true);
    setError("");
    try {
      setUsers(await apiFetch(API_URLS.identity, "/users"));
    } catch (e) {
      setError(e.message || "Не удалось загрузить пользователей");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  if (loading) return <p>Загрузка пользователей...</p>;
  if (error) return <p className="error" role="alert">{error}</p>;
  if (!users.length) return <p>Пользователей пока нет.</p>;

  return (
    <section className="card">
      <h1>Пользователи</h1>
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Имя</th>
            <th>Фамилия</th>
            <th>Роль</th>
          </tr>
        </thead>
        <tbody>
          {users.map((user) => (
            <tr key={user.id}>
              <td>{user.id}</td>
              <td>{user.first_name}</td>
              <td>{user.last_name}</td>
              <td>{user.role}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}