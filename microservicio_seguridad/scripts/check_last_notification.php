<?php
require __DIR__.'/../vendor/autoload.php';
$app = require_once __DIR__.'/../bootstrap/app.php';
$kernel = $app->make(Illuminate\Contracts\Console\Kernel::class);
$kernel->bootstrap();

$last = App\Models\NotificationLog::orderBy('id','desc')->first();
if (! $last) {
    echo "No notification logs found\n";
    exit(0);
}
echo "id: {$last->id}\n";
echo "type: {$last->type}\n";
echo "to: {$last->to}\n";
echo "status: {$last->status}\n";
echo "error: " . ($last->error ?? 'null') . "\n";
echo "sent_at: " . ($last->sent_at ? $last->sent_at->toDateTimeString() : 'null') . "\n";
echo "created_at: {$last->created_at}\n";
