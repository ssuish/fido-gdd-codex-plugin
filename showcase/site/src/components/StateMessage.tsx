export function StateMessage({
  title,
  body,
  loading = false,
}: {
  title: string;
  body: string;
  loading?: boolean;
}) {
  return (
    <main className="state-message">
      <div className={loading ? "loader" : "error-mark"}>{loading ? "" : "!"}</div>
      <h1>{title}</h1>
      <p>{body}</p>
    </main>
  );
}
