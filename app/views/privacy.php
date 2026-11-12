<div class="container privacy-page">
  <header class="privacy-hero">
    <div class="privacy-hero-copy">
      <span class="eyebrow">YOUR INFORMATION</span>
      <h1>Privacy, explained<br><span>without the fine print.</span></h1>
      <p>A clear overview of what information is collected when you get in touch, why it is needed and how you can ask for it to be deleted.</p>
    </div>
    <div class="privacy-hero-mark" aria-hidden="true">
      <span><?=icon('shield')?></span>
      <strong>Limited data.<br>Clear purpose.</strong>
      <small>No advertising trackers</small>
    </div>
  </header>

  <div class="privacy-layout">
    <aside class="privacy-summary" aria-label="Privacy summary">
      <span class="eyebrow">AT A GLANCE</span>
      <h2>Your details stay focused on your enquiry.</h2>
      <ul>
        <li><?=icon('check')?><span>Only information needed to discuss your project</span></li>
        <li><?=icon('check')?><span>No automatic marketing subscription</span></li>
        <li><?=icon('check')?><span>Essential security and anti-spam protection only</span></li>
      </ul>
      <div class="privacy-contact">
        <span class="privacy-contact-icon"><?=icon('mail')?></span>
        <div>
          <small>Privacy contact</small>
          <a href="mailto:<?=e($config['helpdesk_email'])?>"><?=e($config['helpdesk_email'])?></a>
        </div>
      </div>
    </aside>

    <article class="privacy-sections">
      <section class="privacy-card">
        <span class="privacy-number">01</span>
        <div><h2>What you share</h2><p>The enquiry form collects your name, contact information and optional project requirements. Please share only what is needed for an initial project discussion.</p></div>
      </section>
      <section class="privacy-card">
        <span class="privacy-number">02</span>
        <div><h2>Why it is collected</h2><p>MJ DYNAMIC uses these details to review your enquiry, contact you and discuss a potential software development project. Submitting an enquiry does not subscribe you to marketing messages.</p></div>
      </section>
      <section class="privacy-card">
        <span class="privacy-number">03</span>
        <div><h2>Storage and notifications</h2><p>Enquiries are stored in a private application database. A notification may also be sent to the project team’s email account. Hosting and email providers process this information as needed to operate those services.</p></div>
      </section>
      <section class="privacy-card">
        <span class="privacy-number">04</span>
        <div><h2>Essential session data</h2><p>The contact form and content manager use an essential session cookie for request protection and sign-in. The site does not include advertising trackers. Short-lived, hashed network identifiers are used to limit automated form abuse.</p></div>
      </section>
      <section class="privacy-card privacy-card-contact">
        <span class="privacy-number">05</span>
        <div>
          <h2>Questions and deletion requests</h2>
          <p>To ask about your enquiry information or request its deletion, contact <a href="mailto:<?=e($config['helpdesk_email'])?>"><?=e($config['helpdesk_email'])?></a>. Information needed for an active project may be handled under the separate arrangements agreed for that work.</p>
          <a class="privacy-email-button" href="mailto:<?=e($config['helpdesk_email'])?>"><?=icon('mail')?> Email the privacy contact</a>
        </div>
      </section>
    </article>
  </div>
</div>
