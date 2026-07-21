type SiteFooterProps = {
  docsHref?: string;
  homeHref?: string;
};

export function SiteFooter({ docsHref = "./docs/", homeHref = "./" }: SiteFooterProps) {
  return (
    <footer>
      <div className="footer-brand">
        <a href={homeHref}>Fido</a>
        <span>Local design-fidelity checks for your game designs.</span>
      </div>
      <nav className="footer-nav" aria-label="Footer">
        <a href={homeHref}>Showcase</a>
        <a href={docsHref}>Install docs</a>
      </nav>
    </footer>
  );
}
