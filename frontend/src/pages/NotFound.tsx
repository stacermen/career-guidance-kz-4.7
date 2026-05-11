import { Link } from "react-router-dom";

export function NotFoundPage() {
  return (
    <div className="container flex min-h-[60vh] flex-col items-center justify-center py-16 text-center">
      <p className="text-7xl font-extrabold gradient-text">404</p>
      <h1 className="mt-3 text-2xl font-bold">Страница не найдена</h1>
      <p className="mt-2 text-slate-500">Похоже, такой ссылки у нас нет.</p>
      <Link to="/" className="btn-primary mt-6">
        На главную
      </Link>
    </div>
  );
}
