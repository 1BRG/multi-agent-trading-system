import { RegisterForm } from "../../components/auth/RegisterForm";

export default function RegisterPage() {
  return (
    <main className="auth-page">
      <section className="auth-card">
        <p className="eyebrow">AI Stock Lab</p>
        <h1>Create your account</h1>
        <p className="auth-lead">Join the workspace and start generating deterministic strategies from natural language.</p>
        <RegisterForm />
      </section>
    </main>
  );
}
