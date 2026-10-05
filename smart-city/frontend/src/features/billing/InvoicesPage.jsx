import { useEffect, useState } from "react";
import { API_URLS, apiFetch } from "../../api.js";

export default function InvoicesPage({ currentUser }) {
  const [invoices, setInvoices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function load() {
    setLoading(true);
    setError("");
    try {
      setInvoices(
        await apiFetch(API_URLS.billing, `/accounts/${currentUser.id}/invoices`),
      );
    } catch (e) {
      setError(e.message || "Не удалось загрузить счета");
    } finally {
      setLoading(false);
    }
  }

  async function pay(invoice) {
    setError("");
    try {
      await apiFetch(API_URLS.billing, "/payments", {
        method: "POST",
        body: JSON.stringify({
          invoice_id: invoice.id,
          amount_cents: invoice.amount_cents,
          idempotency_key: crypto.randomUUID(),
        }),
      });
      await load();
    } catch (e) {
      setError(e.message || "Не удалось создать платеж");
    }
  }

  useEffect(() => {
    load();
  }, [currentUser.id]);

  if (loading) return <p>Загрузка счетов...</p>;
  if (error) return <p className="error" role="alert">{error}</p>;
  if (!invoices.length) return <p>Счетов пока нет.</p>;

  return (
    <section className="card">
      <h1>Счета</h1>
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Период</th>
            <th>Сумма, коп.</th>
            <th>Статус</th>
            <th>Действие</th>
          </tr>
        </thead>
        <tbody>
          {invoices.map((inv) => (
            <tr key={inv.id}>
              <td>{inv.id}</td>
              <td>{inv.period}</td>
              <td>{inv.amount_cents}</td>
              <td>{inv.status}</td>
              <td>
                <button
                  className="button"
                  onClick={() => pay(inv)}
                  disabled={inv.status === "PAID"}
                >
                  Создать платеж
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}