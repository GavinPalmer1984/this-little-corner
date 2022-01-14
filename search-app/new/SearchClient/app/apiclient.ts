import axios from 'axios';
import {SearchRequestModel} from "./model/SearchRequestModel";

// __API_URL_ comes from webpack DefinePlugin
declare const __API_URL__: string;
const apiUrl: string = __API_URL__;

const handleErrors = err => {
  console.error(err);
  throw err;
};

const responseData = res => res.data;

const requests = {
  get: (url: string) => axios.get(`${apiUrl}${url}`)
    .then(responseData)
    .catch(handleErrors),
  post: (url: string, data: any) => axios.post(`${apiUrl}${url}`, data)
    .then(responseData)
    .catch(handleErrors),
  put: (url: string, data: any) => axios.put(`${apiUrl}${url}`, data)
    .then(responseData)
    .catch(handleErrors),
  patch: (url: string, data: any) => axios.patch(`${apiUrl}${url}`, data)
    .then(responseData)
    .catch(handleErrors),
  del: (url: string) => axios.delete(`${apiUrl}${url}`)
    .then(responseData)
    .catch(handleErrors)
};

export const searchAPI = {
  search: (request: SearchRequestModel) => {
    const { protocol, pathname, host } = window.location;
    const newQuery = 'q=' + request.query
        + '&sort=' + request.sort
        + '&page=' + request.page
        + '&size=' + request.pageSize;
    const newUrl = protocol + '//' + host + pathname + '?' + newQuery;
    return requests.get('/api/search?' + newQuery).finally(() => {
        window.history.pushState({}, '', newUrl);
      })
    }
}