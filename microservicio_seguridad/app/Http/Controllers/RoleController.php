<?php

namespace App\Http\Controllers;

use App\Models\User;
use App\Models\Role;
use Illuminate\Http\Request;

class RoleController extends Controller
{
    public function assign(Request $request, $userId)
    {
        $request->validate(['role' => 'required|string']);
        $user = User::findOrFail($userId);
        $role = Role::where('name', $request->role)->firstOrFail();
        $user->assignRole($role);
        return response()->json(['ok' => true]);
    }

    public function remove(Request $request, $userId)
    {
        $request->validate(['role' => 'required|string']);
        $user = User::findOrFail($userId);
        $user->removeRole($request->role);
        return response()->json(['ok' => true]);
    }

    public function listUserRoles($userId)
    {
        $user = User::findOrFail($userId);
        return response()->json(['roles' => $user->roles()->get()]);
    }
}
