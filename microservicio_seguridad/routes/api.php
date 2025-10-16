<?php

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;
use App\Http\Controllers\UserController;

/*
|--------------------------------------------------------------------------
| API Routes
|--------------------------------------------------------------------------
|
| Here is where you can register API routes for your application. These
| routes are loaded by the RouteServiceProvider within a group which
| is assigned the "api" middleware group. Enjoy building your API!
|
*/


Route::post('/create_user', [UserController::class,'create_user']);
Route::post('/login', [UserController::class,'login'])->name('login');
Route::group(['middleware' => 'auth:sanctum'], function () {
    Route::post('/logout', [UserController::class,'logout']);
    Route::post('/change_password', [UserController::class,'change_password']);

});

 Route::post('forgot_password', [App\Http\Controllers\Auth\ForgotPasswordController::class, 'sendResetLinkEmail']);
 Route::post('reset_password', [App\Http\Controllers\Auth\ResetPasswordController::class, 'reset']);

// Role management
Route::group(['middleware' => ['auth:sanctum']], function () {
    Route::post('/users/{id}/roles/assign', [App\Http\Controllers\RoleController::class, 'assign'])->middleware('role:admin');
    Route::post('/users/{id}/roles/remove', [App\Http\Controllers\RoleController::class, 'remove'])->middleware('role:admin');
    Route::get('/users/{id}/roles', [App\Http\Controllers\RoleController::class, 'listUserRoles'])->middleware('auth:sanctum');
});

// Notifications
Route::group(['middleware' => ['auth:sanctum']], function () {
    Route::post('/notifications/send', [App\Http\Controllers\NotificationController::class, 'send']);
    Route::get('/notifications/{id}/status', [App\Http\Controllers\NotificationController::class, 'status']);
});

// debug route removed (was temporary)

