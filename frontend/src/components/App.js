import React from 'react';
import { Route, Switch, BrowserRouter } from 'react-router-dom';
import Auth from './Auth';
import Main from './Main';

function App() {


  return (
    <>
      <BrowserRouter>
        <Switch>
          <Route exact path="/">
            <Auth />
          </Route>
          <Route path="/main">
            <Main />
          </Route>
        </Switch>
      </BrowserRouter>
    </>
  );
}

export default App;
