<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use App\Models\Role;

class RolesSeeder extends Seeder
{
    public function run()
    {
        collect(['admin','manager','cashier','customer'])->each(function($r){
            Role::firstOrCreate(['name' => $r]);
        });
    }
}
