import Link from "next/link";

export default function HomePage() {
  return (
    <>
      <header className="site-header">
        <Link className="site-logo" href="/">
          AI Stock Lab
        </Link>
        <nav className="site-nav" aria-label="Main navigation">
          <Link href="/login">Login</Link>
          <Link className="nav-button" href="/register">
            Register
          </Link>
        </nav>
      </header>

      <main className="home-page">
        <section className="home-content">
          <p className="eyebrow">AI Stock Lab</p>
          <h1>Platforma pentru analiza actiunilor si testarea strategiilor</h1>
          <p>
            Aplicatia te ajuta sa urmaresti actiuni, sa creezi strategii de
            trading, sa rulezi backtesturi pe date istorice si sa folosesti
            asistenti AI pentru discutii si dezbateri despre piata.
          </p>
          <p>
            Pentru inceput, creeaza un cont sau autentifica-te. Dupa login,
            dashboard-ul iti permite sa vezi si sa modifici datele contului tau.
          </p>
          <div className="home-actions">
            <Link className="primary-link" href="/login">
              Login
            </Link>
            <Link className="secondary-link" href="/register">
              Creeaza cont
            </Link>
          </div>
        </section>
      </main>
    </>
  );
}
