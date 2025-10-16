<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\Notification;
use App\Jobs\SendNotificationJob;
use Illuminate\Support\Facades\Validator;

class NotificationController extends Controller
{
    public function send(Request $request)
    {
        $data = $request->only(['type','to','subject','body','meta']);

        $validator = Validator::make($data, [
            'type' => 'required|in:email,sms,push',
            'to' => 'required',
            'subject' => 'nullable|string',
            'body' => 'required|string',
            'meta' => 'nullable|array',
        ]);

        if ($validator->fails()) {
            return response()->json(['errors' => $validator->errors()], 422);
        }

        $notification = Notification::create([
            'type' => $data['type'],
            'to' => $data['to'],
            'subject' => $data['subject'] ?? null,
            'body' => $data['body'],
            'meta' => $data['meta'] ?? null,
            'status' => 'pending',
        ]);

        // Dispatch job (uses queue connection configured in .env)
        SendNotificationJob::dispatch($notification->id);

        return response()->json(['id' => $notification->id, 'status' => 'queued'], 201);
    }

    public function status($id)
    {
        $notification = Notification::find($id);
        if (! $notification) {
            return response()->json(['message' => 'Not found'], 404);
        }
        return response()->json(['id' => $notification->id, 'status' => $notification->status, 'error' => $notification->error]);
    }
}
