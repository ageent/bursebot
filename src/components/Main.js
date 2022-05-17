import React from 'react';
import account from '../images/account.png';
import github from '../images/github.png';


function Main() {
    return (
        <>
            <header className="header">
                <a href="https://github.com/ageent/bursebot" >
                    <img className="header__git" src={github} />
                </a>
                <nav className="header__nav">
                    <a className="header__link">Войти в песочницу</a>
                    <a className="header__link">Выйти</a>
                </nav>
            </header>
            <main>
                <section className="account">
                    <img src={account} className="account__icon" />
                    <div className="account__column">
                        <h2 className="account__name">Брокерский счет</h2>
                        <p className="account__value">1 000 000 рублей</p>
                    </div>
                </section>

                <section className="table">
                    <div className="table__row">
                        <h2 className="table__heading">Акции</h2>
                        <h2 className="table__heading">Прибыль руб.</h2>
                        <h2 className="table__heading">Прибыль %</h2>
                        <h2 className="table__heading">Ограничения</h2>
                        <h2 className="table__heading table__heading_type_button">Статус</h2>
                    </div>
                    <div className="table__row">
                        <p className="table__column">Сбербанк</p>
                        <p className="table__column">3000 рублей</p>
                        <p className="table__column">+30%</p>
                        <p className="table__column">100 рублей</p>
                        <div className="table__button-container">
                            <button className="table__button">Начать торговлю</button>
                            <button className="table__button">Вывести средства</button>
                            <button className="table__button">Вывести средства сейчас</button>
                        </div>
                    </div>
                    <div className="table__row">
                        <p className="table__column">Яндекс</p>
                        <p className="table__column">1000 рублей</p>
                        <p className="table__column">+10%</p>
                        <p className="table__column">200 рублей</p>
                        <div className="table__button-container">
                            <button className="table__button">Начать торговлю</button>
                            <button className="table__button">Вывести средства</button>
                            <button className="table__button">Вывести средства сейчас</button>
                        </div>
                    </div>
                </section>

                <section className="table">
                    <div className="table__row">
                        <h2 className="table__heading">Акции</h2>
                        <h2 className="table__heading">Прибыль руб.</h2>
                        <h2 className="table__heading">Прибыль %</h2>
                        <h2 className="table__heading">Ограничения</h2>
                        <h2 className="table__heading table__heading_type_button">Статус</h2>
                    </div>
                    <div className="table__row">
                        <p className="table__column">Суммарно</p>
                        <p className="table__column">4000 рублей</p>
                        <p className="table__column">+20%</p>
                        <p className="table__column">300 рублей</p>
                        <div className="table__button-container">
                            <button className="table__button">Вывести все средства</button>
                        </div>
                    </div>
                </section>
            </main >
        </>

    );
}

export default Main;