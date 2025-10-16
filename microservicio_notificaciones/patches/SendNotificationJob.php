<?php

namespace App\Jobs;

use Illuminate\Bus\Queueable;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Bus\Dispatchable;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\Mail;
use App\Models\Notification;
use App\Notifications\GenericNotification;

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
        $notification = Notification::find($this->notificationId);
        if (! $notification) {
            Log::warning("Notification {$this->notificationId} not found");
            return;
        }

        try {
            // For email: use Laravel Notification via Mail
            if ($notification->type === 'email') {
                // Send using a simple mailable via Notification system
                Mail::raw($notification->body, function ($message) use ($notification) {
                    $message->to($notification->to)
                            ->subject($notification->subject ?? 'Notification');
                });
            } else {
                // Placeholder: integrate SMS/Push providers here
                Log::info("Would send {$notification->type} to {$notification->to}: {$notification->body}");
            }

            $notification->status = 'sent';
            $notification->error = null;
            $notification->sent_at = now();
            $notification->save();
        } catch (\Exception $e) {
            Log::error('SendNotificationJob failed: '.$e->getMessage());
            $notification->status = 'failed';
            $notification->error = $e->getMessage();
            $notification->save();
        }
    }
}
