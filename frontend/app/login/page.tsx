import { LoginForm } from "../../components/auth/LoginForm";

export default function LoginPage() {
  return (
    <main className="auth-page">
      <section className="auth-card">
        <p className="eyebrow">AI Stock Lab</p>
        <h1>Welcome back</h1>
        <p className="auth-lead">Sign in to continue building and testing AI-powered trading strategies.</p>
        <LoginForm />
      </section>
    </main>
  );
}
