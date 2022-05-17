import React from 'react';



function Auth() {
    return (
        <div className="auth">
            <h1 className="auth__title">Авторизация</h1>
            <form className="auth__form">
                <input className="auth__form-input" type="text" placeholder="Введите токен" />
                <button type="submit" className="auth__form-button">Войти</button>
            </form>
        </div>
    );
}

export default Auth;