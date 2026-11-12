<?php
declare(strict_types=1);
$config = require __DIR__ . '/config.php';
date_default_timezone_set('Asia/Kolkata');
if (!is_dir($config['storage']) && !mkdir($config['storage'], 0700, true) && !is_dir($config['storage'])) {
    throw new RuntimeException('Cannot create private storage.');
}
$db = new PDO('sqlite:' . $config['storage'] . '/portfolio.sqlite', null, null, [PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION]);
$db->exec('PRAGMA journal_mode=WAL; PRAGMA busy_timeout=5000;');
$db->exec('CREATE TABLE IF NOT EXISTS content (collection TEXT NOT NULL, slug TEXT NOT NULL, data TEXT NOT NULL, PRIMARY KEY(collection, slug));
CREATE TABLE IF NOT EXISTS leads (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, company TEXT, email TEXT NOT NULL, phone TEXT, project_type TEXT, budget TEXT, description TEXT, contact_method TEXT, status TEXT DEFAULT "new", created_at TEXT NOT NULL, mail_status TEXT DEFAULT "pending");
CREATE TABLE IF NOT EXISTS rate_limits (key TEXT PRIMARY KEY, attempts INTEGER NOT NULL, expires INTEGER NOT NULL);');
$count = (int)$db->query('SELECT COUNT(*) FROM content')->fetchColumn();
if (!$count) {
    $seed = json_decode(file_get_contents(__DIR__.'/content.json'), true, 512, JSON_THROW_ON_ERROR);
    $db->beginTransaction();
    $insert = $db->prepare('INSERT OR IGNORE INTO content(collection,slug,data) VALUES(?,?,?)');
    foreach ($seed as $collection => $records) foreach ($records as $record) $insert->execute([$collection, $record['slug'], json_encode($record, JSON_UNESCAPED_UNICODE)]);
    $db->commit();
}
function e(mixed $value): string { return htmlspecialchars((string)$value, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8'); }
function records(string $collection, bool $all = false): array {
    global $db;
    $q = $db->prepare('SELECT data FROM content WHERE collection=? ORDER BY rowid'); $q->execute([$collection]);
    $rows = array_map(fn($r) => json_decode($r, true), $q->fetchAll(PDO::FETCH_COLUMN));
    return $all ? $rows : array_values(array_filter($rows, fn($r) => ($r['published'] ?? true) === true));
}
function record(string $collection, string $slug): ?array { foreach (records($collection) as $r) if ($r['slug'] === $slug) return $r; return null; }
function projects_by_weight(): array {
    $projects=records('projects');
    usort($projects,fn($a,$b)=>(int)($b['weight']??0)<=>(int)($a['weight']??0) ?: strcasecmp($a['title'],$b['title']));
    return $projects;
}
function icon(string $name, string $class = ''): string {
    $paths = ['arrow'=>'<path d="M5 12h14m-6-6 6 6-6 6"/>','diagonal'=>'<path d="M6 18 18 6M6 6h12v12"/>','code'=>'<path d="m8 7-5 5 5 5m8-10 5 5-5 5m-3-14-2 18"/>','layers'=>'<path d="m12 3 10 5-10 5L2 8Zm-10 9 10 5 10-5M2 16l10 5 10-5"/>','grid'=>'<rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/>','link'=>'<path d="m10 13 4-4m-6 7-2 2a4 4 0 0 1-6-6l4-4a4 4 0 0 1 6 0m4 8 4-4a4 4 0 0 0-6-6l-2 2" transform="translate(2 0)"/>','check'=>'<path d="m5 12 4 4L19 6"/>','globe'=>'<circle cx="12" cy="12" r="9"/><ellipse cx="12" cy="12" rx="4" ry="9"/><path d="M3 12h18"/>','mail'=>'<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 6 9 7 9-7"/>','menu'=>'<path d="M4 7h16M4 12h16M4 17h16"/>','shield'=>'<path d="m12 3 8 3v6c0 5-8 9-8 9s-8-4-8-9V6Z"/><path d="m8 12 3 3 5-5"/>','terminal'=>'<path d="m5 7 5 5-5 5m8 0h6"/>','clock'=>'<circle cx="12" cy="12" r="9"/><path d="M12 6v6l4 2"/>'];
    $paths += [
        'chat'=>'<path d="M21 11.5a8 8 0 0 1-8.5 8A9 9 0 0 1 8 18l-5 2 1.7-4.2A8.5 8.5 0 1 1 21 11.5Z"/><path d="M8 10h8M8 14h5"/>',
        'plan'=>'<rect x="5" y="4" width="14" height="17" rx="2"/><path d="M9 4.5V3h6v1.5M9 9h6M9 13h6M9 17h4"/>',
        'prototype'=>'<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M3 9h18M8 9v11M6 6.5h.01M9 6.5h.01"/>',
        'test'=>'<path d="M9 3h6l1 3h3v15H5V6h3Z"/><path d="m8 13 2 2 5-5M9 6h6"/>',
        'rocket'=>'<path d="M14 5c2.2-2.2 5-2 5-2s.2 2.8-2 5l-5.5 5.5-4-4Z"/><path d="m9 8-4 .5L3 12l5 1m5-1 1 5-3.5 2-1-4M6 16l-2 2m4-1-3 3"/><circle cx="15.5" cy="6.5" r="1.5"/>',
        'phone'=>'<path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.7 19.7 0 0 1-8.6-3.1 19.3 19.3 0 0 1-6-6A19.7 19.7 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 2 .7 2.9a2 2 0 0 1-.5 2.1L8 10a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.5c1 .4 1.9.6 2.9.7a2 2 0 0 1 1.7 2Z"/>',
        'whatsapp'=>'<path d="M21 11.5a8.7 8.7 0 0 1-9 8.5 9.4 9.4 0 0 1-4-1l-5 1.5 1.6-4.6A8.5 8.5 0 1 1 21 11.5Z"/><path d="M8.3 7.8c.4-.4.8-.2 1 .2l1 2-1 1c.8 1.6 1.9 2.7 3.5 3.5l1-1 2 1c.5.2.6.6.2 1-1 1.2-2.6 1.4-4.7.3-2.2-1.1-4-2.9-5-5-1-2.1-.8-3.6.3-4.7"/>',
        'broadcast'=>'<circle cx="12" cy="12" r="2"/><path d="M8.5 8.5a5 5 0 0 0 0 7M15.5 8.5a5 5 0 0 1 0 7M5.5 5.5a9 9 0 0 0 0 13M18.5 5.5a9 9 0 0 1 0 13"/>',
        'instagram'=>'<rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><path d="M17.5 6.5h.01"/>'
    ];
    return '<svg class="icon '.e($class).'" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'.($paths[$name] ?? $paths['code']).'</svg>';
}
function start_session(): void {
    if (session_status() !== PHP_SESSION_ACTIVE) {
        session_name('portfolio_session');
        session_start(['cookie_httponly'=>true, 'cookie_secure'=>!empty($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off', 'cookie_samesite'=>'Lax', 'use_strict_mode'=>true]);
    }
    $_SESSION['csrf'] ??= bin2hex(random_bytes(32));
}
function csrf(): string { start_session(); return '<input type="hidden" name="csrf" value="'.e($_SESSION['csrf']).'">'; }
function verify_csrf(): bool { start_session(); return is_string($_POST['csrf'] ?? null) && hash_equals($_SESSION['csrf'], $_POST['csrf']); }
function throttle(string $key, int $limit, int $seconds): bool {
    global $db; $now=time();
    $db->prepare('DELETE FROM rate_limits WHERE expires < ?')->execute([$now]);
    $key = hash('sha256', $key);
    $db->prepare('INSERT INTO rate_limits(key,attempts,expires) VALUES(?,1,?) ON CONFLICT(key) DO UPDATE SET attempts=attempts+1')->execute([$key, $now+$seconds]);
    $q=$db->prepare('SELECT attempts FROM rate_limits WHERE key=?');$q->execute([$key]);return (int)$q->fetchColumn() <= $limit;
}
function send_lead_email(array $lead): bool {
    global $config;
    if (!$config['mail_enabled'] || !filter_var($config['mail_from'], FILTER_VALIDATE_EMAIL)) return false;
    $body="New project enquiry #".$lead['id']."\n\n";
    foreach (['name','email','phone','description'] as $key) $body.=ucwords(str_replace('_',' ',$key)).': '.$lead[$key]."\n\n";
    $headers=['From'=>$config['mail_from'],'Content-Type'=>'text/plain; charset=UTF-8'];
    if (!empty($lead['email'])) $headers['Reply-To']=$lead['email'];
    return @mail($config['email'], 'New portfolio project enquiry #'.$lead['id'], $body, $headers);
}
function project_visual(array $p): void {
    if (!empty($p['screenshots'])) {
        $shot=$p['screenshots'][0];
        $width=(int)($shot['width']??1400); $height=(int)($shot['height']??594);
        echo '<div class="project-preview"><img src="'.e($shot['src']).'" alt="'.e($shot['alt']).'" width="'.$width.'" height="'.$height.'" loading="lazy" decoding="async"></div>';
        return;
    }
    $themes=['medical'=>'Healthcare operations','treeva'=>'Connected patient care','education'=>'One platform. Many organizations.','crm'=>'A clearer customer journey','hrms'=>'People. Policies. Payroll.','warehouse'=>'Every movement, connected.'];
    echo '<div class="project-visual theme-'.e($p['theme']).'" aria-label="'.e($p['title']).' system diagram"><div class="visual-top"><span class="mini-brand">'.icon($p['icon']).' '.e($p['short']).'</span><span class="visual-caption">SYSTEM OVERVIEW</span></div><div class="diagram-title">'.e($themes[$p['theme']] ?? $p['title']).'</div><div class="flow-diagram">';
    foreach (array_slice($p['features'],0,3) as $i=>$f) echo '<div><span class="node-number">0'.($i+1).'</span><span>'.e($f).'</span>'.icon('check').'</div>';
    echo '</div><span class="diagram-note">'.e($p['industry']).' / '.e($p['architecture']).'</span></div>';
}
function project_card(array $p): void { $label=!empty($p['concept'])?'Concept project · '.$p['industry']:$p['industry']; echo '<article class="project-card" data-categories="'.e(implode('|',$p['categories'])).'">'; project_visual($p); echo '<div class="project-card-body"><div class="eyebrow">'.e($label).'</div><h3><a href="/projects/'.e($p['slug']).'">'.e($p['title']).icon('diagonal').'</a></h3><p>'.e($p['description']).'</p><div class="tags">'; foreach($p['technologies'] as $t) echo '<span>'.e($t).'</span>'; echo '</div><a class="text-link" href="/projects/'.e($p['slug']).'">'.(!empty($p['concept'])?'Explore the concept ':'See what the system does ').icon('arrow').'</a></div></article>'; }
function cta(string $heading = 'Have a project in mind?<br>Let’s build it.'): void { echo '<section class="cta-band container"><div><span class="eyebrow">YOUR NEXT CHAPTER</span><h2>'.$heading.'</h2><p>Tell us what is difficult to manage today. We’ll discuss possible solutions, the next steps and a quotation.</p></div><a class="button light" href="/contact">Get a free consultation '.icon('diagonal').'</a></section>'; }
