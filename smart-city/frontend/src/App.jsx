const services = [
  ["Identity", "http://localhost:8001/docs"],
  ["Transport", "http://localhost:8002/docs"],
  ["Utility", "http://localhost:8003/docs"],
  ["Environment", "http://localhost:8004/docs"],
  ["Billing", "http://localhost:8005/docs"],
  ["Notification", "http://localhost:8006/docs"],
];

export default function App() {
  return (
    <main className="container">
      <h1>Умный город</h1>
      <p>
        Технический каркас запущен. Предметные страницы будут добавляться по
        заданиям участников.
      </p>

      <section className="card">
        <h2>Swagger сервисов</h2>
        <ul>
          {services.map(([name, url]) => (
            <li key={name}>
              <a href={url} target="_blank" rel="noreferrer">
                {name}
              </a>
            </li>
          ))}
        </ul>
      </section>
    </main>
  );
}
