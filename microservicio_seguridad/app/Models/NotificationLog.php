<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class NotificationLog extends Model
{
    protected $table = 'notification_logs';

    protected $fillable = ['type','to','subject','body','meta','status','error','sent_at','user_id'];

    protected $casts = [
        'meta' => 'array',
        'sent_at' => 'datetime',
    ];
}
