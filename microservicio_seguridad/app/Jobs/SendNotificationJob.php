<?php

namespace App\Jobs;

use Illuminate\Bus\Queueable;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Bus\Dispatchable;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\Mail;
use App\Models\NotificationLog;

class SendNotificationJob implements ShouldQueue
{
    use Dispatchable, Queueable;

    public $notificationId;

    public function __construct($notificationId)
    {
        $this->notificationId = $notificationId;
    }

    public function handle()
    {
        $log = NotificationLog::find($this->notificationId);
        if (! $log) {
            Log::warning("Notification {$this->notificationId} not found");
            return;
        }

        try {
            if ($log->type === 'email') {
                Mail::raw($log->body, function ($message) use ($log) {
                    $message->to($log->to)
                            ->subject($log->subject ?? 'Notification');
                });
            } else {
                Log::info("Would send {$log->type} to {$log->to}: {$log->body}");
            }

            $log->status = 'sent';
            $log->error = null;
            $log->sent_at = now();
            $log->save();
        } catch (\Exception $e) {
            Log::error('SendNotificationJob failed: '.$e->getMessage());
            $log->status = 'failed';
            $log->error = $e->getMessage();
            $log->save();
        }
    }
}
