import { useEffect, useState } from "react";
import { Link, NavLink, Navigate, Route, Routes, useNavigate } from "react-router-dom";
import UsersPage from "./features/users/UsersPage.jsx";
import TransportPage from "./features/transport/TransportPage.jsx";
import ParkingPage from "./features/parking/ParkingPage.jsx";
import UtilityIssuesPage from "./features/utility/UtilityIssuesPage.jsx";
import SensorsPage from "./features/sensors/SensorsPage.jsx";
import InvoicesPage from "./features/billing/InvoicesPage.jsx";

import { API_URLS, apiFetch, getToken, setToken } from "./api.js";

function Layout({ currentUser, loading, onLogout, children }) {
  return (
    <>
      <header className="site-header">
        <Link className="brand" to="/">
          Умный город
        </Link>
        <nav aria-label="Основная навигация">
          <NavLink to="/">Главная</NavLink>
          {currentUser ? (
            <>
              <NavLink to="/profile">Профиль</NavLink>
              <button className="link-button" onClick={onLogout} type="button">
                Выйти
              </button>
            </>
          ) : !loading ? (
            <>
              <NavLink to="/login">Вход</NavLink>
              <NavLink to="/register">Регистрация</NavLink>
            </>
          ) : null}
        </nav>
      </header>
      <main className="container">{children}</main>
    </>
  );
}

function Home({ currentUser }) {
  return (
    <section className="card hero">
      <p className="eyebrow">Городские сервисы</p>
      <h1>Умный город</h1>
      <p>
        Здесь будут собраны транспорт, парковки, заявки ЖКХ, экологические
        датчики и счета.
      </p>
      {currentUser ? (
        <Link className="button" to="/profile">
          Открыть профиль
        </Link>
      ) : (
        <Link className="button" to="/login">
          Войти в систему
        </Link>
      )}
    </section>
  );
}

function AuthForm({ mode, onAuthenticated }) {
  const navigate = useNavigate();
  const isLogin = mode === "login";
  const [form, setForm] = useState({
    email: "",
    password: "",
    first_name: "",
    last_name: "",
  });
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  function updateField(event) {
    setForm((current) => ({ ...current, [event.target.name]: event.target.value }));
  }

  async function submit(event) {
    event.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      if (isLogin) {
        const result = await apiFetch(API_URLS.identity, "/auth/login", {
          method: "POST",
          body: JSON.stringify({ email: form.email, password: form.password }),
        });
        setToken(result.access_token);
        await onAuthenticated();
        navigate("/profile", { replace: true });
      } else {
        await apiFetch(API_URLS.identity, "/auth/register", {
          method: "POST",
          body: JSON.stringify({
            email: form.email,
            password: form.password,
            first_name: form.first_name,
            last_name: form.last_name,
          }),
        });
        navigate("/login", { replace: true });
      }
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <section className="card form-card">
      <h1>{isLogin ? "Вход" : "Регистрация"}</h1>
      <form onSubmit={submit}>
        {!isLogin && (
          <div className="form-row">
            <label>
              Имя
              <input name="first_name" onChange={updateField} required value={form.first_name} />
            </label>
            <label>
              Фамилия
              <input name="last_name" onChange={updateField} required value={form.last_name} />
            </label>
          </div>
        )}
        <label>
          Email
          <input name="email" onChange={updateField} required type="email" value={form.email} />
        </label>
        <label>
          Пароль
          <input
            minLength="8"
            name="password"
            onChange={updateField}
            required
            type="password"
            value={form.password}
          />
        </label>
        {error && <p className="error" role="alert">{error}</p>}
        <button className="button" disabled={submitting} type="submit">
          {submitting ? "Отправка..." : isLogin ? "Войти" : "Зарегистрироваться"}
        </button>
      </form>
      <p className="muted">
        {isLogin ? "Нет учётной записи? " : "Уже зарегистрированы? "}
        <Link to={isLogin ? "/register" : "/login"}>{isLogin ? "Регистрация" : "Войти"}</Link>
      </p>
    </section>
  );
}

function Profile({ currentUser }) {
  return (
    <section className="card">
      <h1>Профиль</h1>
      <dl className="profile-list">
        <div><dt>Имя</dt><dd>{currentUser.first_name}</dd></div>
        <div><dt>Фамилия</dt><dd>{currentUser.last_name}</dd></div>
        <div><dt>Email</dt><dd>{currentUser.email}</dd></div>
        <div><dt>Роль</dt><dd>{currentUser.role}</dd></div>
      </dl>
    </section>
  );
}

function ProtectedRoute({ currentUser, loading, children }) {
  if (loading) return <p>Загрузка профиля...</p>;
  return currentUser ? children : <Navigate replace to="/login" />;
}

function NotFound() {
  return (
    <section className="card">
      <h1>Страница не найдена</h1>
      <Link to="/">Вернуться на главную</Link>
    </section>
  );
}

export default function App() {
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);

  async function refreshProfile() {
    if (!getToken()) {
      setCurrentUser(null);
      setLoading(false);
      return;
    }
    try {
      setCurrentUser(await apiFetch(API_URLS.identity, "/users/me"));
    } catch {
      setToken(null);
      setCurrentUser(null);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refreshProfile();
  }, []);

  function logout() {
    setToken(null);
    setCurrentUser(null);
  }

  return (
    <Layout currentUser={currentUser} loading={loading} onLogout={logout}>
      <Routes>
        <Route path="/" element={<Home currentUser={currentUser} />} />
        <Route
          path="/login"
          element={currentUser ? <Navigate replace to="/profile" /> : <AuthForm mode="login" onAuthenticated={refreshProfile} />}
        />
        <Route
          path="/register"
          element={currentUser ? <Navigate replace to="/profile" /> : <AuthForm mode="register" onAuthenticated={refreshProfile} />}
        />
        <Route
          path="/profile"
          element={<ProtectedRoute currentUser={currentUser} loading={loading}><Profile currentUser={currentUser} /></ProtectedRoute>}
        />
        <Route path="*" element={<NotFound />} />
      </Routes>
      <Route
  path="/users"
  element={
    <ProtectedRoute currentUser={currentUser} loading={loading}>
      <UsersPage />
    </ProtectedRoute>
  }
/>
<Route
  path="/transport"
  element={
    <ProtectedRoute currentUser={currentUser} loading={loading}>
      <TransportPage />
    </ProtectedRoute>
  }
/>
<Route
  path="/parking"
  element={
    <ProtectedRoute currentUser={currentUser} loading={loading}>
      <ParkingPage />
    </ProtectedRoute>
  }
/>
<Route
  path="/utility"
  element={
    <ProtectedRoute currentUser={currentUser} loading={loading}>
      <UtilityIssuesPage />
    </ProtectedRoute>
  }
/>
<Route
  path="/sensors"
  element={
    <ProtectedRoute currentUser={currentUser} loading={loading}>
      <SensorsPage />
    </ProtectedRoute>
  }
/>
<Route
  path="/invoices"
  element={
    <ProtectedRoute currentUser={currentUser} loading={loading}>
      <InvoicesPage currentUser={currentUser} />
    </ProtectedRoute>
  }
/>
    </Layout>
  );
}
