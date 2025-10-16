<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;

class EnsureUserHasRole
{
    public function handle(Request $request, Closure $next, string $role)
    {
        $user = $request->user();
        if (!$user) {
            return response()->json(['message' => 'unauthenticated'], 401);
        }

        if (!method_exists($user, 'hasRole') || !$user->hasRole($role)) {
            return response()->json(['message' => 'forbidden'], 403);
        }

        return $next($request);
    }
}
