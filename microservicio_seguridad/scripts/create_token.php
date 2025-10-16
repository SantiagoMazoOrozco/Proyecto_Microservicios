<?php
require __DIR__.'/../vendor/autoload.php';
// bootstrap the app
$app = require_once __DIR__.'/../bootstrap/app.php';
$kernel = $app->make(Illuminate\Contracts\Console\Kernel::class);
$kernel->bootstrap();

$user = App\Models\User::where('email','test@example.com')->first();
if (! $user) {
    echo "User not found\n";
    exit(1);
}
$token = $user->createToken('api-token');
echo $token->plainTextToken."\n";
