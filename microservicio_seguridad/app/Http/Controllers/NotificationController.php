<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\NotificationLog;
use App\Jobs\SendNotificationJob;
use Illuminate\Support\Facades\Validator;
use Illuminate\Support\Facades\Auth;

class NotificationController extends Controller
{
    public function __construct()
    {
        $this->middleware('auth:sanctum');
    }

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

        $userId = Auth::id();

        $log = NotificationLog::create([
            'type' => $data['type'],
            'to' => $data['to'],
            'subject' => $data['subject'] ?? null,
            'body' => $data['body'],
            'meta' => $data['meta'] ?? null,
            'status' => 'pending',
            'user_id' => $userId,
        ]);

        SendNotificationJob::dispatch($log->id);

        return response()->json(['id' => $log->id, 'status' => 'queued'], 201);
    }

    public function status($id)
    {
        $log = NotificationLog::find($id);
        if (! $log) {
            return response()->json(['message' => 'Not found'], 404);
        }
        return response()->json(['id' => $log->id, 'status' => $log->status, 'error' => $log->error]);
    }
}
