<?php

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;
use App\Http\Controllers\NotificationController;

Route::get('/health', function () { return response()->json(['status' => 'ok']); });

Route::post('/notifications/send', [NotificationController::class, 'send']);
Route::get('/notifications/{id}/status', [NotificationController::class, 'status']);
