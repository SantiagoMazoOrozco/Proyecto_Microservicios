<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Notification extends Model
{
    protected $table = 'notifications';

    protected $fillable = ['type','to','subject','body','meta','status','error','sent_at'];

    protected $casts = [
        'meta' => 'array',
        'sent_at' => 'datetime',
    ];
}
