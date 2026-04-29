import { LoginForm } from "../../components/auth/LoginForm";

export default function LoginPage() {
  return (
    <main className="auth-page">
      <section className="auth-card">
        <p className="eyebrow">AI Stock Lab</p>
        <h1>Login</h1>
        <LoginForm />
      </section>
    </main>
  );
}
