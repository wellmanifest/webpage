<?php
// ADOPT snippet for subactor/www-sub-actor (runtime_service).
// Do not apply from wellmanifest/webpage — ticket-120 currently owns application.
// After that ticket closes, add these routes next to /favicon.svg in index.php.

$router->get('/sitemap.xml', static function () {
    $origin = 'https://sub.actor';
    $paths = [
        ['/', '1.0'],
        ['/compare', '0.8'],
        ['/registry', '0.8'],
        ['/marketplace', '0.8'],
        ['/legal', '0.8'],
    ];
    $body = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n";
    $body .= "<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">\n";
    foreach ($paths as [$path, $priority]) {
        $loc = $path === '/' ? $origin . '/' : $origin . $path;
        $body .= "  <url><loc>{$loc}</loc><changefreq>weekly</changefreq><priority>{$priority}</priority></url>\n";
    }
    $body .= "</urlset>\n";
    return new Response(200, ['Content-Type' => 'application/xml; charset=UTF-8'], $body);
});

$router->get('/robots.txt', static function () {
    $body = "User-agent: *\nAllow: /\nSitemap: https://sub.actor/sitemap.xml\n";
    return new Response(200, ['Content-Type' => 'text/plain; charset=UTF-8'], $body);
});
