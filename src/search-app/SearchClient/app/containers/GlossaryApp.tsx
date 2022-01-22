import * as React from 'react';
import { observer } from 'mobx-react'
import SearchPage from '../components/SearchPage';
import { SearchResultStore } from '../store/SearchResultStore';
import { AppState } from '../store/AppState';
import {SearchRequestModel} from "../model/SearchRequestModel";
import MenuBar from "../components/MenuBar";
import {
  EuiFlexGroup,
  EuiFlexItem, EuiPage,
  EuiPageBody,
  EuiPageContent,
  EuiPageContentBody,
  EuiPageHeader, EuiSpacer,
  EuiTitle
} from "@elastic/eui";
import SearchQueryInput from "../components/SearchQueryInput";
import SortSelect from "../components/SortSelect";
import {To} from "react-router";

interface IGlossaryAppProps {
  appState: AppState
}

@observer
export default class GlossaryApp extends React.Component<IGlossaryAppProps, {}> {

  render() {
    const { appState } = this.props;

    return (
        <EuiPage>
          <EuiPageBody component="div">
            <EuiPageContent>
              <EuiPageContentBody>
                <EuiFlexGroup>
                  <EuiFlexItem>
                    <EuiTitle size="l">
                      <h1>Glossary</h1>
                    </EuiTitle>
                  </EuiFlexItem>
                </EuiFlexGroup>
                <EuiSpacer />
                <EuiFlexGroup>
                  <EuiFlexItem>
                    This page will be improved soon. For now, here's links to some common topics:
                  </EuiFlexItem>
                </EuiFlexGroup>
                {appState.topics.map((topic) => (
                    <EuiFlexGroup key={topic}>
                      <EuiFlexItem>
                        <a href={'/?q=' + topic}>{topic}</a>
                      </EuiFlexItem>
                    </EuiFlexGroup>
                ))}
              </EuiPageContentBody>
            </EuiPageContent>
          </EuiPageBody>
        </EuiPage>
    );
  }
}