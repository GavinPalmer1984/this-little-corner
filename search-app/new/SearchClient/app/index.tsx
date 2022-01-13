import 'todomvc-app-css/index.css';
import * as React from 'react';
import * as ReactDOM from 'react-dom';
import { AppContainer } from 'react-hot-loader';
import { AppState } from './store/AppState';
import { SearchResultStore } from './store/SearchResultStore';

const appState = new AppState();
const todoStore = new SearchResultStore();

const renderApp = () => {
  const App = require('./containers/App').default;

  ReactDOM.render(
    <AppContainer>
      <App appState={appState} searchResultStore={todoStore} />
    </AppContainer>,
    document.getElementById('root')
  );
};

if (module.hot) {
  const reRenderApp = () => {
    renderApp();
  };

  module.hot.accept('./containers/App', () => {
    setImmediate(() => {
      reRenderApp();
    });
  });
}

renderApp();
