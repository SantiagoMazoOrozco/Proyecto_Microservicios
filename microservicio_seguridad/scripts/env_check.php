<?php
require __DIR__.'/../vendor/autoload.php';
$app = require_once __DIR__.'/../bootstrap/app.php';
$kernel = $app->make(Illuminate\Contracts\Console\Kernel::class);
$kernel->bootstrap();

echo "base_path: " . base_path() . PHP_EOL;
echo "app_path: " . app_path() . PHP_EOL;
echo "database_path: " . database_path() . PHP_EOL;
echo "getcwd: " . getcwd() . PHP_EOL;
echo "config database.default: " . config('database.default') . PHP_EOL;
echo "config connections.sqlite.database: " . config('database.connections.sqlite.database') . PHP_EOL;
$db = config('database.connections.sqlite.database');
if (! $db) {
    echo "DB path empty\n";
    exit(0);
}
$real = realpath($db);
echo "realpath(db): " . ($real ?: 'null') . PHP_EOL;
echo "file_exists(db): " . (file_exists($db) ? 'true' : 'false') . PHP_EOL;
echo "is_readable(db): " . (is_readable($db) ? 'true' : 'false') . PHP_EOL;
echo "is_writable(db): " . (is_writable($db) ? 'true' : 'false') . PHP_EOL;
