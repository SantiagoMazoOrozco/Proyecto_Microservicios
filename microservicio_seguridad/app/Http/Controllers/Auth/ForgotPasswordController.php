<?php

namespace App\Http\Controllers\Auth;

use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Password;

class ForgotPasswordController extends Controller
{
    public function sendResetLinkEmail(Request $request){
        $request->validate(['email'=>'required|email']);
        $status = Password::sendResetLink($request->only('email'));

        if($status == Password::RESET_LINK_SENT){
            return response()->json(['message'=> 'Correo de Recuperacion Enviado'], 200);
        }
        else{
            return response()->json(['message' => 'No se pudo enviar el correo. Intente nuevamente'], 400);
        }
    }
}
