import { RegisterForm } from "../../components/auth/RegisterForm";

export default function RegisterPage() {
  return (
    <main className="auth-page">
      <section className="auth-card">
        <p className="eyebrow">AI Stock Lab</p>
        <h1>Create account</h1>
        <RegisterForm />
      </section>
    </main>
  );
}
